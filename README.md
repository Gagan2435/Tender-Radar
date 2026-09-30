# Tender Radar

Crawls public EU procurement notices (TED API), cleans and de-duplicates them, stores them in a database
(SQLite by default, PostgreSQL optional), classifies each tender into a sector, and shows a Django dashboard with
Python (matplotlib) charts, search/filters and a JSON API. Inspired by government-tender analytics products.

## Run (Windows / VS Code terminal, Python 3.10+)
```
python -m venv venv
venv\Scripts\python -m pip install -r requirements.txt
venv\Scripts\python run.py
```
`run.py` migrates the DB, crawls, prints the classifier accuracy, opens http://127.0.0.1:8000.
No internet? `venv\Scripts\python run.py --sample` uses clearly-labelled SYNTHETIC data.
Tests: `venv\Scripts\python manage.py test`

## Pipeline
TED API (public, keyless JSON) -> `sources.py` (multilingual parsing, pagination, fallbacks) -> `pipeline.py`
(clean, validate, dedupe on source+ref) -> DB (`models.py`, indexes, unique constraint) ->
`classifier.py` (Naive Bayes from scratch; labels from CPV codes, predicts sector where missing) ->
`views.py` (ORM aggregation, filters, pagination, PNG charts, JSON API) -> dashboard.

## PostgreSQL (optional)
Install PostgreSQL, create a database, copy `.env.example` to `.env`, fill the `PG*` values, run again.

## Honest notes
- Sample data is synthetic; its classifier accuracy is meaningless. Quote only the accuracy printed on REAL TED data.
- Public API: keep request volume small.
