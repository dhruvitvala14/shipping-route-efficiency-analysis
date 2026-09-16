"""
Nassau Candy Distributor — Factory-to-Customer Shipping Route Efficiency Dashboard
Run with: streamlit run app.py
"""

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ----------------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Nassau Candy | Shipping Route Efficiency",
    page_icon="🍬",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = "Nassau_Candy_Distributor.csv"

# ----------------------------------------------------------------------------
# STATIC REFERENCE DATA (from project documentation)
# ----------------------------------------------------------------------------
FACTORY_COORDS = {
    "Lot's O' Nuts":    {"lat": 32.881893, "lon": -111.768036},
    "Wicked Choccy's":  {"lat": 32.076176, "lon": -81.088371},
    "Sugar Shack":      {"lat": 48.119140, "lon": -96.181150},
    "Secret Factory":   {"lat": 41.446333, "lon": -90.565487},
    "The Other Factory": {"lat": 35.117500, "lon": -89.971107},
}

PRODUCT_TO_FACTORY = {
    "Wonka Bar - Nutty Crunch Surprise": "Lot's O' Nuts",
    "Wonka Bar - Fudge Mallows": "Lot's O' Nuts",
    "Wonka Bar -Scrumdiddlyumptious": "Lot's O' Nuts",
    "Wonka Bar - Milk Chocolate": "Wicked Choccy's",
    "Wonka Bar - Triple Dazzle Caramel": "Wicked Choccy's",
    "Laffy Taffy": "Sugar Shack",
    "SweeTARTS": "Sugar Shack",
    "Nerds": "Sugar Shack",
    "Fun Dip": "Sugar Shack",
    "Fizzy Lifting Drinks": "Sugar Shack",
    "Everlasting Gobstopper": "Secret Factory",
    "Lickable Wallpaper": "Secret Factory",
    "Wonka Gum": "Secret Factory",
    "Hair Toffee": "The Other Factory",
    "Kazookles": "The Other Factory",
}

# US Census-style state -> region isn't provided; the dataset's own "Region"
# field (Interior / Atlantic / Gulf / Pacific) is used everywhere instead.

STATE_ABBR = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
    "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "District of Columbia": "DC",
    "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL",
    "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA",
    "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN",
    "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR",
    "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD",
    "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA",
    "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY",
}

# ----------------------------------------------------------------------------
# DATA LOADING & CLEANING  (Analytical Methodology Step 1 & 2)
# ----------------------------------------------------------------------------
@st.cache_data(show_spinner="Loading and cleaning shipment data...")
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    # --- Data Cleaning & Validation ---
    df["Order Date"] = pd.to_datetime(df["Order Date"], format="%d-%m-%Y", errors="coerce")
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], format="%d-%m-%Y", errors="coerce")

    before = len(df)
    df = df.dropna(subset=["Order Date", "Ship Date"])

    df["State/Province"] = df["State/Province"].astype(str).str.strip()
    df["City"] = df["City"].astype(str).str.strip()
    df["Region"] = df["Region"].astype(str).str.strip()
    df["Ship Mode"] = df["Ship Mode"].astype(str).str.strip()
    df["Division"] = df["Division"].astype(str).str.strip()

    # --- Feature Engineering ---
    df["Lead Time (days)"] = (df["Ship Date"] - df["Order Date"]).dt.days

    # Remove invalid / negative lead times
    invalid_mask = df["Lead Time (days)"] < 0
    n_invalid = int(invalid_mask.sum())
    df = df[~invalid_mask]

    n_missing = before - len(df) - n_invalid

    # Map product -> factory
    df["Factory"] = df["Product Name"].map(PRODUCT_TO_FACTORY)
    df["Factory Lat"] = df["Factory"].map(lambda f: FACTORY_COORDS.get(f, {}).get("lat"))
    df["Factory Lon"] = df["Factory"].map(lambda f: FACTORY_COORDS.get(f, {}).get("lon"))

    # Route definitions
    df["Route (Factory to State)"] = df["Factory"].fillna("Unknown") + " → " + df["State/Province"]
    df["Route (Factory to Region)"] = df["Factory"].fillna("Unknown") + " → " + df["Region"]

    df["State Abbr"] = df["State/Province"].map(STATE_ABBR)

    df["Order Month"] = df["Order Date"].dt.to_period("M").dt.to_timestamp()

    meta = {"n_invalid_removed": n_invalid, "n_missing_removed": max(n_missing, 0), "rows_used": len(df)}
    return df, meta


