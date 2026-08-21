# Enterprise Power BI DAX Measures & Data Model Guide
**Project:** Multi-Plant SIOP & Dynamic Inventory Optimization Hub

---

## 1. Data Model Architecture (Star Schema)

* **Fact Table:** `fact_inventory_daily_snapshot`
* **Dimension Tables:**
  * `dim_plant` (1-to-many relationship on `plant_id`)
  * `dim_product_sku` (1-to-many relationship on `sku_id`)
  * `dim_supplier` (1-to-many relationship on `supplier_id`)
  * `dim_date` (1-to-many relationship on `date_key`)

---

## 2. Core DAX Calculations

### 1. Total Inventory Valuation ($)
```dax
Total Inventory Value = 
SUM(fact_inventory_daily_snapshot[total_inventory_value])
```

### 2. Days of Inventory on Hand (DOH)
```dax
Days of Inventory on Hand (DOH) = 
VAR CurrentOnHand = SUM(fact_inventory_daily_snapshot[on_hand_qty])
VAR DailyDemand = SUM(fact_inventory_daily_snapshot[trailing_90d_avg_daily_demand])
RETURN
    IF(
        DailyDemand > 0,
        DIVIDE(CurrentOnHand, DailyDemand, 0),
        BLANK()
    )
```

### 3. Dynamic Safety Stock Buffer (Service Level Z-Score @ 95%)
```dax
Dynamic Safety Stock = 
VAR Z_Score = 1.645 -- 95% Cycle Service Level
VAR AvgDailyDemand = AVERAGE(fact_inventory_daily_snapshot[trailing_90d_avg_daily_demand])
VAR DemandVariance = POWER(STDEV.S(fact_inventory_daily_snapshot[daily_actual_demand_qty]), 2)
VAR AvgLeadTime = AVERAGE(fact_inventory_daily_snapshot[lead_time_days])
VAR LeadTimeVariance = POWER(AVERAGE(dim_supplier[lead_time_std_dev_days]), 2)
VAR CombinedVariance = (AvgLeadTime * DemandVariance) + (POWER(AvgDailyDemand, 2) * LeadTimeVariance)
RETURN
    IF(
        CombinedVariance > 0,
        Z_Score * SQRT(CombinedVariance),
        0
    )
```

### 4. Excess & Obsolete (E&O) Inventory Reserves ($)
```dax
Excess and Obsolete (E&O) Value = 
CALCULATE(
    [Total Inventory Value],
    FILTER(
        fact_inventory_daily_snapshot,
        fact_inventory_daily_snapshot[dormant_days_since_last_movement] >= 90 ||
        fact_inventory_daily_snapshot[days_of_inventory_on_hand] > 60
    )
)
```

### 5. Stockout Risk Index (% of SKUs with 0 On-Hand)
```dax
Stockout SKU % = 
VAR TotalSKUs = DISTINCTCOUNT(fact_inventory_daily_snapshot[sku_id])
VAR StockoutSKUs = 
    CALCULATE(
        DISTINCTCOUNT(fact_inventory_daily_snapshot[sku_id]),
        fact_inventory_daily_snapshot[on_hand_qty] = 0
    )
RETURN
    DIVIDE(StockoutSKUs, TotalSKUs, 0)
```

### 6. Inventory Turnover Ratio
```dax
Inventory Turnover Ratio = 
VAR AnnualCOGS = SUM(fact_inventory_daily_snapshot[daily_actual_demand_qty]) * AVERAGE(fact_inventory_daily_snapshot[unit_cost]) * 365
VAR AvgInventoryValue = [Total Inventory Value]
RETURN
    DIVIDE(AnnualCOGS, AvgInventoryValue, 0)
```

---

## 3. Power BI Dashboard Layout Structure

1. **Executive Overview Page**:
   * Card Visuals: Total Inventory Value, Average DOH, Excess Working Capital ($), Stockout SKU %.
   * Slicers: Plant Region, Product Category, ABC Class (A/B/C), XYZ Class (X/Y/Z).
   * Visual: Bar chart of Inventory Value by Plant vs. Target DOH.
2. **SIOP & Plant Capacity Page**:
   * Visual: Line chart comparing Unconstrained Forecast vs. Actual Consumption vs. Scheduled Production.
   * Heatmap matrix: SKUs vs Plants color-coded by Safety Stock Buffer Health (Red = At Risk, Green = Healthy, Orange = Excess).
3. **Data Quality & Governance Page**:
   * Table displaying automated data validation logs, orphaned keys count, and negative stock flags.
