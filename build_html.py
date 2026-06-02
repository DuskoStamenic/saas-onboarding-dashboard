"""Build a standalone HTML dashboard from onboarding.csv."""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).parent
df = pd.read_csv(ROOT / "data" / "onboarding.csv", parse_dates=["signup_date"])

PRIMARY = "#7F56D9"
COLORWAY = ["#7F56D9", "#2E90FA", "#12B76A", "#F79009", "#F04438"]

total_mrr = float(df["mrr"].sum())
total_users = int(len(df))
avg_mrr = float(df["mrr"].mean())
date_min = df["signup_date"].min().strftime("%b %d, %Y")
date_max = df["signup_date"].max().strftime("%b %d, %Y")

mrr_ts = (
    df.set_index("signup_date").resample("W")["mrr"].sum().cumsum().reset_index()
)
mrr_dates = [d.strftime("%Y-%m-%d") for d in mrr_ts["signup_date"]]
mrr_values = mrr_ts["mrr"].tolist()

plan_order = ["Starter", "Pro", "Enterprise"]
plan_counts = df["plan"].value_counts().reindex(plan_order).fillna(0).astype(int).tolist()

country_counts = df["country"].value_counts().sort_values(ascending=True)
countries = country_counts.index.tolist()
country_values = country_counts.tolist()

seats = df.groupby("plan")["seats"].sum().reindex(plan_order).fillna(0).astype(int).tolist()

ctx = {
    "PRIMARY": PRIMARY,
    "COLORWAY": COLORWAY,
    "total_mrr": f"${total_mrr:,.0f}",
    "total_users": f"{total_users:,}",
    "avg_mrr": f"${avg_mrr:,.2f}",
    "date_range": f"{date_min} — {date_max} · {total_users} signups",
    "mrr_dates": mrr_dates,
    "mrr_values": mrr_values,
    "plan_labels": plan_order,
    "plan_counts": plan_counts,
    "countries": countries,
    "country_values": country_values,
    "seats": seats,
}

html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>SaaS Onboarding Dashboard</title>
<meta name="viewport" content="width=device-width, initial-scale=1" />
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
  :root {{
    --primary: #7F56D9;
    --gray-50: #F9FAFB;
    --gray-200: #EAECF0;
    --gray-500: #667085;
    --gray-700: #344054;
    --gray-900: #101828;
    --success: #12B76A;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    background: var(--gray-50);
    color: var(--gray-900);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    -webkit-font-smoothing: antialiased;
  }}
  .container {{ max-width: 1280px; margin: 0 auto; padding: 40px 32px 64px; }}
  .page-title {{ font-size: 30px; font-weight: 600; letter-spacing: -0.02em; margin: 0; }}
  .page-subtitle {{ font-size: 16px; color: var(--gray-500); margin: 4px 0 32px; }}
  .grid {{ display: grid; gap: 20px; }}
  .grid-3 {{ grid-template-columns: repeat(3, 1fr); }}
  .grid-2 {{ grid-template-columns: repeat(2, 1fr); }}
  @media (max-width: 900px) {{
    .grid-3, .grid-2 {{ grid-template-columns: 1fr; }}
  }}
  .card {{
    background: #fff;
    border: 1px solid var(--gray-200);
    border-radius: 12px;
    box-shadow: 0 1px 2px rgba(16,24,40,0.05);
  }}
  .kpi {{ padding: 24px; }}
  .kpi-label {{ font-size: 14px; font-weight: 500; color: var(--gray-500); margin-bottom: 8px; }}
  .kpi-value {{ font-size: 36px; font-weight: 600; letter-spacing: -0.02em; line-height: 1.2; }}
  .chart-card {{ padding: 20px 24px 12px; margin-bottom: 20px; }}
  .chart-title {{ font-size: 16px; font-weight: 600; margin: 0 0 4px; }}
  .chart-subtitle {{ font-size: 14px; color: var(--gray-500); margin: 0 0 12px; }}
  .chart {{ width: 100%; height: 320px; }}
  .chart-tall {{ height: 380px; }}
  .row-spacer {{ margin-top: 20px; }}
