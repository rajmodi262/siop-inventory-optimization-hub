"""
Core Analytical Engine for SIOP & Multi-Plant Inventory Optimization.
Calculates dynamic safety stock buffers, DOH, EOQ, ABC/XYZ classification, and E&O reserve savings.
"""

import numpy as np
import pandas as pd
from scipy.stats import norm

class InventoryOptimizer:
    def __init__(self, service_level_z_score: float = 1.645):
        """
        :param service_level_z_score: Default 1.645 (corresponds to 95% cycle service level).
        """
        self.default_z = service_level_z_score

    @staticmethod
    def calculate_safety_stock(avg_demand: float, demand_std: float, 
                               avg_lead_time: float, lead_time_std: float, 
                               service_level: float = 0.95) -> float:
        """
        Calculates Safety Stock under simultaneous demand and lead-time uncertainty.
        Formula: SS = Z * sqrt( (Avg_LT * Variance_Demand) + (Avg_Demand^2 * Variance_LT) )
        """
        z = norm.ppf(service_level)
        variance_term = (avg_lead_time * (demand_std ** 2)) + ((avg_demand ** 2) * (lead_time_std ** 2))
        return float(z * np.sqrt(max(0.0, variance_term)))

    @staticmethod
    def calculate_reorder_point(avg_demand: float, avg_lead_time: float, safety_stock: float) -> float:
        """
        Formula: ROP = (Average Daily Demand * Average Lead Time) + Safety Stock
        """
        return (avg_demand * avg_lead_time) + safety_stock

    @staticmethod
    def calculate_eoq(annual_demand: float, order_cost: float, unit_cost: float, holding_rate: float) -> float:
        """
        Economic Order Quantity (Wilson formula):
        EOQ = sqrt( (2 * Annual_Demand * Order_Cost) / (Unit_Cost * Holding_Rate) )
        """
        holding_cost = max(0.001, unit_cost * (holding_rate / 100.0 if holding_rate > 1 else holding_rate))
        return float(np.sqrt((2 * annual_demand * order_cost) / holding_cost))

    @staticmethod
    def calculate_doh(on_hand_inventory: float, avg_daily_demand: float) -> float:
        """
        Days of Inventory on Hand (DOH).
        """
        if avg_daily_demand <= 0:
            return 999.0  # Dead / Dormant stock indicator
        return float(on_hand_inventory / avg_daily_demand)

    @staticmethod
    def calculate_inventory_turns(annual_cogs: float, average_inventory_value: float) -> float:
        """
        Inventory Turnover Ratio = Annual COGS / Average Inventory Value
        """
        if average_inventory_value <= 0:
            return 0.0
        return float(annual_cogs / average_inventory_value)

    def classify_abc_xyz(self, df_inventory: pd.DataFrame) -> pd.DataFrame:
        """
        Performs dual ABC-XYZ Matrix segmentation:
        - ABC: Cumulative annual value contribution (A: Top 80%, B: Next 15%, C: Bottom 5%)
        - XYZ: Coefficient of Variation (CV) of demand (X: CV < 0.25, Y: 0.25 <= CV <= 0.50, Z: CV > 0.50)
        """
        df = df_inventory.copy()
        
        # ABC Classification by Total Value
        if "total_inventory_value" in df.columns:
            total_val = df["total_inventory_value"].sum()
            df = df.sort_values(by="total_inventory_value", ascending=False)
            df["cum_pct"] = df["total_inventory_value"].cumsum() / (total_val if total_val > 0 else 1)
            df["calc_abc"] = df["cum_pct"].apply(lambda p: "A" if p <= 0.80 else ("B" if p <= 0.95 else "C"))
        
        # XYZ Classification by Demand Coefficient of Variation
        if "trailing_90d_avg_daily_demand" in df.columns and "trailing_90d_demand_std_dev" in df.columns:
            df["cv_demand"] = df["trailing_90d_demand_std_dev"] / df["trailing_90d_avg_daily_demand"].replace(0, 0.001)
            df["calc_xyz"] = df["cv_demand"].apply(lambda cv: "X" if cv < 0.25 else ("Y" if cv <= 0.50 else "Z"))
            
        return df

    def analyze_excess_and_obsolete(self, df_snapshots: pd.DataFrame, dormant_threshold_days: int = 90) -> dict:
        """
        Identifies Excess & Obsolete (E&O) reserves and working capital reduction potential.
        """
        latest_date = df_snapshots["date_key"].max()
        latest_df = df_snapshots[df_snapshots["date_key"] == latest_date].copy()
        
        dormant_mask = latest_df["dormant_days_since_last_movement"] >= dormant_threshold_days
        excess_mask = (latest_df["days_of_inventory_on_hand"] > 60) & (~dormant_mask)
        healthy_mask = (~dormant_mask) & (~excess_mask) & (latest_df["on_hand_qty"] > 0)
        stockout_mask = latest_df["on_hand_qty"] == 0
        
        total_inv_val = latest_df["total_inventory_value"].sum()
        dormant_val = latest_df.loc[dormant_mask, "total_inventory_value"].sum()
        excess_val = latest_df.loc[excess_mask, "total_inventory_value"].sum()
        healthy_val = latest_df.loc[healthy_mask, "total_inventory_value"].sum()
        
        return {
            "total_inventory_value_usd": round(total_inv_val, 2),
            "dormant_obsolete_value_usd": round(dormant_val, 2),
            "excess_working_capital_usd": round(excess_val, 2),
            "healthy_working_capital_usd": round(healthy_val, 2),
            "dormant_percentage": round((dormant_val / total_inv_val * 100) if total_inv_val > 0 else 0, 2),
            "excess_percentage": round((excess_val / total_inv_val * 100) if total_inv_val > 0 else 0, 2),
            "stockout_sku_count": int(stockout_mask.sum()),
            "total_sku_plant_count": len(latest_df)
        }
