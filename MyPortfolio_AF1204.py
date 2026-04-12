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
    all_sectors = sorted(df['Sector_Key'].unique().tolist())

    sector_dropdown = mo.ui.multiselect(
        options=all_sectors, value=all_sectors[:4],
        label="Filter by Sector",
    )
    cap_slider = mo.ui.slider(
        start=0, stop=200, step=10, value=0,
        label="Min Market Cap ($ Billions)",
    )
    sector_box_select = mo.ui.multiselect(
        options=all_sectors, value=all_sectors[:6],
        label="Select Sectors to Compare",
    )
    return all_sectors, cap_slider, sector_box_select, sector_dropdown


@app.cell
def _(cap_slider, df, sector_dropdown):
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
def _(df, mo, px, sector_box_select):
    df_box = df[df['Sector_Key'].isin(sector_box_select.value)]
    fig_box = px.box(
        df_box, x='Sector_Key', y='Debt_Cost_Percent',
        color='Sector_Key', points='outliers',
        title="Cost of Debt Distribution by Sector",
        labels={'Sector_Key': 'Sector', 'Debt_Cost_Percent': 'Avg. Cost of Debt (%)'},
        template='presentation', width=900, height=520,
    )
    fig_box.update_layout(
        showlegend=False,
        xaxis_tickangle=-45,
        xaxis_tickfont=dict(size=11),
        margin=dict(b=120),
    )
    chart_box = mo.ui.plotly(fig_box)

    summary_stats = (
        df_box.groupby('Sector_Key')['Debt_Cost_Percent']
        .agg(Mean='mean', Median='median', Std='std', N='count')
        .round(2).reset_index()
        .rename(columns={'Sector_Key': 'Sector'})
    )
    return chart_box, df_box, summary_stats


@app.cell
def _(mo, pd, px):
    # ── Plot 3: ESG Keyword Bar Chart (Week 7 pipeline output) ────────────────
    esg_data = pd.DataFrame({
        'Keyword':        ['carbon','emissions','sustainability','climate',
                           'water','diversity','governance','renewable',
                           'net-zero','biodiversity'],
        'Total_Mentions': [842, 761, 694, 580, 423, 390, 355, 310, 278, 196],
        'Category':       ['Environment','Environment','General','Environment',
                           'Environment','Social','Governance','Environment',
                           'Environment','Environment'],
    })
    fig_esg = px.bar(
        esg_data.sort_values('Total_Mentions', ascending=True),
        x='Total_Mentions', y='Keyword', color='Category', orientation='h',
        title="ESG Keyword Frequency — Scraped Sustainability Reports",
        labels={'Total_Mentions': 'Total Keyword Mentions', 'Keyword': ''},
        template='presentation', width=860, height=480,
        color_discrete_map={'Environment':'#2ecc71','Social':'#3498db',
                            'Governance':'#9b59b6','General':'#95a5a6'},
    )
    chart_esg = mo.ui.plotly(fig_esg)
    return chart_esg, esg_data, fig_esg


@app.cell
def _(mo):
    # ── LLM Prompt Builder (Week 8) ───────────────────────────────────────────
    persona_input = mo.ui.text(value="financial analyst", label="Persona")
    task_input    = mo.ui.text(value="assess the credit risk of a given company", label="Task")
    context_input = mo.ui.text_area(
        value="Company: Apple Inc.  |  Sector: Technology  |  Z-Score: 3.4  |  Year: 2023",
        label="Context (grounding data)", rows=2,
    )
    temperature_slider = mo.ui.slider(
        start=0.0, stop=1.0, step=0.1, value=0.2, label="Temperature",
    )
    return context_input, persona_input, task_input, temperature_slider


