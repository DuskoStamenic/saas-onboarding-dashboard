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

# --- Untitled UI inspired palette ---
PRIMARY = "#7F56D9"
PRIMARY_LIGHT = "#F4EBFF"
GRAY_900 = "#101828"
GRAY_700 = "#344054"
GRAY_500 = "#667085"
GRAY_200 = "#EAECF0"
GRAY_50 = "#F9FAFB"
SUCCESS = "#12B76A"
COLORWAY = ["#7F56D9", "#2E90FA", "#12B76A", "#F79009", "#F04438", "#15B79E", "#6172F3", "#EE46BC"]

st.markdown(
    f"""
    <style>
      .stApp {{ background-color: {GRAY_50}; }}
      .block-container {{ padding-top: 2rem; padding-bottom: 3rem; max-width: 1280px; }}
      h1, h2, h3 {{ color: {GRAY_900}; font-family: 'Inter', -apple-system, sans-serif; letter-spacing: -0.02em; }}
      .page-title {{ font-size: 30px; font-weight: 600; color: {GRAY_900}; margin: 0; }}
      .page-subtitle {{ font-size: 16px; color: {GRAY_500}; margin: 4px 0 28px 0; }}
      .kpi-card {{
          background: #fff;
          border: 1px solid {GRAY_200};
          border-radius: 12px;
          padding: 24px;
          box-shadow: 0 1px 2px rgba(16, 24, 40, 0.05);
      }}
      .kpi-label {{ font-size: 14px; font-weight: 500; color: {GRAY_500}; margin-bottom: 8px; }}
      .kpi-value {{ font-size: 36px; font-weight: 600; color: {GRAY_900}; line-height: 1.2; letter-spacing: -0.02em; }}
      .kpi-meta {{ font-size: 14px; color: {SUCCESS}; font-weight: 500; margin-top: 8px; }}
      .chart-card {{
          background: #fff;
          border: 1px solid {GRAY_200};
          border-radius: 12px;
          padding: 20px 24px 8px 24px;
          box-shadow: 0 1px 2px rgba(16, 24, 40, 0.05);
          margin-bottom: 20px;
      }}
      .chart-title {{ font-size: 16px; font-weight: 600; color: {GRAY_900}; margin: 0 0 4px 0; }}
      .chart-subtitle {{ font-size: 14px; color: {GRAY_500}; margin: 0 0 12px 0; }}
      [data-testid="stHeader"] {{ background: transparent; }}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "onboarding.csv", parse_dates=["signup_date"])
    return df


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


df = load_data()

# --- Header ---
st.markdown('<p class="page-title">SaaS Onboarding</p>', unsafe_allow_html=True)
st.markdown(
    f'<p class="page-subtitle">{df["signup_date"].min():%b %d, %Y} — {df["signup_date"].max():%b %d, %Y} · {len(df)} signups</p>',
    unsafe_allow_html=True,
)

# --- KPI row ---
total_mrr = df["mrr"].sum()
total_users = len(df)
avg_mrr = df["mrr"].mean()

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

# --- Middle row: MRR over time + Users by plan ---
m1, m2 = st.columns(2, gap="medium")

with m1:
    st.markdown(
        '<div class="chart-card"><p class="chart-title">MRR over time</p>'
        '<p class="chart-subtitle">Cumulative monthly recurring revenue</p>',
        unsafe_allow_html=True,
    )
    mrr_ts = (
        df.set_index("signup_date")
        .resample("W")["mrr"].sum()
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
    plan_order = ["Starter", "Pro", "Enterprise"]
    plan_counts = df["plan"].value_counts().reindex(plan_order).reset_index()
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

# --- Bottom row: Users by country + Seats by plan ---
b1, b2 = st.columns(2, gap="medium")

with b1:
    st.markdown(
        '<div class="chart-card"><p class="chart-title">Users by country</p>'
        '<p class="chart-subtitle">Geographic distribution of signups</p>',
        unsafe_allow_html=True,
    )
    country_counts = (
        df["country"].value_counts().sort_values(ascending=True).reset_index()
    )
    country_counts.columns = ["country", "users"]
    fig = px.bar(country_counts, x="users", y="country", orientation="h", text="users")
    fig.update_traces(
        marker_color=PRIMARY,
        marker_line_width=0,
        textposition="outside",
        textfont=dict(color=GRAY_700, size=12),
        hovertemplate="<b>%{y}</b><br>%{x} users<extra></extra>",
    )
    fig.update_xaxes(title=None, showticklabels=False)
    fig.update_yaxes(title=None)
    st.plotly_chart(style_fig(fig, height=380), use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with b2:
    st.markdown(
        '<div class="chart-card"><p class="chart-title">Seats by plan</p>'
        '<p class="chart-subtitle">Total licensed seats per tier</p>',
        unsafe_allow_html=True,
    )
    seats = df.groupby("plan")["seats"].sum().reindex(plan_order).reset_index()
    fig = px.bar(seats, x="plan", y="seats", text="seats")
    fig.update_traces(
        marker_color=[COLORWAY[2], COLORWAY[0], COLORWAY[1]],
        marker_line_width=0,
        textposition="outside",
        textfont=dict(color=GRAY_700, size=12),
        hovertemplate="<b>%{x}</b><br>%{y} seats<extra></extra>",
    )
    fig.update_yaxes(title=None, showticklabels=False)
    fig.update_xaxes(title=None)
    st.plotly_chart(style_fig(fig, height=380), use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)