try:
    df_raw, clean_meta = load_data(DATA_PATH)
except FileNotFoundError:
    st.error(
        f"Could not find `{DATA_PATH}`. Place the CSV file in the same folder as app.py "
        "(or update DATA_PATH at the top of the script)."
    )
    st.stop()

# ----------------------------------------------------------------------------
# SIDEBAR — FILTERS  (User Capabilities)
# ----------------------------------------------------------------------------
st.sidebar.title("🍬 Nassau Candy")
st.sidebar.caption("Factory-to-Customer Shipping Route Efficiency")
st.sidebar.divider()
st.sidebar.header("Filters")

min_date, max_date = df_raw["Order Date"].min().date(), df_raw["Order Date"].max().date()
date_range = st.sidebar.date_input(
    "Order date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

regions = sorted(df_raw["Region"].dropna().unique().tolist())
sel_regions = st.sidebar.multiselect("Region", regions, default=regions)

available_states = sorted(df_raw.loc[df_raw["Region"].isin(sel_regions), "State/Province"].dropna().unique().tolist())
sel_states = st.sidebar.multiselect("State / Province", available_states, default=[])

ship_modes = sorted(df_raw["Ship Mode"].dropna().unique().tolist())
sel_ship_modes = st.sidebar.multiselect("Ship mode", ship_modes, default=ship_modes)

factories = sorted(df_raw["Factory"].dropna().unique().tolist())
sel_factories = st.sidebar.multiselect("Factory", factories, default=factories)

st.sidebar.divider()
lead_min = int(df_raw["Lead Time (days)"].min())
lead_max = int(df_raw["Lead Time (days)"].max())
default_threshold = int(df_raw["Lead Time (days)"].quantile(0.75))
delay_threshold = st.sidebar.slider(
    "Delay threshold (days)",
    min_value=lead_min,
    max_value=lead_max,
    value=default_threshold,
    help="Shipments with lead time above this value are counted as 'delayed' for the Delay Frequency KPI and highlighted on charts.",
)

with st.sidebar.expander("ℹ️ Data quality notes"):
    st.write(
        f"- **{clean_meta['n_invalid_removed']}** rows removed for negative lead time\n"
        f"- **{clean_meta['n_missing_removed']}** rows removed for missing/unparseable dates\n"
        f"- **{clean_meta['rows_used']:,}** rows used in this analysis\n\n"
        "Note: Ship Date values in the source file fall several years after Order Date "
        "for every record, so absolute lead-time magnitudes are not calendar-realistic. "
        "All KPIs and rankings below are still valid for **relative** route comparison."
    )

# --- Apply filters ---
mask = (
    (df_raw["Order Date"].dt.date >= start_date)
    & (df_raw["Order Date"].dt.date <= end_date)
    & (df_raw["Region"].isin(sel_regions))
    & (df_raw["Ship Mode"].isin(sel_ship_modes))
    & (df_raw["Factory"].isin(sel_factories))
)
if sel_states:
    mask &= df_raw["State/Province"].isin(sel_states)

df = df_raw[mask].copy()

if df.empty:
    st.warning("No shipments match the current filter selection. Adjust filters in the sidebar.")
    st.stop()

df["Delayed"] = df["Lead Time (days)"] > delay_threshold

# ----------------------------------------------------------------------------
# HEADER
# ----------------------------------------------------------------------------
st.title("Factory-to-Customer Shipping Route Efficiency")
st.caption(
    f"Analyzing **{len(df):,}** shipments from **{start_date}** to **{end_date}** "
    f"across **{df['Route (Factory to State)'].nunique()}** unique factory→state routes."
)

# ----------------------------------------------------------------------------
# KPIs
# ----------------------------------------------------------------------------
route_stats_state = (
    df.groupby("Route (Factory to State)")
    .agg(
        Shipments=("Order ID", "count"),
        Avg_Lead_Time=("Lead Time (days)", "mean"),
        Lead_Time_Std=("Lead Time (days)", "std"),
        Delay_Rate=("Delayed", "mean"),
        Sales=("Sales", "sum"),
    )
    .reset_index()
)
route_stats_state["Lead_Time_Std"] = route_stats_state["Lead_Time_Std"].fillna(0)

# Route Efficiency Score: normalized (0-100, higher = better/faster), based on avg lead time
lt_min, lt_max = route_stats_state["Avg_Lead_Time"].min(), route_stats_state["Avg_Lead_Time"].max()
if lt_max > lt_min:
    route_stats_state["Efficiency Score"] = 100 * (1 - (route_stats_state["Avg_Lead_Time"] - lt_min) / (lt_max - lt_min))
else:
    route_stats_state["Efficiency Score"] = 100.0

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Shipments", f"{len(df):,}")
k2.metric("Avg Shipping Lead Time", f"{df['Lead Time (days)'].mean():.1f} days")
k3.metric("Active Routes", f"{df['Route (Factory to State)'].nunique():,}")
k4.metric("Delay Frequency", f"{df['Delayed'].mean() * 100:.1f}%", help=f"Share of shipments exceeding {delay_threshold} days")
k5.metric("Avg Route Efficiency Score", f"{route_stats_state['Efficiency Score'].mean():.0f} / 100")

st.divider()

# ----------------------------------------------------------------------------
# TABS = Dashboard Modules
# ----------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Route Efficiency Overview", "🗺️ Geographic Shipping Map", "🚚 Ship Mode Comparison", "🔍 Route Drill-Down"]
)

