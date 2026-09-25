"""Build a standalone HTML dashboard from onboarding.csv."""
import csv
import json
from datetime import datetime
from html import escape
from pathlib import Path

ROOT = Path(__file__).parent
with (ROOT / "data" / "onboarding.csv").open(encoding="utf-8", newline="") as source:
    source_rows = list(csv.DictReader(source))

PRIMARY = "#7F56D9"
COLORWAY = ["#7F56D9", "#2E90FA", "#12B76A", "#F79009", "#F04438"]

plan_options = list(dict.fromkeys(row["plan"] for row in source_rows if row["plan"]))
month_values = sorted({row["signup_date"][:7] for row in source_rows if row["signup_date"]})
month_options = [
    {
        "value": month,
        "label": datetime.strptime(month, "%Y-%m").strftime("%b %Y"),
    }
    for month in month_values
]
rows = [
    {
        "plan": row["plan"],
        "signup_date": row["signup_date"],
        "country": row["country"],
        "seats": int(row["seats"]),
        "mrr": float(row["mrr"]),
    }
    for row in source_rows
]
ctx = {
    "PRIMARY": PRIMARY,
    "COLORWAY": COLORWAY,
    "plan_options": plan_options,
    "month_options": month_options,
    "rows": rows,
}
payload = json.dumps(ctx, separators=(",", ":")).replace("<", "\\u003c")
plan_options_html = "".join(
    f'<option value="{escape(plan, quote=True)}">{escape(plan)}</option>'
    for plan in plan_options
)
month_options_html = "".join(
    f'<option value="{escape(option["value"], quote=True)}">{escape(option["label"])}</option>'
    for option in month_options
)

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
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    background: var(--gray-50);
    color: var(--gray-900);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    -webkit-font-smoothing: antialiased;
  }}
  button, select {{ font: inherit; }}
  .container {{ width: 100%; max-width: 1120px; margin: 0 auto; padding: 40px 32px 64px; }}
  .page-title {{ font-size: 30px; font-weight: 600; letter-spacing: -0.02em; margin: 0; }}
  .page-subtitle {{ font-size: 16px; color: var(--gray-500); margin: 4px 0 24px; }}
  .filters {{
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 220px));
    gap: 16px;
    background: #fff;
    border: 1px solid var(--gray-200);
    border-radius: 12px;
    box-shadow: 0 1px 2px rgba(16, 24, 40, 0.05);
    padding: 16px 20px 20px;
    margin-bottom: 24px;
  }}
  .filter {{ display: flex; flex-direction: column; gap: 6px; }}
  .filter label {{ font-size: 13px; font-weight: 600; color: var(--gray-700); }}
  .filter select {{
    width: 100%;
    min-height: 44px;
    border: 1px solid var(--gray-200);
    border-radius: 8px;
    background-color: #fff;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12' fill='none' stroke='%23667085' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m3 4.5 3 3 3-3'/%3E%3C/svg%3E");
    background-position: right 12px center;
    background-repeat: no-repeat;
    background-size: 12px 12px;
    color: var(--gray-900);
    padding: 0 40px 0 12px;
    cursor: pointer;
    -webkit-appearance: none;
    appearance: none;
    transition: border-color 180ms ease, box-shadow 180ms ease;
  }}
  .filter select:hover {{ border-color: var(--gray-500); }}
  .filter select:focus-visible {{
    outline: 0;
    border-color: var(--primary);
    box-shadow: 0 0 0 3px rgba(127, 86, 217, 0.16);
  }}
  .grid {{ display: grid; gap: 20px; }}
  .grid-3 {{ grid-template-columns: repeat(3, 1fr); }}
  .grid-2 {{ grid-template-columns: repeat(2, 1fr); }}
  .card {{
    background: #fff;
    border: 1px solid var(--gray-200);
    border-radius: 12px;
    box-shadow: 0 1px 2px rgba(16, 24, 40, 0.05);
  }}
  .kpi {{ padding: 24px; }}
  .kpi-label {{ font-size: 14px; font-weight: 500; color: var(--gray-500); margin-bottom: 8px; }}
  .kpi-value {{ font-size: 36px; font-weight: 600; letter-spacing: -0.02em; line-height: 1.2; }}
  .chart-card {{ padding: 20px 24px 12px; margin-bottom: 20px; }}
  .chart-title {{ font-size: 16px; font-weight: 600; margin: 0 0 4px; }}
  .chart-subtitle {{ font-size: 14px; color: var(--gray-500); margin: 0 0 12px; }}
  .chart {{ width: 100%; height: 320px; cursor: pointer; }}
  .chart, .chart * {{ cursor: pointer !important; }}
  .chart-tall {{ height: 380px; }}
  .row-spacer {{ margin-top: 20px; }}
  @media (max-width: 900px) {{
    .grid-3, .grid-2 {{ grid-template-columns: 1fr; }}
  }}
  @media (max-width: 560px) {{
    .container {{ padding: 28px 16px 48px; }}
    .filters {{ grid-template-columns: 1fr; }}
    .kpi {{ padding: 20px; }}
    .chart-card {{ padding: 18px 16px 10px; }}
  }}
  @media (prefers-reduced-motion: reduce) {{
    *, *::before, *::after {{ scroll-behavior: auto !important; transition-duration: 0.01ms !important; }}
  }}
