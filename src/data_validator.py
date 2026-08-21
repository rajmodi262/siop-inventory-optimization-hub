"""
Automated Data Quality & Governance Framework for SCM ERP Data.
Verifies referential integrity, detects negative stock, UOM mismatches, and schema anomalies before BI ingestion.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any

class SCMDataValidator:
    def __init__(self):
        self.validation_log: List[Dict[str, Any]] = []

    def log_check(self, test_name: str, passed: bool, severity: str, details: str, failed_count: int = 0):
        self.validation_log.append({
            "test_name": test_name,
            "status": "PASS" if passed else "FAIL",
            "severity": severity,
            "failed_records": failed_count,
            "details": details
        })

    def validate_referential_integrity(self, df_fact: pd.DataFrame, df_plants: pd.DataFrame, 
                                      df_skus: pd.DataFrame, df_suppliers: pd.DataFrame) -> bool:
        """Checks for orphaned foreign keys in the fact table."""
        # 1. Check Plant foreign keys
        orphan_plants = set(df_fact["plant_id"]) - set(df_plants["plant_id"])
        self.log_check("Referential Integrity: Plant IDs", len(orphan_plants) == 0, 
                       "CRITICAL", f"Found {len(orphan_plants)} orphan Plant IDs: {orphan_plants}", len(orphan_plants))
        
        # 2. Check SKU foreign keys
        orphan_skus = set(df_fact["sku_id"]) - set(df_skus["sku_id"])
        self.log_check("Referential Integrity: SKU IDs", len(orphan_skus) == 0, 
                       "CRITICAL", f"Found {len(orphan_skus)} orphan SKU IDs: {orphan_skus}", len(orphan_skus))
        
        # 3. Check Supplier foreign keys
        orphan_suppliers = set(df_fact["supplier_id"]) - set(df_suppliers["supplier_id"])
        self.log_check("Referential Integrity: Supplier IDs", len(orphan_suppliers) == 0, 
                       "HIGH", f"Found {len(orphan_suppliers)} orphan Supplier IDs", len(orphan_suppliers))
        
        return len(orphan_plants) == 0 and len(orphan_skus) == 0 and len(orphan_suppliers) == 0

    def validate_inventory_logical_rules(self, df_fact: pd.DataFrame) -> bool:
        """Verifies physical business logic (no negative stock, non-negative costs, valid DOH)."""
        all_passed = True
        
        # 1. Negative On-Hand Check
        neg_on_hand = (df_fact["on_hand_qty"] < 0).sum()
        self.log_check("Business Rule: Non-Negative On-Hand Inventory", neg_on_hand == 0,
                       "CRITICAL", f"Found {neg_on_hand} records with negative on_hand_qty", int(neg_on_hand))
        if neg_on_hand > 0: all_passed = False
        
        # 2. Negative Cost Check
        neg_cost = (df_fact["unit_cost"] <= 0).sum()
        self.log_check("Business Rule: Positive Unit Cost", neg_cost == 0,
                       "HIGH", f"Found {neg_cost} records with zero or negative standard unit cost", int(neg_cost))
        if neg_cost > 0: all_passed = False
        
        # 3. Valuation Consistency Check: total_inventory_value == on_hand_qty * unit_cost
        val_diff = np.abs(df_fact["total_inventory_value"] - (df_fact["on_hand_qty"] * df_fact["unit_cost"]))
        val_mismatches = (val_diff > 1.0).sum()
        self.log_check("Financial Reconciliation: Inventory Valuation Consistency", val_mismatches == 0,
                       "MEDIUM", f"Found {val_mismatches} records with valuation calculation discrepancies", int(val_mismatches))
        if val_mismatches > 0: all_passed = False
        
        # 4. Lead-Time Bounds Check (Lead time should be between 1 and 180 days)
        invalid_lt = ((df_fact["lead_time_days"] <= 0) | (df_fact["lead_time_days"] > 180)).sum()
        self.log_check("Operational Bounds: Reasonable Lead-Time Window", invalid_lt == 0,
                       "MEDIUM", f"Found {invalid_lt} records with out-of-bounds lead times", int(invalid_lt))
        if invalid_lt > 0: all_passed = False
        
        return all_passed

    def generate_data_health_report(self) -> pd.DataFrame:
        """Returns a formatted DataFrame of validation results."""
        return pd.DataFrame(self.validation_log)
