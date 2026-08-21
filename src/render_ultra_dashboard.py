"""
Ultra-Dense Enterprise Power BI SCM War Room Dashboard Suite (4K / Retina HD Mockup Visualizer).
Renders state-of-the-art, glassmorphic dark-theme executive command centers packed with
dense KPI sparkline cards, slicer bars, capital waterfall walks, plant capacity loading,
stochastic forecast confidence cones, 9-box matrices, and in-cell telemetry tables.
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

def render_ultra_suite():
    os.makedirs("powerbi/screenshots", exist_ok=True)
    df_plants, df_suppliers, df_skus, df_dates, df_snapshots = generate_siop_dataset(num_skus=150, days=60, seed=42)
    
    plt.style.use('dark_background')
    
    # =========================================================================
    # PAGE 1: 🌐 GLOBAL SCM WAR ROOM & WORKING CAPITAL WATERFALL
    # =========================================================================
    fig1 = plt.figure(figsize=(18, 10.5), dpi=220)
    fig1.patch.set_facecolor('#070a12')
    
    # 1. Top Global Navigation & Breadcrumb Header
    ax_top = fig1.add_axes([0.02, 0.925, 0.96, 0.065])
    ax_top.set_facecolor('#0f172a')
    ax_top.axis('off')
    r_top = patches.FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.015", fc="#0f172a", ec="#1e293b", lw=1.5, transform=ax_top.transAxes)
    ax_top.add_patch(r_top)
    ax_top.text(0.015, 0.65, "SCM WAR ROOM | GLOBAL INVENTORY & WORKING CAPITAL PULSE", fontsize=15, fontweight='bold', color='#38bdf8', va='center')
    ax_top.text(0.015, 0.25, "DESIGN MOCKUP (matplotlib) — not a Power BI screen capture · Simulated data · Target layout for the Power BI build", fontsize=8.5, color='#94a3b8', va='center')
    
    # System Status Badge & Refresh
    ax_top.text(0.985, 0.65, "SYSTEM HEALTH: 100% NOMINAL · ZERO ETL ERRORS", fontsize=8, fontweight='bold', color='#10b981', ha='right', va='center')
    ax_top.text(0.985, 0.25, "DATA REFRESH: STATIC MOCKUP (NOT LIVE) | MODEL: STAR SCHEMA V3.2", fontsize=7.5, color='#64748b', ha='right', va='center')

    # 2. Interactive Global Slicer Pill Bar
    ax_slicer = fig1.add_axes([0.02, 0.865, 0.96, 0.048])
    ax_slicer.set_facecolor('#0b1120')
    ax_slicer.axis('off')
    r_slicer = patches.FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.01", fc="#0b1120", ec="#1e293b", lw=1, transform=ax_slicer.transAxes)
    ax_slicer.add_patch(r_slicer)
    
    slicers = [
        ("PLANT:", "All Plants (5)", 0.015),
        ("CATEGORY:", "Electrical & Power", 0.21),
        ("ABC CLASS:", "[A] [B] [C]", 0.43),
        ("SERVICE LEVEL:", "95% SLA Target", 0.61),
        ("TIMEFRAME:", "FY26 YTD (Trailing 90D)", 0.80)
    ]
    for label, val, xpos in slicers:
        ax_slicer.text(xpos, 0.5, label, fontsize=8, fontweight='bold', color='#64748b', va='center')
        ax_slicer.text(xpos + 0.065, 0.5, f" [{val}] ", fontsize=8, fontweight='bold', color='#38bdf8', va='center',
                       bbox=dict(boxstyle='round,pad=0.25', fc='#1e293b', ec='#334155', lw=0.8))

    # 3. Dense 6-KPI Hero Card Row with Mini Sparklines & Variance Badges
    kpis = [
        ("TOTAL CAPITAL VALUATION", "$128.2M", "-14.2% YoY", [120, 122, 125, 128, 124, 128], "#38bdf8", "#10b981", 0.02),
        ("DAYS ON HAND (DOH)", "36.4 Days", "-4.1d vs Target (40d)", [42, 41, 39, 38, 37, 36.4], "#f8fafc", "#38bdf8", 0.183),
        ("DYNAMIC SAFETY STOCK", "$24.6M", "Z=1.645 (95% SLA)", [22, 23, 23.5, 24, 24.2, 24.6], "#818cf8", "#818cf8", 0.346),
        ("DORMANT E&O RESERVES", "$1.24M", "9.4% Capital Risk", [1.8, 1.6, 1.5, 1.4, 1.3, 1.24], "#f59e0b", "#ef4444", 0.509),
        ("INVENTORY VELOCITY", "8.4x / Yr", "+1.2x vs Prev FY", [6.8, 7.1, 7.5, 7.9, 8.2, 8.4], "#10b981", "#10b981", 0.672),
        ("SUPPLIER OTIF COMPLIANCE", "94.2%", "-0.8% below 95% SLA", [96, 95.5, 95, 94.8, 94.5, 94.2], "#38bdf8", "#f59e0b", 0.835)
    ]
    
    for title, val, sub, spark, val_col, sub_col, xpos in kpis:
        ax_kpi = fig1.add_axes([xpos, 0.725, 0.145, 0.125])
        ax_kpi.set_facecolor('#0f172a')
        ax_kpi.axis('off')
        r_k = patches.FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.03", fc="#0f172a", ec="#1e293b", lw=1.2, transform=ax_kpi.transAxes)
        ax_kpi.add_patch(r_k)
        
        ax_kpi.text(0.08, 0.82, title, fontsize=7.2, fontweight='bold', color='#94a3b8', transform=ax_kpi.transAxes)
        ax_kpi.text(0.08, 0.50, val, fontsize=15, fontweight='bold', color=val_col, transform=ax_kpi.transAxes)
        ax_kpi.text(0.08, 0.18, sub, fontsize=6.8, fontweight='bold', color=sub_col, transform=ax_kpi.transAxes)
        
        # Mini sparkline
        ax_sp = fig1.add_axes([xpos + 0.085, 0.735, 0.05, 0.04])
        ax_sp.set_facecolor('none')
        ax_sp.axis('off')
        ax_sp.plot(spark, color=val_col, lw=1.8)
        ax_sp.scatter([len(spark)-1], [spark[-1]], color=val_col, s=12)

    # 4. Chart Left: Working Capital Value Walk (Waterfall Bridge)
    ax_wf = fig1.add_axes([0.02, 0.36, 0.46, 0.34])
    ax_wf.set_facecolor('#0f172a')
    for s in ax_wf.spines.values():
        s.set_color('#1e293b')
        s.set_linewidth(1.2)
        
    wf_labels = ['Begin Capital', '+PO Receipts', '-Demand Cons', '+LT Buffer Adj', '-E&O Scrap', 'Ending Capital']
    wf_vals = [135.0, 34.2, -41.6, 4.1, -1.24, 130.46]
    bottoms = [0, 135.0, 169.2 - 41.6, 127.6, 131.7 - 1.24, 0]
    heights = [135.0, 34.2, 41.6, 4.1, 1.24, 130.46]
    wf_cols = ['#38bdf8', '#10b981', '#ef4444', '#818cf8', '#f59e0b', '#38bdf8']
    
    bars_wf = ax_wf.bar(wf_labels, heights, bottom=bottoms, color=wf_cols, width=0.55, edgecolor='#070a12', lw=1.2)
    ax_wf.set_title("Working Capital Value Walk | SCM Financial Bridge ($M)", fontsize=10.5, fontweight='bold', color='#f8fafc', loc='left', pad=10)
    ax_wf.set_ylabel("Capital ($M)", fontsize=8.5, color='#94a3b8')
    ax_wf.tick_params(colors='#94a3b8', labelsize=7.5)
    ax_wf.grid(axis='y', color='#1e293b', linestyle='--', alpha=0.7)
    
    for i, b in enumerate(bars_wf):
        h = wf_vals[i]
        top = bottoms[i] + heights[i]
        ax_wf.text(b.get_x() + b.get_width()/2, top + 1.5, f"${abs(h):.1f}M", ha='center', color='#f8fafc', fontsize=7.2, fontweight='bold')

    # 5. Chart Right: Multi-Plant Capacity Loading vs 85% Bottleneck Limit
    ax_cap = fig1.add_axes([0.51, 0.36, 0.47, 0.34])
    ax_cap.set_facecolor('#0f172a')
    for s in ax_cap.spines.values():
        s.set_color('#1e293b')
        s.set_linewidth(1.2)
        
    plants = ['Shanghai Plant', 'Houston Facility', 'Pune Plant', 'Stuttgart Hub', 'Juarez Plant']
    utilization = [88.5, 76.2, 91.4, 68.0, 82.3]
    cap_colors = ['#ef4444' if u > 85 else '#38bdf8' for u in utilization]
    
    bars_cap = ax_cap.barh(plants, utilization, color=cap_colors, height=0.5, edgecolor='#070a12')
    ax_cap.axvline(85, color='#f59e0b', linestyle='--', lw=1.5, label='85% Stress Bottleneck Threshold')
    ax_cap.set_title("Manufacturing Plant Capacity Loading (%) | SIOP Bottleneck Radar", fontsize=10.5, fontweight='bold', color='#f8fafc', loc='left', pad=10)
    ax_cap.set_xlabel("Scheduled Production Loading (%)", fontsize=8.5, color='#94a3b8')
    ax_cap.tick_params(colors='#94a3b8', labelsize=8)
    ax_cap.set_xlim(0, 105)
    ax_cap.legend(loc='lower right', fontsize=7.5, facecolor='#0f172a', edgecolor='#1e293b')
    ax_cap.grid(axis='x', color='#1e293b', linestyle='--', alpha=0.7)
    
    for b in bars_cap:
        w = b.get_width()
        ax_cap.text(w + 1.5, b.get_y() + b.get_height()/2, f"{w:.1f}%", va='center', color='#f8fafc', fontsize=7.8, fontweight='bold')

    # 6. Bottom Table: Top Critical SKUs Deep-Dive Telemetry Action Table
    ax_tbl = fig1.add_axes([0.02, 0.04, 0.96, 0.28])
    ax_tbl.set_facecolor('#0f172a')
    ax_tbl.axis('off')
    r_tbl = patches.FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.015", fc="#0f172a", ec="#1e293b", lw=1.2, transform=ax_tbl.transAxes)
    ax_tbl.add_patch(r_tbl)
    
    ax_tbl.text(0.015, 0.88, "TOP CRITICAL SKUs DEEP-DIVE TELEMETRY | WORKING CAPITAL & ACTION STATUS", fontsize=10, fontweight='bold', color='#38bdf8', transform=ax_tbl.transAxes)
    
    # Table Header Row
    headers = [("SKU CODE", 0.02), ("PRODUCT NAME", 0.12), ("PLANT", 0.32), ("ON-HAND QTY", 0.44), ("DOH", 0.54), ("SAFETY STOCK", 0.63), ("TOTAL VALUE", 0.74), ("RISK INDEX", 0.84), ("ACTION", 0.92)]
    for h_name, h_x in headers:
        ax_tbl.text(h_x, 0.75, h_name, fontsize=7.5, fontweight='bold', color='#64748b', transform=ax_tbl.transAxes)
        
    ax_tbl.plot([0.015, 0.985], [0.70, 0.70], color='#1e293b', lw=1, transform=ax_tbl.transAxes)
    
    sample_rows = [
        ("SKU-TRF-001", "High-Voltage Power Transformer 250kVA", "Pune Plant", "482 Units", "12.4d (Low)", "840 Units", "$1,450,000", "0.88 (Critical)", "EXPEDITE PO", "#ef4444"),
        ("SKU-SWG-042", "Medium Voltage Vacuum Switchgear 33kV", "Shanghai Plant", "1,240 Units", "58.2d (High)", "620 Units", "$2,890,000", "0.24 (Excess)", "REBALANCE", "#f59e0b"),
        ("SKU-IGBT-09", "Dual IGBT Silicon Carbide Power Module", "Houston Facility", "3,800 Units", "34.1d (Nominal)", "2,900 Units", "$940,000", "0.12 (Healthy)", "MAINTAIN", "#10b981"),
        ("SKU-COP-018", "Oxygen-Free Copper Busbar 50mm", "Stuttgart Hub", "120 Units", "8.1d (Stockout)", "450 Units", "$420,000", "0.94 (Urgent)", "DUAL-SOURCE", "#ef4444"),
        ("SKU-STL-005", "Grain-Oriented Electrical Steel Core", "Juarez Plant", "850 Units", "92.0d (Dormant)", "180 Units", "$1,120,000", "0.78 (Dormant)", "SCRAP / RECLAIM", "#f59e0b")
    ]
    
    y_tbl = 0.56
    for code, name, plant, oh, doh, ss, val, risk, act, act_col in sample_rows:
        ax_tbl.text(0.02, y_tbl, code, fontsize=7.5, fontweight='bold', color='#f8fafc', transform=ax_tbl.transAxes)
        ax_tbl.text(0.12, y_tbl, name[:32], fontsize=7.2, color='#cbd5e1', transform=ax_tbl.transAxes)
        ax_tbl.text(0.32, y_tbl, plant, fontsize=7.2, color='#94a3b8', transform=ax_tbl.transAxes)
        ax_tbl.text(0.44, y_tbl, oh, fontsize=7.2, color='#f8fafc', transform=ax_tbl.transAxes)
        ax_tbl.text(0.54, y_tbl, doh, fontsize=7.2, color='#38bdf8', transform=ax_tbl.transAxes)
        ax_tbl.text(0.63, y_tbl, ss, fontsize=7.2, color='#818cf8', transform=ax_tbl.transAxes)
        ax_tbl.text(0.74, y_tbl, val, fontsize=7.2, fontweight='bold', color='#f8fafc', transform=ax_tbl.transAxes)
        ax_tbl.text(0.84, y_tbl, risk, fontsize=7.2, color='#94a3b8', transform=ax_tbl.transAxes)
        ax_tbl.text(0.92, y_tbl, f" {act} ", fontsize=6.8, fontweight='bold', color=act_col, transform=ax_tbl.transAxes,
                    bbox=dict(boxstyle='round,pad=0.2', fc='#1e293b', ec=act_col, lw=0.8))
        
        ax_tbl.plot([0.015, 0.985], [y_tbl - 0.035, y_tbl - 0.035], color='#1e293b', lw=0.5, alpha=0.5, transform=ax_tbl.transAxes)
        y_tbl -= 0.11

    p1_out = "powerbi/mockups/page1_executive_command_center.png"
    plt.savefig(p1_out, facecolor=fig1.get_facecolor(), bbox_inches='tight')
    plt.close()
    print(f"  [OK] Rendered Ultra SCM War Room (Page 1): {p1_out}")

    # =========================================================================
    # PAGE 2: 🔬 STOCHASTIC SIOP DIGITAL TWIN & HOLT-WINTERS CONE
    # =========================================================================
    fig2 = plt.figure(figsize=(18, 10.5), dpi=220)
    fig2.patch.set_facecolor('#070a12')
    
    ax_top2 = fig2.add_axes([0.02, 0.925, 0.96, 0.065])
    ax_top2.set_facecolor('#0f172a')
    ax_top2.axis('off')
    r_top2 = patches.FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.015", fc="#0f172a", ec="#1e293b", lw=1.5, transform=ax_top2.transAxes)
    ax_top2.add_patch(r_top2)
    ax_top2.text(0.015, 0.65, "SIOP DEMAND FORECASTING & MONTE CARLO DIGITAL TWIN", fontsize=15, fontweight='bold', color='#38bdf8', va='center')
    ax_top2.text(0.015, 0.25, "DESIGN MOCKUP (matplotlib) — not a Power BI screen capture · Holt-Winters fan cone · Simulated data", fontsize=8.5, color='#94a3b8', va='center')
    ax_top2.text(0.985, 0.50, "WAPE: 6.8% | MAPE: 8.2% | FORECAST BIAS: +0.4 (OPTIMAL)", fontsize=8.5, fontweight='bold', color='#10b981', ha='right', va='center')

    # Chart 1 Left: Holt-Winters Demand Forecasting Line with 95% Confidence Cone
    ax_fc = fig2.add_axes([0.02, 0.48, 0.62, 0.41])
    ax_fc.set_facecolor('#0f172a')
    for s in ax_fc.spines.values():
        s.set_color('#1e293b')
        s.set_linewidth(1.2)
        
    days_hist = np.arange(1, 46)
    days_proj = np.arange(45, 75)
    
    np.random.seed(101)
    hist_demand = 800 + 4.5 * days_hist + np.sin(days_hist/3) * 60 + np.random.normal(0, 25, len(days_hist))
    proj_demand = 800 + 4.5 * days_proj + np.sin(days_proj/3) * 60
    cone_upper = proj_demand + 1.96 * 35 * np.sqrt((days_proj - 44)/5)
    cone_lower = proj_demand - 1.96 * 35 * np.sqrt((days_proj - 44)/5)
    
    ax_fc.plot(days_hist, hist_demand, color='#38bdf8', lw=2.2, label='Actual Daily Demand (ERP Consumption)')
    ax_fc.plot(days_proj, proj_demand, color='#f59e0b', lw=2.2, linestyle='--', label="Holt's Linear Forecast Horizon")
    ax_fc.fill_between(days_proj, cone_lower, cone_upper, color='#f59e0b', alpha=0.2, label='95% Confidence Interval Cone')
    ax_fc.axvline(45, color='#ef4444', linestyle=':', lw=1.5, label='Forecast Horizon Cutoff (Today)')
    
    ax_fc.set_title("Holt-Winters Demand Smoothing & Predictive Forecast Horizon (Units)", fontsize=10.5, fontweight='bold', color='#f8fafc', loc='left', pad=10)
    ax_fc.set_xlabel("Timeline (Days)", fontsize=8.5, color='#94a3b8')
    ax_fc.set_ylabel("Demand Throughput (Units/Day)", fontsize=8.5, color='#94a3b8')
    ax_fc.tick_params(colors='#94a3b8', labelsize=8)
    ax_fc.legend(loc='upper left', fontsize=7.5, facecolor='#0f172a', edgecolor='#1e293b')
    ax_fc.grid(color='#1e293b', linestyle='--', alpha=0.7)

    # Chart 2 Right: Tracking Signal Bias Sentry
    ax_bias = fig2.add_axes([0.67, 0.48, 0.31, 0.41])
    ax_bias.set_facecolor('#0f172a')
    for s in ax_bias.spines.values():
        s.set_color('#1e293b')
        s.set_linewidth(1.2)
        
    ts_days = np.arange(1, 46)
    ts_vals = np.cumsum(np.random.normal(0.05, 0.4, len(ts_days)))
    ax_bias.plot(ts_days, ts_vals, color='#10b981', lw=2)
    ax_bias.axhline(4.0, color='#ef4444', linestyle='--', lw=1.2, label='+4.0 Severe Over-Forecast')
    ax_bias.axhline(-4.0, color='#ef4444', linestyle='--', lw=1.2, label='-4.0 Severe Under-Forecast')
    ax_bias.axhline(0.0, color='#64748b', linestyle=':', lw=1)
    ax_bias.fill_between(ts_days, -4.0, 4.0, color='#10b981', alpha=0.08)
    
    ax_bias.set_title("Forecast Tracking Signal (TS) Bias Sentry", fontsize=10.5, fontweight='bold', color='#f8fafc', loc='left', pad=10)
    ax_bias.set_xlabel("Evaluation Window (Days)", fontsize=8.5, color='#94a3b8')
    ax_bias.set_ylabel("Tracking Signal Metric", fontsize=8.5, color='#94a3b8')
    ax_bias.tick_params(colors='#94a3b8', labelsize=8)
    ax_bias.legend(loc='upper right', fontsize=7.2, facecolor='#0f172a', edgecolor='#1e293b')
    ax_bias.grid(color='#1e293b', linestyle='--', alpha=0.7)

    # Chart 3 Bottom Left: SKU Risk Scatter Matrix with Risk Iso-Lines
    ax_sc2 = fig2.add_axes([0.02, 0.05, 0.47, 0.38])
    ax_sc2.set_facecolor('#0f172a')
    for s in ax_sc2.spines.values():
        s.set_color('#1e293b')
        s.set_linewidth(1.2)
        
    latest_df = df_snapshots[df_snapshots["date_key"]==df_snapshots["date_key"].max()].merge(df_skus, on="sku_id")
    x = latest_df["trailing_90d_demand_std_dev"]
    y = latest_df["lead_time_days"]
    sizes = np.clip(latest_df["total_inventory_value"] / 250, 25, 450)
    c_list = ['#ef4444' if abc=='A' else ('#f59e0b' if abc=='B' else '#10b981') for abc in latest_df["abc_classification"]]
    
    ax_sc2.scatter(x, y, s=sizes, c=c_list, alpha=0.75, edgecolors='#f8fafc', lw=0.6)
    ax_sc2.axvspan(45, 90, color='#ef4444', alpha=0.08, label='High Demand Volatility Zone')
    ax_sc2.axhspan(32, 50, color='#f59e0b', alpha=0.08, label='Extended Lead-Time Risk Zone')
    
    ax_sc2.set_title("Bivariate Stochastic Risk Matrix | Demand Variance vs Lead Time", fontsize=10.5, fontweight='bold', color='#f8fafc', loc='left', pad=10)
    ax_sc2.set_xlabel("Daily Demand Standard Deviation (Units)", fontsize=8.5, color='#94a3b8')
    ax_sc2.set_ylabel("Contracted Supplier Lead Time (Days)", fontsize=8.5, color='#94a3b8')
    ax_sc2.tick_params(colors='#94a3b8', labelsize=8)
    ax_sc2.grid(color='#1e293b', linestyle='--', alpha=0.7)

    # Chart 4 Bottom Right: Monte Carlo 10k-Run Working Capital VaR Density Distribution
    ax_mc = fig2.add_axes([0.52, 0.05, 0.46, 0.38])
    ax_mc.set_facecolor('#0f172a')
    for s in ax_mc.spines.values():
        s.set_color('#1e293b')
        s.set_linewidth(1.2)
        
    mc_sims = np.random.normal(128.2, 6.4, 10000)
    var_95 = np.percentile(mc_sims, 95)
    
    n, bins, patches_mc = ax_mc.hist(mc_sims, bins=50, color='#38bdf8', edgecolor='#070a12', alpha=0.8)
    for i, p in enumerate(patches_mc):
        if bins[i] >= var_95:
            p.set_facecolor('#ef4444')
            
    ax_mc.axvline(var_95, color='#ef4444', linestyle='--', lw=1.8, label=f'95% Value-at-Risk (${var_95:.1f}M)')
    ax_mc.axvline(128.2, color='#10b981', linestyle=':', lw=1.5, label='Expected Baseline ($128.2M)')
    
    ax_mc.set_title("Monte Carlo 10,000-Run Working Capital Simulation | 95% VaR Tail Risk", fontsize=10.5, fontweight='bold', color='#f8fafc', loc='left', pad=10)
    ax_mc.set_xlabel("Simulated Portfolio Capitalization ($ Millions)", fontsize=8.5, color='#94a3b8')
    ax_mc.set_ylabel("Simulation Frequency", fontsize=8.5, color='#94a3b8')
    ax_mc.tick_params(colors='#94a3b8', labelsize=8)
    ax_mc.legend(loc='upper right', fontsize=7.5, facecolor='#0f172a', edgecolor='#1e293b')
    ax_mc.grid(color='#1e293b', linestyle='--', alpha=0.7)

    p2_out = "powerbi/mockups/page2_dynamic_safety_stock.png"
    plt.savefig(p2_out, facecolor=fig2.get_facecolor(), bbox_inches='tight')
    plt.close()
    print(f"  [OK] Rendered Ultra Stochastic Digital Twin (Page 2): {p2_out}")

    # =========================================================================
    # PAGE 3: 📦 9-BOX ABC/XYZ MATRIX & RECOVERY ACTION CENTER
    # =========================================================================
    fig3 = plt.figure(figsize=(18, 10.5), dpi=220)
    fig3.patch.set_facecolor('#070a12')
    
    ax_top3 = fig3.add_axes([0.02, 0.925, 0.96, 0.065])
    ax_top3.set_facecolor('#0f172a')
    ax_top3.axis('off')
    r_top3 = patches.FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.015", fc="#0f172a", ec="#1e293b", lw=1.5, transform=ax_top3.transAxes)
    ax_top3.add_patch(r_top3)
    ax_top3.text(0.015, 0.65, "DUAL ABC-XYZ DEMAND VOLATILITY & E&O CAPITAL RECOVERY", fontsize=15, fontweight='bold', color='#38bdf8', va='center')
    ax_top3.text(0.015, 0.25, "DESIGN MOCKUP (matplotlib) — not a Power BI screen capture · 9-box ABC-XYZ segmentation · Simulated data", fontsize=8.5, color='#94a3b8', va='center')
    ax_top3.text(0.985, 0.50, "RECLAMATION CAPITAL POTENTIAL: $1.24M | WORKING CAPITAL -14%", fontsize=8.5, fontweight='bold', color='#10b981', ha='right', va='center')

    # Chart 1 Left: 9-Box ABC-XYZ Grid
    ax_mat3 = fig3.add_axes([0.02, 0.38, 0.47, 0.50])
    ax_mat3.set_facecolor('#0f172a')
    for s in ax_mat3.spines.values():
        s.set_color('#1e293b')
        s.set_linewidth(1.2)
        
    matrix_data = np.array([
        [42.5, 21.3, 14.8],
        [18.2, 12.4, 7.9],
        [6.1,  4.2,  3.1]
    ])
    
    im = ax_mat3.imshow(matrix_data, cmap="Blues", aspect='auto')
    ax_mat3.set_xticks([0, 1, 2])
    ax_mat3.set_yticks([0, 1, 2])
    ax_mat3.set_xticklabels(['X (Stable / CoV < 0.2)', 'Y (Variable / CoV 0.2-0.5)', 'Z (Sporadic / CoV > 0.5)'], fontsize=8.5, color='#94a3b8')
    ax_mat3.set_yticklabels(['A (High Value 80%)', 'B (Medium Value 15%)', 'C (Low Value 5%)'], fontsize=8.5, color='#94a3b8')
    ax_mat3.set_title("9-Box ABC-XYZ Capital Allocation Matrix ($M)", fontsize=10.5, fontweight='bold', color='#f8fafc', loc='left', pad=10)
    ax_mat3.tick_params(colors='#94a3b8')
    
    quad_actions = [
        ("AX: Automated JIT Replenishment", "AY: Dynamic Safety Stock", "AZ: Strict Order-To-Order / VMI"),
        ("BX: EOQ Periodic Review", "BY: Buffer Stock Rebalance", "BZ: Lead Time Squeeze"),
        ("CX: Bulk Two-Bin Kanban", "CY: Standard Min-Max", "CZ: Write-Off / Rationalize")
    ]
    
    for i in range(3):
        for j in range(3):
            val = matrix_data[i, j]
            tc = "#070a12" if val > 20 else "#f8fafc"
            act_text = quad_actions[i][j]
            ax_mat3.text(j, i, f"${val:.1f}M\n\n{act_text}", ha="center", va="center", color=tc, fontsize=8.2, fontweight='bold')

    # Chart 2 Right: 4-Tier Aging Cohorts Breakdown
    ax_ag3 = fig3.add_axes([0.52, 0.38, 0.46, 0.50])
    ax_ag3.set_facecolor('#0f172a')
    for s in ax_ag3.spines.values():
        s.set_color('#1e293b')
        s.set_linewidth(1.2)
        
    cohorts = ['Fresh Active\n(0-30 Days)', 'Rotating Stock\n(31-60 Days)', 'At-Risk Aging\n(61-90 Days)', 'Dormant E&O\n(90+ Days)']
    amounts = [78.4, 32.1, 16.5, 1.24]
    bar_cols = ['#10b981', '#38bdf8', '#f59e0b', '#ef4444']
    
    bars_ag3 = ax_ag3.bar(cohorts, amounts, color=bar_cols, width=0.52, edgecolor='#070a12', lw=1.2)
    ax_ag3.set_title("Capitalized Inventory Aging Distribution & Dormancy ($M)", fontsize=10.5, fontweight='bold', color='#f8fafc', loc='left', pad=10)
    ax_ag3.set_ylabel("Capitalized On-Hand ($M)", fontsize=8.5, color='#94a3b8')
    ax_ag3.tick_params(colors='#94a3b8', labelsize=8)
    ax_ag3.grid(axis='y', color='#1e293b', linestyle='--', alpha=0.7)
    
    for b in bars_ag3:
        h = b.get_height()
        ax_ag3.text(b.get_x() + b.get_width()/2, h + 1.5, f"${h:.2f}M", ha='center', color='#f8fafc', fontsize=8.2, fontweight='bold')

    # Bottom Panel: $1.24M Capital Reclamation Playbook
    ax_bot3 = fig3.add_axes([0.02, 0.04, 0.96, 0.30])
    ax_bot3.set_facecolor('#0f172a')
    ax_bot3.axis('off')
    r_bot3 = patches.FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.015", fc="#0f172a", ec="#1e293b", lw=1.2, transform=ax_bot3.transAxes)
    ax_bot3.add_patch(r_bot3)
    
    ax_bot3.text(0.015, 0.88, "ACTIONABLE CAPITAL RECLAMATION PROTOCOL | $1.24M WORKING CAPITAL RELEASE", fontsize=10, fontweight='bold', color='#38bdf8', transform=ax_bot3.transAxes)
    
    strategies = [
        ("STRATEGY 1: INTER-PLANT SURPLUS TRANSFER", "$620,000 Reclaimed", "Reallocate 4 dormant raw copper & steel lots from Shanghai Hub to high-demand Pune lines, avoiding new external procurement."),
        ("STRATEGY 2: SUPPLIER BUY-BACK & RETURN", "$380,000 Reclaimed", "Exercise contractual vendor return clauses on excess Tier-1 semiconductor reels with 10% standard restocking credit."),
        ("STRATEGY 3: SCRAP SALVAGE & TAX WRITE-OFF", "$240,000 Reclaimed", "Decommission obsolete legacy switchgear components past 180-day dormancy to harvest corporate R&D tax salvage credits.")
    ]
    
    y_strat = 0.65
    for s_title, s_amt, s_desc in strategies:
        ax_bot3.text(0.02, y_strat, s_title, fontsize=8.5, fontweight='bold', color='#f8fafc', transform=ax_bot3.transAxes)
        ax_bot3.text(0.38, y_strat, s_amt, fontsize=8.5, fontweight='bold', color='#10b981', transform=ax_bot3.transAxes)
        ax_bot3.text(0.02, y_strat - 0.10, s_desc, fontsize=7.8, color='#94a3b8', transform=ax_bot3.transAxes)
        ax_bot3.plot([0.015, 0.985], [y_strat - 0.14, y_strat - 0.14], color='#1e293b', lw=0.6, transform=ax_bot3.transAxes)
        y_strat -= 0.22

    p3_out = "powerbi/mockups/page3_abc_xyz_aging_matrix.png"
    plt.savefig(p3_out, facecolor=fig3.get_facecolor(), bbox_inches='tight')
    plt.close()
    print(f"  [OK] Rendered Ultra ABC-XYZ Matrix & Recovery (Page 3): {p3_out}")
    print("=== All 3 Ultra-Dense 4K Power BI War Room Dashboards Complete! ===")

if __name__ == "__main__":
    render_ultra_suite()
