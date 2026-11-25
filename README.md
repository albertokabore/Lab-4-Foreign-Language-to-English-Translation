# Lab 4: Foreign Language to English Translation

**Albert Kabore** — PhD Student in Artificial Intelligence, University of the Cumberlands.

Translates the WMT16 Romanian–English test set (1,999 sentences) from English to Romanian with the pre-trained `google-t5/t5-small` model, then scores the output with BLEU (SacreBLEU).

The deliverable is [`Lab4_Machine_Translation.ipynb`](Lab4_Machine_Translation.ipynb). It contains:

- **Introduction**: objectives, scope, and evaluation approach
- **Part A**: a 381-word explanation of neural machine translation (including the heading), under the 500-word limit
- **Part B**: tasks 1–5 (setup, tokenizer/model, dataset, `translate` + `Dataset.map`, BLEU)
- **Part C**: commentary on the commands and an analysis of the BLEU results
- **Final Insights, Recommendations, and Conclusion**: findings and proposed next steps
- **References**

The notebook includes saved outputs, so you can read the results without running it.

The dataset is in [`data/`](data/): the 1,999-pair WMT16 ro-en test set, the same data the reference notebook loads from Hugging Face. [`data/README.md`](data/README.md) gives its source and citation, and `scripts/export_dataset.py` recreates the files.

The Word report is [Lab 4: Foreign Language to English Translation](<Lab 4 - Foreign Language to English Translation.docx>), exported from the executed notebook. It includes the author and affiliation, all narrative sections, code, saved outputs, tables, and references. Its filename uses a hyphen because Windows does not permit a colon; the title inside the report is exactly **Lab 4: Foreign Language to English Translation**.

To regenerate the Word report from the notebook's saved content:

```bash
python -m pip install -r requirements-report.txt
python scripts/export_report.py
```

## Results (WMT16 ro-en test, 1,999 sentences, t5-small)

| Decoding | BLEU (raw) | BLEU (ș/ț-normalized) | CPU time |
|---|---|---|---|
| Greedy (reference configuration) | **25.18** | 30.23 | 496 s |
| Beam search, k = 4 | 25.32 | 30.37 | 4,085 s |

- The raw greedy BLEU is 25.18405390123436, with the same n-gram counts as the reference notebook, so the reproduction is exact.
- The beam − greedy difference is +0.14 (paired bootstrap 95% CI [−0.07, +0.35]); the interval includes zero. Beam was no better than greedy in 11.5% of bootstrap resamples; this fraction is not a formal p-value.
- The +5.05 normalized gain comes from a spelling/Unicode mismatch. The model mainly outputs cedilla ş/ţ while the references use comma-below ș/ț. Separate tokenizer checks show that uppercase Ș/Ş/Ț/Ţ do not survive an encode/decode round trip.
- [`results/translations.csv`](results/translations.csv) holds every system output next to its source and reference.

## Run it

```bash
pip install -r requirements.txt
jupyter notebook Lab4_Machine_Translation.ipynb
```

A CPU is enough. The saved full-set greedy run took about 8 minutes; the optional beam-search extension took another 68 minutes. The notebook uses a GPU automatically if one is available. Timings depend on hardware and caching. For a quick run, set `N_SAMPLES = 200` in the first code cell; the reported full-test-set scores then serve only as a reference.

Based on the [gentlenlp chapter 15 notebook](https://github.com/clulab/gentlenlp/blob/main/notebooks/chap15_translation_en_to_ro.ipynb). That notebook uses `evaluate.load("sacrebleu")`; this lab uses the `sacrebleu` package directly with matching settings.

Although the assignment title says “Foreign Language to English,” Parts A and B explicitly request English to a foreign language. The lab follows those detailed requirements and the supplied English-to-Romanian reference.