# =========================================================
# TAB 1 — ROUTE EFFICIENCY OVERVIEW
# =========================================================
with tab1:
    c1, c2 = st.columns([1.3, 1])

    with c1:
        st.subheader("Average Lead Time by Route (Factory → Region)")
        route_region = (
            df.groupby(["Factory", "Region"])
            .agg(Avg_Lead_Time=("Lead Time (days)", "mean"), Shipments=("Order ID", "count"))
            .reset_index()
        )
        fig = px.bar(
            route_region.sort_values("Avg_Lead_Time"),
            x="Avg_Lead_Time",
            y="Region",
            color="Factory",
            orientation="h",
            barmode="group",
            labels={"Avg_Lead_Time": "Avg Lead Time (days)"},
            hover_data={"Shipments": True},
        )
        fig.update_layout(height=420, legend_title="Factory")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Route Volume Share")
        vol = df.groupby("Factory")["Order ID"].count().reset_index(name="Shipments")
        fig2 = px.pie(vol, names="Factory", values="Shipments", hole=0.45)
        fig2.update_layout(height=420)
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Route Performance Leaderboard (Factory → State)")
    leaderboard = route_stats_state.sort_values("Avg_Lead_Time").reset_index(drop=True)
    leaderboard.insert(0, "Rank", np.arange(1, len(leaderboard) + 1))

    lcol1, lcol2 = st.columns(2)
    with lcol1:
        st.markdown("**🏆 Top 10 Most Efficient Routes**")
        top10 = leaderboard.head(10)[["Rank", "Route (Factory to State)", "Shipments", "Avg_Lead_Time", "Delay_Rate", "Efficiency Score"]]
        st.dataframe(
            top10.style.format({"Avg_Lead_Time": "{:.1f}", "Delay_Rate": "{:.1%}", "Efficiency Score": "{:.0f}"}),
            hide_index=True,
            use_container_width=True,
        )
    with lcol2:
        st.markdown("**🐌 Bottom 10 Least Efficient Routes**")
        bottom10 = leaderboard.tail(10).sort_values("Avg_Lead_Time", ascending=False)
        bottom10 = bottom10[["Rank", "Route (Factory to State)", "Shipments", "Avg_Lead_Time", "Delay_Rate", "Efficiency Score"]]
        st.dataframe(
            bottom10.style.format({"Avg_Lead_Time": "{:.1f}", "Delay_Rate": "{:.1%}", "Efficiency Score": "{:.0f}"}),
            hide_index=True,
            use_container_width=True,
        )