</style>
</head>
<body>
  <div class="container">
    <h1 class="page-title">SaaS Onboarding</h1>
    <p id="page-subtitle" class="page-subtitle" aria-live="polite">Loading signups…</p>

    <section class="filters" aria-label="Dashboard filters">
      <div class="filter">
        <label for="plan-filter">Plan</label>
        <select id="plan-filter">
          <option value="all">All plans</option>
          {plan_options_html}
        </select>
      </div>
      <div class="filter">
        <label for="month-filter">Month</label>
        <select id="month-filter">
          <option value="all">All months</option>
          {month_options_html}
        </select>
      </div>
    </section>

    <section class="grid grid-3" aria-label="Key performance indicators">
      <article class="card kpi"><div class="kpi-label">Total MRR</div><div id="total-mrr" class="kpi-value">—</div></article>
      <article class="card kpi"><div class="kpi-label">Total Users</div><div id="total-users" class="kpi-value">—</div></article>
      <article class="card kpi"><div class="kpi-label">Avg MRR / User</div><div id="avg-mrr" class="kpi-value">—</div></article>
    </section>

    <section class="grid grid-2 row-spacer">
      <article class="card chart-card">
        <p class="chart-title">MRR over time</p>
        <p class="chart-subtitle">Cumulative monthly recurring revenue</p>
        <div id="chart-mrr" class="chart"></div>
      </article>
      <article class="card chart-card">
        <p class="chart-title">Users by plan</p>
        <p class="chart-subtitle">Signups across pricing tiers</p>
        <div id="chart-plan" class="chart"></div>
      </article>
    </section>

    <section class="grid grid-2">
      <article class="card chart-card">
        <p class="chart-title">Users by country</p>
        <p class="chart-subtitle">Geographic distribution of signups</p>
        <div id="chart-country" class="chart chart-tall" role="img" aria-label="Users by country bar chart"></div>
      </article>
      <article class="card chart-card">
        <p class="chart-title">Seats by plan</p>
        <p class="chart-subtitle">Total licensed seats per tier</p>
        <div id="chart-seats" class="chart chart-tall"></div>
      </article>
    </section>
  </div>

<script>
const DATA = {payload};
const state = {{ plan: 'all', month: 'all', country: null }};
const AXIS_X = {{ showgrid: false, linecolor: '#EAECF0', tickcolor: '#EAECF0', color: '#667085' }};
const AXIS_Y = {{ gridcolor: '#EAECF0', zerolinecolor: '#EAECF0', color: '#667085' }};
const FONT = {{ family: 'Inter, sans-serif', size: 12, color: '#344054' }};
const config = {{ displayModeBar: false, responsive: true }};
const numberFormat = new Intl.NumberFormat('en-US');
const currencyWhole = new Intl.NumberFormat('en-US', {{ style: 'currency', currency: 'USD', maximumFractionDigits: 0 }});
const currencyCents = new Intl.NumberFormat('en-US', {{ style: 'currency', currency: 'USD', minimumFractionDigits: 2, maximumFractionDigits: 2 }});
const dateFormat = new Intl.DateTimeFormat('en-US', {{ month: 'short', day: '2-digit', year: 'numeric', timeZone: 'UTC' }});

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

