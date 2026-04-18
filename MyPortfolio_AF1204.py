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


# Cell 1: Page Header 
@app.cell
def _(mo):
    mo.md(r"""
    ---
    ## Personal Portfolio Webpage
    AF1204 · Mohsin Ali Imran Rashid · BSc Accounting & Finance · Bayes Business School
    """)
    return


# Cell 2: Core Imports 
@app.cell
def _():
    import marimo as mo
    import pandas as pd

    # micropip is the package installer for the WASM/Pyodide environment.
    # On a local desktop run it is unavailable, so we handle the ImportError.
    try:
        import micropip as micropip
    except ImportError:
        micropip = None     # local run — packages already installed via pip

    return micropip, mo, pd


# Cell 3: Data Loading 
@app.cell
def _(pd):
    csv_url = (
        "https://gist.githubusercontent.com/DrAYim/"
        "80393243abdbb4bfe3b45fef58e8d3c8/raw/"
        "ed5cfd9f210bf80cb59a5f420bf8f2b88a9c2dcd/"
        "sp500_ZScore_AvgCostofDebt.csv"
    )

    try:
        # WASM / Pyodide (GitHub Pages) — cannot call pd.read_csv(url) directly
        from io import StringIO as _StringIO
        from pyodide.http import open_url as _open_url
        df_final = pd.read_csv(_StringIO(_open_url(csv_url).read()))
    except ImportError:
        df_final = pd.read_csv(csv_url)     # local desktop

    df_final = df_final.dropna(subset=["AvgCost_of_Debt", "Z_Score_lag", "Sector_Key"])
    df_final = df_final[df_final["AvgCost_of_Debt"] < 5]

    # Feature engineering
    df_final["Debt_Cost_Percent"] = df_final["AvgCost_of_Debt"] * 100
    df_final["Market_Cap_B"]      = df_final["Market_Cap"] / 1e9

    return (df_final,)


# Cell 4: UI Controls 
@app.cell
def _(df_final, mo):
    all_sectors = sorted(df_final["Sector_Key"].unique().tolist())

    # Scatter-tab controls
    sector_dropdown = mo.ui.multiselect(
        options=all_sectors, value=all_sectors[:4], label="Filter by Sector",
    )
    cap_slider = mo.ui.slider(
        start=0, stop=200, step=10, value=0, label="Min Market Cap ($ Billions)",
    )

    # Sector deep-dive control
    sector_box_select = mo.ui.multiselect(
        options=all_sectors, value=all_sectors[:6], label="Select Sectors to Compare",
    )

    # LLM Prompt Builder (Week 8)
    persona_input = mo.ui.text(value="financial analyst", label="Persona")
    task_input    = mo.ui.text(value="assess the credit risk of a given company", label="Task")
    context_input = mo.ui.text_area(
        value="Company: Apple Inc.  |  Sector: Technology  |  Z-Score: 3.4  |  Year: 2023",
        label="Context (grounding data — RAG simulation)",
        rows=2,
    )
    temperature_slider = mo.ui.slider(
        start=0.0, stop=1.0, step=0.1, value=0.2, label="Temperature",
    )

    # Week 9 addition: Groq API key input (free tier at console.groq.com)
    api_key_input = mo.ui.text(
        value="",
        label="Groq API Key (free at console.groq.com — no credit card needed)",
        placeholder="gsk_...",
        kind="password",
    )

    return (
        all_sectors, api_key_input, cap_slider, context_input,
        persona_input, sector_box_select, sector_dropdown,
        task_input, temperature_slider,
    )


# Cell 5: Reactive Data Filter 
@app.cell
def _(cap_slider, df_final, sector_dropdown):
    """
    Re-runs automatically whenever the sector dropdown or cap slider changes.
    marimo tracks these UI elements as reactive dependencies.
    """
    filtered_portfolio = df_final[
        (df_final["Sector_Key"].isin(sector_dropdown.value)) &
        (df_final["Market_Cap_B"] >= cap_slider.value)
    ]
    count             = len(filtered_portfolio)
    avg_cost_filtered = filtered_portfolio["Debt_Cost_Percent"].mean()
    return avg_cost_filtered, count, filtered_portfolio


# Cell 6: Install & Import Plotly (WASM-safe) 
@app.cell
async def _(micropip):
    if micropip is not None:
        await micropip.install("plotly")
    import plotly.express as px
    return (px,)