</style>
</head>
<body>
  <div class="container">
    <h1 class="page-title">SaaS Onboarding</h1>
    <p class="page-subtitle">{ctx['date_range']}</p>

    <div class="grid grid-3">
      <div class="card kpi"><div class="kpi-label">Total MRR</div><div class="kpi-value">{ctx['total_mrr']}</div></div>
      <div class="card kpi"><div class="kpi-label">Total Users</div><div class="kpi-value">{ctx['total_users']}</div></div>
      <div class="card kpi"><div class="kpi-label">Avg MRR / User</div><div class="kpi-value">{ctx['avg_mrr']}</div></div>
    </div>

    <div class="grid grid-2 row-spacer">
      <div class="card chart-card">
        <p class="chart-title">MRR over time</p>
        <p class="chart-subtitle">Cumulative monthly recurring revenue</p>
        <div id="chart-mrr" class="chart"></div>
      </div>
      <div class="card chart-card">
        <p class="chart-title">Users by plan</p>
        <p class="chart-subtitle">Signups across pricing tiers</p>
        <div id="chart-plan" class="chart"></div>
      </div>
    </div>

    <div class="grid grid-2">
      <div class="card chart-card">
        <p class="chart-title">Users by country</p>
        <p class="chart-subtitle">Geographic distribution of signups</p>
        <div id="chart-country" class="chart chart-tall"></div>
      </div>
      <div class="card chart-card">
        <p class="chart-title">Seats by plan</p>
        <p class="chart-subtitle">Total licensed seats per tier</p>
        <div id="chart-seats" class="chart chart-tall"></div>
      </div>
    </div>
  </div>

<script>
const DATA = {json.dumps(ctx)};
const AXIS_X = {{ showgrid: false, linecolor: '#EAECF0', tickcolor: '#EAECF0', color: '#667085' }};
const AXIS_Y = {{ gridcolor: '#EAECF0', zerolinecolor: '#EAECF0', color: '#667085' }};
const FONT = {{ family: 'Inter, sans-serif', size: 12, color: '#344054' }};
const layoutFor = (xtype, ytype, extra = {{}}) => ({{
  margin: {{ l: 48, r: 16, t: 8, b: 40 }},
  paper_bgcolor: '#fff',
  plot_bgcolor: '#fff',
  font: {{ ...FONT }},
  showlegend: false,
  xaxis: {{ ...AXIS_X, type: xtype }},
  yaxis: {{ ...AXIS_Y, type: ytype }},
  ...extra,
}});
const config = {{ displayModeBar: false, responsive: true }};

Plotly.newPlot('chart-mrr', [{{
  x: DATA.mrr_dates, y: DATA.mrr_values, type: 'scatter', mode: 'lines',
  fill: 'tozeroy', line: {{ color: DATA.PRIMARY, width: 2.5 }},
  fillcolor: 'rgba(127, 86, 217, 0.08)',
  hovertemplate: '%{{x|%b %d, %Y}}<br><b>$%{{y:,.0f}}</b><extra></extra>',
}}], layoutFor('date', 'linear', {{ yaxis: {{ ...AXIS_Y, type: 'linear', tickprefix: '$', separatethousands: true }} }}), config);

Plotly.newPlot('chart-plan', [{{
  x: DATA.plan_labels, y: DATA.plan_counts, type: 'bar',
  marker: {{ color: DATA.PRIMARY }},
  text: DATA.plan_counts.map(String), textposition: 'outside', cliponaxis: false,
  textfont: {{ ...FONT }},
  hovertemplate: '<b>%{{x}}</b><br>%{{y}} users<extra></extra>',
}}], layoutFor('category', 'linear', {{ yaxis: {{ ...AXIS_Y, type: 'linear', showticklabels: false, rangemode: 'tozero' }} }}), config);

Plotly.newPlot('chart-country', [{{
  x: DATA.country_values, y: DATA.countries, type: 'bar', orientation: 'h',
  marker: {{ color: DATA.PRIMARY }},
  text: DATA.country_values.map(String), textposition: 'outside', cliponaxis: false,
  textfont: {{ ...FONT }},
  hovertemplate: '<b>%{{y}}</b><br>%{{x}} users<extra></extra>',
}}], layoutFor('linear', 'category', {{
  margin: {{ l: 120, r: 40, t: 8, b: 32 }},
  xaxis: {{ ...AXIS_X, type: 'linear', showticklabels: false, rangemode: 'tozero' }},
  yaxis: {{ ...AXIS_Y, type: 'category', automargin: true }},
}}), config);

Plotly.newPlot('chart-seats', [{{
  x: DATA.plan_labels, y: DATA.seats, type: 'bar',
  marker: {{ color: [DATA.COLORWAY[2], DATA.COLORWAY[0], DATA.COLORWAY[1]] }},
  text: DATA.seats.map(String), textposition: 'outside', cliponaxis: false,
  textfont: {{ ...FONT }},
  hovertemplate: '<b>%{{x}}</b><br>%{{y}} seats<extra></extra>',
}}], layoutFor('category', 'linear', {{ yaxis: {{ ...AXIS_Y, type: 'linear', showticklabels: false, rangemode: 'tozero' }} }}), config);
</script>
</body>
</html>
"""

out = ROOT / "dashboard.html"
out.write_text(html)
print(f"Wrote {out}")
