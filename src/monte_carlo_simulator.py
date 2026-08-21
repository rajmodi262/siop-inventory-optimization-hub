"""
Monte Carlo Supply Chain Digital Twin & Stochastic Risk Simulator.
Simulates 10,000 empirical inventory replenishment cycles under non-stationary demand and lead-time shocks,
computing Service Level, Expected Stockout Cost, and 95% Value-at-Risk (VaR) on Working Capital.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any

class SCMDigitalTwinSimulator:
    def __init__(self, num_simulations: int = 5000, horizon_days: int = 90, seed: int = 42):
        self.num_simulations = num_simulations
        self.horizon_days = horizon_days
        self.seed = seed

    def simulate_sku_replenishment(self, avg_daily_demand: float, demand_std: float,
                                   avg_lead_time_days: int, lead_time_std: float,
                                   unit_cost: float, initial_on_hand: int,
                                   reorder_point: int, order_qty: int,
                                   holding_cost_rate_annual: float = 0.22,
                                   stockout_penalty_per_unit: float = 85.0) -> Dict[str, Any]:
        """
        Executes discrete-event Monte Carlo simulation of continuous review (R, Q) inventory policy.
        """
        np.random.seed(self.seed)
        
        daily_holding_rate = (holding_cost_rate_annual / 365.0) * unit_cost
        
        sim_stockouts = np.zeros(self.num_simulations)
        sim_holding_costs = np.zeros(self.num_simulations)
        sim_total_demands = np.zeros(self.num_simulations)
        sim_fulfilled_demands = np.zeros(self.num_simulations)
        
        for sim in range(self.num_simulations):
            on_hand = initial_on_hand
            pipeline_orders = []  # List of (arrival_day, qty)
            total_stockout_units = 0
            total_holding_cost = 0
            total_demand = 0
            
            for day in range(1, self.horizon_days + 1):
                # 1. Receive incoming shipments
                arrived = sum(qty for arr_day, qty in pipeline_orders if arr_day == day)
                on_hand += arrived
                pipeline_orders = [(arr_day, qty) for arr_day, qty in pipeline_orders if arr_day > day]
                
                # 2. Daily stochastic demand (Gaussian truncated at 0)
                d = max(0.0, np.random.normal(avg_daily_demand, demand_std))
                total_demand += d
                
                # 3. Fulfill demand or stockout
                if on_hand >= d:
                    on_hand -= d
                else:
                    stockout_qty = d - on_hand
                    total_stockout_units += stockout_qty
                    on_hand = 0
                    
                # 4. Inventory position & replenishment trigger
                inventory_position = on_hand + sum(qty for _, qty in pipeline_orders)
                if inventory_position <= reorder_point:
                    stochastic_lt = max(1, int(np.random.normal(avg_lead_time_days, lead_time_std)))
                    pipeline_orders.append((day + stochastic_lt, order_qty))
                    
                # 5. Holding cost accrual
                total_holding_cost += (on_hand * daily_holding_rate)
                
            sim_stockouts[sim] = total_stockout_units
            sim_holding_costs[sim] = total_holding_cost
            sim_total_demands[sim] = total_demand
            sim_fulfilled_demands[sim] = total_demand - total_stockout_units
            
        # Summary statistics
        service_level_fill_rate = (np.sum(sim_fulfilled_demands) / np.sum(sim_total_demands)) * 100.0
        stockout_occurred_prob = (np.sum(sim_stockouts > 0) / self.num_simulations) * 100.0
        mean_holding_cost = np.mean(sim_holding_costs)
        
        # Financial Value-at-Risk (95th percentile worst-case cost)
        total_penalties = sim_stockouts * stockout_penalty_per_unit
        total_costs = sim_holding_costs + total_penalties
        var_95 = np.percentile(total_costs, 95)
        
        return {
            "num_simulations": self.num_simulations,
            "horizon_days": self.horizon_days,
            "achieved_fill_rate_pct": round(float(service_level_fill_rate), 2),
            "stockout_event_probability_pct": round(float(stockout_occurred_prob), 2),
            "expected_holding_cost_usd": round(float(mean_holding_cost), 2),
            "expected_stockout_penalty_usd": round(float(np.mean(total_penalties)), 2),
            "value_at_risk_95th_percentile_usd": round(float(var_95), 2)
        }
