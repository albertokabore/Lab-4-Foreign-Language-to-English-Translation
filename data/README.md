# Dataset: WMT16 Romanian–English, test split

This folder holds the evaluation data used in `Lab4_Machine_Translation.ipynb`. It is the same dataset the reference notebook ([clulab/gentlenlp `chap15_translation_en_to_ro.ipynb`](https://github.com/clulab/gentlenlp/blob/main/notebooks/chap15_translation_en_to_ro.ipynb)) loads.

| | |
|---|---|
| Source | WMT16 news translation task, Romanian–English (newstest2016) |
| Hugging Face id | `wmt/wmt16`, config `ro-en`, split `test` (the reference notebook calls it `wmt16`, the older id for the same data) |
| Size | 1,999 sentence pairs |
| Domain | News |
| Columns | `id` (row index), `en` (English source), `ro` (human Romanian reference translation) |
| Files | `wmt16_ro-en_test.csv`, `wmt16_ro-en_test.jsonl` (UTF-8; identical content) |

The gentlenlp GitHub repository does not include a copy of the data. Its notebook downloads the data from the Hugging Face Hub when it runs. These files were exported from the Hub with [`scripts/export_dataset.py`](../scripts/export_dataset.py), and nothing in them was edited, sampled or generated. To recreate them:

```bash
python scripts/export_dataset.py
```

Row 0 (`UN Chief Says There Is No Military Solution in Syria` → `Șeful ONU declară că nu există soluții militare în Siria`) matches the first example printed in the reference notebook.

## Citation

Bojar, O., Chatterjee, R., Federmann, C., Graham, Y., Haddow, B., Huck, M., Jimeno Yepes, A., Koehn, P., Logacheva, V., Monz, C., Negri, M., Névéol, A., Neves, M., Popel, M., Post, M., Rubino, R., Scarton, C., Specia, L., Turchi, M., Verspoor, K., & Zampieri, M. (2016). Findings of the 2016 Conference on Machine Translation. *Proceedings of the First Conference on Machine Translation*, 131–198.

For terms of use, see the WMT16 task page (https://www.statmt.org/wmt16/translation-task.html) and the dataset card (https://huggingface.co/datasets/wmt/wmt16). WMT distributes the data for research use.
