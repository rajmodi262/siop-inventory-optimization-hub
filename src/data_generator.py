"""
Enterprise ERP Synthetic Data Generator for SIOP & Inventory Optimization Hub.
Generates realistic multi-plant manufacturing datasets modeled after industrial power & electrical equipment manufacturing.
"""

import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_siop_dataset(num_skus=200, days=90, seed=42):
    random.seed(seed)
    np.random.seed(seed)
    
    # 1. Plants (Manufacturing Centers)
    plants_data = [
        {"plant_id": "PL-PUN", "plant_name": "Pune Power Electronics Plant", "region": "APAC", "country": "India", "city": "Pune", "manufacturing_focus": "EV Inverters & Microcontrollers", "operating_capacity_pct": 88.5, "annual_holding_rate_pct": 22.0},
        {"plant_id": "PL-TEX", "plant_name": "Texas Heavy Transformer Facility", "region": "Americas", "country": "USA", "city": "Houston", "manufacturing_focus": "Grid Step-Down Transformers", "operating_capacity_pct": 92.0, "annual_holding_rate_pct": 24.0},
        {"plant_id": "PL-SHA", "plant_name": "Shanghai Switchgear Automation Hub", "region": "APAC", "country": "China", "city": "Shanghai", "manufacturing_focus": "Medium Voltage Switchgears", "operating_capacity_pct": 85.0, "annual_holding_rate_pct": 20.0},
        {"plant_id": "PL-STU", "plant_name": "Stuttgart Industrial Hydraulics", "region": "EMEA", "country": "Germany", "city": "Stuttgart", "manufacturing_focus": "Aerospace & Industrial Valves", "operating_capacity_pct": 81.0, "annual_holding_rate_pct": 25.0},
        {"plant_id": "PL-JUA", "plant_name": "Juarez Precision Breakers Assembly", "region": "Americas", "country": "Mexico", "city": "Juarez", "manufacturing_focus": "Residential & Commercial Breakers", "operating_capacity_pct": 90.5, "annual_holding_rate_pct": 21.5}
    ]
    df_plants = pd.DataFrame(plants_data)
    
    # 2. Suppliers
    suppliers_data = [
        {"supplier_id": "SUP-101", "supplier_name": "Global Copper & Alloys Ltd", "tier_level": "Strategic", "country": "Chile", "avg_contracted_lead_time_days": 28, "lead_time_std_dev_days": 4.5, "historical_otif_pct": 89.2, "single_source_flag": False},
        {"supplier_id": "SUP-102", "supplier_name": "Apex Semiconductor Fab", "tier_level": "Strategic", "country": "Taiwan", "avg_contracted_lead_time_days": 45, "lead_time_std_dev_days": 8.2, "historical_otif_pct": 82.5, "single_source_flag": True},
        {"supplier_id": "SUP-103", "supplier_name": "Precision Magnetic Steels", "tier_level": "Tier 1", "country": "Japan", "avg_contracted_lead_time_days": 21, "lead_time_std_dev_days": 2.8, "historical_otif_pct": 94.8, "single_source_flag": False},
        {"supplier_id": "SUP-104", "supplier_name": "EuroHydraulics Castings GmbH", "tier_level": "Tier 1", "country": "Germany", "avg_contracted_lead_time_days": 18, "lead_time_std_dev_days": 3.1, "historical_otif_pct": 91.0, "single_source_flag": False},
        {"supplier_id": "SUP-105", "supplier_name": "IndoFasteners & Terminals", "tier_level": "Tier 2", "country": "India", "avg_contracted_lead_time_days": 12, "lead_time_std_dev_days": 1.5, "historical_otif_pct": 96.2, "single_source_flag": False},
        {"supplier_id": "SUP-106", "supplier_name": "Nordic Insulators & Resins", "tier_level": "Tier 1", "country": "Sweden", "avg_contracted_lead_time_days": 25, "lead_time_std_dev_days": 3.9, "historical_otif_pct": 93.4, "single_source_flag": False},
        {"supplier_id": "SUP-107", "supplier_name": "Shenzhen Precision PCB Tech", "tier_level": "Tier 1", "country": "China", "avg_contracted_lead_time_days": 35, "lead_time_std_dev_days": 6.5, "historical_otif_pct": 84.1, "single_source_flag": True}
    ]
    df_suppliers = pd.DataFrame(suppliers_data)
    
    # 3. Product SKUs
    categories = [
        ("Electrical Distribution", "Step-Down Transformers", "Units", (1200.0, 8500.0)),
        ("Electrical Distribution", "Circuit Breakers", "Units", (85.0, 450.0)),
        ("Power Electronics", "IGBT Inverters", "Units", (350.0, 2200.0)),
        ("Power Electronics", "Microcontroller Units (MCU)", "Units", (15.0, 180.0)),
        ("Industrial & Hydraulics", "Proportional Valves", "Units", (210.0, 1100.0)),
        ("Raw Materials", "Oxygen-Free Copper Coils", "Kilograms", (9.5, 14.0)),
        ("Raw Materials", "Grain-Oriented Electrical Steel", "Kilograms", (4.2, 8.5))
    ]
    
    skus_data = []
    for i in range(1, num_skus + 1):
        cat, subfam, uom, cost_range = random.choice(categories)
        sku_id = f"SKU-{1000 + i}"
        sku_name = f"{subfam} - Spec {chr(65 + (i % 26))}{i % 100}"
        
        # ABC & XYZ distribution
        rand_abc = random.random()
        abc = "A" if rand_abc < 0.20 else ("B" if rand_abc < 0.50 else "C")
        rand_xyz = random.random()
        xyz = "X" if rand_xyz < 0.40 else ("Y" if rand_xyz < 0.75 else "Z")
        
        unit_cost = round(random.uniform(*cost_range), 2)
        target_service_level = 98.0 if abc == "A" else (95.0 if abc == "B" else 90.0)
        min_order_qty = 10 if uom == "Units" else 100
        
        skus_data.append({
            "sku_id": sku_id,
            "sku_name": sku_name,
            "product_category": cat,
            "product_subfamily": subfam,
            "abc_classification": abc,
            "xyz_demand_variability": xyz,
            "unit_of_measure": uom,
            "standard_unit_cost": unit_cost,
            "target_service_level_pct": target_service_level,
            "min_order_qty": min_order_qty,
            "pack_size": 5 if uom == "Units" else 50
        })
    df_skus = pd.DataFrame(skus_data)
    
    # 4. Dates
    start_date = datetime(2026, 1, 1)
    dates_data = []
    for d in range(days):
        curr = start_date + timedelta(days=d)
        dates_data.append({
            "date_key": int(curr.strftime("%Y%m%d")),
            "full_date": curr.strftime("%Y-%m-%d"),
            "year": curr.year,
            "quarter": f"Q{(curr.month - 1) // 3 + 1}",
            "month": curr.month,
            "month_name": curr.strftime("%B"),
            "week_of_year": curr.isocalendar()[1],
            "is_weekend": curr.weekday() >= 5,
            "is_holiday": curr.weekday() == 6 and d % 14 == 0,
            "fiscal_quarter": f"FY{str(curr.year)[2:]}-Q{(curr.month - 1) // 3 + 1}"
        })
    df_dates = pd.DataFrame(dates_data)
    
    # 5. Generate Daily Inventory Snapshots (Fact Table)
    snapshots = []
    snapshot_id = 100001
    
    # Pre-assign SKU base parameters across plants
    plant_sku_map = {}
    for plant in df_plants["plant_id"]:
        # Each plant manufactures a subset of SKUs
        assigned_skus = random.sample(df_skus["sku_id"].tolist(), k=min(len(df_skus), 80))
        for sku in assigned_skus:
            base_daily_demand = random.uniform(5, 120)
            demand_std = base_daily_demand * (0.15 if df_skus.loc[df_skus['sku_id']==sku, 'xyz_demand_variability'].values[0] == 'X' else (0.35 if df_skus.loc[df_skus['sku_id']==sku, 'xyz_demand_variability'].values[0] == 'Y' else 0.70))
            supplier = random.choice(df_suppliers["supplier_id"].tolist())
            plant_sku_map[(plant, sku)] = {
                "base_demand": base_daily_demand,
                "demand_std": demand_std,
                "supplier_id": supplier,
                "current_on_hand": int(base_daily_demand * random.uniform(10, 45)),
                "in_transit": int(base_daily_demand * random.uniform(5, 20)),
                "dormant_days": 0 if random.random() > 0.12 else random.randint(30, 220)
            }
            
    for _, date_row in df_dates.iterrows():
        d_key = date_row["date_key"]
        for (plant_id, sku_id), state in plant_sku_map.items():
            sku_meta = df_skus.loc[df_skus["sku_id"] == sku_id].iloc[0]
            sup_meta = df_suppliers.loc[df_suppliers["supplier_id"] == state["supplier_id"]].iloc[0]
            
            # Demand calculation
            is_dormant = state["dormant_days"] > 60
            actual_demand = 0 if is_dormant else max(0, int(np.random.normal(state["base_demand"], state["demand_std"])))
            forecast_demand = int(state["base_demand"] * random.uniform(0.90, 1.10))
            
            # Inventory state update
            state["current_on_hand"] = max(0, state["current_on_hand"] - actual_demand + (int(state["in_transit"] * 0.1) if random.random() < 0.2 else 0))
            if is_dormant:
                state["dormant_days"] += 1
                
            on_hand = state["current_on_hand"]
            in_transit = state["in_transit"]
            unit_cost = sku_meta["standard_unit_cost"]
            total_val = round(on_hand * unit_cost, 2)
            
            # Statistical Parameters
            lead_time = sup_meta["avg_contracted_lead_time_days"]
            lt_std = sup_meta["lead_time_std_dev_days"]
            avg_demand = max(0.1, state["base_demand"])
            d_std = state["demand_std"]
            
            # Z-Score for 95% service level = 1.645, 98% = 2.054
            z_score = 2.054 if sku_meta["target_service_level_pct"] >= 98 else 1.645
            safety_stock = int(z_score * np.sqrt(lead_time * (d_std ** 2) + (avg_demand ** 2) * (lt_std ** 2)))
            reorder_point = int((avg_demand * lead_time) + safety_stock)
            
            # EOQ formula: sqrt((2 * Demand * OrderCost) / HoldingCost)
            annual_demand = avg_demand * 365
            order_cost = 75.0
            holding_cost = unit_cost * (df_plants.loc[df_plants["plant_id"] == plant_id, "annual_holding_rate_pct"].values[0] / 100.0)
            eoQ = int(np.sqrt((2 * annual_demand * order_cost) / max(0.01, holding_cost)))
            
            # DOH
            doh = round(on_hand / avg_demand, 1)
            is_stockout = on_hand == 0
            is_excess = doh > 60 and not is_dormant
            
            snapshots.append({
                "snapshot_id": snapshot_id,
                "date_key": d_key,
                "plant_id": plant_id,
                "sku_id": sku_id,
                "supplier_id": state["supplier_id"],
                "on_hand_qty": on_hand,
                "in_transit_qty": in_transit,
                "allocated_wip_qty": int(on_hand * 0.15),
                "backorder_qty": random.randint(10, 50) if is_stockout else 0,
                "available_to_promise_qty": max(0, int(on_hand * 0.85)),
                "unit_cost": unit_cost,
                "total_inventory_value": total_val,
                "daily_actual_demand_qty": actual_demand,
                "daily_forecasted_demand_qty": forecast_demand,
                "trailing_90d_avg_daily_demand": round(avg_demand, 2),
                "trailing_90d_demand_std_dev": round(d_std, 2),
                "lead_time_days": lead_time,
                "calculated_safety_stock_qty": safety_stock,
                "calculated_reorder_point_qty": reorder_point,
                "calculated_economic_order_qty": eoQ,
                "days_of_inventory_on_hand": doh,
                "is_stockout_flag": is_stockout,
                "is_excess_inventory_flag": is_excess,
                "dormant_days_since_last_movement": state["dormant_days"]
            })
            snapshot_id += 1
            
    df_snapshots = pd.DataFrame(snapshots)
    
    # Save datasets
    os.makedirs("data", exist_ok=True)
    df_plants.to_csv("data/dim_plant.csv", index=False)
    df_suppliers.to_csv("data/dim_supplier.csv", index=False)
    df_skus.to_csv("data/dim_product_sku.csv", index=False)
    df_dates.to_csv("data/dim_date.csv", index=False)
    df_snapshots.to_csv("data/fact_inventory_daily_snapshot.csv", index=False)
    
    print(f"[OK] Generated {len(df_snapshots)} daily inventory snapshots across {len(df_plants)} plants and {len(df_skus)} SKUs.")
    return df_plants, df_suppliers, df_skus, df_dates, df_snapshots

if __name__ == "__main__":
    generate_siop_dataset(num_skus=120, days=60)