# Cell 7: CV Download Button 
@app.cell
def _(mo):
    import base64
    _CV_B64 = "UEsDBBQABgAIAAAAIQAykW9XZgEAAKUFAAATAAgCW0NvbnRlbnRfVHlwZXNdLnhtbCCiBAIooAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC0lMtqwzAQRfeF/oPRtthKuiilxMmij2UbaPoBijRORPVCo7z+vuM4MaUkMTTJxiDP3HvPCDGD0dqabAkRtXcl6xc9loGTXmk3K9nX5C1/ZBkm4ZQw3kHJNoBsNLy9GUw2ATAjtcOSzVMKT5yjnIMVWPgAjiqVj1YkOsYZD0J+ixnw+17vgUvvEriUp9qDDQcvUImFSdnrmn43JBEMsuy5aayzSiZCMFqKRHW+dOpPSr5LKEi57cG5DnhHDYwfTKgrxwN2ug+6mqgVZGMR07uw1MVXPiquvFxYUhanbQ5w+qrSElp97Rail4BId25N0Vas0G7Pf5TDLewUIikvD9Jad0Jg2hjAyxM0vt3xkBIJrgGwc+5EWMH082oUv8w7QSrKnYipgctjtNadEInWADTf/tkcW5tTkdQ5jj4grZX4j7H3e6NW5zRwgJj06VfXJpL12fNBvZIUqAPZfLtkhz8AAAD//wMAUEsDBBQABgAIAAAAIQAekRq37wAAAE4CAAALAAgCX3JlbHMvLnJlbHMgogQCKKAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAArJLBasMwDEDvg/2D0b1R2sEYo04vY9DbGNkHCFtJTBPb2GrX/v082NgCXelhR8vS05PQenOcRnXglF3wGpZVDYq9Cdb5XsNb+7x4AJWFvKUxeNZw4gyb5vZm/cojSSnKg4tZFYrPGgaR+IiYzcAT5SpE9uWnC2kiKc/UYySzo55xVdf3mH4zoJkx1dZqSFt7B6o9Rb6GHbrOGX4KZj+xlzMtkI/C3rJdxFTqk7gyjWop9SwabDAvJZyRYqwKGvC80ep6o7+nxYmFLAmhCYkv+3xmXBJa/ueK5hk/Nu8hWbRf4W8bnF1B8wEAAP//AwBQSwMEFAAGAAgAAAAhANEwDRBtCQAAA2MAABEAAAB3b3JkL2RvY3VtZW50LnhtbOxd23LbuBm+70zfAaOLTjJjWyRFUoeuvdUx652ko4my02uYhCSsSYALgJbV6cW+w/YJ+yT9AVJnxaWVOE0iZMYiicMH8Ce+78eJzA8/PqYJeiBCUs6ua+6VU0OERTymbHZd++XD6LJVQ1JhFuOEM3JdWxJZ+/Hmz3/6YdGJeZSnhCkEEEx2Fll0XZsrlXXqdRnNSYrlVUojwSWfqquIp3U+ndKI1BdcxHXPcR1zlgkeESmhvD5mD1jWSrjosRpaLPACMmtAvx7NsVDkcYPhPhskqLfrrUMg7wQguEPPPYRqPBsqrOtaHQD5JwFBrQ6QgtOQjtxceBqSd4jUPA2pcYjUOg3poDmlhw2cZ4RB5JSLFCu4FLN6isV9nl0CcIYVvaMJVUvAdMIVDKbs/oQaQa41QtqIn43QrKc8JkkjXqHw61ouWKfMf7nOr6veKfKXh3UOklQrFopr18mjSqRa5RVVbFdkH5TCYqxWFyQBO3Im5zRbq0N6KhpEzlcgD08Z4CFNVukWmVuRah+TtkHxGDaAVapfPrs0KWr+NKLrVHiaGmKdo0oVdstc1SSFFrwp+CTTbBnXrSg+KwDvACCMSEVnscJolRj1aMNujUMr0mqFUzwVjUM3hnUrauB+ZbYA4vxZEF5jVQ990Nm3sGSs4vnz4FbPqK7zYoXnWK5JUyBOKwrBCtHfQiwaWMKjtZ5pTPI8owVrwGW69Qyz2acR9Y3gebZBo5+GdruR7IXuPD0DqyT8tgjJT6vMZI4zUPI06tzOGBf4LoEaAX0RMBCZJ6B/oSHrgzkljyZct5/yZJrokzhHWhJrN9AJvOPxUh8ziPA7GRb4FjjkBY7T7ftuzYSCC1U6tFn+g9AOdDjj99c1x/H7rtsM1kEDMsV5og5jxltBpsCx0AeZ4QhuDhLdEWhYcEuu4+g8xWU3V7xMAjE6HE8VEetU5uowUUL14/J8k0ZfvM+1tTAkrNV1sb9GEPGAgQURuBYiilCeK5347UOyinWLCFFUVow4U1IXKyMKbesDTYlEfycL9J6nmOnCCJaqKyk+GjnvMnk8WyQPg03Jd8VvX5rjPRFsVTWnSCD/uQpohKuQvq7jTliCjY03tSPs8k3PxMEDTugMq1xA6frKZGQwWtDR9fLm6+snJlaPeiz2Hqm10qKjbt7xOdAVdROKblOBGXoP6ktjnUYVKQtrHrIubIStZhh0d1nXaLfdRtDyLOu+XHs60oK+cwa9xB1Dg9fOz7Q2aAcZJCbigdRKilwZevwtgvHVFY6u8nu0wxEwl+B8OhTaXGqZAcJM4HSiYExXto/zsePNvxBymoHrhV6jHQZVDDVkcQlyRGrcoe+Oho3GrtRAULvn+TrUSo118NbBH6XiWPApTUgFh97oe85gYFy37Ub/X9uPdeifq/WPKMMsIkiqPNaLB1ihPnjwC/QLo2YdQi0Rn6K3nMUcKkDVHM0xi+UlXJHHjAhKdHboId/l8YwoaG0XaGpAKU6QIBGMei/vCclMDGRFEZcKKYGjewi6QhMlONwIZjhZKhpBJp2I5Slg6yt5T5NElkXT2RyqqKCmFCqgOIqJwjQBFEI0HMJl4bpK0ILNNKVON8NQxQwKLYqgLM6lEsute7iqoAB+dxB0Ry3N9S0F8J2+0wuDwVMKsNOUrCxY52utpNk2jPPILCdUIJ/j9Xrtbhjukq+K+/3+yGdd71fEl8/ChN4kQt0o4jnTPhT9BafZX1HpnffGh1+jkV7GLHfCIKmbj/dJrG0mJFPIc7wA/ef3P9AQOjSRIrEOaVVQ1abnDkcwrrGqalX1+1PVEehpbDoYCMb5eh4ttWp6c8tgRFRIqhXRwiQ/Y7bR0J/zZGmurF0m+d2v4E9kZ6tzcoF6uQRRlfICvcNKL37DqBouhhFnPC1O2Syhcl7BAbnecDRoBue2OG19zffma970J0NpFeMnnhI0ieacJyS+QGN8T/WO5bM3zPG1042+aiXdCCcMdkScbyvtT2BGLsBlvyG6I5PN4bQP2kv1PObF/1xslRlJkjNdbR3PlxK8UiUTPbnO6gfNXrc3aO/6Kq836reGoR0s2WleO817fJp3vcpSoUPotFqh3z1lmdWSzPYSv/Ze4mrBtSul6RcpGHH+G3UTNMrFbzAI/SByqWwvshyPN8x4fKy7S2zXKse1w/OGgTvq+7va4Xq9YbvXf3Ij1GfRDpanxQlNNsuipXUg7jZehZml0vpWBqs6Z6o6L6Uz7zBlCv5IfLAdQ5odFmYHBsRSFukRmw7SmyGYJLsd5Y/0hHuOE7ru3qxNIwi7gedsCGSJZon2nROtcORAJLNDab0LyhAq5YzCoF1fGm7FVANWoFfYard6XmNvoOl3B+2gP9Shll6WXudBL70vUO54Mf0OpN7TJ/Ms40KhmERUfzDhMsV6D2AV7+WPul5zMNqllx1iWpK87B3fFb9ffIj5qs+ZVCKP9Er4azPi/DAnaMzp3qjqnLRlPdbs5rNTxpp+b9BqhoO9eSpn1B/6btB6cRGp7KM966Ot/Lyo4EwKRwxOeuslgJ1t/sXOf8oeOAVh2rwFX4Vm3aDhNQZ7e+6bIfSF2+2hpZml2flM6TA82+0Jlx/TKXa47b43Y3rJOIpygRVJlhWY1nTCftNt7m8F7Q97jV7XNL6PMc2SypLqGyXV7vRNjJeXil/CYf0eGc+IKL54VYFCodsL2w1Xt6MtCoU9PwhH3svP21h2nCk77orfr2Kxf2Je2KxAlqDt+iMv1I36mbMwlheWF5+HF5+lxX8g0ZzpTldnp9WflSM9vr0RDR8jkqBXwLI0T7C8KLqlXMwwo9K41dcX6B9c6J2ifEGEnZL6qm/7y/CpD5psqbRPpWJaVw/7zLcSoNt6cexbCBdIEZwuuLjXczBpmmtlqviKddgedmG8t9d9bY5cv9f2n5zStB7ZeuRvrqf6FkByPKu04cVpB81hEJzbx38sNb51dwK9LvWesJgIEo+hsfcEwfcGXN2UL5ugV6Mkh4f++rw7Xvre9Vs3x81xXBaa/abTBWmoIgsDr222HBzKQhFTiB2J1Hht+K1YU/ZsotVxAZx22/oT9mBCOA9bjVaRO5u9wzqz4hmE+wXbBZ3N1ebyjivF0811QqZbsXOCY60mTcf4+ynnRlzKy1muzGVp+YjrLzOt+io6jQmOefRG6C8XG6EZUxXNtXKbTPXVLZrT4nvF9c3/XnHzXwAAAP//AwBQSwMEFAAGAAgAAAAhALO+ix0FAQAAtgMAABwACAF3b3JkL19yZWxzL2RvY3VtZW50LnhtbC5yZWxzIKIEASigAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAArJPNasMwEITvhb6D2HstO21DCZFzKYFcW/cBZHv9Q/VjpE1av31FShKHBtODjjNiZ76F1XrzrRU7oPO9NQKyJAWGprJ1b1oBH8X24QWYJ2lqqaxBASN62OT3d+s3VJLCkO/6wbOQYryAjmhYce6rDrX0iR3QhJfGOi0pSNfyQVafskW+SNMld9MMyK8y2a4W4Hb1I7BiHPA/2bZp+gpfbbXXaOhGBfdIFDbzIVO6FknAyUlCFvDbCIuoCDQqnAIc9Vx9FrPe7HWJLmx8IThbcxDLmBAUZvECcJS/ZjbH8ByTobGGClmqCcfZmoN4ignxheX7n5OcmCcQfvXb8h8AAAD//wMAUEsDBBQABgAIAAAAIQBngPy0zgYAAM0gAAAVAAAAd29yZC90aGVtZS90aGVtZTEueG1s7FnNixs3FL8X+j+IuTsej7+XeIM/s012kyXrpOQo2/KM1prRIMm7MSFQklMvhUJaein01kMpDTTQ0Ev/mIWENv0jKmlsz8jWdPOxoaHsGtYj6feefnrv6elZc/Xag5CAE8Q4plHLKV1xHYCiMZ3gyG85d4eDQsMBXMBoAgmNUMtZIO5c2/30k6twRwQoREDKR3wHtpxAiHinWORj2Q35FRqjSI5NKQuhkE3mFycMnkq9ISl6rlsrhhBHDohgKNXenk7xGIGhUunsrpT3ifwXCa46xoQdKdXIkNDYyaykvviCdwkDJ5C0HDnPhJ4O0QPhAAK5kAMtx9V/TnH3anEtRESObEZuoP+WckuByczTcswfrQXdvteolNb6NYCIbVy/oT5rfRoAx2O50oRLFluq1tyGt8RmQMmjRXezXiqb+Iz+8rb+Zq3jVQy8BiWPle01Dpr9XtXAa1DyWN3Ct12v0ywbeA1KHmtb+Eq/Xff6Bl6DAoKj2Ta6Vm80akv0GjKlZM8Kb9Zqbr23hKeoYia6EvlI5MVaCI8pG0iAdi4UOAJiEaMpHEtcOxaUgx7mMYELB8Qwolx2u16pJAOv4nrrj7Y43EEwI510jflWl+ID+JjhWLScG1Krk4G8fPHi7PHzs8e/nT15cvb4F7CP/UBY5PZg5GflXv/49d/ffwH++vWH10+/seN5Fv/q5y9f/f7Hv6kXBq1vn716/uzld1/9+dNTC7zN4CgLH+IQcXALnYI7NJQLtEyARuztJIYBxFmJduRzGEElY0H3RWCgby0ggRZcB5l2vMdkurABr8+PDcJHAZsLbAHeDEIDeEAp6VBmXdNNNVfWCvPIt0/O5lncHQhPbHN3N7zcn8cy7rFNZTdABs1DIl0OfRQhAdQYnSFkEbuPsWHXAzxmlNOpAPcx6EBsNckQj4xoSoX2cCj9srARlP42bHNwD3QosanvoRMTKfcGJDaViBhmvA7nAoZWxjAkWeQ+FIGN5NGCjQ2DcyE97SNCQX+COLfJ3GYLg+5NKPOW1e0HZBGaSCbwzIbch5RmkT066wYwjK2ccRRksZ/xmQxRCA6psJKg5g5RbekHGOW6+x5GhrvP39t3ZRqyB4gamTPblkDU3I8LMoXIprzNQiPFthm2Rkdn7huhvY8QgadwghC4+5kNT2PD5inpG4HMKnvIZpsb0IxV1Y4Ql7WSKm4sjsXcCNkj5NMcPgeLjcSzgFEIWZ7mWzMzZPojJjejLV7JeGakUszUprWTuM1DY325Wg8DaISVanN7vC6Y4b832WNS5vgdZNBby8jE/sa2GUJiTJAGzBBisG9Lt1LEcH8qoraTFptb5abmpk3dUNwoekIcnVMB/TeVj0XiYmoeO/B9qp28hLJZ4+ThNiubLmUT/PEXNj04jw6RPEss0Mu65rKu+d/XNXn7+bKauaxmLqsZu8gHqGbSAkZfA60ue7SWMPfmZ4oJORILgva5Ln243PuTgezUDS20vmiKA/m4nM7A+QzqZ8Co+ByL4CiAsZympGfw+VK1z0FMuSyfdLdVtxog8/CATpb3eKrO0nebUgCKtN+trvtlqSaS3lo9vQhdq9ctX1+2rggo2bchkZnMJFG2kKivOs8hoVd2ISyaFhYNpT6Xhf5aekUeTgCqa/FqJWEkw02G9ET5KZFfeffCPZ1nTHPZnmV5TcX1YjxtkMiEm0kiE4aBPDw2uy/Y183UpQY9ZYptGvXGh/C1SiIbuYFEZgucyj1Xrko1Yxi3nKn82SQfw1jq4ypTQeJHLWcsloZ+l8wSMy56kAcJTA8l6w+xQAwQHMpYz7qBRCm3kldXa/xIyTXdj89y+ivrZDSdorHI6UmbcixRYh19T7Bq0LkkfRRMTsGIzNkdKA1VrZeUASeYi7U1J5hlgju14ka6Wm5F4w1QukUhiQO4PFGyyTyB6+c1ncw6NNPNVZnt5WJGvnLSe5+65wupgUzSzDlA1Klpzx8f7pDPsErzvsEqSd2bua65ynV5p8T7HwgZaulkBjXF2EIt7TWpXWBBkJluHZp5Z8RFnwabUasOiFVdqVtbL7fp6FhGfk9Wq3MiuKYqf7Uw2F29lkwyge5dZZcHAswZbjkP3Wq70vWq3YLbqPYLlXLFLTSq7XKhXa2WS/1qye11vEfSKCIIS9Vk7oH8sU8Wy3f3un/r/X24KrWvjGlYpLoOLmph/f6+5OW/vwdYWuZhzRs0y81OrdAstweFSq/TKDS7tU6hV+vWe4Net9poDh454ESDK+1yt1LrNwq1UrdbqNRcRb/RLNQrnteu1NuNfqX9aGlrufLV98q8mtfuPwAAAP//AwBQSwMEFAAGAAgAAAAhANQuVkp6BAAAIQ0AABEAAAB3b3JkL3NldHRpbmdzLnhtbLRXUXPaOBB+v5n7DwzPR8DGBuIp6QRcmnTCtVNyc8+yLYMGydJIMoTe3H+/lSxh0nCd0E5egrzf7rer1WpXeff+idHODktFeDXtBleDbgdXOS9ItZ52/3pc9CbdjtKoKhDlFZ52D1h139/8/tu7faKw1qCmOkBRqYTl0+5Ga5H0+yrfYIbUFRe4ArDkkiENn3LdZ0hua9HLORNIk4xQog/9cDAYdR0Nn3ZrWSWOosdILrnipTYmCS9LkmP34y3ka/w2JinPa4YrbT32JaYQA6/Uhgjl2djPsgG48SS7H21ix6jX2weDV2x3z2VxtHhNeMZASJ5jpeCAGPUBkqp1HL0gOvq+At9ui5YKzIOBXZ1GHl9GEL4gGOX46TKOiePog+UpDyku4xkdeUib2GD0c8GcEBT1RRTh0Mdhfoz5CZcqdLG5jM6fUd/YIo02SB0rsmEs6WWM0QljU2CU59tTTnxZ0uIj4YG1Z6hehnWmqhvogWQSyaZnuJJmeXK/rrhEGYVwoLQ7UJ0dG535C4dsfuwSP1m5ya1blNQsIPU30NK+cc46+0RgmcO9hn4YDLp9AxT8T65TogRFhy9ojWe8hpYoCVYWhsvGy5VGGhwmSmBKbf/MKUYQ3z5ZS8Sg83lJQ4lLVFP9iLKV5gKUdgjSMA6dx3yDJMo1liuBcmCb80pLTr2eDWgOXVTCJXcWtqe2q1XTn8GiQgwS86znLnmBTWS1JK8/QWNgvQfxqcvvHXGYJ5IU+NEcyEofKF5A8CvyDd9WxadaaQKMtvP+QgQ/CgBXxvNnKKHHg8ALjHQNaXojZ/YkFpSIJZGSy/uqgNJ5M2ekLLEEBwRqbQnlQyTf2zzfYVTAGH8jv7XCf4My3ODhI5Tldsa15uzuIDaQ6187SVvv/dPyhcdIofziK+f6qDqI5kEwdsVn0BYJP4TpB7eH58j/20RpeJ0uziFxEI3jszaTyXgcTs4ht1EUpdE5ZDEYp7PU7dPtjiXmwfBF+pW5Ih3WWMwRyyRBnaV5UvSNRia3M1J5PMPQF/EpsqozD/Z6DaAYonQBh+UBm2iWFNDFUlzaNV0iuW55nYY8K4V+9enIZdojlh8lr0WD7iUSTel7lSCKnCWp9ANhXq7qbOWtKujkJxD01M87afPUpmefaCgl20IekC1Jq4ur3seZK1kqV6bc8BIJ0VRttg6mXUrWGx2YQtPwBe16az+ydeiw0GJhg9kPlJudgbZbtLLQy070hl42bGWRl0WtLPayuJWNvGxkZBvoUxKGxhYukF8aeckp5Xtc3LX4C1GTBLVBAqfNTIHy4o3ADRnV2SX4CQYaLoiGB70gBUPw+AoG4ciYO20YbrzWz3QNZpTFcwbzvHAto//M2Jb4d7GYWZcTKMfVgWXtCLtqAqdEQbsRMO00lx77w2JBBIM3vzfjO2rkw9vFPJwMm5sZxHZKatuR4Ny/4nKGFC4c5k3jxvSf0e0wHV1Hk954MYx610F025vFi7AXh+E8mASzIJqM/3WX1P9vc/MfAAAA//8DAFBLAwQUAAYACAAAACEA0t0Wwz4EAAAAJAAAEgAAAHdvcmQvbnVtYmVyaW5nLnhtbOyZy27bOBSG9wP0HQztE1myLF9Qp2hiZJDBoBigGXRNS7QthBeBpGxnln2ZeYR5rL7CHFKibEetIMtZaKGNKfHwfDz6eT3wx08HSgY7LGTC2cLxbofOALOIxwnbLJy/nx9vps5AKsRiRDjDC+cVS+fT3YffPu7nLKMrLKDhABhMzvdptHC2SqVz15XRFlMkb2kSCS75Wt1GnLp8vU4i7O65iF1/6A3NUyp4hKUEzgNiOySdAhcdmtFigfbgrIGBG22RUPhwZHgXQ8buzJ1WQX4LEHyh71VRo4tRoaujqoCCViCIqkIatyP95OPCdiS/Spq0I42qpGk7UmU60eoE5ylmYFxzQZGCV7FxKRIvWXoD4BSpZJWQRL0CcxhaDErYS4uIwKsk0FF8MWHiUh5jMoothS+cTLB54X9T+uvQ57l/UZQemDTrFrqbufigiFTWVzTRLndf8iijmCmjmiswAR05k9skLXcH2pYGxq2F7OoE2FFi2+1Tr+FS+9XWtsyH4QhsEn4xdpTkkdcTvWGD0dSI0qNJCOd92kgozOBjx62kORHXa7j5WIBfAYQRbnhYWMa0YLjRcXVrTtJwWVlOPiqakxyF9RrugW+DOQHE2UUIf2Tj0IV2P2HJWMXby3B2jFztixTaIlkumpy4brgRWGJwQswnGOFRuZ9pJr5MtHEJfKUnY5hurluovwuepUdach3t6bhl7/Xt6QJWseBPNyF5XTBftyiFnZxG86cN4wKtCEQEy3cAK3BgRkD/wkTWhXnEB1Ov50/xsCb6Ic4Gekt07uAWiFZSCRSpLxkdnL09wVKC2yTA5wLDFVLoyvzC+HmtsLgXGL3oJprCpO52vkMwrTx/Eniz+6HjagvNiEr+xDtMnl9TbNuYWqJr81aKpsTaxv4sXI5H09xCdtqQQGH7MrGUneWt4C77SMvKVUYIVqX/Mxxk1vTj+39l/R+RrSV4XTRP/xImHhCiKG0b6ALUmKcchnHim69zjw0Tpr9fc3IrvGwR25hr+Ci0rQu6KIpHzpTUqssogZn69ZWuODGun0HQs4qEATjGawTC5ZHKf2xkZTCG65pveyudpykKTlE4indYv18tJX8HIb0gqFPSmNtI+cAzkWAx+IL3J3q+rb1WVP/9Rf3x/d93kNX3Sp1+Jqsxt5H1G7TWqaU8EfW87lpJR52VdDqtlVSbuylp0FVJQaI6SY25m5KOuyppMKo9mYy5m5KGXZV0PKw9ooy5m5JOOivppPZ4MuZuSjrtqqRhUHs8GXNXJHXP8gztUZuE6KvrxUnI5H7ph8uRn0d0eRLyMAmDx9mkT0L6JKRPQtrJ2ichfRJSStonIX0S0ichfRLSJyF9EtLRJISZ5IOdJB36z5R5nJm/WnRlEMKtOgy8PAU4S1POhHcNpsLUN7UK0xvOwlkwns3Gv4baDzDQvMxzoLv/AQAA//8DAFBLAwQUAAYACAAAACEAgNsl1ZQQAADiqQAADwAAAHdvcmQvc3R5bGVzLnhtbOxd23LbRhJ936r9B5SekgdbokhRsitKSpLt2LW2o5jy+nkIDEVEIIYLgJaVr9+5AQTZGBA9aDGKd8tVFnHpM4M5fRrTjdtPv3xbJMFXnuWxSM8PBs+PDgKehiKK09vzg883b56dHQR5wdKIJSLl5wcPPD/45ed//uOn+5d58ZDwPJAAaf5yEZ4fzIti+fLwMA/nfMHy52LJU7lxJrIFK+Ridnu4YNndavksFIslK+JpnMTFw+Hx0dH4wMJkXVDEbBaH/JUIVwueFtr+MOOJRBRpPo+XeYl23wXtXmTRMhMhz3N50IvE4C1YnFYwgxEAWsRhJnIxK57Lg7E90lDSfHCkfy2SNcAJDuAYAIxD/g2HcWYxDqVlHSeOcDjjCieOajh+nakBRCsUxPGw7If6o8xrWHlURHMcXMnRobJlBZuzfL6JOEtwiKMaonGwRIR3dUyOG7STCvBhoThchC/f3aYiY9NEIkmvDKRjBRpY/S/5UX/0T/5Nr1fDYn/MEvVDjtrPUrqRCF/xGVslRa4Ws+vMLtol/eeNSIs8uH/J8jCOb2R/ZaOLWLb/9iLN4wO5hbO8uMhj1rhxrn40bgnzorb6Mo7ig0PV4h3PUrn5K5MDf2xW5X9WK0blmivVqY11CUtvy3U8ffbrZb1zetXniVo1lU2dH7Ds2eRCGw5GL5P4lhWrTMYxtaQRTLjLoit5/PxbsWKJ2vnQDoz5Wxuu5faS7uWShbHuFJsVXEa1wfhI9SCJVRA9Pj0rFz6tFJdsVQjbiAYwfyvYQ8CYDHYy9E1MBJZb+ey99DUeTQq54fxAtyVXfn53ncUik1H2/ODFC7tywhfx2ziKeFrbMZ3HEf8y5+nnnEfr9b+/0Y5sV4Rilcrfw9Ox9qIkj15/C/lSxV25NWWK04/KIFF7r+J149r8PyXYwNLWZD/nTJ18gsE2hO4+CuJYWeS1o23GXG0du94L1dBwXw2N9tXQyb4aGu+rodN9NaSlvY+GNMxjNhSnkTyP6P1hMwB1F45DjWgch9jQOA4toXEcUkHjOJSAxnE4OhrH4cdoHIebInAKEbq8sObsQ4e3t+PuPkf44e4+Jfjh7j4D+OHuDvh+uLvjux/u7nDuh7s7evvh7g7WeFwz1QreSZmlRW+VzYQoUlHwQE16e6OxVGLpjJwGT530eEZykAQwJrLZE3FvtJDp5d0eokXqfz4vVOIYiFkwi29VytO74zz9yhOx5AGLIolHCJhxmZQ5RsTHpzM+4xlPQ07p2HSgKhMM0tViSuCbS3ZLhsXTiHj4SkSSoFA5tMyf50okMYFTL1iYif5dE4wsPryP8/5jpUCCy1WScCKsjzQuprH65wYapn9qoGH6ZwYapn9iUOOMaogsGtFIWTSiAbNoRONm/JNq3Cwa0bhZNKJxs2j9x+0mLhId4uuzjkH32t1VItQ1lN79mMS3qa7K9kayNdPgmmXsNmPLeaCq2s2w9WPGtnMpoofghuKcViFRzeu1i6hadpyu+g/oBhqVuCo8InlVeEQCq/D6S+yDnCarCdpbmnxmspoWjaLVSJ1EO2HJykxo+6uNFf09bC2AN3GWk8mgGZbAgz+q6ayikyLyrXvZv2NrrP6y2o5KpN2zkAS9VBdcacLw24clz2Radtcb6Y1IEnHPIzrESZEJ42t1yR9rSjpJ/vViOWd5rHOlDYjup/ry7ovgA1v2PqDrhMUpDW+vny1YnAR0M4i3Nx/eBzdiqdJMNTA0gJeiKMSCDNNWAn/4wqc/0nTwQibB6QPR0V4QlYc02FVMcJIxSCIiQpLTzDiNSc6hGu9f/GEqWBbRoF1n3NyPUnAixAlbLM2kg0BbMi7ey/hDMBvSeP9mWazqQlSiuiEBq5UN89X0Dx72D3UfRUBSGfptVej6o57qams6uP7ThA24/lMEzaY8PSj/JTjYDbj+B7sBR3WwVwnL89h5CdUbj+pwSzzq4+2f/Fk8kYhstkroBrAEJBvBEpBsCEWyWqQ55RFrPMID1njUx0voMhqPoCSn8X7N4oiMDA1GxYQGo6JBg1FxoMFICeh/h04NrP9tOjWw/vfqGDCiKUANjMrPSE//RFd5amBUfqbBqPxMg1H5mQaj8rPhq4DPZnISTHeKqUFS+VwNku5EkxZ8sRQZyx6IIF8n/JYRFEgN2nUmZupJGJGam7gJIFWNOiGcbBs4KpK/8ClZ1xQWZb8IKqIsSYQgqq2tTzjacvPetV1m+kmQ3l24TljI5yKJeOY4JretzJcn5rGM7e7rbnQqe76Pb+dFMJlX1f46zPhop2WZsG+Y7W6waczH9hGZRrMPPIpXi7Kj8GGK8bC7sfboDePysZsW4/VMYsPypKMlbHO823I9S96wPO1oCds862ipdbph2aaHVyy7a3SE0zb/qXI8h/OdtnlRZdzYbJsjVZZNLnja5kUbUgkuwlBdLYDsdNOM276beNz2GBW5UTBycqN01pUbok1gn/jXWJ3ZMUFTt1fdPQHivp5Ed4qcv6+EqdtvXHDq/lDXOzlxSnMeNOIMu1+42ogy7nHsHG7cEJ3jjhuicwByQ3SKRE5zVEhyo3SOTW6IzkHKDYGOVvCMgItW0B4XraC9T7SCKD7RqscswA3ReTrghkALFUKghdpjpuCGQAkVmHsJFaKghQoh0EKFEGihwgkYTqjQHidUaO8jVIjiI1SIghYqhEALFUKghQoh0EKFEGihes7tneZeQoUoaKFCCLRQIQRaqHq+2EOo0B4nVGjvI1SI4iNUiIIWKoRACxVCoIUKIdBChRBooUIIlFCBuZdQIQpaqBACLVQIgRaqedTQX6jQHidUaO8jVIjiI1SIghYqhEALFUKghQoh0EKFEGihQgiUUIG5l1AhClqoEAItVAiBFqq+WNhDqNAeJ1Ro7yNUiOIjVIiCFiqEQAsVQqCFCiHQQoUQaKFCCJRQgbmXUCEKWqgQAi1UCNHmn/YSpes2+wG+6um8Y7/7pSvbqU/1R7nrUMPuUGWv3Fjdn0W4FOIuaHzwcKjzjW4g8TSJhS5ROy6r13H1LRGoC5+/XbU/4VNH7/nSJfsshL5mCsBHXS1BTWXU5vJ1S5Dkjdo8vW4JZp2jtuhbtwSnwVFb0NW6LG9KkacjYNwWZmrGA4d5W7SumcMhbovRNUM4wm2RuWYIB7gtHtcMTwIVnLetTzqO07i6vxQgtLljDeHUjdDmlpCrMhxDYXQlzY3QlT03Qlca3QgoPp0weGLdUGiG3VB+VEOZYan2F6obAUs1RPCiGsD4Uw2hvKmGUH5Uw8CIpRoiYKn2D85uBC+qAYw/1RDKm2oI5Uc1PJVhqYYIWKohApbqnidkJ4w/1RDKm2oI5Uc1nNxhqYYIWKohApZqiOBFNYDxpxpCeVMNofyoBlkymmqIgKUaImCphgheVAMYf6ohlDfVEKqNal1F2aAaxXDNHDcJqxniTsg1Q1xwrhl6ZEs1a89sqYbgmS1BrkrOcdlSnTQ3Qlf23AhdaXQjoPh0wuCJdUOhGXZD+VGNy5aaqPYXqhsBSzUuW3JSjcuWWqnGZUutVOOyJTfVuGypiWpcttREtX9wdiN4UY3LllqpxmVLrVTjsiU31bhsqYlqXLbURDUuW2qiuucJ2QnjTzUuW2qlGpctuanGZUtNVOOypSaqcdlSE9W4bMlJNS5baqUaly21Uo3LltxU47KlJqpx2VIT1bhsqYlqXLbkpBqXLbVSjcuWWqnGZUsfpElM8AqoyYJlRUD3vri3LJ8XrP/LCT+nGc9F8pVHAe2hvkcd5eH9xuevFLb+FKHcv5Bjpt6AXntcKTJvgLWAesd3UfWZKmWsehLYr4fZ1brD9nKtaVEb7miqArfXigcAfv1xK93ClMmj+k2NBmg8VS9GbFivHKJcXzZzNWeZ2bp21XIfK8b1sdy/zPI4KjcfHY2uBoNTe7nVfrzsjvPlR9m+XqcWJD8810vr75pN1TvF5AgMzYfN7GfOzqxqhXlr0/uvSdWSpc620fqROfZHy0fm1MbXdp3avvGduQ3L9Xfm1OrL6jtzoVJ51a83o9Ox9g29s44A5wdM63+9Wt2UIoEu3xiE9WfpyovN9c/SmXW1D8b5OM+x03lsCKJxnuMOzrOpwkf2J/uhvJ3+VIaC78yfhpbduj+ZdT39aej0J3t/B40/DTv40zrMP133Kofc4V67nGgfrnJsp2obX8TU63q6ysjpKvaGHhpXGT1xVzmre0oZ56GnaPnQe0ps/r8yvevrNz094sTpEXZ8aTzi5PvwCK2Spxc7evqA+eZrkw/YtJXGB8ZP3AdGdR9wuoBuYK9B4eSF+rftEOozS2t3uInV53svNF89veHU6Q22BEHjDaffhTeUA/6YAWHP/J85+bezEhr+z54o/7sY1yLYq/6PT9W/Lvy/opgjvnDyb1mh4f/F35T/cogfU/H0jIdysFlo38TuKJzZLypVrwTS31Pa9gXHZ5ccPNpq2C4e3f0uVPm2pc+6vNta8TMVYKejdfa0YpoYquWPd6lytHvlJVVPo2/MQMntVzxJPjCzt1i6d034TMlFbh0c6Rdwbm2fmm9JOO0zfdHBCXC42Rmz2O4n5uuSsXkaxllgVZX1huHWj2b1HemOPhyucjk0E7XDdv82iqfbvbQbg0Gwjj9bAa1RB64wZj3cGcLcQen/dVI0paak6aL0mIhSW6f7H6a0T6kSSampKrooHRJRaguhXSca3Rn+qzL+Olt9qoVItkxhz8XWiIgtW4t8Omztu2KHZMUU11ysnBCxYsf0+9EQOQ+mwOXiYUzEg63J/S3UQV+6QFJiqkwuSk6JKLGFsScqjb+cBFPqcZFwRkSCPQv+LXTxyAn+bkpM9cVFyQsiSuzIP1Fd7KuuZl6BsT3WZm3TEGMLahppTVhDFcZmaKhiGaiImUtkqhomh85Ux9XCp5VyMrYqRDnEqRrCFUvsK/nNyD2BmznWR6SP+lk5LHc8q8Z+PZcu15zY8219dm3W0YlyzWCjl/RVY83V3M7xNLPa/XPWrOHqa9zbBFUbKJRcgrWK2VacUGJOVwvzI07gfVZ24yPXtLGzEMD9wB7SfhPfDUpc5PcV6KYTuTl/4hPHR6asWZnmqwHbzJi1FJrUSG2CPLaTGc+za/32Nb3HH2FpqXJXrtsF2myZW46O1L8urFGnweuhaqSjr0pqnLpZ2CmRvY5cs8uqyyTrD29sj5V+bGG9eZcPw6EY2voZyiFjfUlLXZBSL9Gzrtg2l+voLtVB2zfLVa+72z5s8D48nKM0eATqRLnbO/Z4X5Ydi+bQtvm5lF3u0SXE1Ztri3RDnzxieRnpv+ZCqN4vl55kP7z9p7qnTv2Q/qXiiVafHnbPsnh1yfSRW1IysEe268kJtWTcqqaxs7Hujb6Ca5b0Ln2D/19aBgV+1Oq6fU8HGyLZ4bFPTvetMXL98k3XAK736Bsly0t9qCg5Na3a0cplUEmu2JJm7MAkUjftO6KTIhPpLZy4m9V9B++47+D5niBMJP/Cp+DI7E0vP8htP+48OfS5H8Zninukw6JZvFgVwu5i44gNl3YvvQR32lF/2lFpUrWQBc+Dj/w++CQWTD/mWOZKjRt1yaJxS5jD1fr467WJ8lFXpgdi3RJPn/16qbcNRvIwblmxyiSSWtJ2qUi1tqGDlL/yn/8LAAD//wMAUEsDBBQABgAIAAAAIQAm3vpIbwEAAC0EAAAUAAAAd29yZC93ZWJTZXR0aW5ncy54bWyc091uwiAUAOD7JXuHhnulOjVLYzVZFpfdLEu2PQDCqSUCpwFcdU8/qNXVeGN3Uw7Q8+XwN1/utUq+wTqJJiejYUoSMByFNJucfH2uBo8kcZ4ZwRQayMkBHFku7u/mdVbD+gO8D3+6JCjGZZrnpPS+yih1vATN3BArMGGyQKuZD127oZrZ7a4acNQV83ItlfQHOk7TGWkZe4uCRSE5PCPfaTC+yacWVBDRuFJW7qTVt2g1WlFZ5OBcWI9WR08zac7MaHIFacktOiz8MCymraihQvoobSKt/oBpP2B8Bcw47PsZj61BQ2bXkaKfMzs7UnSc/xXTAcSuFzF+ONURm5jesZzwouzHnc6IxlzmWclceSkWqp846YjHC6aQb7sm9Nu06Rk86HiGmmevG4OWrVWQwq1MwsVKGjh+w/nEpglh34zHbWmDQsUg7NoivF+svNTyB1ZonyzWDiyNw0wprN/fXkKHXjzyxS8AAAD//wMAUEsDBBQABgAIAAAAIQDI7prdgAIAAFIKAAASAAAAd29yZC9mb250VGFibGUueG1s5JVbb5swFIDfJ+0/IN4bLiFXNanWppX2soet054dY4JVX5Dt3P79jg2kpKRVPE17WVCCOfb5sD+Ow+3dgbNgR5SmUizCZBCHARFY5lRsFuHP56ebaRhog0SOmBRkER6JDu+Wnz/d7ueFFEYHkC/0nONFWBpTzaNI45JwpAeyIgI6C6k4MnCpNhFH6mVb3WDJK2TomjJqjlEax+OwwahrKLIoKCYribecCOPyI0UYEKXQJa10S9tfQ9tLlVdKYqI1rJmzmscRFSdMkvVAnGIltSzMABbTzMihID2JXYuzV8DID5D2AGNMDn6MacOIILPLobkfZ3zi0LzD+bPJdAD51guRDtt52JNN77B0bvLSD9c+o8jmIoNKpMtzYsH8iFmHWBcYk/ilyyR+0kYn4JHbZ8jx/OtGSIXWDEhQlQEUVuDA9heejz25Jjm4uNXSNApmG2Bt2ezcYD8XiAPox5GvJXPxCgmpSQJdOwSrj0dwJLGt6Ek8hvMonoSRHYhLpDSxjHpgWocLxCk7ttGcYJisoTtS91bU4LLt3CFF7ULqLk030LHV6xhgzSesIwn8K51H0t6Y4XkEO870PJJ0xsA9o9pCz8Yz5UQH38g++C45Ehe12PIZx0PQkcE3hVZ2WYu701stynF9jDzCnNPHp6dXIw8QmUxH9z0js4+MuMuk5lxv5EFuFSXKOnnHxgQMzJwVayPzssFlTtQlHQU9kPx6F9nwX7j4Ba8I+2rU72yX3ueiiWz197dLu/zuQt4KuWa7JH5CvlRGXpaRxveQm7myqA+fstB7qrWXh9RONZ1Oeh76hfGhh9rCzLMwnIdgRXXF0PF/9NE09PI3AAAA//8DAFBLAwQUAAYACAAAACEAXlBhwXkBAAAFAwAAEQAIAWRvY1Byb3BzL2NvcmUueG1sIKIEASigAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAnJJdT8IwFIbvTfwPS68d3UdCdBkjUYMxkcQoRONdbQ9QWT/SFgb/3m6D4SLeeHdOz3Pec/q2+XgnymALxnIlRygeRCgASRXjcjlC89kkvEaBdUQyUioJI7QHi8bF5UVOdUaVgWejNBjHwQZeSdqM6hFaOaczjC1dgSB24AnpiwtlBHE+NUusCV2TJeAkioZYgCOMOIJrwVB3iuggyWgnqTembAQYxVCCAOksjgcxPrEOjLBnG5rKD1Jwt9dwFj0WO3pneQdWVTWo0gb1+8f4ffr02lw15LL2igIqckYzx10JRY5PoY/s5vMLqGuPu8TH1ABxyhTzh/BRGCKDF2JXnF0FU7WyXDb8kandX8O+UoZZr9TLPMbAUsO182/azukdeLok1k39Iy84sNv93yN/o3W3gS2v/0uRNESX5gfz2zWBBd60rLX4WHlL7+5nE1QkUTIMozRM0ll8naU3WRR91Jv2+k+C4rDAvxWPAq1Z/Y9bfAMAAP//AwBQSwMEFAAGAAgAAAAhAEhkdlN5AQAAzwIAABAACAFkb2NQcm9wcy9hcHAueG1sIKIEASigAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAnFJNT8QgEL2b+B+a3ndp148YM4sxuzEe/Eq26pnAtCVSIIDG/fcOVmuNNznNvJl5vHkAF++DKd4wRO3suqyXVVmglU5p263Lx+ZqcVYWMQmrhHEW1+UeY3nBDw/gITiPIWmMBVHYuC77lPw5Y1H2OIi4pLKlSuvCIBKloWOubbXErZOvA9rEVlV1yvA9oVWoFn4iLEfG87f0X1LlZNYXn5q9Jz4ODQ7eiIT8Lk+apXJpADah0LgkTKMH5BXBUwIPosPIV8DGAJ5dUJHXp0fAxhA2vQhCJnKQ1/Uxdc4AuPTeaCkSmctvtQwuujYV95+Ki0wAbN4CtMUO5WvQaZ+FzFO40ZYU5BvGiLQF0QXhexJ4khVOKeykMLghB3grTERgPwBs3OCFJUI2RUT4Eh9947bZjK+R3+Bsz2ed+p0XkjTUq7NqvvGsBDtCUdEKk4YJgGt6lmDyBTRrO1TfPX8L2cOn8X+S78uKzqdp3xgtPn0c/gEAAP//AwBQSwECLQAUAAYACAAAACEAMpFvV2YBAAClBQAAEwAAAAAAAAAAAAAAAAAAAAAAW0NvbnRlbnRfVHlwZXNdLnhtbFBLAQItABQABgAIAAAAIQAekRq37wAAAE4CAAALAAAAAAAAAAAAAAAAAJ8DAABfcmVscy8ucmVsc1BLAQItABQABgAIAAAAIQDRMA0QbQkAAANjAAARAAAAAAAAAAAAAAAAAL8GAAB3b3JkL2RvY3VtZW50LnhtbFBLAQItABQABgAIAAAAIQCzvosdBQEAALYDAAAcAAAAAAAAAAAAAAAAAFsQAAB3b3JkL19yZWxzL2RvY3VtZW50LnhtbC5yZWxzUEsBAi0AFAAGAAgAAAAhAGeA/LTOBgAAzSAAABUAAAAAAAAAAAAAAAAAohIAAHdvcmQvdGhlbWUvdGhlbWUxLnhtbFBLAQItABQABgAIAAAAIQDULlZKegQAACENAAARAAAAAAAAAAAAAAAAAKMZAAB3b3JkL3NldHRpbmdzLnhtbFBLAQItABQABgAIAAAAIQDS3RbDPgQAAAAkAAASAAAAAAAAAAAAAAAAAEweAAB3b3JkL251bWJlcmluZy54bWxQSwECLQAUAAYACAAAACEAgNsl1ZQQAADiqQAADwAAAAAAAAAAAAAAAAC6IgAAd29yZC9zdHlsZXMueG1sUEsBAi0AFAAGAAgAAAAhACbe+khvAQAALQQAABQAAAAAAAAAAAAAAAAAezMAAHdvcmQvd2ViU2V0dGluZ3MueG1sUEsBAi0AFAAGAAgAAAAhAMjumt2AAgAAUgoAABIAAAAAAAAAAAAAAAAAHDUAAHdvcmQvZm9udFRhYmxlLnhtbFBLAQItABQABgAIAAAAIQBeUGHBeQEAAAUDAAARAAAAAAAAAAAAAAAAAMw3AABkb2NQcm9wcy9jb3JlLnhtbFBLAQItABQABgAIAAAAIQBIZHZTeQEAAM8CAAAQAAAAAAAAAAAAAAAAAHw6AABkb2NQcm9wcy9hcHAueG1sUEsFBgAAAAAMAAwAAQMAACs9AAAAAA=="
    cv_download_btn = mo.download(
        data=base64.b64decode(_CV_B64),
        filename="Mohsin_Ali_Imran_Rashid_CV.docx",
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        label="Download Resume (Word File .docx)",
    )
    return (cv_download_btn,)


