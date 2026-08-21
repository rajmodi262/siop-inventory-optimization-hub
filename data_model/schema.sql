-- ============================================================================
-- SIOP & MULTI-PLANT INVENTORY OPTIMIZATION HUB
-- Star Schema Data Model (PostgreSQL / DuckDB / SQLite Compatible)
-- Grain: 1 Row per Plant per SKU per Snapshot Date
-- ============================================================================

-- 1. DIMENSION: Plant / Manufacturing Facility
CREATE TABLE IF NOT EXISTS dim_plant (
    plant_id VARCHAR(10) PRIMARY KEY,
    plant_name VARCHAR(100) NOT NULL,
    region VARCHAR(50) NOT NULL,              -- Americas, EMEA, APAC
    country VARCHAR(50) NOT NULL,
    city VARCHAR(50) NOT NULL,
    manufacturing_focus VARCHAR(100) NOT NULL, -- Transformers, Switchgears, EV Inverters, Hydraulics
    operating_capacity_pct NUMERIC(5,2) DEFAULT 85.00,
    annual_holding_rate_pct NUMERIC(5,2) DEFAULT 22.50 -- Standard inventory holding cost %
);

-- 2. DIMENSION: Product SKU & Component Catalog
CREATE TABLE IF NOT EXISTS dim_product_sku (
    sku_id VARCHAR(20) PRIMARY KEY,
    sku_name VARCHAR(150) NOT NULL,
    product_category VARCHAR(80) NOT NULL,    -- Electrical Distribution, Power Electronics, Hydraulics, Raw Materials
    product_subfamily VARCHAR(80) NOT NULL,   -- Step-Down Transformers, Circuit Breakers, IGBT Inverters, Copper Coils
    abc_classification VARCHAR(1) NOT NULL,   -- A (High Value), B (Medium), C (Low)
    xyz_demand_variability VARCHAR(1) NOT NULL, -- X (Constant), Y (Fluctuating), Z (Sporadic/Lumpy)
    unit_of_measure VARCHAR(20) NOT NULL,     -- Units, Meters, Kilograms, Liters
    standard_unit_cost NUMERIC(12,2) NOT NULL,
    target_service_level_pct NUMERIC(5,2) DEFAULT 95.00,
    min_order_qty INT DEFAULT 1,
    pack_size INT DEFAULT 1
);

-- 3. DIMENSION: Primary Supplier
CREATE TABLE IF NOT EXISTS dim_supplier (
    supplier_id VARCHAR(20) PRIMARY KEY,
    supplier_name VARCHAR(120) NOT NULL,
    tier_level VARCHAR(10) NOT NULL,          -- Tier 1, Tier 2, Strategic
    country VARCHAR(50) NOT NULL,
    avg_contracted_lead_time_days INT NOT NULL,
    lead_time_std_dev_days NUMERIC(5,2) NOT NULL,
    historical_otif_pct NUMERIC(5,2) NOT NULL,
    single_source_flag BOOLEAN DEFAULT FALSE
);

-- 4. DIMENSION: Date & Fiscal Calendar
CREATE TABLE IF NOT EXISTS dim_date (
    date_key INT PRIMARY KEY,                 -- YYYYMMDD
    full_date DATE NOT NULL UNIQUE,
    year INT NOT NULL,
    quarter VARCHAR(2) NOT NULL,              -- Q1, Q2, Q3, Q4
    month INT NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    week_of_year INT NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    is_holiday BOOLEAN NOT NULL,
    fiscal_quarter VARCHAR(10) NOT NULL       -- FY26-Q1, etc.
);

-- 5. DIMENSION: SIOP Consensus Plan
CREATE TABLE IF NOT EXISTS dim_siop_plan (
    plan_id VARCHAR(30) PRIMARY KEY,
    plant_id VARCHAR(10) REFERENCES dim_plant(plant_id),
    sku_id VARCHAR(20) REFERENCES dim_product_sku(sku_id),
    plan_month DATE NOT NULL,
    unconstrained_forecast_qty INT NOT NULL,
    constrained_production_plan_qty INT NOT NULL,
    committed_capacity_hours NUMERIC(10,2) NOT NULL,
    target_doh_days NUMERIC(5,1) NOT NULL,
    planner_name VARCHAR(80)
);

-- 6. FACT TABLE: Daily Inventory & Operations Snapshot
CREATE TABLE IF NOT EXISTS fact_inventory_daily_snapshot (
    snapshot_id BIGINT PRIMARY KEY,
    date_key INT NOT NULL REFERENCES dim_date(date_key),
    plant_id VARCHAR(10) NOT NULL REFERENCES dim_plant(plant_id),
    sku_id VARCHAR(20) NOT NULL REFERENCES dim_product_sku(sku_id),
    supplier_id VARCHAR(20) NOT NULL REFERENCES dim_supplier(supplier_id),
    
    -- Inventory State Metrics
    on_hand_qty INT NOT NULL,
    in_transit_qty INT NOT NULL,
    allocated_wip_qty INT NOT NULL,           -- Work In Progress
    backorder_qty INT NOT NULL,
    available_to_promise_qty INT NOT NULL,
    
    -- Financial Valuations
    unit_cost NUMERIC(12,2) NOT NULL,
    total_inventory_value NUMERIC(15,2) NOT NULL,
    
    -- Consumption & Demand
    daily_actual_demand_qty INT NOT NULL,
    daily_forecasted_demand_qty INT NOT NULL,
    trailing_90d_avg_daily_demand NUMERIC(10,2) NOT NULL,
    trailing_90d_demand_std_dev NUMERIC(10,2) NOT NULL,
    
    -- Replenishment Parameters
    lead_time_days INT NOT NULL,
    calculated_safety_stock_qty INT NOT NULL,
    calculated_reorder_point_qty INT NOT NULL,
    calculated_economic_order_qty INT NOT NULL,
    
    -- SCM Health Indicators
    days_of_inventory_on_hand NUMERIC(10,2) NOT NULL,
    is_stockout_flag BOOLEAN NOT NULL DEFAULT FALSE,
    is_excess_inventory_flag BOOLEAN NOT NULL DEFAULT FALSE,
    dormant_days_since_last_movement INT DEFAULT 0
);

-- Indexes for High Performance BI Aggregations
CREATE INDEX idx_fact_inventory_date ON fact_inventory_daily_snapshot(date_key);
CREATE INDEX idx_fact_inventory_plant ON fact_inventory_daily_snapshot(plant_id);
CREATE INDEX idx_fact_inventory_sku ON fact_inventory_daily_snapshot(sku_id);
CREATE INDEX idx_fact_inventory_doh ON fact_inventory_daily_snapshot(days_of_inventory_on_hand);
