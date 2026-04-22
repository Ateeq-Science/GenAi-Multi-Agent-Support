#!/usr/bin/env bash
set -e

python -m app.db.seed_data
python -m app.ingestion.pdf_ingest
streamlit run app/ui.py
