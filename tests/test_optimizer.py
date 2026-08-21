"""
Automated PyTest Suite for SCM Inventory Optimizer, Forecaster, Data Validator & ETL.
"""

import pytest
import pandas as pd
import numpy as np
from src.inventory_optimizer import InventoryOptimizer
from src.data_validator import SCMDataValidator
from src.demand_forecaster import SIOPDemandForecaster
from src.etl_pipeline import SIOPEtlPipeline

@pytest.fixture
def optimizer():
    return InventoryOptimizer()

@pytest.fixture
def validator():
    return SCMDataValidator()

@pytest.fixture
def forecaster():
    return SIOPDemandForecaster()

def test_safety_stock_calculation(optimizer):
    ss_zero = optimizer.calculate_safety_stock(avg_demand=100, demand_std=0, avg_lead_time=10, lead_time_std=0, service_level=0.95)
    assert ss_zero == 0.0

    ss = optimizer.calculate_safety_stock(avg_demand=50, demand_std=10, avg_lead_time=16, lead_time_std=2, service_level=0.95)
    assert ss > 0.0
    assert isinstance(ss, float)

def test_doh_calculation(optimizer):
    doh = optimizer.calculate_doh(on_hand_inventory=500, avg_daily_demand=25)
    assert doh == 20.0
    doh_zero = optimizer.calculate_doh(on_hand_inventory=100, avg_daily_demand=0)
    assert doh_zero == 999.0

def test_eoq_calculation(optimizer):
    eoq = optimizer.calculate_eoq(annual_demand=1000, order_cost=50, unit_cost=100, holding_rate=20.0)
    assert round(eoq, 2) == 70.71

def test_demand_forecaster_metrics(forecaster):
    actual = np.array([100, 110, 95, 105, 120])
    forecast = np.array([102, 108, 98, 100, 115])
    
    mape = forecaster.calculate_mape(actual, forecast)
    wape = forecaster.calculate_wape(actual, forecast)
    bias = forecaster.calculate_forecast_bias(actual, forecast)
    
    assert mape > 0
    assert wape > 0
    assert "bias_percentage" in bias
    assert "interpretation" in bias

def test_holt_winters_forecast(forecaster):
    series = pd.Series([10, 12, 15, 14, 18, 20, 22, 25, 24, 28, 30, 32, 35, 38, 40])
    df_fc = forecaster.generate_holt_winters_forecast(series, forecast_horizon=7)
    assert len(df_fc) == 7
    assert "forecast_demand_units" in df_fc.columns
    assert (df_fc["forecast_demand_units"] >= 0).all()

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

def test_etl_pipeline_execution():
    pipeline = SIOPEtlPipeline(db_path="data/test_warehouse.duckdb")
    success = pipeline.run_pipeline(num_skus=20, days=10)
    assert success is True
