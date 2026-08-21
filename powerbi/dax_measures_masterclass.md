# 🏆 Enterprise Power BI DAX Masterclass Reference Guide
**Platform:** Multi-Plant SIOP & Dynamic Inventory Optimization Hub  
**Theme:** Dark Glassmorphic Executive Suite (`#0B0F19`)  
**Design Level:** Senior SCM Analytics / Power BI MVP Grade

---

## 1. Executive KPI Hero Cards & Telemetry Measures

### 1.1 Total Capitalized Inventory Valuation ($)
```dax
Total Inventory Value = 
SUM(fact_inventory_daily_snapshot[total_inventory_value])
```

### 1.2 Target Inventory Value ($) & Variance Delta Pill
```dax
Target Inventory Value = 
[Total Inventory Value] * 0.86 -- 14% Lean Capital Reduction Benchmark

Inventory Variance to Target = 
[Total Inventory Value] - [Target Inventory Value]

Inventory Variance % = 
DIVIDE([Inventory Variance to Target], [Target Inventory Value], 0)
```

### 1.3 Dynamic Card Title with Date Context
```dax
Card Title - Inventory Health = 
"Total Inventory Valuation | " & FORMAT(MAX(dim_date[full_date]), "MMM YYYY")
```

---

## 2. Dynamic Safety Stock & Service Level Modeling

### 2.1 Bivariate Normal Distribution Safety Stock ($Z$-Score)
Calculates continuous safety buffers incorporating **demand volatility ($\sigma_D$)** and **supplier lead-time variance ($\sigma_L$)**:

```dax
Dynamic Safety Stock Units = 
VAR ServiceLevelPct = 0.95 -- 95% Cycle Service Level Target
VAR Z_Score = 1.645
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

### 2.2 Safety Stock Capital Allocation ($)
```dax
Safety Stock Capital Allocated = 
SUMX(
    fact_inventory_daily_snapshot,
    [Dynamic Safety Stock Units] * fact_inventory_daily_snapshot[unit_cost]
)
```

---

## 3. SIOP & Operational Health Telemetry

### 3.1 Days of Inventory on Hand (DOH)
```dax
Days of Inventory on Hand (DOH) = 
VAR CurrentOnHand = SUM(fact_inventory_daily_snapshot[on_hand_qty])
VAR DailyDemand = SUM(fact_inventory_daily_snapshot[trailing_90d_avg_daily_demand])
RETURN
    IF(
        DailyDemand > 0,
        DIVIDE(CurrentOnHand, DailyDemand, 0),
        999
    )
```

### 3.2 Dynamic Conditional Formatting Color Hex for DOH
```dax
DOH Status Color Hex = 
VAR DOH = [Days of Inventory on Hand (DOH)]
RETURN
    SWITCH(
        TRUE(),
        DOH < 15, "#EF4444", -- Critical Stockout Danger (Red)
        DOH >= 15 && DOH <= 45, "#10B981", -- Healthy Buffer (Green)
        DOH > 45 && DOH <= 75, "#F59E0B", -- Excess Inventory (Amber)
        DOH > 75, "#DC2626" -- Severely Bloated Capital (Crimson)
    )
```

### 3.3 Inventory Turnover Ratio
```dax
Inventory Turnover Ratio = 
VAR AnnualCOGS = SUM(fact_inventory_daily_snapshot[daily_actual_demand_qty]) * AVERAGE(fact_inventory_daily_snapshot[unit_cost]) * 365
VAR AvgInventory = [Total Inventory Value]
RETURN
    DIVIDE(AnnualCOGS, AvgInventory, 0)