# Cell 8: All Visualisations 
@app.cell
def _(count, df_final, filtered_portfolio, mo, pd, px, sector_box_select):
    import numpy as np

    # Plot 1: Credit Risk Scatter with OLS overlay 
    fig_scatter = px.scatter(
        filtered_portfolio,
        x="Z_Score_lag", y="Debt_Cost_Percent",
        color="Sector_Key", size="Market_Cap_B",
        hover_name="Name", hover_data=["Ticker"],
        title=f"Cost of Debt vs. Altman Z-Score ({count} observations)",
        labels={"Z_Score_lag": "Altman Z-Score (lagged)", "Debt_Cost_Percent": "Avg. Cost of Debt (%)"},
        template="presentation", width=900, height=600,
    )
    fig_scatter.add_vline(x=1.81, line_dash="dash", line_color="red",
        annotation=dict(text="Distress Threshold (Z = 1.81)", font=dict(color="red"),
                        x=1.5, xref="x", y=1.10, yref="paper", showarrow=False, yanchor="top"))
    fig_scatter.add_vline(x=2.99, line_dash="dash", line_color="green",
        annotation=dict(text="Safe Threshold (Z = 2.99)", font=dict(color="green"),
                        x=3.10, xref="x", y=1.04, yref="paper", showarrow=False, yanchor="top"))

    # Self-exploration: OLS regression overlay using numpy.polyfit
    _df_r = filtered_portfolio[filtered_portfolio["Debt_Cost_Percent"] < 5]
    if not _df_r.empty:
        _x = _df_r["Z_Score_lag"].astype(float)
        _y = _df_r["Debt_Cost_Percent"].astype(float)
        _slope, _intercept = np.polyfit(_x, _y, 1)
        _xl = np.linspace(_x.min(), _x.max(), 100)
        _yl = _intercept + _slope * _xl
        _trace = px.line(x=_xl, y=_yl).data[0]
        _trace.update(line=dict(width=1.5, color="black", dash="dot"))
        fig_scatter.add_trace(_trace)

    chart_element = mo.ui.plotly(fig_scatter)

    # Plot 2: Box Plot — Sector Deep Dive 
    df_box  = df_final[df_final["Sector_Key"].isin(sector_box_select.value)]
    fig_box = px.box(
        df_box, x="Sector_Key", y="Debt_Cost_Percent", color="Sector_Key",
        points="outliers",
        title="Cost of Debt Distribution by Sector",
        labels={"Sector_Key": "Sector", "Debt_Cost_Percent": "Avg. Cost of Debt (%)"},
        template="presentation", width=900, height=520,
    )
    fig_box.update_layout(showlegend=False, xaxis_tickangle=-45,
                          xaxis_tickfont=dict(size=11), margin=dict(b=120))
    chart_box = mo.ui.plotly(fig_box)

    # Self-exploration: auto summary statistics table via .agg()
    summary_stats = (
        df_box.groupby("Sector_Key")["Debt_Cost_Percent"]
        .agg(Mean="mean", Median="median", Std="std", N="count")
        .round(2).reset_index()
        .rename(columns={"Sector_Key": "Sector"})
    )

    # Plot 3: ESG Keyword Bar Chart (Week 7 pipeline demo data) 
    esg_data = pd.DataFrame({
        "Keyword":        ["carbon","emissions","sustainability","climate",
                           "water","diversity","governance","renewable","net-zero","biodiversity"],
        "Total_Mentions": [842, 761, 694, 580, 423, 390, 355, 310, 278, 196],
        "Category":       ["Environment","Environment","General","Environment",
                           "Environment","Social","Governance","Environment","Environment","Environment"],
    })
    fig_esg = px.bar(
        esg_data.sort_values("Total_Mentions", ascending=True),
        x="Total_Mentions", y="Keyword", color="Category", orientation="h",
        title="ESG Keyword Frequency — Scraped Sustainability Reports (Week 7 Pipeline)",
        labels={"Total_Mentions": "Total Keyword Mentions", "Keyword": ""},
        template="presentation", width=860, height=480,
        color_discrete_map={"Environment":"#2ecc71","Social":"#3498db",
                            "Governance":"#9b59b6","General":"#95a5a6"},
    )
    chart_esg = mo.ui.plotly(fig_esg)

    # Plot 4: Travel Map 
    travel_data = pd.DataFrame({
        "City":           ["London","Karachi","Lahore","Dubai","Istanbul"],
        "Lat":            [51.5,    24.8,     31.5,    25.2,   41.0     ],
        "Lon":            [-0.1,    67.0,     74.3,    55.3,   28.9     ],
        "Visit_Year_str": ["2025",  "2023",   "2022",  "2024", "2023"   ],
    })
    _yrs = sorted(travel_data["Visit_Year_str"].unique(), key=int)
    fig_travel = px.scatter_geo(
        travel_data, lat="Lat", lon="Lon",
        hover_name="City", color="Visit_Year_str",
        category_orders={"Visit_Year_str": _yrs},
        color_discrete_sequence=px.colors.qualitative.Plotly,
        projection="natural earth", title="My Travel Footprint",
        labels={"Visit_Year_str": "Visit Year"},
    )
    fig_travel = fig_travel.update_traces(marker=dict(size=14))

    return chart_box, chart_element, chart_esg, df_box, fig_travel, summary_stats


