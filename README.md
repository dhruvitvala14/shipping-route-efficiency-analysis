# Nassau Candy Distributor — Shipping Route Efficiency Dashboard

An interactive Streamlit dashboard for the Factory-to-Customer Shipping Route
Efficiency Analysis project.

## What's included
- `app.py` — the Streamlit application
- `Nassau_Candy_Distributor.csv` — the shipment dataset
- `requirements.txt` — Python dependencies

## Run it locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app will open at `http://localhost:8501`.

## Dashboard modules
1. **Route Efficiency Overview** — average lead time by route, route volume
   share, and a top-10 / bottom-10 route performance leaderboard.
2. **Geographic Shipping Map** — a US choropleth of average lead time by
   state, a volume-vs-lead-time bottleneck scatter (with a congestion-prone
   states table), and factory locations.
3. **Ship Mode Comparison** — lead-time distribution and delay rate by ship
   mode, plus a cost-vs-lead-time tradeoff view.
4. **Route Drill-Down** — pick a state to see its KPIs, monthly lead-time
   trend, factory split, and a full order-level shipment timeline (downloadable).

## Filters (sidebar)
- Order date range
- Region (Interior / Atlantic / Gulf / Pacific)
- State / Province
- Ship mode
- Factory
- Delay threshold slider (days) — drives the "Delay Frequency" KPI and
  highlights on charts

## Data notes
- Factory is derived from Product Name using the Products & Factories
  correlation table from the project documentation; factory coordinates come
  from the same source.
- Rows with unparseable or negative lead times are dropped during cleaning
  (see the "Data quality notes" expander in the sidebar for counts).
- Ship Date values in the source file are consistently several years after
  Order Date, so absolute lead-time magnitudes (900+ days) are not
  calendar-realistic. This doesn't affect the analysis, since every KPI and
  ranking here is a **relative** comparison across routes/states/modes.
