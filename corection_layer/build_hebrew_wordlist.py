#!/usr/bin/env python3
"""
Build a Hebrew word-frequency list from one or more .txt corpora.

Output format (UTF-8):
    word<space>count

Suitable for SymSpell.
"""

import argparse
import re
from collections import Counter
from pathlib import Path


# -----------------------------
# Hebrew normalization
# -----------------------------

HEB_LETTERS = r"א-ת"
NIQQUD_RE = re.compile(r"[\u0591-\u05C7]")  # cantillation + niqqud

FINAL_MAP = {
    "ך": "כ",
    "ם": "מ",
    "ן": "נ",
    "ף": "פ",
    "ץ": "צ",
}

WORD_RE = re.compile(rf"[{HEB_LETTERS}]+")


def strip_niqqud(text: str) -> str:
    return NIQQUD_RE.sub("", text)


def normalize_final_letters(text: str) -> str:
    """Convert final letters to base forms for dictionary consistency."""
    return "".join(FINAL_MAP.get(ch, ch) for ch in text)


def normalize_text(text: str) -> str:
    text = strip_niqqud(text)
    text = normalize_final_letters(text)
    return text


# -----------------------------
# Corpus processing
# -----------------------------

def process_file(path: Path, counter: Counter):
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        print(f"Skipping {path}: {e}")
        return

    text = normalize_text(text)

    for word in WORD_RE.findall(text):
        if len(word) > 1:   # drop single-letter noise (ו, ב, ל, etc.)
            counter[word] += 1


def build_wordlist(input_paths, min_count: int) -> Counter:
    counter = Counter()
    for p in input_paths:
        if p.is_dir():
            for txt in p.rglob("*.txt"):
                process_file(txt, counter)
        else:
            process_file(p, counter)

    # Filter low-frequency noise
    return Counter({w: c for w, c in counter.items() if c >= min_count})


# -----------------------------
# Main
# -----------------------------

def main():
    ap = argparse.ArgumentParser(description="Build Hebrew word frequency list from text corpora")
    ap.add_argument("inputs", nargs="+", help="Input .txt files or directories")
    ap.add_argument("-o", "--output", default="hebrew_freq.txt", help="Output word list file")
    ap.add_argument("--min-count", type=int, default=2, help="Minimum word frequency to keep")
    args = ap.parse_args()

    input_paths = [Path(p) for p in args.inputs]

    counter = build_wordlist(input_paths, min_count=args.min_count)

    with open(args.output, "w", encoding="utf-8") as f:
        for word, count in counter.most_common():
            f.write(f"{word} {count}\n")

    print(f"Done.")
    print(f"Words written: {len(counter)}")
    print(f"Output file: {args.output}")


if __name__ == "__main__":
    main()

