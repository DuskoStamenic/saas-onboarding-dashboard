"""SaaS Onboarding Dashboard — Untitled UI inspired styling."""
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

DATA_DIR = Path(__file__).parent / "data"

st.set_page_config(
    page_title="SaaS Onboarding Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed",
)

PRIMARY = "#7F56D9"
GRAY_900 = "#101828"
GRAY_700 = "#344054"
GRAY_500 = "#667085"
GRAY_300 = "#D0D5DD"
GRAY_200 = "#EAECF0"
GRAY_50 = "#F9FAFB"
COLORWAY = ["#7F56D9", "#2E90FA", "#12B76A", "#F79009", "#F04438", "#15B79E", "#6172F3", "#EE46BC"]

st.markdown(
    f"""
    <style>
      .stApp {{ background-color: {GRAY_50}; }}
      .block-container {{ width: 100%; max-width: 1120px !important; padding-top: 2rem; padding-bottom: 3rem; }}
      h1, h2, h3 {{ color: {GRAY_900}; font-family: 'Inter', -apple-system, sans-serif; letter-spacing: -0.02em; }}
      .page-title {{ font-size: 30px; font-weight: 600; color: {GRAY_900}; margin: 0; }}
      .page-subtitle {{ font-size: 16px; color: {GRAY_500}; margin: 4px 0 24px 0; }}
      .kpi-card {{
          background: #fff;
          border: 1px solid {GRAY_200};
          border-radius: 12px;
          padding: 24px;
          box-shadow: 0 1px 2px rgba(16, 24, 40, 0.05);
      }}
      .kpi-label {{ font-size: 14px; font-weight: 500; color: {GRAY_500}; margin-bottom: 8px; }}
      .kpi-value {{ font-size: 36px; font-weight: 600; color: {GRAY_900}; line-height: 1.2; letter-spacing: -0.02em; }}
      .chart-card {{
          background: #fff;
          border: 1px solid {GRAY_200};
          border-radius: 12px;
          padding: 20px 24px 12px 24px;
          box-shadow: 0 1px 2px rgba(16, 24, 40, 0.05);
          margin-bottom: 20px;
      }}
      .chart-title {{ font-size: 16px; font-weight: 600; color: {GRAY_900}; margin: 0 0 4px 0; }}
      .chart-subtitle {{ font-size: 14px; color: {GRAY_500}; margin: 0 0 12px 0; }}
      [data-testid="stHeader"] {{ background: transparent; }}
      [data-testid="stVerticalBlockBorderWrapper"] {{ background: #fff; border-radius: 12px; }}
      [data-testid="stSelectbox"] [data-baseweb="select"] > div {{ padding-right: 2.75rem !important; }}
      [data-testid="stSelectbox"] [data-baseweb="select"] svg {{ right: 1rem !important; margin-right: 0.35rem; }}
      [data-testid="stPlotlyChart"], [data-testid="stPlotlyChart"] * {{ cursor: pointer !important; }}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_data() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "onboarding.csv", parse_dates=["signup_date"])


def style_fig(fig: go.Figure, height: int = 320) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=8, r=8, t=8, b=8),
        paper_bgcolor="#fff",
        plot_bgcolor="#fff",
        font=dict(family="Inter, -apple-system, sans-serif", size=12, color=GRAY_700),
        colorway=COLORWAY,
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, x=0, font=dict(size=12)),
        xaxis=dict(showgrid=False, linecolor=GRAY_200, tickcolor=GRAY_200, color=GRAY_500),
        yaxis=dict(gridcolor=GRAY_200, zerolinecolor=GRAY_200, color=GRAY_500),
    )
    return fig


def apply_country_selection() -> None:
    chart_state = st.session_state.get("country_chart", {})
    points = chart_state.get("selection", {}).get("points", [])
    if not points:
        st.session_state.selected_country = None
        return
    country = points[-1].get("y")
    if country is None:
        return
    st.session_state.selected_country = (
        None if st.session_state.selected_country == country else country
    )


df = load_data()
plan_order = df["plan"].dropna().drop_duplicates().tolist()
month_options = (
    df["signup_date"].dropna().dt.to_period("M").drop_duplicates().sort_values().tolist()
)
if "selected_country" not in st.session_state:
    st.session_state.selected_country = None
if "country_filter_signature" not in st.session_state:
    st.session_state.country_filter_signature = None

st.markdown('<p class="page-title">SaaS Onboarding</p>', unsafe_allow_html=True)
subtitle = st.empty()

with st.container(border=True):
    plan_col, month_col = st.columns(2, gap="medium")
    selected_plan = plan_col.selectbox("Plan", ["All plans", *plan_order])
    selected_month = month_col.selectbox(
        "Month",
        [None, *month_options],
        format_func=lambda value: "All months" if value is None else value.strftime("%b %Y"),
    )

country_filter_signature = (selected_plan, str(selected_month))
if st.session_state.country_filter_signature != country_filter_signature:
    st.session_state.selected_country = None
    st.session_state.pop("country_chart", None)
    st.session_state.country_filter_signature = country_filter_signature

base_df = df
if selected_plan != "All plans":
    base_df = base_df[base_df["plan"] == selected_plan]
if selected_month is not None:
    base_df = base_df[base_df["signup_date"].dt.to_period("M") == selected_month]

available_countries = set(base_df["country"].dropna().tolist())
if (
    st.session_state.selected_country is not None
    and st.session_state.selected_country not in available_countries
):
    st.session_state.selected_country = None
    st.session_state.pop("country_chart", None)
selected_country = st.session_state.selected_country
metric_df = (
    base_df[base_df["country"] == selected_country]
    if selected_country is not None
    else base_df
)

with subtitle.container():
    if metric_df.empty:
        st.markdown(
            '<p class="page-subtitle">No signups match the selected filters</p>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<p class="page-subtitle">{metric_df["signup_date"].min():%b %d, %Y} — '
            f'{metric_df["signup_date"].max():%b %d, %Y} · {len(metric_df):,} signups</p>',
            unsafe_allow_html=True,
        )

st.write("")

total_mrr = metric_df["mrr"].sum()
total_users = len(metric_df)
avg_mrr = metric_df["mrr"].mean() if not metric_df.empty else 0

k1, k2, k3 = st.columns(3, gap="medium")
for col, label, value in [
    (k1, "Total MRR", f"${total_mrr:,.0f}"),
    (k2, "Total Users", f"{total_users:,}"),
    (k3, "Avg MRR / User", f"${avg_mrr:,.2f}"),
]:
    col.markdown(
        f'<div class="kpi-card"><div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div></div>',
        unsafe_allow_html=True,
    )

st.write("")

m1, m2 = st.columns(2, gap="medium")

with m1:
    st.markdown(
        '<div class="chart-card"><p class="chart-title">MRR over time</p>'
        '<p class="chart-subtitle">Cumulative monthly recurring revenue</p>',
        unsafe_allow_html=True,
    )
    mrr_ts = (
        metric_df.set_index("signup_date")
        .resample("W")["mrr"]
        .sum()
        .cumsum()
        .reset_index()
    )
    fig = px.area(mrr_ts, x="signup_date", y="mrr")
    fig.update_traces(
        line=dict(color=PRIMARY, width=2.5),
        fillcolor="rgba(127, 86, 217, 0.08)",
        hovertemplate="%{x|%b %d, %Y}<br><b>$%{y:,.0f}</b><extra></extra>",
    )
    fig.update_yaxes(title=None, tickprefix="$", separatethousands=True)
    fig.update_xaxes(title=None)
    st.plotly_chart(style_fig(fig), use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with m2:
    st.markdown(
        '<div class="chart-card"><p class="chart-title">Users by plan</p>'
        '<p class="chart-subtitle">Signups across pricing tiers</p>',
        unsafe_allow_html=True,
    )
    plan_counts = (
        metric_df["plan"]
        .value_counts()
        .reindex(plan_order)
        .fillna(0)
        .astype(int)
        .reset_index()
    )
    plan_counts.columns = ["plan", "users"]
    fig = px.bar(plan_counts, x="plan", y="users", text="users")
    fig.update_traces(
        marker_color=PRIMARY,
        marker_line_width=0,
        textposition="outside",
        textfont=dict(color=GRAY_700, size=12),
        hovertemplate="<b>%{x}</b><br>%{y} users<extra></extra>",
    )
    fig.update_yaxes(title=None, showticklabels=False)
    fig.update_xaxes(title=None)
    st.plotly_chart(style_fig(fig), use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

b1, b2 = st.columns(2, gap="medium")

with b1:
    st.markdown(
        '<div class="chart-card"><p class="chart-title">Users by country</p>'
        '<p class="chart-subtitle">Geographic distribution of signups</p>',
        unsafe_allow_html=True,
    )
    country_counts = (
        base_df.groupby("country", as_index=False, dropna=True)
        .size()
        .rename(columns={"size": "users"})
        .sort_values(["users", "country"], ascending=[False, True])
    )
    country_colors = [
        GRAY_300
        if selected_country is not None and country != selected_country
        else PRIMARY
        for country in country_counts["country"]
    ]
    fig = px.bar(
        country_counts,
        x="users",
        y="country",
        orientation="h",
        text="users",
    )
    fig.update_traces(
        marker_color=country_colors,
        marker_line_width=0,
        textposition="outside",
        textfont=dict(color=GRAY_700, size=12),
        hovertemplate="<b>%{y}</b><br>%{x} users<extra></extra>",
    )
    fig.update_xaxes(title=None, showticklabels=False)
    fig.update_yaxes(title=None, autorange="reversed")
    fig.update_layout(clickmode="event+select", dragmode=False)
    st.plotly_chart(
        style_fig(fig, height=380),
        use_container_width=True,
        key="country_chart",
        on_select=apply_country_selection,
        selection_mode="points",
        config={"displayModeBar": False},
    )
    st.markdown("</div>", unsafe_allow_html=True)

with b2:
    st.markdown(
        '<div class="chart-card"><p class="chart-title">Seats by plan</p>'
        '<p class="chart-subtitle">Total licensed seats per tier</p>',
        unsafe_allow_html=True,
    )
    seats = (
        metric_df.groupby("plan")["seats"]
        .sum()
        .reindex(plan_order)
        .fillna(0)
        .astype(int)
        .reset_index()
    )
    seats.columns = ["plan", "seats"]
    fig = px.bar(seats, x="plan", y="seats", text="seats")
    fig.update_traces(
        marker_color=[COLORWAY[(index + 2) % len(COLORWAY)] for index in range(len(plan_order))],
        marker_line_width=0,
        textposition="outside",
        textfont=dict(color=GRAY_700, size=12),
        hovertemplate="<b>%{x}</b><br>%{y} seats<extra></extra>",
    )
    fig.update_yaxes(title=None, showticklabels=False)
    fig.update_xaxes(title=None)
    st.plotly_chart(style_fig(fig, height=380), use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)
