# TimeDistill: Efficient Long-Term Time Series Forecasting with MLP via Cross-Architecture Distillation

> Ni, Juntong and Liu, Zewen and Wang, Shiyu and Jin, Ming and Jin, Wei. *Proceedings of the 32nd ACM SIGKDD Conference on Knowledge Discovery and Data Mining (KDD '26)*, 2026. [[arXiv]](https://arxiv.org/abs/2502.15016) · [[GitHub]](https://github.com/LingFengGold/TimeDistill)

**Citation key:** `ni2025timedistill` — see [`citation.bib`](./citation.bib)

---

## Problem Statement

Transformer-based and CNN-based models (iTransformer, PatchTST, ModernTCN, TimesNet) deliver strong long-term time series forecasting (LTSF) performance, but their high computational and storage requirements hinder large-scale or latency-sensitive deployment.

Lightweight MLP models are efficient but consistently underperform their complex counterparts. The gap between the two camps raises a key question: **can we combine the efficiency of MLP with the predictive power of Transformers and CNNs?**

The paper argues that naive knowledge distillation (KD) — simply matching predictions — fails because:
1. It risks overfitting to noise in the teacher's predictions.
2. MLP struggles to directly replicate complex teacher patterns (seasonality, trends, periodicity).
3. It ignores intermediate feature-level knowledge.

## Key Contributions

- **First cross-architecture KD framework for LTSF**: teacher = Transformer/CNN; student = MLP.
- Identifies two complementary pattern families that MLP lacks but teachers capture: **multi-scale** (temporal domain) and **multi-period** (frequency domain).
- **Theoretical interpretation**: the distillation loss can be viewed as an upper bound on a specialised *mixup* data-augmentation loss (Theorems 4.1 & 4.2), providing guarantees on generalisation.
- Extensive ablation and versatility experiments showing the framework works with 8 different teachers and 3+ different student architectures.

## Methodology

### Preliminary: Why KD is Useful

A "win ratio" analysis (% of samples where MLP beats the teacher) shows MLP wins ~49.9% of samples on average despite lagging overall. This confirms **complementary strengths** — making distillation valuable even when the teacher is not universally better.

### Multi-Scale Distillation (temporal domain)

Teachers capture coarse-to-fine temporal trends well; MLP fails at most downsampled scales.

Both teacher and student predictions/features are downsampled hierarchically using 1-D convolutions with stride 2, producing $M+1$ scale levels:

$$\hat{\mathbf{Y}}^m = \text{Conv}(\hat{\mathbf{Y}}^{m-1},\; \text{stride}=2), \quad m=1,\dots,M$$

Two MSE-based alignment losses are minimised:

$$\mathcal{L}_{\text{scale}}^{\mathbf{Y}} = \frac{1}{M+1}\sum_{m=0}^{M}\|\hat{\mathbf{Y}}_t^m - \hat{\mathbf{Y}}_s^m\|^2$$

$$\mathcal{L}_{\text{scale}}^{\mathbf{H}} = \frac{1}{M+1}\sum_{m=0}^{M}\|\mathbf{H}_t^m - \mathbf{H}_s^m\|^2 \quad (\text{after dimension alignment via Regressor})$$

Default: $M=3$ scales.

### Multi-Period Distillation (frequency domain)

Teachers capture dominant periodicities accurately; MLP shows large amplitude mismatches in spectrograms.

FFT is applied to predictions/features to obtain amplitude spectra. A temperature-sharpened softmax converts amplitudes into period distributions $\mathbf{Q}$ ($\tau = 0.5$):

$$\mathbf{Q}^{\mathbf{Y}} = \frac{\exp(\mathbf{A}_i / \tau)}{\sum_j \exp(\mathbf{A}_j / \tau)}$$

KL divergence aligns the student's period distribution to the teacher's:

$$\mathcal{L}_{\text{period}}^{\mathbf{Y}} = \text{KL}(\mathbf{Q}_t^{\mathbf{Y}},\; \mathbf{Q}_s^{\mathbf{Y}}), \quad \mathcal{L}_{\text{period}}^{\mathbf{H}} = \text{KL}(\mathbf{Q}_t^{\mathbf{H}},\; \mathbf{Q}_s^{\mathbf{H}})$$

### Overall Loss

$$\mathcal{L} = \mathcal{L}_{\text{sup}} + \alpha \cdot (\mathcal{L}_{\text{scale}}^{\mathbf{Y}} + \mathcal{L}_{\text{period}}^{\mathbf{Y}}) + \beta \cdot (\mathcal{L}_{\text{scale}}^{\mathbf{H}} + \mathcal{L}_{\text{period}}^{\mathbf{H}})$$

The teacher is **frozen** throughout. The student is a channel-independent 2-layer MLP with hidden dimension 512, combined with a decomposition scheme.

### Theoretical Link to Mixup

**Theorem 4.1** (multi-scale): $\mathcal{L}_{\text{sup}} + \eta\,\mathcal{L}_{\text{scale}} \geq \mathcal{L}_{\text{aug}}$, where $\mathcal{L}_{\text{aug}}$ is the loss on mixup-augmented targets $\mathbf{Y}' = \lambda\mathbf{Y} + (1-\lambda)\hat{\mathbf{Y}}_t$ with $\lambda = 1/(1+\eta)$.

**Theorem 4.2** (multi-period): analogous result in KL-divergence for period distributions.

This implies distillation acts as soft label augmentation — enhancing generalisation, stabilising training dynamics, and explicitly injecting multi-scale/multi-period structure.

## Results

### Main Results (8 benchmarks, averaged over prediction lengths 96/192/336/720)

| Metric vs. | MSE Improvement |
|---|---|
| Standalone MLP | up to **18.6%** |
| Teacher (ModernTCN) | up to **5.4%** |
| Teacher (iTransformer) | competitive / better on most |

TimeDistill outperforms all baselines on **7/8 datasets** (MSE) and **all 8 datasets** (MAE). Default teacher: **ModernTCN**.

### Efficiency (ECL dataset)

| Model | Inference time (relative) | Parameters (relative) |
|---|---|---|
| TimeDistill (MLP) | **1×** (baseline) | **1×** (1.08 M) |
| iTransformer | ~3.3× | ~5× |
| ModernTCN | ~5.7× | ~122× |
| PatchTST | ~7.1× | ~5× |
| Autoformer | ~179× | ~14× |

Up to **7× faster inference** and **130× fewer parameters** than teacher models.

### Versatility

- **Different teachers**: Works with all 8 tested teachers (iTransformer, ModernTCN, TimeMixer, PatchTST, MICN, FEDformer, TimesNet, Autoformer). Average MLP improvement of ~8–11% depending on teacher.
- **Different students**: TSMixer (+6.3% MSE), LightTS (+8.0%), FITS (+4.0%) — all improve under TimeDistill.
- **Different look-back lengths**: Consistently improves MLP across all window lengths tested.

### Ablation Study (Table 4, teacher = ModernTCN, ECL)

| Configuration | MSE |
|---|---|
| Full TimeDistill | **0.157** |
| Teacher (ModernTCN) | 0.167 |
| Standalone MLP | 0.173 |
| w/o $\mathcal{L}_{\text{period}}$ | 0.157 |
| w/o $\mathcal{L}_{\text{scale}}$ | 0.161 |
| w/o $\mathcal{L}^{\mathbf{H}}$ (feature-level) | 0.162 |
| w/o $\mathcal{L}^{\mathbf{Y}}$ (prediction-level) | 0.157 |
| w/o $\mathcal{L}_{\text{sup}}$ (supervised only KD) | 0.165 |

Each distillation component contributes; removing $\mathcal{L}_{\text{sup}}$ still beats standalone MLP.

## Limitations & Potential Weaknesses

- **Teacher dependency**: A weak teacher can degrade student performance (e.g., Autoformer on Solar: −29% MAE after distillation). Selecting a good teacher remains a practical challenge.
- **Periodic/multi-scale structure assumed**: TimeDistill is best suited for datasets with strong periodicities. Although the mixup view provides some generality, purely aperiodic or highly irregular series (e.g., volatile financial tick data) may benefit less.
- **Channel-independent student**: The student MLP processes each variable independently. While distillation implicitly transfers some multivariate correlations (Figure 9), it cannot match channel-dependent teachers' full cross-variable expressiveness.
- **Offline distillation only**: Teacher must be pre-trained; the framework does not support online/joint training with the teacher, which limits adaptability to distribution shifts.
- **Hyperparameter sensitivity**: $\alpha$, $\beta$ require dataset-specific tuning (e.g., large $\alpha$ helps on ETT but hurts on ECL/Solar). In practice, a grid search over $\{0.1, 0.5, 1, 2\}$ is needed per dataset.

## Personal Notes

- The **mixup interpretation** is elegant — it reframes distillation as data augmentation in label space, connecting to well-understood regularisation theory and providing a clean theoretical foundation beyond empirical motivation.
- The **complementary strengths** framing (high win ratio despite lower overall MSE) is a convincing justification for KD even when the teacher is not uniformly superior. This is a more subtle argument than the usual "teacher is better, student is smaller."
- The multi-period loss (KL on FFT amplitudes) is novel in LTSF distillation; most prior KD work in time series used only prediction-level MSE alignment.
- From a **quant/finance lens**: the efficiency story (7× faster inference, 130× fewer params) is highly compelling for deployment in latency-sensitive trading systems. Channel-independence also makes the framework interpretable variable-by-variable.
- **Future direction**: distilling from time series foundation models (TimesFM etc.) as teachers is an interesting open problem flagged by the authors — could be a significant capability jump.
- The theoretical bound (Thm 4.1) is an *upper bound* on the augmentation loss — not a tight characterisation. Whether the bound is practically informative (i.e., tight enough to predict behaviour) is not explored.
