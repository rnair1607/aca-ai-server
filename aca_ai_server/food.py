"""Food photo -> items + estimated grams. Macros come later from the nutrition DB (D17/D18)."""

from pathlib import Path

from . import images, llm

SYSTEM = (
    "You are a nutrition assistant. Identify each food item in the photo and estimate its "
    "weight in grams. Include sauces, oils and drinks if visible. Do not give calories or macros. "
    "Reply as a list: item - grams - confidence (low/med/high)."
)
PROMPT = "What food is on this plate and roughly how many grams of each?"


def identify(path: str | Path, **kw) -> llm.Reply:
    url = images.to_data_url(images.prepare(path))
    return llm.vision(PROMPT, url, system=SYSTEM, **kw)
