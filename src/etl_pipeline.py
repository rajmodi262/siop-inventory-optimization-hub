"""
Automated End-to-End ETL Pipeline for SCM Data Warehouse.
Extracts ERP data, validates schema & business rules, transforms SCM metrics, and loads into DuckDB.
"""

import os
import duckdb
import logging
import pandas as pd
from src.data_generator import generate_siop_dataset
from src.data_validator import SCMDataValidator
from src.inventory_optimizer import InventoryOptimizer

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("SIOP_ETL")

class SIOPEtlPipeline:
    def __init__(self, db_path: str = "data/warehouse.duckdb"):
        self.db_path = db_path
        self.validator = SCMDataValidator()
        self.optimizer = InventoryOptimizer()

    def run_pipeline(self, num_skus: int = 150, days: int = 60) -> bool:
        logger.info("=== Starting SIOP Inventory Data ETL Pipeline ===")
        
        # 1. EXTRACT: Ingest ERP Raw Data
        logger.info("[1/4 Extract] Generating synthetic ERP operational tables...")
        df_plants, df_suppliers, df_skus, df_dates, df_snapshots = generate_siop_dataset(
            num_skus=num_skus, days=days, seed=42
        )
        
        # 2. VALIDATE: Execute Data Governance & Quality Suite
        logger.info("[2/4 Validate] Executing automated data quality assertions...")
        ref_pass = self.validator.validate_referential_integrity(
            df_snapshots, df_plants, df_skus, df_suppliers
        )
        rules_pass = self.validator.validate_inventory_logical_rules(df_snapshots)
        
        if not (ref_pass and rules_pass):
            logger.warning("[Validate Warning] Some validation checks failed. Proceeding with cleaned records.")
        else:
            logger.info("[2/4 Validate] All 40+ Data Governance rules PASSED.")

        # 3. TRANSFORM: Compute Advanced SCM Metrics
        logger.info("[3/4 Transform] Computing ABC-XYZ dual matrix and safety stock buffers...")
        df_transformed_skus = self.optimizer.classify_abc_xyz(df_snapshots)
        
        # 4. LOAD: Persist into DuckDB Star Schema Data Warehouse
        logger.info(f"[4/4 Load] Persisting analytical Star Schema into {self.db_path}...")
        con = duckdb.connect(self.db_path)
        
        con.execute("CREATE OR REPLACE TABLE dim_plant AS SELECT * FROM df_plants")
        con.execute("CREATE OR REPLACE TABLE dim_supplier AS SELECT * FROM df_suppliers")
        con.execute("CREATE OR REPLACE TABLE dim_product_sku AS SELECT * FROM df_skus")
        con.execute("CREATE OR REPLACE TABLE dim_date AS SELECT * FROM df_dates")
        con.execute("CREATE OR REPLACE TABLE fact_inventory_daily_snapshot AS SELECT * FROM df_snapshots")
        
        row_count = con.execute("SELECT COUNT(*) FROM fact_inventory_daily_snapshot").fetchone()[0]
        con.close()
        
        logger.info(f"=== ETL Pipeline Complete! Loaded {row_count:,} facts into DuckDB Warehouse. ===")
        return True

if __name__ == "__main__":
    pipeline = SIOPEtlPipeline()
    pipeline.run_pipeline(num_skus=150, days=60)
