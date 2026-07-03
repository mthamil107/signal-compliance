# IBSC Paper — Build Instructions

LaTeX source for **In-Band Signal Compliance: One Metric for Prompt Injection and
Temporal Blindness** (Thamilvendhan Munirathinam).

## Files

| File | Purpose |
|------|---------|
| `main.tex` | The full paper (standard `article` class, `booktabs` tables). |
| `refs.bib` | Bibliography (12 entries; author's own prior work is marked). |
| `README.md` | This file. |

The paper is self-contained: no external figures, no custom `.sty` files. It
compiles with a stock TeX Live / MiKTeX install.

## Build

From this directory:

```bash
pdflatex main
bibtex   main
pdflatex main
pdflatex main
```

This produces `main.pdf`. The two trailing `pdflatex` passes resolve the
`\cite`/`\ref` cross-references and the bibliography.

### Using latexmk (equivalent, one command)

```bash
latexmk -pdf main.tex
```

### Clean auxiliary files

```bash
latexmk -c            # if using latexmk
# or manually:
rm -f main.aux main.bbl main.blg main.log main.out
```

## arXiv submission

arXiv runs the same `pdflatex` + `bibtex` sequence. Upload `main.tex`, `refs.bib`,
and the generated `main.bbl` (arXiv does not always run BibTeX, so include the
`.bbl`):

```bash
pdflatex main && bibtex main   # generates main.bbl
# then submit: main.tex, refs.bib, main.bbl
```

No other assets are required.

## Numbers

All results in the paper are from the audited study run of **2026-07-03**
(6 models, 2 vendors, 75 items/model, single seed). The raw per-item responses
that back every table are stored in `../results/*.json` in the repository root.

## License

Apache-2.0. Code and benchmark: <https://github.com/mthamil107/signal-compliance>.
