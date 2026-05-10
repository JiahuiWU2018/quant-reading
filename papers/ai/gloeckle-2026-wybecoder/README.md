# WybeCoder: Verified Imperative Code Generation

> Gloeckle, Fabian\*, Bakšys, Mantas\*, Feher, Darius, Zheng, Kunhao, Hayat, Amaury, Holden, Sean B., Synnaeve, Gabriel, O'Hearn, Peter. *Preprint*, 2026. [[arXiv]](https://arxiv.org/abs/2603.29088) · [[GitHub]](https://github.com/facebookresearch/wybecoder) · [[Project Page]](https://facebookresearch.github.io/wybecoder/)

\* Equal contribution · FAIR at Meta, CERMICS/ENPC, University of Cambridge, UCL

**Citation key:** `gloeckle2026wybecoder` — see [`citation.bib`](./citation.bib)

---

## Problem Statement

LLMs have made rapid progress in code generation and formal theorem proving, but **automated software verification** — proving that a program is correct with respect to a formal specification — has lagged behind. The main challenges are:

- Writing loop invariants is difficult and highly non-trivial even for experts.
- SMT solvers handle simple goals automatically but get stuck on complex ones.
- Interactive Lean proofs are expressive but require expert guidance.

Prior agentic approaches plateau quickly as compute scales. This paper proposes **WybeCoder**, which addresses these gaps by co-evolving code, invariants, and proofs in a single agent loop.

---

## Key Contributions

1. **Hybrid Verification Loop** — combines SMT solvers (cvc5) with interactive Lean 4 proofs. SMT discharges easy goals automatically; hard residual goals are tackled in Lean.
2. **Prove-as-you-generate** — code, loop invariants, and proofs are synthesised and refined jointly rather than sequentially.
3. **Subgoal Decomposition** — verification conditions are split into independent subgoals dispatched to parallel sub-agents, with conflict-driven method modification across iterations.
4. **Imperativeness Judge** — an LLM-based judge filters solutions that "cheat" by leaking the specification or implementing a functional rather than imperative style.
5. **New benchmarks** — Verina and Clever are translated from Lean functional style to imperative Velvet/Loom format (Clever-Loom).
6. **No scaling plateau** — consistent performance gains up to ~1,200 model calls per problem, far beyond the plateau reported in prior work.

---

## Methodology

### Target Language: Velvet (via Loom)

WybeCoder generates code in **Velvet**, a Dafny-like imperative DSL embedded in Lean 4 through the [Loom](https://github.com/faabian/loom) framework. A Velvet method looks like:

```lean
method binarySearch (arr : Array Int) (target : Int) return (idx : Int)
  requires sorted arr
  ensures idx ≥ 0 → arr[idx] = target
do
  let mut lo := 0
  let mut hi := arr.size
  while lo < hi
    invariant 0 ≤ lo ∧ lo ≤ hi ∧ hi ≤ arr.size
    invariant ∀ i < lo, arr[i] < target
    invariant ∀ i ≥ hi, arr[i] > target
  do
    ...
```

The Loom compiler auto-generates verification conditions (VCs) from the annotations. Easy VCs are dispatched to cvc5; remaining goals become Lean proof obligations.

### Agent Pipeline

```
Problem spec
    │
    ▼
┌─────────────────────────────┐
│  Generate Velvet code +     │
│  loop invariants (LLM)      │
└────────────┬────────────────┘
             │
             ▼
        cvc5 SMT solver
       /              \
   solved          residual goals
                        │
                        ▼
              ┌──────────────────┐
              │  Lean 4 REPL     │
              │  interactive     │
              │  proof attempt   │
              └────────┬─────────┘
                       │
              success / failure + feedback
                       │
                       ▼
              refine code / invariants
              (iterative loop, up to T turns)
```

### Two Agent Strategies

| Strategy | Description | Parallelism |
|----------|-------------|-------------|
| **Sequential Agent** | Single-agent turn-based refinement loop | $k$ independent attempts (pass@$k$) |
| **Subgoal Decomposition** | Splits VCs into subgoals; dispatches parallel sub-agents per subgoal; merges results | Up to 128 sub-agents per problem |

---

## Results

### Verina (189 problems)

| Strategy | Model | Budget | Solve Rate |
|----------|-------|--------|-----------|
| Baseline | DS Prover V2 7B | 64×1 | 20.0% |
| Sequential | GPT-OSS-120B | 16×4 | 30.2% |
| Sequential | Gemini 3 Pro | 32×16 | 55.6% |
| Sequential | Claude 4.5 Sonnet | 32×16 | 63.3% |
| Sequential | GPT-5 | 32×16 | 64.6% |
| **Sequential** | **Claude 4.5 Opus** | **32×16** | **74.1%** |
| Subgoal Decomp. | Claude 4.5 Opus | 8×128 | 66.7% |

### Clever-Loom (161 problems)

| Strategy | Model | Budget | Solve Rate |
|----------|-------|--------|-----------|
| Baseline | COPRA (Claude 3.7) | 600s | 8.7% |
| Sequential | GPT-5 | 32×16 | 53.8% |
| **Sequential** | **Claude 4.5 Opus** | **32×16** | **62.1%** |

### Sorting Algorithm Verification

Complex sorting algorithms verified end-to-end:

| Algorithm | Components verified |
|-----------|-------------------|
| Heapsort | Heapify ✅, Maxheap ✅, Sort ✅ — required 357 sub-agents |
| Quicksort | Partition ✅, Sort ✅ (Step ✗) |
| Mergesort | Mergeruns ✅, Sort ✅ (Mergepass ✗) |
| Insertion/Bubble/Selection Sort | ✅ |

---

## Limitations & Open Questions

- **Recursive algorithms** remain hard (Recursive Quicksort fails entirely); the loop-invariant approach is inherently iterative.
- **Disproof** — the sequential agent can detect buggy specs; subgoal decomposition currently cannot.
- **Language scope** — Velvet is purpose-built; transferring to general languages (C, Rust) is future work.
- **Cost** — 32 turns × 16 agents at frontier-model rates is non-trivial; the approach is currently research-scale.
- **Quant relevance** — direct applicability to quant finance is limited, but the framework is relevant for *verified numerical algorithms* (sorting, searching, fixed-point arithmetic) and could inform correctness guarantees in execution systems.

---

## Reproduction

- [x] Notebook: [`notebooks/wybecoder_concepts.ipynb`](./notebooks/wybecoder_concepts.ipynb)
  - Walks through the core WybeCoder concepts in pure Python/pseudocode (no Lean required).
  - Demonstrates the hybrid SMT + Lean verification loop conceptually.
  - Shows the subgoal decomposition strategy with a toy example.
  - Includes a worked example of invariant generation for a simple loop.

---

## Personal Notes & Critique

The *prove-as-you-generate* framing is compelling — it avoids the brittleness of post-hoc verification by making correctness a first-class citizen during synthesis. The subgoal decomposition is the key engineering insight: it converts a hard sequential dependency (the full proof) into a mostly-parallel workload that scales naturally with compute.

The plateau-breaking claim is well supported empirically. The main open question is generalisation beyond Velvet — Dafny and Frama-C have much larger user bases, and it would be interesting to see whether the hybrid SMT/Lean loop transfers there.

For quant finance specifically, the most relevant thread is **verified numerical routines**: pricing kernels, sorting/searching in order book matching engines, and fixed-point arithmetic in embedded execution systems are all candidates where formal correctness proofs would add real value.

---

*Added: 2026-04-30*
