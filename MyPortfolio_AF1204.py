# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo>=0.19.10",
#     "pandas>=2.3.3",
#     "plotly>=6.5.1",
#     "pyarrow>=22.0.0",
#     "pyzmq>=27.1.0",
# ]
# ///

import marimo

__generated_with = "0.19.11"
app = marimo.App()


@app.cell
def _(mo):
    mo.md(r"""
    ---
    ## 🎓 AF1204 — Personal Portfolio Webpage
    Mohsin Ali Imran Rashid · BSc Accounting & Finance · Bayes Business School
    """)
    return


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import micropip
    return micropip, mo, pd


@app.cell
def _(pd):
    # Load & Clean Data 
    csv_url = (
        "https://gist.githubusercontent.com/DrAYim/"
        "80393243abdbb4bfe3b45fef58e8d3c8/raw/"
        "ed5cfd9f210bf80cb59a5f420bf8f2b88a9c2dcd/"
        "sp500_ZScore_AvgCostofDebt.csv"
    )
    df = pd.read_csv(csv_url)
    df = df.dropna(subset=['AvgCost_of_Debt', 'Z_Score_lag', 'Sector_Key'])
    df = df[df['AvgCost_of_Debt'] < 5]
    df['Debt_Cost_Percent'] = df['AvgCost_of_Debt'] * 100
    df['Market_Cap_B']      = df['Market_Cap'] / 1e9
    return (df,)


@app.cell
def _(df, mo):
    # UI Controls 
    all_sectors = sorted(df['Sector_Key'].unique().tolist())

    sector_dropdown = mo.ui.multiselect(
        options=all_sectors, value=all_sectors[:4],
        label="Filter by Sector",
    )
    cap_slider = mo.ui.slider(
        start=0, stop=200, step=10, value=0,
        label="Min Market Cap ($ Billions)",
    )
    return all_sectors, cap_slider, sector_dropdown


@app.cell
def _(cap_slider, df, sector_dropdown):
    # Reactive Filter 
    filtered_df = df[
        (df['Sector_Key'].isin(sector_dropdown.value)) &
        (df['Market_Cap_B'] >= cap_slider.value)
    ]
    obs_count         = len(filtered_df)
    avg_cost_filtered = filtered_df['Debt_Cost_Percent'].mean()
    return avg_cost_filtered, filtered_df, obs_count


@app.cell
async def _(micropip):
    await micropip.install('plotly')
    import plotly.express as px
    return (px,)


@app.cell
def _(filtered_df, mo, obs_count, px):
    # Plot 1: Scatter 
    import numpy as np

    fig_scatter = px.scatter(
        filtered_df,
        x='Z_Score_lag', y='Debt_Cost_Percent',
        color='Sector_Key', size='Market_Cap_B',
        hover_name='Name', hover_data=['Ticker'],
        title=f"Cost of Debt vs. Altman Z-Score  ({obs_count} observations)",
        labels={'Z_Score_lag': 'Altman Z-Score (lagged)',
                'Debt_Cost_Percent': 'Avg. Cost of Debt (%)'},
        template='presentation', width=900, height=560,
    )

    # Distress / safe threshold lines 
    for _x, _col, _label, _xann, _yann in [
        (1.81, 'red',   'Distress (1.81)', 1.5, 1.10),
        (2.99, 'green', 'Safe (2.99)',      3.1, 1.04),
    ]:
        fig_scatter.add_vline(
            x=_x, line_dash='dash', line_color=_col,
            annotation=dict(text=_label, font=dict(color=_col),
                            x=_xann, xref='x', y=_yann, yref='paper',
                            showarrow=False, yanchor='top'),
        )

    # Self-exploration: live OLS regression overlay using numpy.polyfit
    df_reg = filtered_df[filtered_df['Debt_Cost_Percent'] < 5]
    if not df_reg.empty:
        x_r = df_reg['Z_Score_lag'].astype(float)
        y_r = df_reg['Debt_Cost_Percent'].astype(float)
        slope, intercept = np.polyfit(x_r, y_r, 1)
        x_line = np.linspace(x_r.min(), x_r.max(), 100)
        reg_trace = px.line(x=x_line, y=intercept + slope * x_line).data[0]
        reg_trace.update(line=dict(width=1.5, color='black', dash='dot'))
        fig_scatter.add_trace(reg_trace)

    chart_scatter = mo.ui.plotly(fig_scatter)
    return chart_scatter, np


