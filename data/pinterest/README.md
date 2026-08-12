# Permanent Pinterest CSV tracker

This directory is tracked in git so every future Sentimentalica article/CSV
session begins with the same Pinterest history.

- `PINTEREST_ARTICLE_TRACKER.csv`: one row per published article, comparing its
  current unique content images with the durable ledger.
- `PIN_MEDIA_LEDGER.csv`: one row per exact Media URL ever included in a CSV.
  This is the deduplication source of truth.
- `PINTEREST_BATCH_LEDGER.csv`: one row per CSV batch with handoff and confirmed
  upload state.
- `batches/`: exact durable copies of batches handed to Ksenia or confirmed
  uploaded.

Statuses are deliberately separate:

- **Historical CSV record**: the image was found in an older CSV; handoff and
  upload are not independently confirmed.
- **CSV provided**: the complete batch was handed to Ksenia or its Google Drive
  mirror was confirmed; Pinterest success is not implied.
- **Pinterest upload confirmed**: Ksenia explicitly confirmed the upload.

Before making a requested batch:

```bash
python3 tools/pinterest_tracker.py refresh
python3 tools/pinterest_tracker.py check ARTICLE-SLUG
```

After handing off the validated batch:

```bash
python3 tools/pinterest_tracker.py record-batch PATH.csv --status provided
```

Only after Ksenia confirms the Pinterest upload:

```bash
python3 tools/pinterest_tracker.py record-batch PATH.csv --status uploaded
```

`tools/pin_csv.py mark-provided BATCH-NAME` and `mark-uploaded BATCH-NAME`
perform the same ledger updates for batches built with that utility.
