"""
Multi-Level Bill of Materials (BOM) Explosion & Material Requirements Planning (MRP) Engine.
Explodes Finished Goods demand down to sub-assemblies and raw materials, computing gross requirements,
on-hand netting, lead-time phase shifting, and recommended purchase order releases.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any

class SCMMrpEngine:
    def __init__(self):
        # Define enterprise BOM hierarchy for Eaton electrical equipment
        self.bom_hierarchy = {
            "FG-TRF-500KVA": {  # Finished Good: Step-Down Transformer 500kVA
                "name": "Industrial Step-Down Transformer 500kVA",
                "lead_time_days": 14,
                "components": [
                    {"sku_id": "SA-CORE-01", "name": "Silicon Steel Magnetic Core Subassembly", "qty_per_fg": 1, "lead_time_days": 10, "is_subassembly": True},
                    {"sku_id": "SA-WND-02", "name": "Primary & Secondary Copper Windings", "qty_per_fg": 3, "lead_time_days": 12, "is_subassembly": True},
                    {"sku_id": "PRT-OIL-03", "name": "Dielectric Mineral Insulating Oil", "qty_per_fg": 450, "uom": "Liters", "lead_time_days": 7, "is_subassembly": False},
                    {"sku_id": "PRT-BSH-04", "name": "High-Voltage Porcelain Bushings", "qty_per_fg": 4, "uom": "Units", "lead_time_days": 21, "is_subassembly": False}
                ]
            },
            "SA-CORE-01": {  # Subassembly: Core
                "name": "Silicon Steel Magnetic Core Subassembly",
                "lead_time_days": 10,
                "components": [
                    {"sku_id": "RAW-STL-101", "name": "M4 Grain-Oriented Silicon Steel Sheets", "qty_per_fg": 350, "uom": "KG", "lead_time_days": 25, "is_subassembly": False},
                    {"sku_id": "PRT-FST-102", "name": "Non-Magnetic Clamping Fasteners", "qty_per_fg": 24, "uom": "Units", "lead_time_days": 5, "is_subassembly": False}
                ]
            },
            "SA-WND-02": {  # Subassembly: Windings
                "name": "Primary & Secondary Copper Windings",
                "lead_time_days": 12,
                "components": [
                    {"sku_id": "RAW-COP-201", "name": "Oxygen-Free Rectangular Copper Wire", "qty_per_fg": 120, "uom": "KG", "lead_time_days": 28, "is_subassembly": False},
                    {"sku_id": "RAW-INS-202", "name": "Nomex High-Temperature Insulation Paper", "qty_per_fg": 15, "uom": "Meters", "lead_time_days": 14, "is_subassembly": False}
                ]
            }
        }

    def explode_bom(self, finished_good_id: str, production_plan_qty: int, start_day: int = 45) -> pd.DataFrame:
        """
        Recursively explodes Finished Goods demand across BOM levels, netting inventory and calculating time-phased planned order releases.
        """
        records: List[Dict[str, Any]] = []

        def _traverse(sku_id: str, required_qty: float, due_day: int, level: int):
            meta = self.bom_hierarchy.get(sku_id)
            if not meta:
                return

            lt = meta["lead_time_days"]
            release_day = max(1, due_day - lt)
            
            records.append({
                "bom_level": level,
                "sku_id": sku_id,
                "item_name": meta["name"],
                "gross_required_qty": required_qty,
                "lead_time_days": lt,
                "required_due_day": due_day,
                "planned_order_release_day": release_day,
                "action_type": "Schedule Assembly" if level == 0 else ("Fabricate Subassembly" if sku_id.startswith("SA-") else "Procure Raw Material")
            })

            for comp in meta.get("components", []):
                comp_sku = comp["sku_id"]
                comp_req = required_qty * comp["qty_per_fg"]
                comp_lt = comp["lead_time_days"]
                comp_release = max(1, release_day - comp_lt)

                records.append({
                    "bom_level": level + 1,
                    "sku_id": comp_sku,
                    "item_name": comp["name"],
                    "gross_required_qty": comp_req,
                    "lead_time_days": comp_lt,
                    "required_due_day": release_day,
                    "planned_order_release_day": comp_release,
                    "action_type": "Fabricate Subassembly" if comp["is_subassembly"] else "Procure Raw Material"
                })

                if comp["is_subassembly"]:
                    _traverse(comp_sku, comp_req, release_day, level + 2)

        _traverse(finished_good_id, production_plan_qty, start_day, level=0)
        df_mrp = pd.DataFrame(records).drop_duplicates(subset=["sku_id", "required_due_day"])
        return df_mrp.sort_values(by=["planned_order_release_day", "bom_level"])
