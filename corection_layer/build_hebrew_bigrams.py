#!/usr/bin/env python3
"""
Build Hebrew bigram frequency list from .txt corpora.
Output format:
    word1 word2 count
"""

import argparse
import re
from collections import Counter
from pathlib import Path

HEB_LETTERS = r"א-ת"
NIQQUD_RE = re.compile(r"[\u0591-\u05C7]")
FINAL_MAP = {"ך":"כ","ם":"מ","ן":"נ","ף":"פ","ץ":"צ"}
WORD_RE = re.compile(rf"[{HEB_LETTERS}]+")

def normalize(text: str) -> list[str]:
    text = NIQQUD_RE.sub("", text)
    text = "".join(FINAL_MAP.get(c, c) for c in text)
    return WORD_RE.findall(text)

def process_file(path: Path, counter: Counter):
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return
    words = normalize(text)
    for w1, w2 in zip(words, words[1:]):
        if len(w1) > 1 and len(w2) > 1:
            counter[(w1, w2)] += 1

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("-o", "--output", default="hebrew_bigrams.txt")
    ap.add_argument("--min-count", type=int, default=3)
    args = ap.parse_args()

    counter = Counter()
    for p in map(Path, args.inputs):
        if p.is_dir():
            for f in p.rglob("*.txt"):
                process_file(f, counter)
        else:
            process_file(p, counter)

    with open(args.output, "w", encoding="utf-8") as f:
        for (w1, w2), c in counter.most_common():
            if c >= args.min_count:
                f.write(f"{w1} {w2} {c}\n")

    print(f"Saved {len(counter)} bigrams → {args.output}")

if __name__ == "__main__":
    main()