@app.cell
def _(mo):
    tab_about = mo.md("""
### Mohsin Ali Imran Rashid
📧 Mohsin.Imran@city.ac.uk &nbsp;|&nbsp; 📞 07512 623 965

---

**Profile**

Finance student at Bayes Business School with hands-on experience in budgeting,
financial record-keeping, and cost tracking across two professional roles.
Passionate about combining financial analysis with modern data tools — Python, Marimo,
Plotly, and LLMs — to extract actionable insights from large datasets.

---

**Education**

| Degree | Institution | Period |
|--------|-------------|--------|
| BSc Accounting & Finance | Bayes Business School, City, University of London | Sept 2025 – Expected 2028 |
| Foundation Programme | Into City, London | Jan 2025 – Jul 2025 |

*Key Module:* AF1204 — Introduction to Data Science and AI Tools

---

**Experience**

**Finance Assistant — Al Furqan Trust** *(Jan 2023 – Present)*
- Maintained financial records and tracked income/expenses across multiple project cycles
- Built and maintained Excel models to streamline budgeting and expenditure monitoring
- Analysed financial data trends to inform strategic decisions

**Finance Assistant (Construction) — The Point** *(Aug 2023 – Present)*
- Supported budgeting, cost tracking, and invoice processing for construction projects
- Managed financial documentation and ensured numerical accuracy across multi-stage reporting

---

**Technical Skills**

| Area | Tools & Techniques |
|------|--------------------|
| 🐍 Programming | Python · pandas · numpy · exception handling · f-strings |
| 📊 Visualisation | Plotly Express — scatter, box, bar, geo maps |
| 🌐 Web Scraping | Playwright · PyMuPDF · pytesseract · asyncio |
| 🤖 AI & LLMs | Prompt Engineering · RAG · Grounding · AI-as-Judge |
| 🗄️ Data Sources | yfinance · WRDS (Compustat / CRSP) · GitHub Gist |
| 🔧 Dev Tools | Marimo · GitHub Codespaces · GitHub Pages (WASM) |
| 📋 Office | Excel · Word · PowerPoint |

**Languages:** English (Fluent) · Urdu (Fluent)
    """)
    return (tab_about,)


@app.cell
def _(avg_cost_filtered, cap_slider, chart_scatter, mo, obs_count, sector_dropdown, tab_about):
    tab_finance = mo.vstack([
        mo.md("## 📊 S&P 500 Credit Risk Analyzer"),
        mo.callout(mo.md(
            "Explores whether **last year's Altman Z-Score** predicts **this year's cost of debt** — "
            "directly relevant to the budgeting and financial analysis work I do professionally. "
            "Extended with a live **OLS regression line** via `numpy.polyfit` beyond the Week 4 template."
        ), kind="info"),
        mo.hstack([sector_dropdown, cap_slider], justify="center", gap=2),
        mo.md(f"**{obs_count}** observations · Avg. cost of debt: **{avg_cost_filtered:.2f}%**"),
        chart_scatter,
        mo.md("""
**Skills demonstrated:**
- Reactive filtering with `mo.ui.multiselect` + `mo.ui.slider` — **Week 4**
- Altman Z-Score thresholds and financial health logic — **Week 2**
- `px.scatter` with bubble sizing, hover, threshold annotations — **Weeks 3–4**
- `numpy.polyfit` regression overlay — **self-exploration**
        """),
    ])

    portfolio_tabs = mo.ui.tabs({
        "📄 About Me":             tab_about,
        "📊 Credit Risk Analysis": tab_finance,
    })

    mo.md(
        f"""
        # **Mohsin Ali Imran Rashid**
        *AF1204 Individual Portfolio · BSc Accounting & Finance · Bayes Business School*

        ---

        {portfolio_tabs}
        """
    )
    return


if __name__ == "__main__":
    app.run()
