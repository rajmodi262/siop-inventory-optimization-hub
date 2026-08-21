"""
SIOP Demand Forecasting & Planning Module.
Implements Pure-NumPy Time-Series Forecasting (Holt's Double Exponential Smoothing & Moving Averages),
along with Forecast Accuracy Metrics: MAPE, WAPE, and Forecast Bias (Tracking Signal).
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Any

class SIOPDemandForecaster:
    def __init__(self, alpha: float = 0.3, beta: float = 0.1):
        """
        :param alpha: Level smoothing parameter (0 < alpha < 1).
        :param beta: Trend smoothing parameter (0 < beta < 1).
        """
        self.alpha = alpha
        self.beta = beta

    @staticmethod
    def calculate_mape(actual: np.ndarray, forecast: np.ndarray) -> float:
        """
        Mean Absolute Percentage Error (MAPE).
        Formula: MAPE = (1/n) * sum(|Actual - Forecast| / Actual) * 100
        """
        actual, forecast = np.array(actual, dtype=float), np.array(forecast, dtype=float)
        mask = actual > 0
        if np.sum(mask) == 0:
            return 0.0
        return float(np.mean(np.abs((actual[mask] - forecast[mask]) / actual[mask])) * 100.0)

    @staticmethod
    def calculate_wape(actual: np.ndarray, forecast: np.ndarray) -> float:
        """
        Weighted Absolute Percentage Error (WAPE / MAD/Mean Ratio).
        Standard enterprise supply chain metric resistant to zero-demand skew.
        Formula: WAPE = sum(|Actual - Forecast|) / sum(Actual) * 100
        """
        actual, forecast = np.array(actual, dtype=float), np.array(forecast, dtype=float)
        total_actual = np.sum(actual)
        if total_actual <= 0:
            return 0.0
        return float((np.sum(np.abs(actual - forecast)) / total_actual) * 100.0)

    @staticmethod
    def calculate_forecast_bias(actual: np.ndarray, forecast: np.ndarray) -> Dict[str, float]:
        """
        Calculates Forecast Bias (Tracking Signal & Normalized Error).
        Positive bias = Over-forecasting (Excess inventory risk).
        Negative bias = Under-forecasting (Stockout risk).
        """
        actual, forecast = np.array(actual, dtype=float), np.array(forecast, dtype=float)
        error = forecast - actual
        total_actual = np.sum(actual)
        net_bias_units = float(np.sum(error))
        bias_pct = float((net_bias_units / total_actual * 100.0) if total_actual > 0 else 0.0)
        
        return {
            "net_bias_units": round(net_bias_units, 2),
            "bias_percentage": round(bias_pct, 2),
            "interpretation": "Over-Forecasting (Excess Stock Risk)" if bias_pct > 5 else ("Under-Forecasting (Stockout Risk)" if bias_pct < -5 else "Well-Calibrated (Balanced)")
        }

    def generate_holt_winters_forecast(self, historical_demand: pd.Series, forecast_horizon: int = 30) -> pd.DataFrame:
        """
        Pure NumPy implementation of Holt's Linear Exponential Smoothing.
        Level: L_t = alpha * Y_t + (1 - alpha) * (L_{t-1} + T_{t-1})
        Trend: T_t = beta * (L_t - L_{t-1}) + (1 - beta) * T_{t-1}
        Forecast: F_{t+h} = L_t + h * T_t
        """
        y = historical_demand.fillna(method="ffill").fillna(0).astype(float).values
        n = len(y)
        
        if n < 2:
            base_val = y[0] if n == 1 else 10.0
            return pd.DataFrame({
                "step": list(range(1, forecast_horizon + 1)),
                "forecast_demand_units": [round(float(base_val), 1)] * forecast_horizon
            })
            
        level = y[0]
        trend = y[1] - y[0]
        
        for t in range(1, n):
            prev_level = level
            level = self.alpha * y[t] + (1 - self.alpha) * (prev_level + trend)
            trend = self.beta * (level - prev_level) + (1 - self.beta) * trend
            
        # Extrapolate forward
        forecasts = []
        for h in range(1, forecast_horizon + 1):
            f_h = max(0.0, level + h * trend)
            forecasts.append(round(float(f_h), 1))
            
        return pd.DataFrame({
            "step": list(range(1, forecast_horizon + 1)),
            "forecast_demand_units": forecasts
        })

    def evaluate_plant_capacity_loading(self, df_snapshots: pd.DataFrame, df_plants: pd.DataFrame) -> pd.DataFrame:
        """
        Evaluates plant capacity utilization against SIOP production demand.
        """
        latest_date = df_snapshots["date_key"].max()
        latest_df = df_snapshots[df_snapshots["date_key"] == latest_date]
        
        plant_demand = latest_df.groupby("plant_id")["daily_actual_demand_qty"].sum().reset_index()
        merged = plant_demand.merge(df_plants, on="plant_id")
        
        merged["daily_capacity_units"] = (merged["operating_capacity_pct"] / 100.0) * 1200
        merged["current_loading_pct"] = np.round((merged["daily_actual_demand_qty"] / merged["daily_capacity_units"]) * 100.0, 1)
        merged["capacity_status"] = merged["current_loading_pct"].apply(
            lambda p: "Over-Capacity (Bottleneck)" if p > 100 else ("Optimal (80-100%)" if p >= 80 else "Under-Utilized (<80%)")
        )
        return merged