@app.cell
def _(context_input, mo, persona_input, task_input, temperature_slider):
    _temp = temperature_slider.value
    _temp_label = (
        "🎯 Deterministic — best for facts & calculations" if _temp <= 0.2 else
        "✍️ Controlled creativity — good for CVs & reports" if _temp <= 0.5 else
        "🎨 Highly creative / random"
    )
    _prompt = f"""## OBJECTIVE_AND_PERSONA
You are a {persona_input.value}. Your task is to {task_input.value}.

## INSTRUCTIONS
1. Read the context below carefully.
2. Identify key financial risk signals.
3. Provide a structured, evidence-based assessment.

## CONTEXT
{context_input.value}

## CONSTRAINTS
- Do: ground every claim in the provided context.
- Don't: speculate beyond the data given.

## OUTPUT_FORMAT
Bullet-point summary, max 5 points."""

    prompt_preview = mo.vstack([
        mo.callout(mo.md(f"**Temperature = {_temp}** → {_temp_label}"), kind="info"),
        mo.md("**Generated Prompt (Week 8 template):**"),
        mo.md(f"```\n{_prompt}\n```"),
    ])
    return (prompt_preview,)


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
def _(avg_cost_filtered, cap_slider, chart_scatter, mo, obs_count, sector_dropdown):
    tab_finance = mo.vstack([
        mo.md("## 📊 S&P 500 Credit Risk Analyzer"),
        mo.callout(mo.md(
            "Explores whether **last year's Altman Z-Score** predicts **this year's cost of debt**. "
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
    return (tab_finance,)


@app.cell
def _(chart_box, mo, sector_box_select, summary_stats):
    tab_sector = mo.vstack([
        mo.md("## 📈 Sector Deep Dive: Cost of Debt Distribution"),
        mo.callout(mo.md(
            "Box plots reveal the **spread and outliers** of borrowing costs within each sector."
        ), kind="info"),
        sector_box_select,
        chart_box,
        mo.md("**Auto-generated summary statistics** (`groupby().agg()` — self-exploration):"),
        mo.ui.table(summary_stats),
        mo.md("""
**Skills demonstrated:**
- `px.box` with `points='outliers'` — **Week 3**
- Grouped aggregations (mean, median, std, count) — **Week 4** pandas
- Reactive chart + table from one widget — **Week 4** reactivity
- `.agg()` summary table as Marimo UI element — **self-exploration**
        """),
    ])
    return (tab_sector,)


@app.cell
def _(
    chart_esg, context_input, mo,
    persona_input, prompt_preview,
    task_input, temperature_slider,
):
    tab_pipeline = mo.vstack([
        mo.md("## 🌐 Data Pipeline: Web Scraping & LLM Exploration"),
        mo.md("### Part A — ESG Keyword Analysis (Week 7 Pipeline)"),
        mo.callout(mo.md(
            "The Week 7 pipeline uses **Playwright** to bypass bot detection, "
            "crawls corporate sites for sustainability PDFs, downloads them, and counts "
            "keyword occurrences using **PyMuPDF** or **pytesseract** OCR."
        ), kind="warn"),
        chart_esg,
        mo.md("""
**Pipeline stages (Week 7):**
- Script 1 — Playwright + User Agent spoofing, cookie storage
- Script 2 — Recursive web crawling, keyword-filtered URL list
- Script 3 — PDF download, PyMuPDF / pytesseract, download ledger (`df_DL.csv`)
        """),
        mo.md("---"),
        mo.md("### Part B — LLM Prompt Engineering Playground (Week 8)"),
        mo.callout(mo.md(
            "Adjust persona, task, grounding context, and temperature — "
            "the structured prompt updates reactively."
        ), kind="info"),
        mo.hstack([persona_input, task_input], justify="start", gap=2),
        context_input,
        temperature_slider,
        prompt_preview,
        mo.md("""
**Skills demonstrated:**
- Prompt template (Persona, Instructions, Context, Constraints, Output Format) — **Week 8**
- Temperature / Top_P hyperparameter awareness — **Week 8**
- RAG concept via grounding context field — **Week 8**
- Reactive prompt builder — **self-exploration**
        """),
    ])
    return (tab_pipeline,)


@app.cell
def _(mo, tab_about, tab_finance, tab_pipeline, tab_sector):
    portfolio_tabs = mo.ui.tabs({
        "📄 About Me":             tab_about,
        "📊 Credit Risk Analysis": tab_finance,
        "📈 Sector Deep Dive":     tab_sector,
        "🌐 Pipeline & LLM":       tab_pipeline,
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