# Cell 9: Build Prompt (Week 8) 
@app.cell
def _(context_input, persona_input, task_input, temperature_slider):
    """
    Constructs the structured prompt string from the UI controls.
    Separated from the API call cell so the prompt is always visible
    even when no API key is provided.
    """
    _temp  = temperature_slider.value
    _label = (
        "Deterministic" if _temp <= 0.2
        else ("Controlled creativity" if _temp <= 0.5
              else "Highly creative")
    )

    llm_prompt = (
        "## OBJECTIVE_AND_PERSONA\n"
        f"You are a {persona_input.value}. "
        f"Your task is to {task_input.value}.\n\n"
        "## INSTRUCTIONS\n"
        "1. Read the context below carefully.\n"
        "2. Identify the key financial risk signals.\n"
        "3. Provide a structured, evidence-based credit assessment.\n\n"
        "## CONTEXT\n"
        f"{context_input.value}\n\n"
        "## CONSTRAINTS\n"
        "- Do: ground every claim in the provided context.\n"
        "- Don't: speculate beyond the data given.\n"
        "- Don't: hallucinate figures not in the context.\n\n"
        "## OUTPUT_FORMAT\n"
        "Bullet-point summary, maximum 5 points. "
        "End with a one-sentence overall credit verdict."
    )
    prompt_temp_label = _label
    return llm_prompt, prompt_temp_label