# =========================================================
# TAB 2 — GEOGRAPHIC SHIPPING MAP
# =========================================================
with tab2:
    st.subheader("US Heatmap of Shipping Efficiency (Avg Lead Time by State)")

    state_stats = (
        df.groupby(["State/Province", "State Abbr"])
        .agg(
            Avg_Lead_Time=("Lead Time (days)", "mean"),
            Shipments=("Order ID", "count"),
            Delay_Rate=("Delayed", "mean"),
        )
        .reset_index()
        .dropna(subset=["State Abbr"])
    )

    fig_map = px.choropleth(
        state_stats,
        locations="State Abbr",
        locationmode="USA-states",
        color="Avg_Lead_Time",
        scope="usa",
        color_continuous_scale="RdYlGn_r",
        hover_name="State/Province",
        hover_data={"State Abbr": False, "Shipments": True, "Delay_Rate": ":.1%"},
        labels={"Avg_Lead_Time": "Avg Lead Time (days)"},
    )
    fig_map.update_layout(height=480, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig_map, use_container_width=True)

    st.subheader("Geographic Bottleneck Analysis")
    st.caption("States with both high average lead time AND high shipment volume — prime candidates for logistics intervention.")

    bcol1, bcol2 = st.columns([2, 1])
    with bcol1:
        median_vol = state_stats["Shipments"].median()
        median_lead = state_stats["Avg_Lead_Time"].median()
        fig_scatter = px.scatter(
            state_stats,
            x="Shipments",
            y="Avg_Lead_Time",
            size="Shipments",
            color="Delay_Rate",
            hover_name="State/Province",
            color_continuous_scale="OrRd",
            labels={"Shipments": "Shipment Volume", "Avg_Lead_Time": "Avg Lead Time (days)", "Delay_Rate": "Delay Rate"},
        )
        fig_scatter.add_hline(y=median_lead, line_dash="dot", line_color="gray")
        fig_scatter.add_vline(x=median_vol, line_dash="dot", line_color="gray")
        fig_scatter.update_layout(height=420)
        st.plotly_chart(fig_scatter, use_container_width=True)

    with bcol2:
        bottleneck_states = state_stats[
            (state_stats["Avg_Lead_Time"] > median_lead) & (state_stats["Shipments"] > median_vol)
        ].sort_values("Avg_Lead_Time", ascending=False)
        st.markdown("**⚠️ Congestion-Prone States**")
        st.caption("High volume + high lead time (top-right quadrant)")
        st.dataframe(
            bottleneck_states[["State/Province", "Shipments", "Avg_Lead_Time"]]
            .rename(columns={"Avg_Lead_Time": "Avg Lead Time"})
            .style.format({"Avg Lead Time": "{:.1f}"}),
            hide_index=True,
            use_container_width=True,
            height=340,
        )

    st.subheader("Factory Locations")
    factory_df = pd.DataFrame(
        [{"Factory": f, "Lat": c["lat"], "Lon": c["lon"], "Shipments": (df["Factory"] == f).sum()} for f, c in FACTORY_COORDS.items()]
    )
    fig_fac = px.scatter_geo(
        factory_df,
        lat="Lat",
        lon="Lon",
        text="Factory",
        size="Shipments",
        scope="usa",
        color="Factory",
    )
    fig_fac.update_traces(textposition="top center")
    fig_fac.update_layout(height=420, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig_fac, use_container_width=True)