const parseDate = value => new Date(`${{value}}T00:00:00Z`);
const formatDate = value => dateFormat.format(parseDate(value));
const baseRows = () => DATA.rows.filter(row => (
  (state.plan === 'all' || row.plan === state.plan)
  && (state.month === 'all' || row.signup_date.startsWith(state.month))
));
const metricRows = rows => state.country ? rows.filter(row => row.country === state.country) : rows;

const mrrSeries = rows => {{
  const weeklyMrr = new Map();
  rows.forEach(row => {{
    const date = parseDate(row.signup_date);
    const mondayOffset = (date.getUTCDay() + 6) % 7;
    date.setUTCDate(date.getUTCDate() - mondayOffset + 6);
    const week = date.toISOString().slice(0, 10);
    weeklyMrr.set(week, (weeklyMrr.get(week) || 0) + row.mrr);
  }});
  let cumulative = 0;
  return [...weeklyMrr.entries()]
    .sort(([first], [second]) => first.localeCompare(second))
    .map(([date, value]) => {{
      cumulative += value;
      return {{ date, value: cumulative }};
    }});
}};

const renderKpis = rows => {{
  const totalMrr = rows.reduce((sum, row) => sum + row.mrr, 0);
  const averageMrr = rows.length ? totalMrr / rows.length : 0;
  document.getElementById('total-mrr').textContent = currencyWhole.format(totalMrr);
  document.getElementById('total-users').textContent = numberFormat.format(rows.length);
  document.getElementById('avg-mrr').textContent = currencyCents.format(averageMrr);
  if (rows.length) {{
    const firstDate = rows.reduce((earliest, row) => row.signup_date < earliest ? row.signup_date : earliest, rows[0].signup_date);
    const lastDate = rows.reduce((latest, row) => row.signup_date > latest ? row.signup_date : latest, rows[0].signup_date);
    document.getElementById('page-subtitle').textContent = `${{formatDate(firstDate)}} — ${{formatDate(lastDate)}} · ${{numberFormat.format(rows.length)}} signups`;
  }} else {{
    document.getElementById('page-subtitle').textContent = 'No signups match the selected filters';
  }}
}};

const countryClickHandler = event => {{
  const country = event.points && event.points.length ? event.points[0].y : null;
  if (!country) return;
  state.country = state.country === country ? null : country;
  renderDashboard();
}};
const countryHoverHandler = event => {{
  const chart = document.getElementById('chart-country');
  chart.style.cursor = event.points && event.points.length ? 'pointer' : 'default';
}};
const countryUnhoverHandler = () => {{
  document.getElementById('chart-country').style.cursor = 'pointer';
}};
const bindCountryChart = () => {{
  const chart = document.getElementById('chart-country');
  if (!chart || typeof chart.on !== 'function') return;
  if (typeof chart.removeListener === 'function') {{
    chart.removeListener('plotly_click', countryClickHandler);
    chart.removeListener('plotly_hover', countryHoverHandler);
    chart.removeListener('plotly_unhover', countryUnhoverHandler);
  }}
  chart.on('plotly_click', countryClickHandler);
  chart.on('plotly_hover', countryHoverHandler);
  chart.on('plotly_unhover', countryUnhoverHandler);
  chart.style.cursor = 'pointer';
}};

