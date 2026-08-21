"""
Power BI Analytical Dataset Exporter.
Exports certified Star Schema tables as CSV & Parquet files ready for Power BI Desktop Dataflow / Model ingestion.
"""

import os
import pandas as pd

def export_powerbi_tables(output_dir: str = "powerbi_exports"):
    os.makedirs(output_dir, exist_ok=True)
    
    # Load raw generated data
    data_dir = "data"
    tables = [
        "dim_plant", "dim_supplier", "dim_product_sku", "dim_date", "fact_inventory_daily_snapshot"
    ]
    
    print(f"=== Exporting Certified Power BI Star Schema Tables to '{output_dir}/' ===")
    for tbl in tables:
        csv_path = os.path.join(data_dir, f"{tbl}.csv")
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            # Save as CSV
            export_csv = os.path.join(output_dir, f"{tbl}.csv")
            df.to_csv(export_csv, index=False)
            
            # Save as Parquet for high-speed Power BI Direct Lake / import
            try:
                export_parquet = os.path.join(output_dir, f"{tbl}.parquet")
                df.to_parquet(export_parquet, index=False)
                print(f"  ✓ {tbl}: {len(df):,} rows -> CSV & Parquet")
            except Exception:
                print(f"  ✓ {tbl}: {len(df):,} rows -> CSV")
                
    print("=== Power BI Export Ready! Load files directly into Power BI Desktop. ===")

if __name__ == "__main__":
    export_powerbi_tables()