# =========================================================
# TAB 3 — SHIP MODE COMPARISON
# =========================================================
with tab3:
    st.subheader("Shipping Efficiency by Ship Mode")

    mode_stats = (
        df.groupby("Ship Mode")
        .agg(
            Shipments=("Order ID", "count"),
            Avg_Lead_Time=("Lead Time (days)", "mean"),
            Median_Lead_Time=("Lead Time (days)", "median"),
            Delay_Rate=("Delayed", "mean"),
            Avg_Sales=("Sales", "mean"),
            Avg_Cost=("Cost", "mean"),
        )
        .reset_index()
        .sort_values("Avg_Lead_Time")
    )

    mcol1, mcol2 = st.columns(2)
    with mcol1:
        fig_box = px.box(
            df,
            x="Ship Mode",
            y="Lead Time (days)",
            color="Ship Mode",
            points=False,
            category_orders={"Ship Mode": mode_stats["Ship Mode"].tolist()},
        )
        fig_box.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)

    with mcol2:
        fig_bar = px.bar(
            mode_stats,
            x="Ship Mode",
            y="Delay_Rate",
            color="Ship Mode",
            category_orders={"Ship Mode": mode_stats["Ship Mode"].tolist()},
            labels={"Delay_Rate": "Delay Rate"},
            text_auto=".1%",
        )
        fig_bar.update_layout(height=400, showlegend=False, yaxis_tickformat=".0%")
        st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("Cost vs. Lead Time Tradeoff by Ship Mode (descriptive)")
    st.caption("Average sales value and cost per shipment alongside average lead time for each ship mode.")
    st.dataframe(
        mode_stats.style.format(
            {
                "Avg_Lead_Time": "{:.1f}",
                "Median_Lead_Time": "{:.1f}",
                "Delay_Rate": "{:.1%}",
                "Avg_Sales": "${:.2f}",
                "Avg_Cost": "${:.2f}",
            }
        ),
        hide_index=True,
        use_container_width=True,
    )

    fig_scatter2 = px.scatter(
        mode_stats,
        x="Avg_Lead_Time",
        y="Avg_Cost",
        size="Shipments",
        color="Ship Mode",
        text="Ship Mode",
        labels={"Avg_Lead_Time": "Avg Lead Time (days)", "Avg_Cost": "Avg Cost per Shipment ($)"},
    )
    fig_scatter2.update_traces(textposition="top center")
    fig_scatter2.update_layout(height=400)
    st.plotly_chart(fig_scatter2, use_container_width=True)

# =========================================================
# TAB 4 — ROUTE DRILL-DOWN
# =========================================================
with tab4:
    st.subheader("Route Drill-Down")

    drill_state = st.selectbox(
        "Select a State / Province to inspect",
        options=sorted(df["State/Province"].dropna().unique().tolist()),
    )

    state_df = df[df["State/Province"] == drill_state]

    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Shipments", f"{len(state_df):,}")
    d2.metric("Avg Lead Time", f"{state_df['Lead Time (days)'].mean():.1f} days")
    d3.metric("Delay Rate", f"{state_df['Delayed'].mean() * 100:.1f}%")
    d4.metric("Total Sales", f"${state_df['Sales'].sum():,.0f}")

    dcol1, dcol2 = st.columns(2)
    with dcol1:
        st.markdown(f"**Lead Time Trend for {drill_state}**")
        trend = state_df.groupby("Order Month")["Lead Time (days)"].mean().reset_index()
        fig_trend = px.line(trend, x="Order Month", y="Lead Time (days)", markers=True)
        fig_trend.update_layout(height=350)
        st.plotly_chart(fig_trend, use_container_width=True)

    with dcol2:
        st.markdown(f"**Shipments by Factory for {drill_state}**")
        fac_split = state_df.groupby("Factory")["Order ID"].count().reset_index(name="Shipments")
        fig_fac_split = px.pie(fac_split, names="Factory", values="Shipments", hole=0.45)
        fig_fac_split.update_layout(height=350)
        st.plotly_chart(fig_fac_split, use_container_width=True)

    st.markdown("**Order-Level Shipment Timeline**")
    timeline_cols = [
        "Order ID", "Order Date", "Ship Date", "Lead Time (days)", "Ship Mode",
        "Factory", "City", "Product Name", "Division", "Sales", "Units", "Delayed",
    ]
    st.dataframe(
        state_df[timeline_cols].sort_values("Order Date", ascending=False).reset_index(drop=True),
        use_container_width=True,
        height=420,
    )

    st.download_button(
        "⬇️ Download this state's shipment data (CSV)",
        data=state_df[timeline_cols].to_csv(index=False).encode("utf-8"),
        file_name=f"{drill_state.replace(' ', '_')}_shipments.csv",
        mime="text/csv",
    )

st.divider()
st.caption(
    "Nassau Candy Distributor — Factory-to-Customer Shipping Route Efficiency Analysis · "
    "Built with Streamlit · Data source: internal order/shipment records"
)