const renderCountryChart = rows => {{
  const counts = new Map();
  rows.forEach(row => counts.set(row.country, (counts.get(row.country) || 0) + 1));
  const countries = [...counts.entries()].sort(([first, firstCount], [second, secondCount]) => (
    secondCount - firstCount || first.localeCompare(second)
  ));
  const countryNames = countries.map(([country]) => country);
  const countryValues = countries.map(([, count]) => count);
  const countryColors = countryNames.map(country => (
    state.country && country !== state.country ? '#D0D5DD' : DATA.PRIMARY
  ));
  const chart = document.getElementById('chart-country');
  const countryAriaLabel = countryNames.map((country, index) => `${{country}}: ${{countryValues[index]}} users`).join(', ');
  const selectedCountryAria = state.country ? ` Selected country: ${{state.country}}.` : '';
  chart.setAttribute('aria-label', `${{countryAriaLabel}}.${{selectedCountryAria}}`);

  const result = Plotly.react('chart-country', [{{
    x: countryValues,
    y: countryNames,
    type: 'bar',
    orientation: 'h',
    marker: {{ color: countryColors }},
    text: countryValues.map(String),
    textposition: 'outside',
    cliponaxis: false,
    textfont: {{ ...FONT }},
    hovertemplate: '<b>%{{y}}</b><br>%{{x}} users<extra></extra>',
  }}], layoutFor('linear', 'category', {{
    margin: {{ l: 120, r: 40, t: 8, b: 32 }},
    xaxis: {{ ...AXIS_X, type: 'linear', showticklabels: false, rangemode: 'tozero' }},
    yaxis: {{ ...AXIS_Y, type: 'category', automargin: true, autorange: 'reversed' }},
  }}), config);
  if (result && typeof result.then === 'function') result.then(bindCountryChart);
  else bindCountryChart();
}};

const renderCharts = rows => {{
  const series = mrrSeries(rows);
  Plotly.react('chart-mrr', [{{
    x: series.map(point => point.date), y: series.map(point => point.value),
    type: 'scatter', mode: 'lines', fill: 'tozeroy',
    line: {{ color: DATA.PRIMARY, width: 2.5 }},
    fillcolor: 'rgba(127, 86, 217, 0.08)',
    hovertemplate: '%{{x|%b %d, %Y}}<br><b>$%{{y:,.0f}}</b><extra></extra>',
  }}], layoutFor('date', 'linear', {{
    yaxis: {{ ...AXIS_Y, type: 'linear', tickprefix: '$', separatethousands: true }},
  }}), config);

  const planCounts = DATA.plan_options.map(plan => rows.filter(row => row.plan === plan).length);
  Plotly.react('chart-plan', [{{
    x: DATA.plan_options, y: planCounts, type: 'bar', marker: {{ color: DATA.PRIMARY }},
    text: planCounts.map(String), textposition: 'outside', cliponaxis: false,
    textfont: {{ ...FONT }}, hovertemplate: '<b>%{{x}}</b><br>%{{y}} users<extra></extra>',
  }}], layoutFor('category', 'linear', {{
    yaxis: {{ ...AXIS_Y, type: 'linear', showticklabels: false, rangemode: 'tozero' }},
  }}), config);

  const seats = DATA.plan_options.map(plan => rows
    .filter(row => row.plan === plan)
    .reduce((sum, row) => sum + row.seats, 0));
  const seatColors = DATA.plan_options.map((_, index) => DATA.COLORWAY[(index + 2) % DATA.COLORWAY.length]);
  Plotly.react('chart-seats', [{{
    x: DATA.plan_options, y: seats, type: 'bar', marker: {{ color: seatColors }},
    text: seats.map(String), textposition: 'outside', cliponaxis: false,
    textfont: {{ ...FONT }}, hovertemplate: '<b>%{{x}}</b><br>%{{y}} seats<extra></extra>',
  }}], layoutFor('category', 'linear', {{
    yaxis: {{ ...AXIS_Y, type: 'linear', showticklabels: false, rangemode: 'tozero' }},
  }}), config);
}};

const renderDashboard = () => {{
  const rowsForPlansAndMonths = baseRows();
  const availableCountries = new Set(rowsForPlansAndMonths.map(row => row.country));
  if (state.country && !availableCountries.has(state.country)) state.country = null;
  const rowsForMetrics = metricRows(rowsForPlansAndMonths);
  renderKpis(rowsForMetrics);
  renderCharts(rowsForMetrics);
  renderCountryChart(rowsForPlansAndMonths);
}};

document.getElementById('plan-filter').addEventListener('change', event => {{
  state.plan = event.target.value;
  renderDashboard();
}});
document.getElementById('month-filter').addEventListener('change', event => {{
  state.month = event.target.value;
  renderDashboard();
}});

renderDashboard();
</script>
</body>
</html>
"""

out = ROOT / "index.html"
out.write_text(html, encoding="utf-8")
print(f"Wrote {out}")
