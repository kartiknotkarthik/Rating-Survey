# Phase 1: Data Ingestion (Play Store Scraper)

This folder contains the standalone implementation of Phase 1: **Robust Data Ingestion**.

## Features
- **Bypasses 200-review limit**: Uses `continuation_token` orchestration to fetch large batches of reviews.
- **Date Filtering**: Automatically stops fetching once the target lookback period (e.g., 12 weeks) is reached.
- **PII Stripping**: Ensures usernames and profile photos are never stored.
- **Automated CSV Export**: Saves cleaned results into the `/data` directory.

## Usage
Run the script directly:
```bash
python scrape_reviews.py
```

## Dependencies
- `google-play-scraper`
- `pandas`
