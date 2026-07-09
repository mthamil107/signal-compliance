# JOSS submission — checklist & timing

Target: **Journal of Open Source Software (JOSS)** — free, fully remote, peer-reviewed,
reviews the *software* (not novelty). Gives a citable DOI + a real peer-reviewed publication.

## ⏰ Timing (the one gate)
JOSS (2026 policy) requires **≥ 6 months of public repository history** before submission.
This repo went public 2026-07. **Earliest eligible submission: ~2026-01 → 2027-01.** Keep the
repo public and maintained until then; the clock is already running.

## What's ready (in `paper/joss/`)
- [x] `paper.md` — the JOSS paper (~600 words; summary, statement of need, comparison, research use, **AI-usage disclosure**).
- [x] `paper.bib` — references (AgentDojo, InjecAgent, IFEval, Zenodo DOI).

## Eligibility checklist (JOSS review criteria)
- [x] **OSI license** — Apache-2.0 (`LICENSE`).
- [x] **Public VCS repo**, browsable, open issues/PRs — GitHub.
- [x] **Automated tests** — 52 tests (`tests/`, `pytest`).
- [x] **Documentation** — `README.md`, `docs/`, docstrings, usage examples.
- [x] **Contribution guidelines** — `CONTRIBUTING.md`.
- [x] **Substantial, feature-complete** — metric + 5 families + action-based grader + providers + CLI (not a thin wrapper).
- [x] **Statement of need** — in `paper.md`.
- [x] **AI-usage disclosure** — in `paper.md` (required by JOSS 2026).
- [ ] **6-month public history** — pending (see Timing).
- [ ] **ORCID** — add yours to `paper.md` frontmatter before submitting (register free at orcid.org).

## How to submit (when eligible)
1. Register an **ORCID** (orcid.org) and put it in `paper.md`.
2. Cut a tagged **release** of the version you're submitting.
3. Go to **https://joss.theoj.org** → *Submit a paper* → give the repo URL + release version.
4. An editor assigns reviewers; review happens **openly on a GitHub issue** (checklist-based).
5. Address reviewer comments (JOSS allows Minor/Major Revisions, no hard reject); on accept you get a **DOI + a peer-reviewed publication**.

First-pass review typically starts within ~2–4 weeks. Fully remote; no travel; no fee.

## Note
JOSS credentials the *software* (signalbench), not the IBSC research findings. Pursue a
findings venue (e.g. DMLR, a remote-friendly workshop) separately for the *research* claims.
