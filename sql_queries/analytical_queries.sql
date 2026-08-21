-- ============================================================================
-- SCM & INVENTORY ANALYTICS PRODUCTION SQL QUERY PACK
-- Demonstrates Advanced Window Functions, CTEs, Moving Averages, and Aging Cohorts
-- Compatible with PostgreSQL, DuckDB, Snowflake, and BigQuery
-- ============================================================================

-- QUERY 1: Rolling 30-Day Moving Average Demand & Volatility with Window Functions
SELECT 
    date_key,
    plant_id,
    sku_id,
    daily_actual_demand_qty,
    AVG(daily_actual_demand_qty) OVER(
        PARTITION BY plant_id, sku_id 
        ORDER BY date_key 
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ) AS rolling_30d_avg_demand,
    STDDEV(daily_actual_demand_qty) OVER(
        PARTITION BY plant_id, sku_id 
        ORDER BY date_key 
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ) AS rolling_30d_demand_std_dev
FROM fact_inventory_daily_snapshot;

-- QUERY 2: Inventory Aging Cohorts & Excess Capital Breakdown
WITH latest_snapshot AS (
    SELECT * 
    FROM fact_inventory_daily_snapshot 
    WHERE date_key = (SELECT MAX(date_key) FROM fact_inventory_daily_snapshot)
)
SELECT 
    p.plant_name,
    s.product_category,
    COUNT(ls.sku_id) AS total_skus,
    SUM(ls.total_inventory_value) AS total_capital_usd,
    SUM(CASE WHEN ls.dormant_days_since_last_movement < 30 THEN ls.total_inventory_value ELSE 0 END) AS cohort_fresh_0_30d,
    SUM(CASE WHEN ls.dormant_days_since_last_movement BETWEEN 30 AND 60 THEN ls.total_inventory_value ELSE 0 END) AS cohort_aging_31_60d,
    SUM(CASE WHEN ls.dormant_days_since_last_movement BETWEEN 61 AND 90 THEN ls.total_inventory_value ELSE 0 END) AS cohort_at_risk_61_90d,
    SUM(CASE WHEN ls.dormant_days_since_last_movement > 90 THEN ls.total_inventory_value ELSE 0 END) AS cohort_dormant_obsolete_90d_plus
FROM latest_snapshot ls
JOIN dim_plant p ON ls.plant_id = p.plant_id
JOIN dim_product_sku s ON ls.sku_id = s.sku_id
GROUP BY p.plant_name, s.product_category
ORDER BY cohort_dormant_obsolete_90d_plus DESC;

-- QUERY 3: Stockout Frequency & Days on Hand (DOH) Outlier Ranking
WITH ranked_doh AS (
    SELECT 
        sku_id,
        plant_id,
        on_hand_qty,
        days_of_inventory_on_hand,
        total_inventory_value,
        ROW_NUMBER() OVER(PARTITION BY plant_id ORDER BY days_of_inventory_on_hand DESC) AS doh_rank_desc,
        ROW_NUMBER() OVER(PARTITION BY plant_id ORDER BY days_of_inventory_on_hand ASC) AS doh_rank_asc
    FROM fact_inventory_daily_snapshot
    WHERE date_key = (SELECT MAX(date_key) FROM fact_inventory_daily_snapshot)
)
SELECT 
    plant_id,
    sku_id,
    days_of_inventory_on_hand,
    total_inventory_value,
    CASE 
        WHEN doh_rank_desc <= 5 THEN 'Top 5 Excess Working Capital'
        WHEN doh_rank_asc <= 5 THEN 'Top 5 Critical Stockout Risk'
        ELSE 'Normal Band'
    END AS risk_classification
FROM ranked_doh
WHERE doh_rank_desc <= 5 OR doh_rank_asc <= 5;

-- QUERY 4: Cumulative Pareto ABC Value Contribution (80/20 Rule)
WITH sku_valuations AS (
    SELECT 
        s.sku_id,
        s.sku_name,
        s.product_category,
        SUM(f.total_inventory_value) AS aggregate_value_usd
    FROM fact_inventory_daily_snapshot f
    JOIN dim_product_sku s ON f.sku_id = s.sku_id
    WHERE f.date_key = (SELECT MAX(date_key) FROM fact_inventory_daily_snapshot)
    GROUP BY s.sku_id, s.sku_name, s.product_category
),
pareto_calc AS (
    SELECT 
        sku_id,
        sku_name,
        product_category,
        aggregate_value_usd,
        SUM(aggregate_value_usd) OVER(ORDER BY aggregate_value_usd DESC) AS cumulative_value,
        SUM(aggregate_value_usd) OVER() AS total_value
    FROM sku_valuations
)
SELECT 
    sku_id,
    sku_name,
    product_category,
    aggregate_value_usd,
    ROUND((cumulative_value / total_value) * 100, 2) AS cumulative_value_pct,
    CASE 
        WHEN (cumulative_value / total_value) <= 0.80 THEN 'A'
        WHEN (cumulative_value / total_value) <= 0.95 THEN 'B'
        ELSE 'C'
    END AS dynamic_abc_class
FROM pareto_calc;
