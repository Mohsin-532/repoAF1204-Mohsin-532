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
    # Remote gist URL
    csv_url = (
        "https://gist.githubusercontent.com/DrAYim/"
        "80393243abdbb4bfe3b45fef58e8d3c8/raw/"
        "ed5cfd9f210bf80cb59a5f420bf8f2b88a9c2dcd/"
        "sp500_ZScore_AvgCostofDebt.csv"
    )
    df = pd.read_csv(csv_url)

    # Drop rows missing key variables
    df = df.dropna(subset=['AvgCost_of_Debt', 'Z_Score_lag', 'Sector_Key'])

    # Winsorise at 500% cost of debt — removes extreme outliers
    df = df[df['AvgCost_of_Debt'] < 5]

    # Feature engineering — convert to readable percentage
    df['Debt_Cost_Percent'] = df['AvgCost_of_Debt'] * 100
    df['Market_Cap_B']      = df['Market_Cap'] / 1e9

    return (df,)


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
def _(mo, tab_about):
    portfolio_tabs = mo.ui.tabs({
        "📄 About Me": tab_about,
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
