"""
Power BI High-Resolution Dashboard Mockup & Telemetry Visualizer (3-Page Executive Suite).
Renders stunning, glassmorphic dark-theme executive dashboard pages as showcase PNG images.
"""

import os
import sys
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd
import numpy as np

sys.path.append(os.path.abspath("."))
try:
    from src.data_generator import generate_siop_dataset
except ImportError:
    from data_generator import generate_siop_dataset

def render_executive_dashboard():
    os.makedirs("powerbi/screenshots", exist_ok=True)
    df_plants, df_suppliers, df_skus, df_dates, df_snapshots = generate_siop_dataset(num_skus=150, days=60, seed=42)
    
    # -------------------------------------------------------------
    # PAGE 1: EXECUTIVE COMMAND CENTER & SCM PULSE
    # -------------------------------------------------------------
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(16, 9), dpi=200)
    fig.patch.set_facecolor('#0b0f19')
    
    # Header Banner
    ax_head = fig.add_axes([0.03, 0.90, 0.94, 0.08])
    ax_head.set_facecolor('#111827')
    ax_head.axis('off')
    rect = patches.FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.02", fc="#111827", ec="#1e293b", lw=1.5, transform=ax_head.transAxes)
    ax_head.add_patch(rect)
    ax_head.text(0.02, 0.55, "EATON GLOBAL SCM EXECUTIVE COMMAND CENTER", fontsize=16, fontweight='bold', color='#38bdf8', va='center')
    ax_head.text(0.02, 0.22, "Multi-Plant SIOP Intelligence | Plant Capacity Loading | Safety Stock Buffer Health | E&O Reserves", fontsize=9, color='#94a3b8', va='center')
    ax_head.text(0.98, 0.50, "REFRESHED: LIVE (DIRECT LAKE) | FY26-Q1", fontsize=9, fontweight='bold', color='#10b981', ha='right', va='center')
    
    # 4 KPI Hero Cards
    total_val = df_snapshots[df_snapshots["date_key"]==df_snapshots["date_key"].max()]["total_inventory_value"].sum()
    avg_doh = 36.4
    
    card_configs = [
        ("TOTAL INVENTORY VALUE", f"${total_val:,.0f}", "-14.2% vs Baseline Budget", "#38bdf8", "#10b981", [0.03, 0.74, 0.22, 0.13]),
        ("MEDIAN DAYS ON HAND (DOH)", f"{avg_doh:.1f} Days", "Benchmark: 30-45 Days (Healthy)", "#f8fafc", "#38bdf8", [0.27, 0.74, 0.22, 0.13]),
        ("DORMANT E&O RESERVES", "$1.24M", "9.4% of Total Capital", "#f59e0b", "#ef4444", [0.51, 0.74, 0.22, 0.13]),
        ("SERVICE LEVEL FILL RATE", "96.4%", "+1.4% above 95% SLA Target", "#10b981", "#10b981", [0.75, 0.74, 0.22, 0.13])
    ]
    
    for title, val, sub, val_col, sub_col, pos in card_configs:
        ax = fig.add_axes(pos)
        ax.set_facecolor('#111827')
        ax.axis('off')
        r = patches.FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.03", fc="#111827", ec="#1e293b", lw=1.2, transform=ax.transAxes)
        ax.add_patch(r)
        ax.text(0.08, 0.80, title, fontsize=8, fontweight='bold', color='#94a3b8', transform=ax.transAxes)
        ax.text(0.08, 0.45, val, fontsize=16, fontweight='bold', color=val_col, transform=ax.transAxes)
        ax.text(0.08, 0.18, sub, fontsize=7.5, color=sub_col, transform=ax.transAxes)

    # Chart 1: Inventory Valuation by Manufacturing Facility
    ax_bar = fig.add_axes([0.03, 0.10, 0.46, 0.58])
    ax_bar.set_facecolor('#111827')
    for spine in ax_bar.spines.values():
        spine.set_color('#1e293b')
        spine.set_linewidth(1.2)
        
    plant_summary = df_snapshots[df_snapshots["date_key"]==df_snapshots["date_key"].max()].merge(df_plants, on="plant_id").groupby("city")["total_inventory_value"].sum().sort_values()
    colors = ['#0284c7', '#0369a1', '#0ea5e9', '#38bdf8', '#7dd3fc']
    bars = ax_bar.barh(plant_summary.index, plant_summary.values / 1e6, color=colors, height=0.55, edgecolor='#0b0f19')
    ax_bar.set_title("Capitalized Inventory by Manufacturing Facility ($M)", fontsize=11, fontweight='bold', color='#f8fafc', pad=12, loc='left')
    ax_bar.set_xlabel("Capitalized On-Hand ($ Millions)", fontsize=9, color='#94a3b8')
    ax_bar.tick_params(colors='#94a3b8', labelsize=8.5)
    ax_bar.grid(axis='x', color='#1e293b', linestyle='--', alpha=0.7)
    
    for bar in bars:
        w = bar.get_width()
        ax_bar.text(w + 0.1, bar.get_y() + bar.get_height()/2, f"${w:.2f}M", va='center', color='#f8fafc', fontsize=8, fontweight='bold')

    # Chart 2: Category Breakdown Donut
    ax_pie = fig.add_axes([0.53, 0.10, 0.44, 0.58])
    ax_pie.set_facecolor('#111827')
    for spine in ax_pie.spines.values():
        spine.set_color('#1e293b')
        spine.set_linewidth(1.2)
        
    cat_summary = df_snapshots[df_snapshots["date_key"]==df_snapshots["date_key"].max()].merge(df_skus, on="sku_id").groupby("product_category")["total_inventory_value"].sum()
    pie_colors = ['#38bdf8', '#3b82f6', '#10b981', '#f59e0b']
    wedges, texts, autotexts = ax_pie.pie(
        cat_summary.values, labels=cat_summary.index, autopct='%1.1f%%',
        startangle=140, colors=pie_colors,
        wedgeprops=dict(width=0.45, edgecolor='#0b0f19', lw=2),
        textprops=dict(color="#f8fafc", fontsize=8.5)
    )
    for at in autotexts:
        at.set_color('#0b0f19')
        at.set_fontweight('bold')
    ax_pie.set_title("Inventory Allocation by Product Category", fontsize=11, fontweight='bold', color='#f8fafc', pad=12, loc='left')

    out_p1 = "powerbi/screenshots/page1_executive_command_center.png"
    plt.savefig(out_p1, facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.close()
    print(f"  [OK] Rendered Masterclass Page 1 Mockup: {out_p1}")

    # -------------------------------------------------------------
    # PAGE 2: DYNAMIC SAFETY STOCK & LEAD-TIME STRESS TESTER
    # -------------------------------------------------------------
    fig2 = plt.figure(figsize=(16, 9), dpi=200)
    fig2.patch.set_facecolor('#0b0f19')
    
    ax_head2 = fig2.add_axes([0.03, 0.90, 0.94, 0.08])
    ax_head2.set_facecolor('#111827')
    ax_head2.axis('off')
    rect2 = patches.FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.02", fc="#111827", ec="#1e293b", lw=1.5, transform=ax_head2.transAxes)
    ax_head2.add_patch(rect2)
    ax_head2.text(0.02, 0.55, "SIOP DYNAMIC SAFETY STOCK & STRESS TESTER", fontsize=16, fontweight='bold', color='#38bdf8', va='center')
    ax_head2.text(0.02, 0.22, "Bivariate Stochastic Normal Z-Score Modeling | Lead-Time Volatility Shocks | Working Capital Sensitivity", fontsize=9, color='#94a3b8', va='center')
    ax_head2.text(0.98, 0.50, "TARGET SERVICE LEVEL: 95% (Z = 1.645)", fontsize=9, fontweight='bold', color='#f59e0b', ha='right', va='center')

    ax_scat = fig2.add_axes([0.03, 0.10, 0.60, 0.74])
    ax_scat.set_facecolor('#111827')
    for spine in ax_scat.spines.values():
        spine.set_color('#1e293b')
        spine.set_linewidth(1.2)
        
    latest_df = df_snapshots[df_snapshots["date_key"]==df_snapshots["date_key"].max()].merge(df_skus, on="sku_id")
    x = latest_df["trailing_90d_demand_std_dev"]
    y = latest_df["lead_time_days"]
    sizes = np.clip(latest_df["total_inventory_value"] / 300, 20, 500)
    
    color_map = {"A": "#ef4444", "B": "#f59e0b", "C": "#10b981"}
    c_list = [color_map[abc] for abc in latest_df["abc_classification"]]
    
    sc = ax_scat.scatter(x, y, s=sizes, c=c_list, alpha=0.75, edgecolors='#f8fafc', linewidth=0.8)
    ax_scat.set_title("SKU Risk Matrix: Demand Variance vs. Supplier Lead Time (Bubble Size = Inventory Value)", fontsize=11, fontweight='bold', color='#f8fafc', loc='left', pad=12)
    ax_scat.set_xlabel("Daily Demand Standard Deviation (Units)", fontsize=9, color='#94a3b8')
    ax_scat.set_ylabel("Contracted Lead Time (Days)", fontsize=9, color='#94a3b8')
    ax_scat.tick_params(colors='#94a3b8', labelsize=8.5)
    ax_scat.grid(color='#1e293b', linestyle='--', alpha=0.7)
    
    ax_scat.text(0.03, 0.90, "Class A (High Value / High Risk)\nClass B (Moderate Risk)\nClass C (Low Risk / Commodity)", 
                 fontsize=8.5, color='#f8fafc', transform=ax_scat.transAxes, bbox=dict(boxstyle='round,pad=0.5', fc='#0b0f19', ec='#1e293b'))

    ax_side = fig2.add_axes([0.67, 0.10, 0.30, 0.74])
    ax_side.set_facecolor('#111827')
    ax_side.axis('off')
    r_side = patches.FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.03", fc="#111827", ec="#1e293b", lw=1.2, transform=ax_side.transAxes)
    ax_side.add_patch(r_side)
    
    ax_side.text(0.08, 0.92, "WHAT-IF SHOCK SENSITIVITY", fontsize=11, fontweight='bold', color='#38bdf8', transform=ax_side.transAxes)
    
    shocks = [
        ("Base Case (95% SLA / 1.0x LT)", "$3,420,000", "Baseline Buffer", "#10b981"),
        ("+20% Demand Volatility Spike", "$3,890,000", "+$470,000 Buffer Need", "#f59e0b"),
        ("+50% Lead-Time Transit Delay Shock", "$4,610,000", "+$1,190,000 Buffer Need", "#ef4444"),
        ("98% High-Reliability SLA Target", "$4,270,000", "+$850,000 Buffer Need", "#8b5cf6")
    ]
    
    y_pos = 0.78
    for name, val, delta, col in shocks:
        ax_side.text(0.08, y_pos, name, fontsize=8.5, fontweight='bold', color='#f8fafc', transform=ax_side.transAxes)
        ax_side.text(0.08, y_pos - 0.06, val, fontsize=13, fontweight='bold', color=col, transform=ax_side.transAxes)
        ax_side.text(0.08, y_pos - 0.11, delta, fontsize=7.5, color='#94a3b8', transform=ax_side.transAxes)
        y_pos -= 0.20

    out_p2 = "powerbi/screenshots/page2_dynamic_safety_stock.png"
    plt.savefig(out_p2, facecolor=fig2.get_facecolor(), bbox_inches='tight')
    plt.close()
    print(f"  [OK] Rendered Masterclass Page 2 Mockup: {out_p2}")

    # -------------------------------------------------------------
    # PAGE 3: 9-BOX ABC/XYZ MATRIX & 4-TIER E&O AGING COHORT
    # -------------------------------------------------------------
    fig3 = plt.figure(figsize=(16, 9), dpi=200)
    fig3.patch.set_facecolor('#0b0f19')
    
    ax_head3 = fig3.add_axes([0.03, 0.90, 0.94, 0.08])
    ax_head3.set_facecolor('#111827')
    ax_head3.axis('off')
    rect3 = patches.FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.02", fc="#111827", ec="#1e293b", lw=1.5, transform=ax_head3.transAxes)
    ax_head3.add_patch(rect3)
    ax_head3.text(0.02, 0.55, "DUAL ABC-XYZ DEMAND SEGMENTATION & E&O AGING MATRIX", fontsize=16, fontweight='bold', color='#38bdf8', va='center')
    ax_head3.text(0.02, 0.22, "9-Box Multi-Dimensional Segmentation | 4-Tier Aging Cohorts | Capital Reclamation Strategy", fontsize=9, color='#94a3b8', va='center')
    ax_head3.text(0.98, 0.50, "RECLAMATION VALUE: $1.24M", fontsize=9, fontweight='bold', color='#10b981', ha='right', va='center')

    # Chart 1: 9-Box ABC-XYZ Heatmap Matrix
    ax_mat = fig3.add_axes([0.03, 0.10, 0.46, 0.74])
    ax_mat.set_facecolor('#111827')
    for spine in ax_mat.spines.values():
        spine.set_color('#1e293b')
        spine.set_linewidth(1.2)
        
    matrix_data = np.array([
        [42.5, 21.3, 14.8],  # A (X, Y, Z)
        [18.2, 12.4, 7.9],   # B (X, Y, Z)
        [6.1,  4.2,  3.1]    # C (X, Y, Z)
    ])
    
    im = ax_mat.imshow(matrix_data, cmap="Blues", aspect='auto')
    ax_mat.set_xticks([0, 1, 2])
    ax_mat.set_yticks([0, 1, 2])
    ax_mat.set_xticklabels(['X (Stable)', 'Y (Variable)', 'Z (Sporadic)'], fontsize=9, color='#94a3b8')
    ax_mat.set_yticklabels(['A (High Value 80%)', 'B (Medium 15%)', 'C (Low 5%)'], fontsize=9, color='#94a3b8')
    ax_mat.set_title("9-Box ABC-XYZ Capital Allocation Matrix ($M)", fontsize=11, fontweight='bold', color='#f8fafc', loc='left', pad=12)
    ax_mat.tick_params(colors='#94a3b8')
    
    for i in range(3):
        for j in range(3):
            val = matrix_data[i, j]
            tc = "#0b0f19" if val > 20 else "#f8fafc"
            ax_mat.text(j, i, f"${val:.1f}M\n({['AX','AY','AZ','BX','BY','BZ','CX','CY','CZ'][i*3+j]})", ha="center", va="center", color=tc, fontsize=10, fontweight='bold')

    # Chart 2: 4-Tier E&O Aging Breakdown Stacked Bar
    ax_aging = fig3.add_axes([0.53, 0.10, 0.44, 0.74])
    ax_aging.set_facecolor('#111827')
    for spine in ax_aging.spines.values():
        spine.set_color('#1e293b')
        spine.set_linewidth(1.2)
        
    cohorts = ['Fresh (0-30d)', 'Active (31-60d)', 'At-Risk (61-90d)', 'Dormant (90d+)']
    amounts = [78.4, 32.1, 16.5, 1.24]
    bar_cols = ['#10b981', '#38bdf8', '#f59e0b', '#ef4444']
    
    bars_ag = ax_aging.bar(cohorts, amounts, color=bar_cols, width=0.55, edgecolor='#0b0f19')
    ax_aging.set_title("Inventory Aging Distribution & E&O Risk ($M)", fontsize=11, fontweight='bold', color='#f8fafc', loc='left', pad=12)
    ax_aging.set_ylabel("Capitalized Inventory ($ Millions)", fontsize=9, color='#94a3b8')
    ax_aging.tick_params(colors='#94a3b8', labelsize=8.5)
    ax_aging.grid(axis='y', color='#1e293b', linestyle='--', alpha=0.7)
    
    for b in bars_ag:
        h = b.get_height()
        ax_aging.text(b.get_x() + b.get_width()/2, h + 1.2, f"${h:.2f}M", ha='center', color='#f8fafc', fontsize=8.5, fontweight='bold')

    out_p3 = "powerbi/screenshots/page3_abc_xyz_aging_matrix.png"
    plt.savefig(out_p3, facecolor=fig3.get_facecolor(), bbox_inches='tight')
    plt.close()
    print(f"  [OK] Rendered Masterclass Page 3 Mockup: {out_p3}")
    print("=== All 3 Masterclass Power BI Dashboards Rendered! ===")

if __name__ == "__main__":
    render_executive_dashboard()
