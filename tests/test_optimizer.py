"""
Automated PyTest Suite for SCM Inventory Optimizer & Data Validator.
"""

import pytest
import pandas as pd
import numpy as np
from src.inventory_optimizer import InventoryOptimizer
from src.data_validator import SCMDataValidator

@pytest.fixture
def optimizer():
    return InventoryOptimizer()

@pytest.fixture
def validator():
    return SCMDataValidator()

def test_safety_stock_calculation(optimizer):
    # Test deterministic case (zero variance should yield zero safety stock)
    ss_zero = optimizer.calculate_safety_stock(avg_demand=100, demand_std=0, avg_lead_time=10, lead_time_std=0, service_level=0.95)
    assert ss_zero == 0.0

    # Test standard case (95% service level -> z approx 1.645)
    ss = optimizer.calculate_safety_stock(avg_demand=50, demand_std=10, avg_lead_time=16, lead_time_std=2, service_level=0.95)
    assert ss > 0.0
    assert isinstance(ss, float)

def test_doh_calculation(optimizer):
    doh = optimizer.calculate_doh(on_hand_inventory=500, avg_daily_demand=25)
    assert doh == 20.0
    
    # Zero demand edge case
    doh_zero = optimizer.calculate_doh(on_hand_inventory=100, avg_daily_demand=0)
    assert doh_zero == 999.0

def test_eoq_calculation(optimizer):
    # Annual Demand = 1000, Order Cost = 50, Unit Cost = 100, Holding Rate = 20% (Holding cost = $20)
    # EOQ = sqrt((2 * 1000 * 50) / 20) = sqrt(100000 / 20) = sqrt(5000) = ~70.71
    eoq = optimizer.calculate_eoq(annual_demand=1000, order_cost=50, unit_cost=100, holding_rate=20.0)
    assert round(eoq, 2) == 70.71

def test_data_validator_integrity(validator):
    df_plants = pd.DataFrame([{"plant_id": "P1"}])
    df_skus = pd.DataFrame([{"sku_id": "S1"}])
    df_suppliers = pd.DataFrame([{"supplier_id": "SUP1"}])
    
    df_fact_valid = pd.DataFrame([{
        "plant_id": "P1", "sku_id": "S1", "supplier_id": "SUP1",
        "on_hand_qty": 100, "unit_cost": 25.0, "total_inventory_value": 2500.0,
        "lead_time_days": 14
    }])
    
    passed = validator.validate_referential_integrity(df_fact_valid, df_plants, df_skus, df_suppliers)
    assert passed is True
    
    rules_passed = validator.validate_inventory_logical_rules(df_fact_valid)
    assert rules_passed is True

def test_data_validator_catches_negative_stock(validator):
    df_fact_bad = pd.DataFrame([{
        "on_hand_qty": -50, "unit_cost": 10.0, "total_inventory_value": -500.0,
        "lead_time_days": 10
    }])
    rules_passed = validator.validate_inventory_logical_rules(df_fact_bad)
    assert rules_passed is False