# Cell 10: Live LLM API Call — Week 9 
@app.cell
async def _(
    api_key_input, context_input, llm_prompt,
    mo, persona_input, prompt_temp_label, temperature_slider,
):
    """
    Sends the structured prompt to the Groq REST API (Week 9 — programmatic LLM).
    Works in both WASM (GitHub Pages) and local desktop environments.
    - WASM path  : pyodide.http.pyfetch (async HTTP, no requests package needed)
    - Local path : requests (synchronous HTTP, already pip-installed)
    Get a free Groq API key at https://console.groq.com — no credit card required.
    """
    import json as _json

    _key  = api_key_input.value.strip()
    _temp = temperature_slider.value

    if not _key:
        # No key yet — show prompt preview so the student can see what will be sent
        llm_api_out = mo.vstack([
            mo.md("**Generated Prompt (Week 8 template — live API call when key added):**"),
            mo.md(f"```\n{llm_prompt}\n```"),
            mo.callout(mo.md(
                f"**Temperature = {_temp}** → {prompt_temp_label}.  "
                "Enter a free **Groq API key** above to send this prompt live to "
                "`llama-3.1-8b-instant` and display the AI response here. "
                "Get your key at [console.groq.com](https://console.groq.com)."
            ), kind="warn"),
        ])
    else:
        _payload = _json.dumps({
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": llm_prompt}],
            "temperature": float(_temp),
            "max_tokens": 500,
        })
        _headers = {
            "Authorization": f"Bearer {_key}",
            "Content-Type": "application/json",
        }
        try:
            try:
                # WASM / Pyodide path (runs in GitHub Pages browser) 
                from pyodide.http import pyfetch as _pyfetch
                _resp = await _pyfetch(
                    "https://api.groq.com/openai/v1/chat/completions",
                    method="POST",
                    headers=_headers,
                    body=_payload,
                )
                _data = await _resp.json()
            except ImportError:
                #  Local desktop path (synchronous requests) 
                import requests as _req
                _r    = _req.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers=_headers,
                    data=_payload,
                    timeout=30,
                )
                _data = _r.json()

            if "choices" in _data:
                _answer = _data["choices"][0]["message"]["content"]
                _model  = _data.get("model", "llama-3.1-8b-instant")
                llm_api_out = mo.vstack([
                    mo.callout(mo.md(
                        f"**Live AI Response (Week 9 — Groq API)**  ·  "
                        f"Model: `{_model}`  ·  Temperature: `{_temp}`  ·  "
                        f"Persona: *{persona_input.value}*"
                    ), kind="success"),
                    mo.md(_answer),
                    mo.md("---"),
                    mo.md("**Prompt sent:**"),
                    mo.md(f"```\n{llm_prompt}\n```"),
                ])
            else:
                _err = _data.get("error", {}).get("message", str(_data))
                llm_api_out = mo.callout(mo.md(f"**API error:** {_err}"), kind="danger")

        except Exception as _exc:
            llm_api_out = mo.callout(
                mo.md(f"**Connection error:** {_exc}  "
                      "Check your API key or internet connection."),
                kind="danger",
            )

    return (llm_api_out,)


