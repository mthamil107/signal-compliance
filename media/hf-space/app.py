"""signalbench leaderboard — In-Band Signal Compliance (IBSC).

A Hugging Face Space that renders the SRC leaderboard for 21 LLM systems. Data is bundled
(leaderboard.csv) so the Space has no network dependency.
"""
import gradio as gr
import pandas as pd

RAW = pd.read_csv("leaderboard.csv")

# Prettier column names + ordering for display.
DISPLAY_COLS = {
    "system": "System",
    "src": "SRC ↓",
    "lsu": "LSU",
    "isr": "ISR",
    "time": "time",
    "access_deny": "access-deny",
    "memory_label": "memory-label",
    "injection": "injection",
    "bot_policy": "bot-policy",
}

df = RAW[list(DISPLAY_COLS)].rename(columns=DISPLAY_COLS)
df = df.sort_values("SRC ↓", ascending=False).reset_index(drop=True)
df.insert(0, "#", range(1, len(df) + 1))

INTRO = """
# signalbench — In-Band Signal Compliance (IBSC)

**One metric for prompt injection *and* temporal blindness.** An LLM agent reads control
instructions and ordinary data through the *same* channel, so on every turn it must decide, from
content alone, whether an in-band instruction is legitimate. It fails two symmetric ways:
**over-compliance** (obeying an illegitimate signal — prompt injection) and **under-compliance**
(ignoring a legitimate one — an injected date, an access-deny, a `do-not-share` memory label, a
no-automation policy).

**Signal-Response Correctness (SRC)** scores both on one axis: the balanced mean of
legitimate-signal uptake (LSU) and illegitimate-signal resistance (ISR). A trivial always-comply
or always-refuse policy scores **0.5** — you only win by adjudicating.

**Headline:** across 21 systems, **none exceeds ~0.85**, capability is non-monotonic (a small
model beats much larger ones), and the five families are all positively correlated
(mean Pearson *r* ≈ 0.73) — evidence of one underlying ability, not five separate skills.
"""

FOOTER = """
---
**Columns:** SRC = overall Signal-Response Correctness · LSU = legitimate-signal uptake ·
ISR = illegitimate-signal resistance · then per-family balanced SRC. All scores: seed 0, 75 items,
deterministic action-based grading (no LLM judge).

**Links:** [code / harness](https://github.com/mthamil107/signal-compliance) ·
[dataset + raw responses](https://huggingface.co/datasets/thamilvendhan/signalbench) ·
[DOI 10.5281/zenodo.21223956](https://doi.org/10.5281/zenodo.21223956)
"""

score_cols = [c for c in df.columns if c not in ("#", "System")]

with gr.Blocks(title="signalbench leaderboard (IBSC)", theme=gr.themes.Soft()) as demo:
    gr.Markdown(INTRO)
    gr.Dataframe(
        value=df,
        datatype=["number", "str"] + ["number"] * len(score_cols),
        interactive=False,
        wrap=True,
    )
    gr.Markdown(FOOTER)

if __name__ == "__main__":
    demo.launch()
