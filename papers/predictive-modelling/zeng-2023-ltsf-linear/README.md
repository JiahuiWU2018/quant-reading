# Are Transformers Effective for Time Series Forecasting?

> Zeng, Ailing and Chen, Muxi and Zhang, Lei and Xu, Qiang. *Proceedings of the AAAI Conference on Artificial Intelligence*, 2023. [[arXiv]](https://arxiv.org/abs/2205.13504) · [[GitHub]](https://github.com/cure-lab/LTSF-Linear)

**Citation key:** `zeng2023transformers` — see [`citation.bib`](./citation.bib)

---

## Problem Statement

Transformer-based models (Informer, Autoformer, FEDformer, Pyraformer) had become the dominant approach for Long-Term Time Series Forecasting (LTSF). This paper asks a pointed question: **are these complex architectures actually necessary, or does their self-attention mechanism actively harm temporal dependency modelling?**

The core concern is that self-attention is *permutation-invariant* — it treats the input as a set, discarding temporal order unless positional encodings are added, which may be insufficient for capturing fine-grained sequential structure.

## Key Contributions

- Demonstrates that a family of simple linear models (**LTSF-Linear**) outperforms all existing Transformer-based LTSF methods across most benchmarks, often by a large margin.
- Provides an empirical and analytical argument for why self-attention is poorly suited to long-term temporal dependencies.
- Introduces a lightweight benchmark covering 9 real-world datasets.

## Methodology

Three models form the **LTSF-Linear** family. All map a look-back window of length $L$ directly to a forecast horizon of $T$:

### Linear

The simplest possible baseline — a single learned linear projection per channel:

$$\hat{X}_t = W \cdot X_t, \quad W \in \mathbb{R}^{T \times L}$$

### NLinear (Normalisation-Linear)

Addresses distribution shift between train and test sets. The last observed value is subtracted before the linear layer and added back afterwards:

$$\hat{X}_t = W \cdot (X_t - x_{t,L}) + x_{t,L}$$

This simple normalisation is surprisingly effective when the dataset has a non-stationary mean.

### DLinear (Decomposition-Linear)

Inspired by the decomposition in Autoformer/FEDformer. A moving average kernel separates the input into **trend** and **seasonal** components; each gets its own linear layer:

$$X_\text{trend} = \text{MovingAvg}(X_t), \quad X_\text{seasonal} = X_t - X_\text{trend}$$
$$\hat{X}_t = W_\text{seasonal} \cdot X_\text{seasonal} + W_\text{trend} \cdot X_\text{trend}$$

Default kernel size: 25.

### Why linear works

- **O(1) signal traversal path**: every output token sees every input token directly with a single matrix multiply, whereas Transformers rely on multi-hop attention.
- **No permutation invariance problem**: the weight matrix implicitly encodes position.
- **Interpretability**: learned weights can be visualised to reveal periodic patterns in the data.

## Results & Limitations

On multivariate forecasting (ETTh1, ETTh2, ETTm1, ETTm2, Exchange, Weather, ILI, Traffic, Electricity), **DLinear beats all Transformer variants on the majority of settings** (MSE / MAE).

| Model | Params | MACs (720-step) | Relative MSE vs best Transformer |
|-------|--------|-----------------|----------------------------------|
| Linear | ~1 K | ~1 K | ↓ significantly |
| DLinear | ~2 K | ~2 K | ↓ significantly |
| Autoformer | ~11 M | ~1 B | baseline |

**Limitations:**
- Linear models assume a fixed, stationary relationship between positions — may struggle with highly irregular or event-driven series (e.g. tick data, earnings announcements).
- No probabilistic forecasts; the models produce point predictions only.
- The benchmark datasets are all low-frequency (hourly / daily); performance on high-frequency financial data is unexplored.
- Later work (PatchTST, TimesNet, iTransformer) has partially closed the gap or surpassed DLinear on some tasks.

## Reproduction

- [x] Notebook: [`notebooks/ltsf_linear_demo.ipynb`](./notebooks/ltsf_linear_demo.ipynb)
  - Implements Linear, NLinear, DLinear from scratch in PyTorch.
  - Demonstrates training on synthetic data and the ETTh1 dataset.
  - Visualises DLinear weights to show periodicity detection.

## Personal Notes & Critique

The central message is well-supported: the community had been chasing architectural complexity when the task itself is relatively linear. The decomposition idea in DLinear is elegant and cheap.

One important caveat: the paper tests on *smooth, relatively stationary* multivariate series. For equity returns — which are near-IID with heavy tails — the advantage of any sequential model over a baseline is much less clear. The interesting follow-up question for quant applications is whether the decomposition can be adapted to handle regime changes or non-stationarity more robustly.

---

*Added: 2026-04-26*
