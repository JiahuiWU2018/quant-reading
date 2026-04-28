# quant-reading

A curated collection of research paper summaries, critiques, and model reproductions in quantitative finance and related areas.

## Topics

| Topic | Description |
|---|---|
| [timeseries](papers/timeseries/README.md) | Time series forecasting, return prediction |

## How to Navigate

- Each paper lives under `papers/<topic>/<author-year-short-title>/`
- Every paper folder contains:
  - `README.md` — summary, methodology, critique, personal notes
  - `citation.bib` — BibTeX entry for the paper
  - `notebooks/` — reproductions or example usage (where applicable)
- [`CITATIONS.bib`](CITATIONS.bib) — master BibTeX file aggregating all entries

## Adding a New Paper

1. Pick the appropriate topic folder (or create a new one).
2. Create a folder named `author-year-short-title` (e.g. `kyle-1985-continuous-auctions`).
3. Copy [`.github/PAPER_TEMPLATE.md`](.github/PAPER_TEMPLATE.md) to `README.md` and fill it in.
4. Add a `citation.bib` and append the same entry to the root [`CITATIONS.bib`](CITATIONS.bib).
5. Add notebooks to `notebooks/` if reproducing results.

## Shared Utilities

Common data helpers and utilities shared across reproductions live in [`shared/`](shared/).

---

*All model code reproduced here is for educational purposes. Please respect the licences of the original repositories.*
Personal repository for quant finance reading notes and model reproduction experiments.
