"""
Interactive Streamlit Dashboard for SIOP & Multi-Plant Inventory Optimization Hub.
Live web twin of the Power BI enterprise reporting suite with real-time scenario simulation & SIOP forecasting.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from src.data_generator import generate_siop_dataset
from src.inventory_optimizer import InventoryOptimizer
from src.data_validator import SCMDataValidator
from src.demand_forecaster import SIOPDemandForecaster
from src.export_powerbi_dataset import export_powerbi_tables

st.set_page_config(
    page_title="Eaton SIOP & Inventory Optimization Hub",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Enterprise Aesthetics
st.markdown("""
<style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stMetric { background-color: #1a1f2c; border: 1px solid #2d3748; border-radius: 8px; padding: 12px; }
    .metric-label { font-size: 0.85rem; color: #a0aec0; }
    .metric-val { font-size: 1.4rem; font-weight: 700; color: #38bdf8; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    return generate_siop_dataset(num_skus=150, days=60, seed=42)

df_plants, df_suppliers, df_skus, df_dates, df_snapshots = load_data()
optimizer = InventoryOptimizer()
validator = SCMDataValidator()
forecaster = SIOPDemandForecaster()

# Sidebar Controls
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/11/Eaton_Corporation_logo.svg/320px-Eaton_Corporation_logo.svg.png", width=160)
st.sidebar.title("SIOP Control Center")
st.sidebar.markdown("---")

selected_plants = st.sidebar.multiselect(
    "Select Manufacturing Plants",
    options=df_plants["plant_name"].tolist(),
    default=df_plants["plant_name"].tolist()
)

plant_ids = df_plants[df_plants["plant_name"].isin(selected_plants)]["plant_id"].tolist()
selected_abc = st.sidebar.multiselect("ABC Class (Value)", options=["A", "B", "C"], default=["A", "B", "C"])
selected_xyz = st.sidebar.multiselect("XYZ Class (Variability)", options=["X", "Y", "Z"], default=["X", "Y", "Z"])

# Filter snapshots
valid_skus = df_skus[
    (df_skus["abc_classification"].isin(selected_abc)) & 
    (df_skus["xyz_demand_variability"].isin(selected_xyz))
]["sku_id"].tolist()

filtered_snapshots = df_snapshots[
    (df_snapshots["plant_id"].isin(plant_ids)) &
    (df_snapshots["sku_id"].isin(valid_skus))
]

latest_date_key = filtered_snapshots["date_key"].max()
latest_view = filtered_snapshots[filtered_snapshots["date_key"] == latest_date_key].merge(
    df_skus, on="sku_id"
).merge(df_plants, on="plant_id")

# Header Section
st.title("⚡ Multi-Plant SIOP & Dynamic Inventory Optimization Hub")
st.markdown("**Enterprise SCM Decision Intelligence** · Plant Capacity · Safety Stock Buffer Health · Working Capital & Forecasting")
st.markdown("---")

# Tab Navigation
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Executive KPI Scorecard", 
    "🎯 Dynamic Safety Stock Simulator", 
    "📦 ABC/XYZ & E&O Segmentation", 
    "📈 SIOP Demand Forecasting & Plant Loading",
    "🛡️ Data Governance & Power BI Export"
])

with tab1:
    eo_analysis = optimizer.analyze_excess_and_obsolete(filtered_snapshots)
    total_val = latest_view["total_inventory_value"].sum()
    avg_doh = latest_view["days_of_inventory_on_hand"].median()
    stockout_count = (latest_view["on_hand_qty"] == 0).sum()
    stockout_pct = (stockout_count / len(latest_view) * 100) if len(latest_view) > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Inventory Value", f"${total_val:,.0f}", help="Total capitalized value of on-hand inventory")
    with col2:
        st.metric("Median Days on Hand (DOH)", f"{avg_doh:.1f} Days", help="Target benchmark: 30-45 Days")
    with col3:
        st.metric("Excess & Obsolete (E&O)", f"${eo_analysis['dormant_obsolete_value_usd']:,.0f}", f"{eo_analysis['dormant_percentage']:.1f}% of total", delta_color="inverse")
    with col4:
        st.metric("Stockout Risk Count", f"{stockout_count} SKUs", f"{stockout_pct:.1f}% stockout rate", delta_color="inverse")
        
    st.markdown("###")
    c1, c2 = st.columns([3, 2])
    with c1:
        st.subheader("Inventory Valuation by Manufacturing Plant")
        plant_agg = latest_view.groupby("plant_name")["total_inventory_value"].sum().reset_index()
        fig_plant = px.bar(
            plant_agg, x="plant_name", y="total_inventory_value",
            color="total_inventory_value", color_continuous_scale="Blues",
            labels={"plant_name": "Manufacturing Facility", "total_inventory_value": "Valuation ($)"},
            template="plotly_dark"
        )
        st.plotly_chart(fig_plant, use_container_width=True)
    with c2:
        st.subheader("Inventory Value by Category")
        cat_agg = latest_view.groupby("product_category")["total_inventory_value"].sum().reset_index()
        fig_cat = px.pie(
            cat_agg, names="product_category", values="total_inventory_value",
            hole=0.4, template="plotly_dark", color_discrete_sequence=px.colors.sequential.Teal
        )
        st.plotly_chart(fig_cat, use_container_width=True)

with tab2:
    st.subheader("Dynamic Safety Stock & Service Level What-If Scenario Engine")
    st.markdown("Simulate the impact of supplier lead-time shocks and desired service levels ($Z$-score) on required working capital.")
    
    sim_col1, sim_col2, sim_col3 = st.columns(3)
    with sim_col1:
        target_service = st.slider("Target Service Level (%)", min_value=85.0, max_value=99.9, value=95.0, step=0.5) / 100.0
    with sim_col2:
        lead_time_multiplier = st.slider("Supplier Lead Time Shock Multiplier", min_value=0.5, max_value=2.5, value=1.0, step=0.1)
    with sim_col3:
        demand_volatility_multiplier = st.slider("Demand Volatility Shock Multiplier", min_value=0.5, max_value=2.0, value=1.0, step=0.1)
        
    sim_df = latest_view.copy()
    sim_df["sim_lead_time"] = sim_df["lead_time_days"] * lead_time_multiplier
    sim_df["sim_demand_std"] = sim_df["trailing_90d_demand_std_dev"] * demand_volatility_multiplier
    
    sim_ss = []
    for _, row in sim_df.iterrows():
        ss = optimizer.calculate_safety_stock(
            avg_demand=row["trailing_90d_avg_daily_demand"],
            demand_std=row["sim_demand_std"],
            avg_lead_time=row["sim_lead_time"],
            lead_time_std=3.0,
            service_level=target_service
        )
        sim_ss.append(ss)
    sim_df["simulated_safety_stock_units"] = sim_ss
    sim_df["simulated_safety_stock_usd"] = sim_df["simulated_safety_stock_units"] * sim_df["standard_unit_cost"]
    
    total_baseline_ss_usd = (sim_df["calculated_safety_stock_qty"] * sim_df["standard_unit_cost"]).sum()
    total_sim_ss_usd = sim_df["simulated_safety_stock_usd"].sum()
    delta_capital = total_sim_ss_usd - total_baseline_ss_usd
    
    sc1, sc2 = st.columns(2)
    with sc1:
        st.metric("Required Safety Stock Capital (Simulated)", f"${total_sim_ss_usd:,.0f}", f"${delta_capital:+,.0f} vs Baseline", delta_color="inverse")
    with sc2:
        st.info(f"💡 At **{target_service*100:.1f}% service level** with **{lead_time_multiplier}x lead time shock**, inventory buffer requires **${total_sim_ss_usd:,.0f}** in allocated capital.")
        
    fig_sim = px.scatter(
        sim_df, x="days_of_inventory_on_hand", y="simulated_safety_stock_usd",
        color="abc_classification", size="total_inventory_value",
        hover_data=["sku_name", "plant_name"],
        labels={"days_of_inventory_on_hand": "Days of Inventory on Hand", "simulated_safety_stock_usd": "Safety Stock ($)"},
        template="plotly_dark"
    )
    st.plotly_chart(fig_sim, use_container_width=True)

with tab3:
    st.subheader("ABC-XYZ Demand Volatility & E&O Segmentation")
    st.markdown("Dual matrix segmentation to isolate high-value erratic SKUs requiring executive SIOP intervention.")
    
    abc_xyz_counts = latest_view.groupby(["abc_classification", "xyz_demand_variability"]).agg(
        sku_count=("sku_id", "count"),
        total_value=("total_inventory_value", "sum")
    ).reset_index()
    
    fig_matrix = px.density_heatmap(
        abc_xyz_counts, x="abc_classification", y="xyz_demand_variability", z="total_value",
        labels={"abc_classification": "ABC Classification (Cost Contribution)", "xyz_demand_variability": "XYZ Demand Volatility"},
        color_continuous_scale="Viridis", template="plotly_dark", text_auto=True
    )
    st.plotly_chart(fig_matrix, use_container_width=True)

with tab4:
    st.subheader("📈 SIOP Demand Forecasting & Plant Capacity Loading")
    st.markdown("Time-series demand forecast with Holt-Winters Exponential Smoothing, Forecast Accuracy (MAPE/WAPE), and Plant Loading status.")
    
    sample_sku = st.selectbox("Select SKU for Forecast Analysis", options=latest_view["sku_id"].unique().tolist(), format_func=lambda x: f"{x} - {df_skus.loc[df_skus['sku_id']==x, 'sku_name'].values[0]}")
    sku_history = filtered_snapshots[filtered_snapshots["sku_id"] == sample_sku].sort_values("date_key")
    
    actual_series = sku_history["daily_actual_demand_qty"].reset_index(drop=True)
    forecast_df = forecaster.generate_holt_winters_forecast(actual_series, forecast_horizon=30)
    
    # Accuracy Metrics
    mape = forecaster.calculate_mape(actual_series.values, sku_history["daily_forecasted_demand_qty"].values)
    wape = forecaster.calculate_wape(actual_series.values, sku_history["daily_forecasted_demand_qty"].values)
    bias = forecaster.calculate_forecast_bias(actual_series.values, sku_history["daily_forecasted_demand_qty"].values)
    
    fcol1, fcol2, fcol3 = st.columns(3)
    with fcol1:
        st.metric("Forecast Accuracy (WAPE)", f"{100 - wape:.1f}%", f"{wape:.1f}% Error", delta_color="normal")
    with fcol2:
        st.metric("Mean Absolute % Error (MAPE)", f"{mape:.1f}%")
    with fcol3:
        st.metric("Forecast Bias (Tracking Signal)", f"{bias['bias_percentage']:+.1f}%", bias['interpretation'])
        
    fig_fc = go.Figure()
    fig_fc.add_trace(go.Scatter(y=actual_series, mode="lines+markers", name="Historical Actual Demand", line=dict(color="#38bdf8", width=2)))
    fig_fc.add_trace(go.Scatter(x=list(range(len(actual_series), len(actual_series) + len(forecast_df))), y=forecast_df["forecast_demand_units"], mode="lines+markers", name="30-Day Forward Forecast (Holt-Winters)", line=dict(color="#f59e0b", width=2, dash="dash")))
    fig_fc.update_layout(template="plotly_dark", title="Demand Forecast vs Historical Actuals", xaxis_title="Timeline (Days)", yaxis_title="Units Demanded")
    st.plotly_chart(fig_fc, use_container_width=True)
    
    st.subheader("Manufacturing Plant Capacity Loading Status")
    capacity_df = forecaster.evaluate_plant_capacity_loading(filtered_snapshots, df_plants)
    st.dataframe(capacity_df[["plant_id", "plant_name", "region", "daily_actual_demand_qty", "daily_capacity_units", "current_loading_pct", "capacity_status"]], use_container_width=True)

with tab5:
    st.subheader("Automated SCM Data Governance & QA Health Suite")
    st.markdown("Automated assertion suite executing referential integrity, schema bounds, and financial reconciliation checks prior to BI refresh.")
    
    validator.validate_referential_integrity(df_snapshots, df_plants, df_skus, df_suppliers)
    validator.validate_inventory_logical_rules(df_snapshots)
    report_df = validator.generate_data_health_report()
    st.dataframe(report_df, use_container_width=True)
    
    st.markdown("---")
    st.subheader("Power BI Dataset Direct Export")
    st.markdown("Export certified Star Schema tables to CSV / Parquet formats for drag-and-drop ingestion into Power BI Desktop.")
    
    if st.button("🚀 Export Certified Power BI Star Schema Tables"):
        export_powerbi_tables()
        st.success("✅ Power BI Star Schema tables successfully exported to `powerbi_exports/` directory!")
