"""Run 3 fixed prompts against an OpenAI-compatible server. Usage: LLM_BASE_URL=http://localhost:8081/v1 python scripts/bench_prompts.py <label>"""

import json, sys, time
from pathlib import Path
from aca_ai import llm, config

doc = Path("/usr/share/common-licenses/GPL-3").read_text()[:9000]  # ~2.3k tokens
PROMPTS = {
    "short": (
        "In 3 bullet points, what is a stock's P/E ratio and why does it matter?",
        False,
    ),
    "long": (
        f"Document:\n{doc}\n\nQuestion: Summarise in 4 bullets what this licence requires "
        "when someone distributes modified versions. Quote section numbers.",
        False,
    ),
    "reason": (
        "A portfolio has 3 holdings: A 50% (+10% this month), B 30% (-5%), C 20% (+2%). "
        "What was the portfolio return? Show the working, then say which holding drove it.",
        True,
    ),
}
label = sys.argv[1] if len(sys.argv) > 1 else "run"
out = config.DATA_DIR / "evals" / "llm-bench" / f"{label}.jsonl"
out.parent.mkdir(parents=True, exist_ok=True)
for name, (prompt, think) in PROMPTS.items():
    t0 = time.time()
    r = llm.chat([{"role": "user", "content": prompt}], thinking=think, max_tokens=1500)
    t = r.timings
    print(
        f"\n=== {label} / {name}  {time.time()-t0:.1f}s | prefill {t.get('prompt_per_second',0):.0f} | gen {t.get('predicted_per_second',0):.0f} tok/s\n{r.content[:1200]}"
    )
    out.open("a").write(
        json.dumps({"label": label, "prompt": name, "reply": r.content, "timings": t})
        + "\n"
    )
print(f"\nsaved -> {out}")
