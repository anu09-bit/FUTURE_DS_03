# Marketing Funnel Performance Analysis — Package Guide

This package contains a full funnel analysis: an interactive dashboard, a formatted
Word report, the underlying data, and the Python scripts used to produce everything.
It's built on a **synthetic demo dataset** so you can see the full method end-to-end;
swap in your real data and every file regenerates automatically.

## What's inside

| File | What it is | Open with |
|---|---|---|
| `Marketing_Funnel_Analysis_Report.docx` | Full written report: executive summary, funnel breakdown, channel performance, drop-off diagnosis, monthly trend, and recommendations | Microsoft Word / Google Docs |
| `funnel_dashboard.html` | Interactive dashboard — filter by month range and channel, click any channel row to isolate it across every chart | Any web browser (double-click to open) |
| `funnel_data.csv` | Raw dataset: month x channel x funnel stage (visitors → leads → MQLs → SQLs → opportunities → customers), plus spend and revenue | Excel / Google Sheets |
| `channel_performance_summary.csv` | Channel-level rollup: conversion rates, CAC, ROI | Excel / Google Sheets |
| `dropoff_by_channel.csv` | Stage-to-stage conversion rate for each channel | Excel / Google Sheets |
| `monthly_trend.csv` | Month-over-month leads, customers, conversion rate, ROAS | Excel / Google Sheets |
| `generate_data.py` | Script that generated the synthetic dataset — replace with your own data loader | Python 3 |
| `analyze_funnel.py` | Full analysis + static chart generation (matplotlib) — reusable on real data | Python 3 |
| `chart1_funnel_overview.png` … `chart5_monthly_trend.png` | Static chart images used in the Word report | Any image viewer |

## Quick start

**To read the findings:** open `Marketing_Funnel_Analysis_Report.docx`. It's the
complete narrative — start to finish, no setup needed.

**To explore the data interactively:** open `funnel_dashboard.html` in any browser
(Chrome, Safari, Edge, Firefox). No installation, no server — it's a single
self-contained file with the dataset embedded. Use the month range selectors and
channel chips at the top to filter every chart and table at once; click a row in
the channel table to isolate that channel.

**To reproduce or update the analysis on real data:**
1. Export your CRM/marketing analytics data with these columns (rename as needed):
   `month, channel, visitors, leads, mqls, sqls, opportunities, customers, spend, revenue`
2. Replace `funnel_data.csv` with your export.
3. Run:
   ```bash
   pip install pandas numpy matplotlib seaborn
   python3 analyze_funnel.py
   ```
   This regenerates all five charts and the three summary CSVs.
4. For the dashboard, convert your updated `funnel_data.csv` to JSON and paste it
   into the `const RAW = [...]` line near the top of the `<script>` block in
   `funnel_dashboard.html`, replacing the existing array. (A one-line pandas command
   does this: `df.to_json(orient="records")`.)
5. For the Word report, edit the numbers in `build_docx.js` if you generated it
   from source (not included in this package by default — ask if you'd like the
   generator script as well) or simply update the figures manually in Word.

## Key findings summary

- Overall lead-to-customer conversion: **4.11%**
- Biggest drop-off: **Visitor → Lead at 4.7%** (every later stage converts 33–55%)
- Best channel: **Referral** (12.99% lead-to-customer, +52,804% ROI)
- Weakest channel: **Paid Social** (0.50% lead-to-customer, -65% ROI)
- See the full report for stage-by-stage diagnosis and five concrete recommendations.

## Notes on the data

This is a synthetic dataset generated to demonstrate the analysis method — realistic
in shape and scale, but not real customer data. Random noise is seeded for
reproducibility (`numpy.random.seed(42)` in `generate_data.py`), so re-running that
script produces the same numbers used in this report.
