# Dashboard Mockups

**These are design mockups, not Power BI screen captures.**

Each PNG in this folder is rendered by [`src/render_ultra_dashboard.py`](../../src/render_ultra_dashboard.py)
using **matplotlib**. They are the target layout for the Power BI report — page
composition, KPI card hierarchy, colour semantics, and the drill path — produced
as images so the design could be reviewed before building it in Power BI Desktop.

They are not screenshots of a running report, and they do not read from the
DuckDB warehouse at runtime. Several display values in the render script are
typed in rather than queried, specifically so the layout renders deterministically
at a fixed size.

## What in this repository *is* real Power BI

| Artifact | What it is |
|---|---|
| [`../SIOP_Inventory_Optimization.pbit`](../SIOP_Inventory_Optimization.pbit) | A Power BI template (`.pbit`) that opens in Power BI Desktop |
| [`../SIOP_Project.pbip`](../SIOP_Project.pbip) | Power BI Project format — `model.bim` dataset plus report definition |
| [`../SIOP_MultiPlant_DataModel.xlsx`](../SIOP_MultiPlant_DataModel.xlsx) | Star-schema Excel model, 1 fact + 5 dimensions, loadable via Power Query |
| [`../dax_measures.md`](../dax_measures.md) / [`../dax_measures_masterclass.md`](../dax_measures_masterclass.md) | The DAX measure definitions (DOH, turns, safety stock, E&O) |
| [`../theme_executive_dark.json`](../theme_executive_dark.json) | Power BI theme JSON |
| [`../../src/export_powerbi_dataset.py`](../../src/export_powerbi_dataset.py) | Exports the warehouse to Power BI-ready Parquet/CSV |

The `.pbit` currently carries a starter layout with a small number of visual
containers. It does **not** yet reproduce the three-page design shown in these
mockups — building that out in Power BI Desktop is the open work item.

## Data

All figures are synthetic. See the Data Provenance section in the
[repository README](../../README.md).