# Cell 11: Tab Layout 
@app.cell
def _(
    api_key_input, avg_cost_filtered, cap_slider,
    chart_box, chart_element, chart_esg,
    context_input, count, cv_download_btn,
    fig_travel, llm_api_out,
    mo, persona_input, sector_box_select,
    sector_dropdown, summary_stats,
    task_input, temperature_slider,
):
    # Tab 1: About Me / CV 
    tab_cv = mo.vstack([
        mo.md("""
### Mohsin Ali Imran Rashid
Mohsin.Imran@city.ac.uk &nbsp;|&nbsp; 07512 623 965 &nbsp;|&nbsp; London, United Kingdom

---

**About Me**

I am a first-year BSc Accounting & Finance student at Bayes Business School, City, University of London — one of the UK's leading finance institutions. Originally from Pakistan, I relocated to London in early 2025 to pursue my undergraduate degree, following the completion of a Foundation Programme at Into City. That transition — moving across cultures, navigating a new academic environment, and managing real professional responsibilities simultaneously — shaped me into someone who is adaptable, self-motivated, and genuinely driven by a desire to grow.

Growing up in Pakistan gave me an early appreciation for the real-world stakes of financial decision-making. I saw firsthand how budgeting constraints, cash flow management, and financial planning shaped outcomes for both families and organisations. That grounding is something I carry into every role and project I take on — finance, to me, is never just numbers on a spreadsheet; it is about the decisions those numbers inform.

---

**Why Finance & Data Science?**

My interest in finance began through my work experience before university. Managing records, tracking expenditures, and building Excel models for two organisations taught me that financial insight is only as good as the systems used to surface it. When I encountered data science tools — Python, Plotly, and eventually LLMs — I immediately saw their potential to transform the way financial analysis is done.

This portfolio is a direct expression of that intersection. Rather than treating AF1204 as a standalone technical module, I approached it as an opportunity to apply data science methods to genuinely meaningful financial questions — specifically, whether a company's Altman Z-Score predicts its future cost of debt. The answer, as the scatter chart in this portfolio shows, is nuanced and sector-dependent, which is exactly the kind of insight that traditional spreadsheet tools struggle to surface at scale.

I intend to carry this dual focus — rigorous financial understanding paired with modern analytical tools — throughout my degree and into my career.

---

**Education**

| Degree | Institution | Period |
|--------|-------------|--------|
| BSc Accounting & Finance | Bayes Business School, City, University of London | Sept 2025 – Expected 2028 |
| Foundation Programme | Into City, London | Jan 2025 – Jul 2025 |

*Key Module:* AF1204 — Introduction to Data Science and AI Tools

During my Foundation Programme I developed strong academic English, quantitative reasoning, and study skills specifically designed to bridge international educational backgrounds with UK university standards. This preparation gave me the confidence to hit the ground running at Bayes — a school consistently ranked among the top finance schools in Europe.

---

**Professional Experience**

**Finance Assistant — Al Furqan Trust** *(Jan 2023 – Present)*

Al Furqan Trust is a non-profit organisation, and working here introduced me to the unique financial pressures that charitable organisations face — tight budgets, accountability to donors, and the need for meticulous record-keeping without the resources of a commercial finance team. My responsibilities included:
- Maintaining financial records and tracking income/expenses across multiple project cycles
- Building and maintaining Excel models to streamline budgeting and expenditure monitoring
- Analysing financial data trends to inform strategic decisions and donor reporting
- Supporting end-of-cycle financial reconciliation across project accounts

This role gave me a strong foundation in disciplined financial record-keeping and taught me to work carefully under conditions where errors carry real consequences.

**Finance Assistant (Construction) — The Point** *(Aug 2023 – Present)*

The Point operates in the construction sector, where financial management is particularly complex due to multi-stage project timelines, fluctuating material costs, and layered contractor invoicing. My work here has been more commercially oriented, giving me exposure to:
- Budgeting and cost tracking across active construction projects
- Invoice processing and supplier payment scheduling
- Financial documentation management across multi-stage reporting cycles
- Identifying cost variances and escalating discrepancies to senior management

Working across both a non-profit and a commercial construction firm has given me an unusually broad perspective on how financial management adapts to organisational context — a perspective I find directly valuable in my academic studies.

---

**Technical Skills**

| Area | Tools & Techniques |
|------|-------------------|
| Programming | Python · pandas · numpy · exception handling · f-strings |
| Visualisation | Plotly Express — scatter (OLS overlay) · box · bar · geo maps |
| Web Scraping | Playwright · PyMuPDF · pytesseract · asyncio |
| AI & LLMs | Prompt Engineering · RAG · Grounding · AI-as-Judge · Groq API |
| Data Sources | yfinance · WRDS (Compustat/CRSP) · GitHub Gist |
| Dev Tools | Marimo · GitHub Codespaces · GitHub Pages (WASM) |
| Office | Excel · Word · PowerPoint |

**Languages:** English (Fluent) · Urdu (Fluent)

---

**Career Goals**

In the short term, I am focused on building a strong academic foundation at Bayes while continuing to develop practical data skills that complement my finance studies. I am particularly interested in roles at the intersection of financial analysis and technology — whether that is fintech, investment analytics, or data-driven corporate finance.

Longer term, I aspire to work in a role where I can apply quantitative methods to strategic financial decisions — the kind of work where knowing how to write a Python pipeline and read a balance sheet are equally valuable. I believe that finance professionals who are genuinely comfortable with data tools will have a significant advantage in the coming decade, and this portfolio is my first step in building that profile.
        """),
        mo.md("---"),
        mo.md("**Download a copy of my full CV:**"),
        cv_download_btn,
    ])

    # Tab 2: Credit Risk Analysis 
    tab_data_content = mo.vstack([
        mo.md("## S&P 500 Credit Risk Analyser"),
        mo.callout(mo.md(
            "Explores whether **last year's Altman Z-Score** predicts **this year's cost of debt** — "
            "directly relevant to my professional finance work. "
            "Extended with a live **OLS regression line** via `numpy.polyfit` (self-exploration)."
        ), kind="info"),
        mo.hstack([sector_dropdown, cap_slider], justify="center", gap=2),
        mo.md(f"**{count}** observations · Avg. cost of debt: **{avg_cost_filtered:.2f}%**"),
        chart_element,
        mo.md("""
**Skills demonstrated:**
- Reactive filtering with `mo.ui.multiselect` + `mo.ui.slider` — **Week 4**
- Altman Z-Score thresholds and financial health logic — **Week 2**
- `px.scatter` with bubble sizing, hover labels, threshold annotations — **Weeks 3–4**
- `numpy.polyfit` OLS regression overlay — **self-exploration**
        """),
    ])

    # Tab 3: Sector Deep Dive 
    tab_sector = mo.vstack([
        mo.md("## Sector Deep Dive: Cost of Debt Distribution"),
        mo.callout(mo.md(
            "Box plots reveal the **spread and outliers** of borrowing costs within each sector. "
            "A summary statistics table updates automatically alongside the chart."
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
- `.agg()` summary table displayed as a Marimo UI element — **self-exploration**
        """),
    ])

    # Tab 4: Pipeline & LLM 
    tab_pipeline = mo.vstack([
        mo.md("## Data Pipeline: Web Scraping & LLM Exploration"),
        mo.md("### Part A — ESG Keyword Analysis (Week 7 Pipeline)"),
        mo.callout(mo.md(
            "The Week 7 three-script pipeline uses **Playwright** to bypass bot detection, "
            "crawls corporate sustainability pages, downloads PDFs, and counts keyword "
            "occurrences using **PyMuPDF** or **pytesseract** OCR."
        ), kind="warn"),
        chart_esg,
        mo.md("""
**Pipeline stages (Week 7):**
- Script 1 — Playwright + User-Agent spoofing, cookie storage (`cookies.json`)
- Script 2 — Recursive web crawling, keyword-filtered URL list
- Script 3 — PDF download · PyMuPDF / pytesseract extraction · download ledger (`df_DL.csv`)
        """),
        mo.md("---"),
        mo.md("### Part B — LLM Prompt Engineering & Live API Call (Weeks 8 & 9)"),
        mo.callout(mo.md(
            "Adjust persona, task, context, and temperature — the structured **Week 8 prompt** "
            "builds reactively. Add a free **Groq API key** to send it live to "
            "`llama-3.1-8b-instant` and display the real AI response — demonstrating **Week 9** "
            "programmatic LLM API usage."
        ), kind="info"),
        api_key_input,
        mo.hstack([persona_input, task_input], justify="start", gap=2),
        context_input,
        temperature_slider,
        llm_api_out,
        mo.md("""
**Skills demonstrated:**
- Prompt template (Persona · Instructions · Context · Constraints · Output Format) — **Week 8**
- Temperature / Top_P hyperparameter awareness — **Week 8**
- RAG concept via grounding context field — **Week 8**
- **Live programmatic LLM API call (Groq REST endpoint, `llama-3.1-8b-instant`)** — **Week 9**
- WASM-safe `pyfetch` (async) with `requests` (local) fallback — **self-exploration**
- Reactive prompt builder — **self-exploration** (Week 4 reactivity applied to LLMs)
        """),
    ])

    # Tab 5: Personal Interests 
    tab_personal = mo.vstack([
        mo.md("## My Hobbies: Travel & Culture"),
        mo.md(
            "Growing up in Pakistan and moving to London for university gave me a strong "
            "cross-cultural perspective. I enjoy travelling and experiencing new environments."
        ),
        mo.ui.plotly(fig_travel),
        mo.md("*`px.scatter_geo` geographic visualisation — **Week 4**.*"),
    ])

    return tab_cv, tab_data_content, tab_personal, tab_pipeline, tab_sector


# Cell 12: Final Assembly & Display 
@app.cell
def _(mo, tab_cv, tab_data_content, tab_personal, tab_pipeline, tab_sector):
    app_tabs = mo.ui.tabs({
        "About Me":             tab_cv,
        "Credit Risk Analysis": tab_data_content,
        "Sector Deep Dive":     tab_sector,
        "Pipeline & LLM":       tab_pipeline,
        "Personal Interests":   tab_personal,
    })
    mo.md(f"""
# **Mohsin Ali Imran Rashid**
*AF1204 Individual Portfolio · BSc Accounting & Finance · Bayes Business School*

---

{app_tabs}
    """)
    return


if __name__ == "__main__":
    app.run()
