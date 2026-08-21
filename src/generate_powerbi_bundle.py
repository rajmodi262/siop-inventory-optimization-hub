"""
Enterprise Power BI Template & Dataset Bundle Builder for Eaton SIOP & Inventory Optimization Hub.
Generates:
1. Eaton_SIOP_Inventory_Optimization.pbit (Power BI Template Archive)
2. Eaton_SIOP_Inventory_Project.pbip (Power BI Modern Project Format)
3. Eaton_SIOP_MultiPlant_DataModel.xlsx (Pre-loaded Excel Power Pivot Data Model)
"""

import os
import sys
import json
import zipfile
import pandas as pd
import numpy as np

sys.path.append(os.path.abspath("."))
try:
    from src.data_generator import generate_siop_dataset
except ImportError:
    from data_generator import generate_siop_dataset

def create_powerbi_bundle():
    print("=== Generating Enterprise Power BI Files ===")
    
    # Ensure datasets exist
    df_plants, df_suppliers, df_skus, df_dates, df_snapshots = generate_siop_dataset(num_skus=150, days=60, seed=42)
    
    # 1. Create Pre-Packaged Excel Workbook with All Star-Schema Tables
    excel_path = "powerbi/Eaton_SIOP_MultiPlant_DataModel.xlsx"
    os.makedirs("powerbi", exist_ok=True)
    
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        df_snapshots.to_excel(writer, sheet_name="fact_inventory_snapshot", index=False)
        df_plants.to_excel(writer, sheet_name="dim_plant", index=False)
        df_skus.to_excel(writer, sheet_name="dim_product_sku", index=False)
        df_suppliers.to_excel(writer, sheet_name="dim_supplier", index=False)
        df_dates.to_excel(writer, sheet_name="dim_date", index=False)
        
    print(f"  [OK] Created Pre-loaded Star Schema Excel Model: {excel_path}")

    # 2. Build Power BI Tabular Model Schema (BIM / DataModelSchema)
    data_model_schema = {
        "name": "Eaton_SIOP_DataModel",
        "compatibilityLevel": 1550,
        "model": {
            "culture": "en-US",
            "dataSources": [
                {
                    "type": "structured",
                    "name": "Local_CSV_Exports",
                    "connectionDetails": {
                        "protocol": "file",
                        "address": {"path": "./data/"}
                    }
                }
            ],
            "tables": [
                {
                    "name": "dim_plant",
                    "columns": [{"name": col, "dataType": "string" if df_plants[col].dtype == 'object' else "double"} for col in df_plants.columns]
                },
                {
                    "name": "dim_product_sku",
                    "columns": [{"name": col, "dataType": "string" if df_skus[col].dtype == 'object' else "double"} for col in df_skus.columns]
                },
                {
                    "name": "dim_supplier",
                    "columns": [{"name": col, "dataType": "string" if df_suppliers[col].dtype == 'object' else "double"} for col in df_suppliers.columns]
                },
                {
                    "name": "dim_date",
                    "columns": [{"name": col, "dataType": "string" if df_dates[col].dtype == 'object' else "int64"} for col in df_dates.columns]
                },
                {
                    "name": "fact_inventory_daily_snapshot",
                    "columns": [{"name": col, "dataType": "string" if df_snapshots[col].dtype == 'object' else "double"} for col in df_snapshots.columns],
                    "measures": [
                        {
                            "name": "Total Inventory Value",
                            "expression": "SUM(fact_inventory_daily_snapshot[total_inventory_value])",
                            "formatString": "\\$#,0"
                        },
                        {
                            "name": "Days of Inventory on Hand (DOH)",
                            "expression": "VAR OnHand = SUM(fact_inventory_daily_snapshot[on_hand_qty]) VAR DailyDem = SUM(fact_inventory_daily_snapshot[trailing_90d_avg_daily_demand]) RETURN IF(DailyDem > 0, DIVIDE(OnHand, DailyDem, 0), BLANK())",
                            "formatString": "0.0"
                        },
                        {
                            "name": "Dynamic Safety Stock",
                            "expression": "VAR Z_Score = 1.645 VAR AvgDailyDemand = AVERAGE(fact_inventory_daily_snapshot[trailing_90d_avg_daily_demand]) VAR DemandVar = POWER(STDEV.S(fact_inventory_daily_snapshot[daily_actual_demand_qty]), 2) VAR AvgLT = AVERAGE(fact_inventory_daily_snapshot[lead_time_days]) VAR LTVar = POWER(AVERAGE(dim_supplier[lead_time_std_dev_days]), 2) VAR CombVar = (AvgLT * DemandVar) + (POWER(AvgDailyDemand, 2) * LTVar) RETURN IF(CombVar > 0, Z_Score * SQRT(CombVar), 0)",
                            "formatString": "#,0"
                        },
                        {
                            "name": "Excess & Obsolete (E&O) Value",
                            "expression": "CALCULATE([Total Inventory Value], FILTER(fact_inventory_daily_snapshot, fact_inventory_daily_snapshot[dormant_days_since_last_movement] >= 90 || fact_inventory_daily_snapshot[days_of_inventory_on_hand] > 60))",
                            "formatString": "\\$#,0"
                        },
                        {
                            "name": "Inventory Turnover Ratio",
                            "expression": "VAR AnnualCOGS = SUM(fact_inventory_daily_snapshot[daily_actual_demand_qty]) * AVERAGE(fact_inventory_daily_snapshot[unit_cost]) * 365 RETURN DIVIDE(AnnualCOGS, [Total Inventory Value], 0)",
                            "formatString": "0.0"
                        }
                    ]
                }
            ],
            "relationships": [
                {"name": "rel_plant", "fromTable": "fact_inventory_daily_snapshot", "fromColumn": "plant_id", "toTable": "dim_plant", "toColumn": "plant_id"},
                {"name": "rel_sku", "fromTable": "fact_inventory_daily_snapshot", "fromColumn": "sku_id", "toTable": "dim_product_sku", "toColumn": "sku_id"},
                {"name": "rel_supplier", "fromTable": "fact_inventory_daily_snapshot", "fromColumn": "supplier_id", "toTable": "dim_supplier", "toColumn": "supplier_id"},
                {"name": "rel_date", "fromTable": "fact_inventory_daily_snapshot", "fromColumn": "date_key", "toTable": "dim_date", "toColumn": "date_key"}
            ]
        }
    }

    # 3. Build Power BI Layout JSON
    report_layout = {
        "id": 0,
        "resourcePackages": [],
        "sections": [
            {
                "id": 0,
                "name": "ReportSection_ExecSummary",
                "displayName": "Executive SIOP & Inventory Scorecard",
                "filters": "[]",
                "ordinal": 0,
                "visualContainers": [
                    {
                        "x": 20, "y": 20, "z": 1000, "width": 300, "height": 140,
                        "config": json.dumps({"name": "Card_TotalValue", "singleVisual": {"visualType": "card", "projections": {"Values": [{"queryRef": "fact_inventory_daily_snapshot.Total Inventory Value"}]}}})
                    },
                    {
                        "x": 340, "y": 20, "z": 1000, "width": 300, "height": 140,
                        "config": json.dumps({"name": "Card_DOH", "singleVisual": {"visualType": "card", "projections": {"Values": [{"queryRef": "fact_inventory_daily_snapshot.Days of Inventory on Hand (DOH)"}]}}})
                    },
                    {
                        "x": 660, "y": 20, "z": 1000, "width": 300, "height": 140,
                        "config": json.dumps({"name": "Card_EO", "singleVisual": {"visualType": "card", "projections": {"Values": [{"queryRef": "fact_inventory_daily_snapshot.Excess & Obsolete (E&O) Value"}]}}})
                    },
                    {
                        "x": 980, "y": 20, "z": 1000, "width": 280, "height": 140,
                        "config": json.dumps({"name": "Card_Turns", "singleVisual": {"visualType": "card", "projections": {"Values": [{"queryRef": "fact_inventory_daily_snapshot.Inventory Turnover Ratio"}]}}})
                    },
                    {
                        "x": 20, "y": 180, "z": 2000, "width": 750, "height": 480,
                        "config": json.dumps({"name": "Bar_PlantValuation", "singleVisual": {"visualType": "columnChart", "projections": {"Category": [{"queryRef": "dim_plant.plant_name"}], "Y": [{"queryRef": "fact_inventory_daily_snapshot.Total Inventory Value"}]}}})
                    },
                    {
                        "x": 790, "y": 180, "z": 2000, "width": 470, "height": 480,
                        "config": json.dumps({"name": "Donut_CategoryValuation", "singleVisual": {"visualType": "donutChart", "projections": {"Category": [{"queryRef": "dim_product_sku.product_category"}], "Y": [{"queryRef": "fact_inventory_daily_snapshot.Total Inventory Value"}]}}})
                    }
                ]
            }
        ],
        "config": json.dumps({"version": "5.50", "themeCollection": {"baseTheme": {"name": "CY24SU08", "version": "5.50"}}})
    }

    # 4. Pack into Power BI Template Archive (.pbit)
    pbit_path = "powerbi/Eaton_SIOP_Inventory_Optimization.pbit"
    content_types_xml = """<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="json" ContentType="" />
  <Default Extension="xml" ContentType="application/xml" />
  <Override PartName="/DataModelSchema" ContentType="" />
  <Override PartName="/Report/Layout" ContentType="" />
  <Override PartName="/Settings" ContentType="" />
  <Override PartName="/Version" ContentType="" />
</Types>"""

    with zipfile.ZipFile(pbit_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types_xml)
        zf.writestr("Version", "1.28".encode("utf-16-le"))
        zf.writestr("Settings", json.dumps({"version": "1.0"}))
        zf.writestr("DataModelSchema", json.dumps(data_model_schema, indent=2).encode("utf-16-le"))
        zf.writestr("Report/Layout", json.dumps(report_layout, indent=2).encode("utf-16-le"))

    print(f"  [OK] Assembled Power BI Template File (.pbit): {pbit_path}")

    # 5. Build Power BI Project (.pbip) Directory Structure
    pbip_dir = "powerbi/Eaton_SIOP_Project.pbip"
    os.makedirs(f"{pbip_dir}/Eaton_SIOP.Report", exist_ok=True)
    os.makedirs(f"{pbip_dir}/Eaton_SIOP.Dataset", exist_ok=True)
    
    with open(f"{pbip_dir}/definition.pbip", "w") as f:
        json.dump({"version": "1.0", "artifacts": [{"report": {"path": "Eaton_SIOP.Report"}}]}, f, indent=2)
        
    with open(f"{pbip_dir}/Eaton_SIOP.Dataset/model.bim", "w") as f:
        json.dump(data_model_schema, f, indent=2)
        
    with open(f"{pbip_dir}/Eaton_SIOP.Report/report.json", "w") as f:
        json.dump(report_layout, f, indent=2)
        
    print(f"  [OK] Created Modern Power BI Project Format (.pbip): {pbip_dir}")
    print("=== Power BI Bundle Generation Complete! ===")

if __name__ == "__main__":
    create_powerbi_bundle()
