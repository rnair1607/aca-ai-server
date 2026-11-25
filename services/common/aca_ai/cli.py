"""CLI: `aca food img1.jpg img2.jpg --save`"""

import argparse
import json
import time
from datetime import datetime, timezone

from . import food
from . import config


def _fmt(t: dict) -> str:
    if not t:
        return ""
    return (
        f"prefill {t.get('prompt_per_second', 0):.0f} tok/s | gen {t.get('predicted_per_second', 0):.0f} tok/s"
        f" | {t.get('prompt_ms', 0) + t.get('predicted_ms', 0):.0f} ms"
    )


def cmd_food(a):
    out = config.DATA_DIR / "evals" / "food" / "runs.jsonl"
    for p in a.images:
        t0 = time.time()
        r = food.identify(p)
        print(f"== {p}  ({time.time() - t0:.1f}s)\n{r.content}\n-- {_fmt(r.timings)}\n")
        if a.save:
            out.parent.mkdir(parents=True, exist_ok=True)
            with out.open("a") as f:
                f.write(
                    json.dumps(
                        {
                            "ts": datetime.now(timezone.utc).isoformat(),
                            "image": str(p),
                            "reply": r.content,
                            "timings": r.timings,
                            "usage": r.usage,
                        }
                    )
                    + "\n"
                )
    if a.save:
        print(f"saved -> {out}")


def main():

    ap = argparse.ArgumentParser(prog="aca")
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("food", help="identify food items + grams from photos")
    f.add_argument("images", nargs="+")
    f.add_argument(
        "--save",
        action="store_true",
        help="append results to $DATA_DIR/evals/food/runs.jsonl",
    )
    f.set_defaults(func=cmd_food)
    a = ap.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
