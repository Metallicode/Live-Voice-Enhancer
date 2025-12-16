
# Hebrew STT Post-Correction Toolkit (Wordlist + Bigrams + Corrector)

This repository contains a **lightweight, language-aware post-processing toolkit** for improving **Hebrew speech-to-text (STT)** output, especially for:

- impaired or unclear speech
- noisy environments
- realtime or batch STT systems

The approach is **conservative and deterministic**:
- no hallucinating text
- no free rewriting
- corrections are based on **real Hebrew usage statistics**

---

## What This Toolkit Does

Given a raw Hebrew STT transcript (often noisy or partially wrong), the system:

1. **Cleans up** the text (spacing, niqqud, repetitions)
2. **Corrects words** using a frequency dictionary (SymSpell)
3. **Uses context** via bigram frequencies to choose the most likely word sequence
4. Returns **multiple ranked candidates** instead of a single “guessed” sentence

This is ideal for **assistive communication**, where user confirmation matters.

---

## Components Overview

| Script | Purpose |
|------|--------|
| `build_hebrew_wordlist.py` | Builds a Hebrew word-frequency list (unigrams) from `.txt` corpora |
| `build_hebrew_bigrams.py` | Builds Hebrew bigram frequencies (word-pair statistics) |
| `HebrewCorrector.py` | Main correction engine + interactive tester |

---

## Directory Structure

Recommended layout:

```

project/
├── corpora/
│   ├── news.txt
│   ├── subtitles.txt
│   └── books/
│       ├── book1.txt
│       └── book2.txt
│
├── build_hebrew_wordlist.py
├── build_hebrew_bigrams.py
├── HebrewCorrector.py
│
├── hebrew_freq.txt        # generated
├── hebrew_bigrams.txt     # generated
│
└── README.md

````

---

## Requirements

### Python
- Python 3.8+
- UTF-8 locale

### Python packages
```bash
pip install rapidfuzz symspellpy
````

---

## 1️⃣ Building a Hebrew Word Frequency List

### Script

```
build_hebrew_wordlist.py
```

### Purpose

Creates a file of:

```
word frequency
```

Used by SymSpell to correct misspelled or mis-recognized words.

### Usage

From a single file:

```bash
python build_hebrew_wordlist.py corpus.txt
```

From a directory (recursive):

```bash
python build_hebrew_wordlist.py ./corpora/
```

With minimum frequency filter:

```bash
python build_hebrew_wordlist.py ./corpora/ --min-count 5
```

Custom output file:

```bash
python build_hebrew_wordlist.py ./corpora/ -o hebrew_freq.txt
```

### Output example

```
אני 84231
צריך 31244
עזרה 12455
מים 9231
```

---

## 2️⃣ Building Hebrew Bigram Frequencies

### Script

```
build_hebrew_bigrams.py
```

### Purpose

Creates word-pair frequency statistics:

```
word1 word2 frequency
```

These are used to score **contextual correctness**.

### Usage

```bash
python build_hebrew_bigrams.py ./corpora/
```

With frequency threshold:

```bash
python build_hebrew_bigrams.py ./corpora/ --min-count 3
```

Custom output:

```bash
python build_hebrew_bigrams.py ./corpora/ -o hebrew_bigrams.txt
```

### Output example

```
אני צריך 19321
צריך עזרה 8421
מה קורה 9211
```

---

## 3️⃣ HebrewCorrector – Main Correction Engine

### Script

```
HebrewCorrector.py
```

### What It Does

* Cleans noisy STT text
* Suggests word-level corrections
* Uses **unigram + bigram scoring**
* Performs **beam search** to find the most plausible sentence
* Returns **multiple ranked candidates**

### Modes of Operation

| Mode         | What You Get                           |
| ------------ | -------------------------------------- |
| Cleanup only | Text normalization only                |
| + Wordlist   | Spell-like correction                  |
| + Bigrams    | Context-aware correction (recommended) |

---

## Running the Interactive Tester

### Cleanup-only (no corpora)

```bash
python HebrewCorrector.py
```

### With wordlist

```bash
python HebrewCorrector.py --wordlist hebrew_freq.txt
```

### With wordlist + bigrams (recommended)

```bash
python HebrewCorrector.py \
  --wordlist hebrew_freq.txt \
  --bigrams hebrew_bigrams.txt
```

---

## Example Session

Input:

```
> אני צרך מים
```

Output:

```
1. אני צריך מים      [score=12.41]
2. אני צורך מים      [score=-2.13]
3. אני צרך מים       [score=-5.87]
```

The user (or UI) can now **choose the intended meaning**.

---

## Important Design Principles

* ✅ No hallucination
* ✅ No long-range rewriting
* ✅ Corrections are **local and explainable**
* ✅ Multiple options instead of silent “fixes”
* ✅ Suitable for impaired speech use cases

This is intentionally **not** a generative language model.

---

## Integration Example (Code)

```python
from HebrewCorrector import HebrewCorrector

corr = HebrewCorrector(
    wordlist_path="hebrew_freq.txt",
    bigram_path="hebrew_bigrams.txt",
)

raw = "אני צרך מים"
candidates = corr.suggest(raw, n=3)

best = candidates[0].text
```

---

## Recommended Next Steps

* Add a **phrase-preset layer** for assistive use
* Collect real STT outputs from your target speaker
* Tune:

  * `per_word_k`
  * `beam_width`
  * bigram penalties
* Show top 2–3 candidates in a UI instead of auto-accepting

---

## Disclaimer

This toolkit is:

* Experimental
* Not a medical device
* Not clinically validated

It is intended for **research and prototyping** in assistive speech technology.