```

---

## 4. Excess & Obsolete (E&O) Aging Cohort Measures

### 4.1 E&O Dormant Reserves ($)
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

### 4.2 Aging Cohort 0-30 Days (Fresh Capital)
```dax
Aging Cohort 0-30d = 
CALCULATE(
    [Total Inventory Value],
    fact_inventory_daily_snapshot[dormant_days_since_last_movement] < 30
)
```

### 4.3 Aging Cohort 31-60 Days (Active Rotation)
```dax
Aging Cohort 31-60d = 
CALCULATE(
    [Total Inventory Value],
    fact_inventory_daily_snapshot[dormant_days_since_last_movement] >= 30 &&
    fact_inventory_daily_snapshot[dormant_days_since_last_movement] < 60
)
```

### 4.4 Aging Cohort 61-90 Days (At-Risk Inventory)
```dax
Aging Cohort 61-90d = 
CALCULATE(
    [Total Inventory Value],
    fact_inventory_daily_snapshot[dormant_days_since_last_movement] >= 60 &&
    fact_inventory_daily_snapshot[dormant_days_since_last_movement] < 90
)
```

### 4.5 Aging Cohort 90+ Days (Dormant Write-Off Candidate)
```dax
Aging Cohort 90d+ = 
CALCULATE(
    [Total Inventory Value],
    fact_inventory_daily_snapshot[dormant_days_since_last_movement] >= 90
)
```

---

## 5. Advanced Power BI In-Table SVG Sparkline Measure

This DAX measure dynamically renders an **inline SVG micro-chart** directly inside Power BI table visuals showing the trailing 30-day demand trend for any SKU:

```dax
SKU Demand Sparkline SVG = 
VAR SparklineData = 
    ADDCOLUMNS(
        SUMMARIZE(fact_inventory_daily_snapshot, dim_date[date_key]),
        "DailyDemand", CALCULATE(SUM(fact_inventory_daily_snapshot[daily_actual_demand_qty]))
    )
VAR MaxDemand = MAXX(SparklineData, [DailyDemand])
VAR MinDemand = MINX(SparklineData, [DailyDemand])
VAR Range = IF(MaxDemand - MinDemand = 0, 1, MaxDemand - MinDemand)
VAR SparklinePoints = 
    CONCATENATEX(
        SparklineData,
        VAR X = INT(DIVIDE(RANKX(SparklineData, dim_date[date_key], , ASC) - 1, COUNTROWS(SparklineData) - 1, 0) * 100)
        VAR Y = 30 - INT(DIVIDE([DailyDemand] - MinDemand, Range, 0) * 25)
        RETURN X & "," & Y,
        " "
    )
RETURN
    "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 30'><polyline fill='none' stroke='%2338BDF8' stroke-width='2' points='" & SparklinePoints & "'/></svg>"
```

*(Note: In Power BI Desktop, set Data Category for `[SKU Demand Sparkline SVG]` to **Image URL**).*

---

## 6. Multi-Page Canvas Layout Guide

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   EATON SCM EXECUTIVE SUITE (5 PAGES)                                  │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Page 1: 📊 Executive Command Center & Capital Pulse                                                    │
│         • 4 Top Telemetry KPI Cards with target delta badges                                           │
│         • Plant Allocation Donut Chart & Regional Inventory Bar Chart                                  │
│         • Inventory Value Walk (Receipts -> Demand Consumption -> Ending Position)                     │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Page 2: 🎯 SIOP Dynamic Safety Stock & Stress Tester                                                   │
│         • What-If Parameter Slicers (Service Level %, Lead Time Multiplier)                            │
│         • Scatter Matrix: SKU Demand Variance vs Lead Time Std Dev (Bubble Size = Cost)                 │
│         • Multi-Echelon Stockout Probability Heatmap Matrix                                            │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Page 3: 📦 Dual ABC/XYZ & 4-Tier E&O Aging Matrix                                                      │
│         • 9-Box ABC-XYZ Grid Matrix with interactive cross-filtering                                   │
│         • 4-Tier Aging Cohort Stacked Bar (0-30d, 31-60d, 61-90d, 90d+)                                │
│         • Capital Reclamation Action Table with Dormancy Badges                                        │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Page 4: 📈 Multi-Plant Capacity Loading & Forecast Variance                                            │
│         • Unconstrained Forecast vs Scheduled Production vs Actual Consumption Line                    │
│         • Plant Capacity Loading Gauges with Over-Capacity Bottleneck Flags                            │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Page 5: 🛡️ Automated Data Governance & QA Health Telemetry                                            │
│         • Referential Integrity Health Scorecard (40+ automated assertions)                            │
│         • Negative Stock Balance and UOM Discrepancy Log                                               │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```
