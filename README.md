# SaaS Onboarding Dashboard

A small analytics dashboard built from a synthetic SaaS onboarding dataset (100 signups across Starter / Pro / Enterprise plans, 13 countries, Jan–Apr 2024). Ships in two flavors:

- **`dashboard.html`** — fully standalone HTML file. No server, no Python. Double-click to view.
- **`dashboard.py`** — Streamlit version, same charts, live-reloads while you edit.

Styled with an Untitled UI-inspired palette (Inter typography, soft cards, purple `#7F56D9` primary).

## What's in it

Top row: three KPI cards — Total MRR, Total Users, Avg MRR per User.
Middle: cumulative MRR over time (area) + Users by plan (bar).
Bottom: Users by country (horizontal bar) + Seats by plan (bar).


## Project layout

```
data/onboarding.csv     # source dataset (committed)
dashboard.html          # standalone built dashboard
dashboard.py            # Streamlit app (same charts)
build_html.py           # regenerates dashboard.html from the CSV
exploration.ipynb       # EDA scratch notebook
requirements.txt        # pinned deps
setup.sh                # venv + deps + Jupyter kernel
```

## Dataset

`data/onboarding.csv` — synthetic, 100 rows.

| column        | type   | notes                                |
|---------------|--------|--------------------------------------|
| `user_id`     | int    | 1–100                                |
| `email`       | string |                                      |
| `plan`        | enum   | Starter / Pro / Enterprise           |
| `signup_date` | date   | YYYY-MM-DD                           |
| `country`     | string | 13 countries                         |
| `seats`       | int    | licensed seats                       |
| `mrr`         | float  | monthly recurring revenue, USD       |
