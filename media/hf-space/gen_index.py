#!/usr/bin/env python3
"""Generate a static index.html leaderboard from leaderboard.csv (no CPU/quota needed)."""
import csv
import os
import html

HERE = os.path.dirname(os.path.abspath(__file__))
FAMS = ["time", "access_deny", "memory_label", "injection", "bot_policy"]
FAM_LABEL = {"access_deny": "access-deny", "memory_label": "memory-label"}

rows = list(csv.DictReader(open(os.path.join(HERE, "leaderboard.csv"), encoding="utf-8")))
rows.sort(key=lambda r: -float(r["src"]))


def cell(v):
    f = float(v)
    # shade by score: red(0) -> green(1)
    hue = int(f * 120)  # 0=red,120=green
    return f'<td style="background:hsl({hue},70%,88%)">{f:.3f}</td>'


trows = []
for i, r in enumerate(rows, 1):
    tds = "".join(cell(r[f]) for f in FAMS)
    trows.append(
        f'<tr><td class="rank">{i}</td><td class="sys">{html.escape(r["system"])}</td>'
        f'<td class="src">{float(r["src"]):.3f}</td>'
        f'<td>{float(r["lsu"]):.3f}</td><td>{float(r["isr"]):.3f}</td>{tds}</tr>'
    )

fam_headers = "".join(f"<th>{FAM_LABEL.get(f, f)}</th>" for f in FAMS)
body = "\n".join(trows)

HTML = f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>signalbench leaderboard (IBSC)</title>
<style>
  :root {{ --ink:#1a1a1a; --muted:#666; --line:#e6e6e6; --accent:#2b6cb0; }}
  * {{ box-sizing:border-box; }}
  body {{ font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
         color:var(--ink); line-height:1.6; margin:0; background:#fff; }}
  .wrap {{ max-width:960px; margin:0 auto; padding:40px 20px 72px; }}
  h1 {{ font-size:1.8rem; margin:0 0 .3rem; letter-spacing:-.01em; }}
  .sub {{ color:var(--muted); font-size:1.05rem; margin:0 0 1.2rem; }}
  p {{ margin:.8rem 0; }}
  a {{ color:var(--accent); text-decoration:none; }} a:hover {{ text-decoration:underline; }}
  .table-scroll {{ overflow-x:auto; margin:1.4rem 0; }}
  table {{ border-collapse:collapse; width:100%; font-size:.92rem; }}
  th,td {{ padding:6px 10px; text-align:right; border-bottom:1px solid var(--line); white-space:nowrap; }}
  th {{ font-weight:600; color:var(--muted); text-transform:none; border-bottom:2px solid var(--line); }}
  td.rank {{ color:var(--muted); text-align:right; }}
  td.sys {{ text-align:left; font-family:ui-monospace,Menlo,Consolas,monospace; font-size:.86rem; }}
  td.src {{ font-weight:700; }}
  .note {{ color:var(--muted); font-size:.88rem; }}
  code {{ background:#f3f4f6; padding:1px 5px; border-radius:4px; }}
  @media (prefers-color-scheme: dark) {{
    body {{ background:#0f1115; color:#e6e6e6; }}
    :root {{ --line:#2a2d34; --muted:#9aa0aa; }}
    code {{ background:#1a1d24; }}
    th {{ color:#9aa0aa; }}
  }}
</style></head><body><div class="wrap">

<h1>🛡️ signalbench — In-Band Signal Compliance (IBSC)</h1>
<p class="sub">One metric for prompt injection <em>and</em> temporal blindness.</p>

<p>An LLM agent reads control instructions and ordinary data through the <em>same</em> channel, so
on every turn it must decide, from content alone, whether an in-band instruction is legitimate. It
fails two symmetric ways: <strong>over-compliance</strong> (obeying an illegitimate signal — prompt
injection) and <strong>under-compliance</strong> (ignoring a legitimate one — an injected date, an
access-deny, a <code>do-not-share</code> memory label, a no-automation policy).</p>

<p><strong>Signal-Response Correctness (SRC)</strong> scores both on one axis: the balanced mean of
legitimate-signal uptake (LSU) and illegitimate-signal resistance (ISR). A trivial always-comply or
always-refuse policy scores <strong>0.5</strong> — you only win by adjudicating. <strong>Across 21
systems, none exceeds ~0.85</strong>; capability is non-monotonic (a small model beats much larger
ones); and the five families are all positively correlated (mean Pearson <em>r</em> ≈ 0.73) —
evidence of one underlying ability, not five separate skills.</p>

<div class="table-scroll"><table>
<thead><tr><th>#</th><th style="text-align:left">System</th><th>SRC&#8595;</th><th>LSU</th><th>ISR</th>{fam_headers}</tr></thead>
<tbody>
{body}
</tbody></table></div>

<p class="note">SRC = overall Signal-Response Correctness · LSU = legitimate-signal uptake ·
ISR = illegitimate-signal resistance · then per-family balanced SRC (cell shaded red→green).
All scores: seed 0, 75 items, deterministic action-based grading (no LLM judge).</p>

<p>Links:
<a href="https://github.com/mthamil107/signal-compliance">code / harness</a> ·
<a href="https://huggingface.co/datasets/thamilvendhan/signalbench">dataset + raw responses</a> ·
<a href="https://doi.org/10.5281/zenodo.21223956">DOI 10.5281/zenodo.21223956</a></p>

</div></body></html>
"""

with open(os.path.join(HERE, "index.html"), "w", encoding="utf-8") as f:
    f.write(HTML)
print("wrote index.html", len(HTML), "bytes,", len(rows), "rows")
