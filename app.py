import json
import re
from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st
import yfinance as yf

COMPANIES_DIR = Path("companies")
MAX_YEARS = 5

# ── Formatting ────────────────────────────────────────────────────────────────

def fmt(value, style="number"):
    if value is None:
        return "N/A"
    try:
        v = float(value)
        if pd.isna(v):
            return "N/A"
    except (TypeError, ValueError):
        return "N/A"

    if style == "pct":
        return f"{v * 100:.1f}%"
    elif style == "large":
        sign = "-" if v < 0 else ""
        av = abs(v)
        if av >= 1e12:
            return f"{sign}${av/1e12:.1f}T"
        elif av >= 1e9:
            return f"{sign}${av/1e9:.1f}B"
        elif av >= 1e6:
            return f"{sign}${av/1e6:.1f}M"
        elif av >= 1e3:
            return f"{sign}${av/1e3:.1f}K"
        return f"{sign}${av:.1f}"
    elif style == "ratio":
        return f"{v:.2f}x"
    elif style == "currency":
        return f"${v:.2f}"
    elif style == "eps":
        return f"${v:.2f}"
    elif style == "yoy":
        return f"{v * 100:+.1f}%"
    return f"{v:,.2f}"


def safe_val(d, *keys):
    for key in keys:
        val = d.get(key) if isinstance(d, dict) else None
        if val is None:
            continue
        try:
            if pd.isna(val):
                continue
        except (TypeError, ValueError):
            pass
        return val
    return None


# ── Frontmatter ───────────────────────────────────────────────────────────────

def parse_frontmatter(md_text):
    if not md_text or not md_text.startswith("---"):
        return {}, md_text
    match = re.match(r"^---\n(.*?)\n---\n", md_text, re.DOTALL)
    if not match:
        return {}, md_text
    body = md_text[match.end():]
    fm = {}
    for line in match.group(1).split("\n"):
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            fm[key] = [i.strip().strip('"').strip("'") for i in inner.split(",")] if inner else []
        else:
            fm[key] = val.strip('"').strip("'")
    return fm, body


def build_frontmatter(ticker, generated, last_checked, fiscal_years):
    fy_list = ", ".join(f'"{fy}"' for fy in fiscal_years)
    return f"---\nticker: {ticker}\ngenerated: {generated}\nlast_checked: {last_checked}\nfiscal_years: [{fy_list}]\n---\n"


def update_frontmatter(md_text, updates):
    if not md_text or not md_text.startswith("---"):
        return md_text
    match = re.match(r"^---\n(.*?)\n---\n", md_text, re.DOTALL)
    if not match:
        return md_text
    body = md_text[match.end():]
    lines = match.group(1).split("\n")
    new_lines = []
    for line in lines:
        if ":" in line:
            key = line.split(":", 1)[0].strip()
            if key in updates:
                new_lines.append(f"{key}: {updates[key]}")
                continue
        new_lines.append(line)
    return "---\n" + "\n".join(new_lines) + "\n---\n" + body


def strip_frontmatter(md_text):
    if not md_text or not md_text.startswith("---"):
        return md_text
    match = re.match(r"^---\n.*?\n---\n", md_text, re.DOTALL)
    return md_text[match.end():] if match else md_text


# ── File I/O ──────────────────────────────────────────────────────────────────

def _md_path(ticker):
    return COMPANIES_DIR / f"{ticker}.md"


def _json_path(ticker):
    return COMPANIES_DIR / f"{ticker}_data.json"


def load_raw_cache(ticker):
    path = _json_path(ticker)
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    return None


def save_raw_cache(ticker, data):
    COMPANIES_DIR.mkdir(parents=True, exist_ok=True)
    with _json_path(ticker).open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def load_cached_md(ticker):
    path = _md_path(ticker)
    if not path.exists():
        return None, None
    md_text = path.read_text(encoding="utf-8")
    fm, _ = parse_frontmatter(md_text)
    return md_text, fm


def save_analysis(ticker, md_text):
    COMPANIES_DIR.mkdir(parents=True, exist_ok=True)
    _md_path(ticker).write_text(md_text, encoding="utf-8")


# ── Data Fetch ────────────────────────────────────────────────────────────────

def fetch_yfinance_data(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol.upper())
    try:
        info = ticker.info
    except Exception as e:
        raise ValueError(f"Could not connect to Yahoo Finance: {e}")
    if not info or info.get("quoteType") is None:
        raise ValueError(f"No data found for '{ticker_symbol}'. Check the symbol and try again.")
    return {
        "info": info,
        "income_stmt": ticker.income_stmt,
        "balance_sheet": ticker.balance_sheet,
        "cashflow": ticker.cashflow,
    }


def _df_col_to_dict(df, col):
    result = {}
    if df is None or df.empty or col is None:
        return result
    for idx in df.index:
        try:
            val = df.loc[idx, col]
            if pd.isna(val):
                result[str(idx)] = None
            else:
                try:
                    result[str(idx)] = float(val)
                except (TypeError, ValueError):
                    result[str(idx)] = str(val)
        except Exception:
            result[str(idx)] = None
    return result


def _find_col_by_year(df, year):
    if df is None or df.empty:
        return None
    for col in df.columns:
        try:
            if col.year == year:
                return col
        except AttributeError:
            pass
    return None


def yfinance_to_cache_format(raw_data):
    info = raw_data["info"]
    income_stmt = raw_data["income_stmt"]
    balance_sheet = raw_data["balance_sheet"]
    cashflow = raw_data["cashflow"]

    if income_stmt is None or income_stmt.empty:
        return {}, info

    info_snapshot_keys = [
        "trailingPE", "forwardPE", "enterpriseToEbitda",
        "priceToSalesTrailing12Months", "priceToBook", "dividendYield",
        "trailingEps", "marketCap", "currentPrice",
    ]
    info_snapshot = {k: info.get(k) for k in info_snapshot_keys}

    cols = sorted(income_stmt.columns, reverse=True)[:MAX_YEARS]
    fiscal_years = {}
    for col in cols:
        date_key = col.strftime("%Y-%m-%d")
        bs_col = _find_col_by_year(balance_sheet, col.year)
        cf_col = _find_col_by_year(cashflow, col.year)
        fiscal_years[date_key] = {
            "income_stmt": _df_col_to_dict(income_stmt, col),
            "balance_sheet": _df_col_to_dict(balance_sheet, bs_col),
            "cashflow": _df_col_to_dict(cashflow, cf_col),
            "info_snapshot": info_snapshot,
        }

    return fiscal_years, info


def merge_data(existing_cache, new_fiscal_years, new_info):
    today = date.today().isoformat()
    ticker = new_info.get("symbol", existing_cache.get("ticker", "") if existing_cache else "")

    if existing_cache is None:
        merged = {
            "ticker": ticker,
            "last_updated": today,
            "fiscal_years": new_fiscal_years,
            "current_info": new_info,
        }
        return merged, sorted(new_fiscal_years.keys(), reverse=True), True

    existing_fys = set(existing_cache.get("fiscal_years", {}).keys())
    new_fys = set(new_fiscal_years.keys())
    added = new_fys - existing_fys

    merged_fys = dict(existing_cache.get("fiscal_years", {}))
    for key in added:
        merged_fys[key] = new_fiscal_years[key]

    merged = {
        "ticker": existing_cache.get("ticker", ticker),
        "last_updated": today,
        "fiscal_years": merged_fys,
        "current_info": new_info,
    }
    return merged, sorted(merged_fys.keys(), reverse=True), len(added) > 0


# ── Compute ───────────────────────────────────────────────────────────────────

def _sorted_fy_keys(cache_data):
    return sorted(cache_data.get("fiscal_years", {}).keys(), reverse=True)[:MAX_YEARS]


def _fy(cache_data, key, stmt):
    return cache_data.get("fiscal_years", {}).get(key, {}).get(stmt, {})


def compute_overview(cache_data):
    info = cache_data.get("current_info", {})
    name = info.get("longName") or info.get("shortName") or "N/A"
    desc = info.get("longBusinessSummary", "")
    if len(desc) > 400:
        desc = desc[:397] + "..."
    return [
        ("Company", name),
        ("Sector", info.get("sector", "N/A")),
        ("Industry", info.get("industry", "N/A")),
        ("Market Cap", fmt(info.get("marketCap"), "large")),
        ("Current Price", f"{info.get('currency','USD')} {fmt(info.get('currentPrice') or info.get('regularMarketPrice'), 'currency')}"),
        ("Description", desc),
    ]


def compute_profitability(cache_data):
    fy_keys = _sorted_fy_keys(cache_data)
    if not fy_keys:
        return {"years": [], "rows": []}
    years = [k[:4] for k in fy_keys]
    rows = []

    def _inc(k):
        return _fy(cache_data, k, "income_stmt")

    def _bs(k):
        return _fy(cache_data, k, "balance_sheet")

    revenues = [safe_val(_inc(k), "Total Revenue") for k in fy_keys]
    rows.append(("Revenue", [fmt(v, "large") for v in revenues]))

    def margin(num_key, rev_list):
        out = []
        for k, rev in zip(fy_keys, rev_list):
            num = safe_val(_inc(k), num_key)
            rv = safe_val(_inc(k), "Total Revenue")
            out.append(num / rv if (num is not None and rv) else None)
        return out

    rows.append(("Gross Margin", [fmt(v, "pct") for v in margin("Gross Profit", revenues)]))
    rows.append(("Operating Margin", [fmt(v, "pct") for v in margin("Operating Income", revenues)]))
    rows.append(("Net Margin", [fmt(v, "pct") for v in margin("Net Income", revenues)]))
    rows.append(("EBITDA Margin", [fmt(v, "pct") for v in margin("EBITDA", revenues)]))

    eps_vals = [safe_val(_inc(k), "Basic EPS", "Basic Earnings Per Share", "Diluted EPS") for k in fy_keys]
    rows.append(("EPS (Basic)", [fmt(v, "eps") for v in eps_vals]))

    roe_vals = []
    for k in fy_keys:
        ni = safe_val(_inc(k), "Net Income")
        eq = safe_val(_bs(k), "Stockholders Equity")
        roe_vals.append(ni / eq if (ni is not None and eq) else None)
    rows.append(("ROE", [fmt(v, "pct") for v in roe_vals]))

    roic_vals = []
    for k in fy_keys:
        ebit = safe_val(_inc(k), "Operating Income")
        tax = safe_val(_inc(k), "Tax Provision")
        pretax = safe_val(_inc(k), "Pretax Income")
        eq = safe_val(_bs(k), "Stockholders Equity")
        debt = safe_val(_bs(k), "Total Debt") or 0
        cash = safe_val(_bs(k), "Cash And Cash Equivalents") or 0
        if ebit is not None and eq:
            tax_rate = abs(tax / pretax) if (tax is not None and pretax) else 0.21
            nopat = ebit * (1 - tax_rate)
            ic = eq + debt - cash
            roic_vals.append(nopat / ic if ic != 0 else None)
        else:
            roic_vals.append(None)
    rows.append(("ROIC", [fmt(v, "pct") for v in roic_vals]))

    return {"years": years, "rows": rows}


def compute_liquidity(cache_data):
    fy_keys = _sorted_fy_keys(cache_data)
    if not fy_keys:
        return {"years": [], "rows": []}
    years = [k[:4] for k in fy_keys]
    rows = []

    def _bs(k):
        return _fy(cache_data, k, "balance_sheet")

    def _inc(k):
        return _fy(cache_data, k, "income_stmt")

    def _cf(k):
        return _fy(cache_data, k, "cashflow")

    cr_vals = []
    for k in fy_keys:
        ca = safe_val(_bs(k), "Current Assets")
        cl = safe_val(_bs(k), "Current Liabilities")
        cr_vals.append(ca / cl if (ca is not None and cl) else None)
    rows.append(("Current Ratio", [fmt(v, "ratio") for v in cr_vals]))

    qr_vals = []
    qr_label = "Quick Ratio"
    has_inventory = False
    for k in fy_keys:
        ca = safe_val(_bs(k), "Current Assets")
        cl = safe_val(_bs(k), "Current Liabilities")
        inv = safe_val(_bs(k), "Inventory")
        if ca is not None and cl:
            if inv is not None:
                has_inventory = True
                qr_vals.append((ca - inv) / cl)
            else:
                qr_vals.append(ca / cl)
        else:
            qr_vals.append(None)
    if not has_inventory:
        qr_label = "Quick Ratio*"
    rows.append((qr_label, [fmt(v, "ratio") for v in qr_vals]))

    rows.append(("Cash & Equivalents", [fmt(safe_val(_bs(k), "Cash And Cash Equivalents"), "large") for k in fy_keys]))
    rows.append(("Total Debt", [fmt(safe_val(_bs(k), "Total Debt"), "large") for k in fy_keys]))

    de_vals = []
    for k in fy_keys:
        debt = safe_val(_bs(k), "Total Debt")
        eq = safe_val(_bs(k), "Stockholders Equity")
        de_vals.append(debt / eq if (debt is not None and eq) else None)
    rows.append(("Debt / Equity", [fmt(v, "ratio") for v in de_vals]))

    ic_vals = []
    for k in fy_keys:
        ebit = safe_val(_inc(k), "Operating Income")
        interest = safe_val(_inc(k), "Interest Expense")
        ic_vals.append(ebit / abs(interest) if (ebit is not None and interest) else None)
    rows.append(("Interest Coverage", [fmt(v, "ratio") for v in ic_vals]))

    fcf_vals = []
    for k in fy_keys:
        ocf = safe_val(_cf(k), "Operating Cash Flow")
        capex = safe_val(_cf(k), "Capital Expenditure")
        if ocf is not None and capex is not None:
            fcf_vals.append(ocf + capex)
        elif ocf is not None:
            fcf_vals.append(ocf)
        else:
            fcf_vals.append(None)
    rows.append(("Free Cash Flow", [fmt(v, "large") for v in fcf_vals]))

    return {"years": years, "rows": rows}


def _yoy(cur, pri):
    if cur is None or pri is None or pri == 0:
        return None
    try:
        return (float(cur) - float(pri)) / abs(float(pri))
    except (TypeError, ValueError):
        return None


def compute_growth(cache_data):
    fy_keys = _sorted_fy_keys(cache_data)
    if len(fy_keys) < 2:
        return []

    def _inc(k):
        return _fy(cache_data, k, "income_stmt")

    def _cf(k):
        return _fy(cache_data, k, "cashflow")

    def _fcf(k):
        ocf = safe_val(_cf(k), "Operating Cash Flow")
        capex = safe_val(_cf(k), "Capital Expenditure")
        if ocf is not None and capex is not None:
            return ocf + capex
        return ocf

    rows = []
    cur = fy_keys[0]
    for pri in fy_keys[1:]:
        label = f"{cur[:4]} vs {pri[:4]}"
        rows.append((f"Revenue Growth ({label})", fmt(_yoy(safe_val(_inc(cur), "Total Revenue"), safe_val(_inc(pri), "Total Revenue")), "yoy")))
        rows.append((f"Net Income Growth ({label})", fmt(_yoy(safe_val(_inc(cur), "Net Income"), safe_val(_inc(pri), "Net Income")), "yoy")))
        rows.append((f"EPS Growth ({label})", fmt(_yoy(
            safe_val(_inc(cur), "Basic EPS", "Basic Earnings Per Share"),
            safe_val(_inc(pri), "Basic EPS", "Basic Earnings Per Share"),
        ), "yoy")))
        rows.append((f"FCF Growth ({label})", fmt(_yoy(_fcf(cur), _fcf(pri)), "yoy")))
    return rows


def compute_valuation(cache_data):
    info = cache_data.get("current_info", {})
    fy_keys = _sorted_fy_keys(cache_data)
    snap = _fy(cache_data, fy_keys[0], "info_snapshot") if fy_keys else {}

    def gv(key):
        v = info.get(key)
        return v if v is not None else snap.get(key)

    div = gv("dividendYield")
    return [
        ("Trailing P/E", fmt(gv("trailingPE"), "ratio")),
        ("Forward P/E", fmt(gv("forwardPE"), "ratio")),
        ("EV / EBITDA", fmt(gv("enterpriseToEbitda"), "ratio")),
        ("Price / Sales", fmt(gv("priceToSalesTrailing12Months"), "ratio")),
        ("Price / Book", fmt(gv("priceToBook"), "ratio")),
        ("Dividend Yield", fmt(div, "pct") if div is not None else "N/A"),
    ]


# ── Definitions & Benchmarks ──────────────────────────────────────────────────

PROFITABILITY_DEFS = """
### Definitions & Benchmarks

| Metric | What it measures | Healthy | Concerning |
|---|---|---|---|
| Gross Margin | (Revenue − COGS) / Revenue | >40% tech/SaaS; >20% retail | Declining trend or below industry avg |
| Operating Margin | Operating Income / Revenue | >15% most sectors | <5% or compressing YoY |
| Net Margin | Net Income / Revenue | >10% most sectors | Negative or thin and volatile |
| EBITDA Margin | EBITDA / Revenue | >20% tech; >10% industrial | Below cost of capital |
| EPS | Earnings per share | Growing consistently | Declining or highly volatile |
| ROE | Net Income / Shareholders' Equity | >15% sustained | <10% or negative |
| ROIC | NOPAT / Invested Capital | Above WACC (~8–12%) | Below WACC — value being destroyed |

*Benchmarks are general guidelines. Healthy ranges vary significantly by industry.*
"""

LIQUIDITY_DEFS = """
### Definitions & Benchmarks

| Metric | What it measures | Healthy | Concerning |
|---|---|---|---|
| Current Ratio | Current Assets / Current Liabilities | 1.5–3.0x | <1.0x (can't cover short-term obligations) |
| Quick Ratio | (Current Assets − Inventory) / Current Liabilities | >1.0x | <0.5x |
| Debt / Equity | Total Debt / Shareholders' Equity | <1.0x most sectors | >2.0x with thin margins |
| Interest Coverage | EBIT / Interest Expense | >3.0x | <1.5x (earnings barely cover interest) |
| Free Cash Flow | Operating Cash Flow − CapEx | Positive and growing | Persistently negative |

*\\* Quick Ratio shown as Current Ratio where Inventory is unavailable (common for service companies).*
"""

GROWTH_DEFS = """
### Definitions & Benchmarks

| Metric | What it measures | Healthy | Concerning |
|---|---|---|---|
| Revenue Growth | YoY change in total revenue | >10% growth co.; >3% mature | Flat or declining over multiple years |
| Net Income Growth | YoY change in bottom-line earnings | Outpacing revenue growth | Lagging revenue (margin compression) |
| EPS Growth | YoY change in earnings per share | Growing consistently | Declining even if revenue grows |
| FCF Growth | YoY change in free cash flow | Growing; faster than net income | Negative while net income is positive |

*Growth figures compare the most recent fiscal year to each prior year shown.*
"""

VALUATION_DEFS = """
### Definitions & Benchmarks

| Metric | What it measures | Reasonable | Elevated |
|---|---|---|---|
| Trailing P/E | Price / last 12 months EPS | 15–25x market avg | >40x requires very high growth |
| Forward P/E | Price / next 12 months est. EPS | Lower than trailing = growth expected | Forward > Trailing = earnings expected to decline |
| EV / EBITDA | Enterprise Value / EBITDA | 8–15x most sectors | >20x or negative EBITDA (N/A) |
| Price / Sales | Market Cap / Revenue | <2x value; 2–10x growth | >20x requires exceptional growth |
| Price / Book | Market Cap / Book Value | 1–3x mature; higher asset-light | <1x may signal distress |
| Dividend Yield | Annual Dividend / Price | 2–5% typical income stocks | >7% may signal sustainability concern |

*Valuation metrics reflect current market price, not fiscal year-end price.*
"""


# ── Markdown Generation ───────────────────────────────────────────────────────

def _md_table(headers, rows):
    widths = [len(str(h)) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(widths):
                widths[i] = max(widths[i], len(str(cell)))
    fmt_row = lambda cells: "| " + " | ".join(str(c).ljust(widths[i]) for i, c in enumerate(cells)) + " |"
    sep = "| " + " | ".join("-" * w for w in widths) + " |"
    return "\n".join([fmt_row(headers), sep] + [fmt_row(r) for r in rows])


def generate_markdown(cache_data, results):
    today = date.today().isoformat()
    ticker = cache_data.get("ticker", "")
    fy_keys = _sorted_fy_keys(cache_data)

    overview = results["overview"]
    profitability = results["profitability"]
    liquidity = results["liquidity"]
    growth = results["growth"]
    valuation = results["valuation"]

    company_name = next((v for k, v in overview if k == "Company"), ticker)
    fm = build_frontmatter(ticker, today, today, fy_keys)

    lines = [fm, f"# {ticker} — {company_name} Financial Analysis", f"\n*Generated: {today}*\n"]

    lines.append("## Company Overview\n")
    for label, value in overview:
        if label == "Description":
            lines.append(f"\n**Description:** {value}\n")
        else:
            lines.append(f"**{label}:** {value}  ")
    lines.append("")

    lines.append("## Profitability\n")
    if profitability["years"]:
        headers = ["Metric"] + profitability["years"]
        rows = [[m] + v for m, v in profitability["rows"]]
        lines.append(_md_table(headers, rows))
    lines.append(PROFITABILITY_DEFS)

    lines.append("## Liquidity & Solvency\n")
    if liquidity["years"]:
        headers = ["Metric"] + liquidity["years"]
        rows = [[m] + v for m, v in liquidity["rows"]]
        lines.append(_md_table(headers, rows))
    lines.append(LIQUIDITY_DEFS)

    lines.append("## Growth Trends\n")
    if growth:
        lines.append(_md_table(["Metric", "Change"], [[l, v] for l, v in growth]))
    lines.append(GROWTH_DEFS)

    lines.append("## Valuation\n")
    if valuation:
        lines.append(_md_table(["Metric", "Value"], [[l, v] for l, v in valuation]))
    lines.append(VALUATION_DEFS)

    return "\n".join(lines)


# ── Analysis Pipeline ─────────────────────────────────────────────────────────

def run_analysis(cache_data):
    return {
        "overview": compute_overview(cache_data),
        "profitability": compute_profitability(cache_data),
        "liquidity": compute_liquidity(cache_data),
        "growth": compute_growth(cache_data),
        "valuation": compute_valuation(cache_data),
    }


def full_pipeline(ticker, existing_cache=None):
    """
    Fetch → merge → compute → generate MD.
    Returns (md_text, cache_data, is_new_data, error_msg).
    error_msg is None on success; md_text may be non-None even on error (from cache).
    """
    try:
        raw = fetch_yfinance_data(ticker)
        new_fys, new_info = yfinance_to_cache_format(raw)
        cache_data, _, is_new_data = merge_data(existing_cache, new_fys, new_info)
    except ValueError as e:
        return None, existing_cache, False, str(e)
    except Exception as e:
        if existing_cache:
            results = run_analysis(existing_cache)
            md = generate_markdown(existing_cache, results)
            return md, existing_cache, False, f"Live data unavailable — showing cached analysis. ({e})"
        return None, None, False, f"Could not fetch data and no cache exists: {e}"

    results = run_analysis(cache_data)
    md = generate_markdown(cache_data, results)
    return md, cache_data, is_new_data, None


# ── Streamlit UI ──────────────────────────────────────────────────────────────

def _notice(level, msg):
    if level == "success":
        st.success(msg)
    elif level == "warning":
        st.warning(msg)
    else:
        st.info(msg)


def main():
    st.set_page_config(page_title="Company Financial Analysis", page_icon="📊", layout="wide")
    st.title("Company Financial Analysis")
    st.caption("Powered by Yahoo Finance · Data is cached locally and grows richer with each update.")

    col1, col2 = st.columns([4, 1])
    with col1:
        ticker_input = st.text_input(
            "Ticker",
            placeholder="e.g. AAPL, MSFT, TSLA, BRK-B",
            label_visibility="collapsed",
        ).upper().strip()
    with col2:
        submitted = st.button("Analyze", use_container_width=True, type="primary")

    if not ticker_input:
        st.info("Enter a stock ticker symbol above and click **Analyze** to get started.")
        return

    ticker = ticker_input

    # ── Handle new submission ──────────────────────────────────────────────────
    if submitted:
        # Clear stale state for this ticker
        for key in [f"show_prompt_{ticker}", f"display_{ticker}", f"notice_{ticker}",
                    f"fm_{ticker}", f"cache_{ticker}"]:
            st.session_state.pop(key, None)

        md_text, fm = load_cached_md(ticker)
        existing_cache = load_raw_cache(ticker)

        if md_text is not None:
            st.session_state[f"show_prompt_{ticker}"] = True
            st.session_state[f"fm_{ticker}"] = fm
            st.session_state[f"cache_{ticker}"] = existing_cache
        else:
            with st.spinner(f"Fetching financial data for {ticker}…"):
                new_md, new_cache, _, err = full_pipeline(ticker, existing_cache)

            if err and not new_md:
                st.error(err)
                return

            save_raw_cache(ticker, new_cache)
            save_analysis(ticker, new_md)
            st.session_state[f"display_{ticker}"] = new_md
            st.session_state[f"notice_{ticker}"] = (
                "warning" if err else "success",
                err if err else f"Analysis saved to companies/{ticker}.md"
            )

    # ── Cache prompt ───────────────────────────────────────────────────────────
    if st.session_state.get(f"show_prompt_{ticker}"):
        fm = st.session_state.get(f"fm_{ticker}") or {}
        existing_cache = st.session_state.get(f"cache_{ticker}")
        generated = fm.get("generated", "unknown")
        last_checked = fm.get("last_checked", generated)

        st.info(
            f"**Cached analysis found for {ticker}**  \n"
            f"Generated: **{generated}** · Last checked: **{last_checked}**"
        )

        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            show_existing = st.button("Show existing analysis", key=f"show_{ticker}")
        with btn_col2:
            check_update = st.button("Check for updates", key=f"update_{ticker}", type="primary")

        if show_existing:
            md_text, _ = load_cached_md(ticker)
            st.session_state[f"show_prompt_{ticker}"] = False
            st.session_state[f"display_{ticker}"] = md_text
            st.session_state[f"notice_{ticker}"] = None
            st.rerun()

        if check_update:
            st.session_state[f"show_prompt_{ticker}"] = False
            md_text, _ = load_cached_md(ticker)
            with st.spinner(f"Checking for new data for {ticker}…"):
                new_md, new_cache, is_new_data, err = full_pipeline(ticker, existing_cache)

            today = date.today().isoformat()

            if err and not new_md:
                st.error(err)
                return

            if is_new_data and new_md:
                save_raw_cache(ticker, new_cache)
                save_analysis(ticker, new_md)
                st.session_state[f"display_{ticker}"] = new_md
                st.session_state[f"notice_{ticker}"] = ("success", "New data found — analysis updated.")
            else:
                if md_text:
                    updated_md = update_frontmatter(md_text, {"last_checked": today})
                    save_analysis(ticker, updated_md)
                    st.session_state[f"display_{ticker}"] = updated_md
                notice = (
                    ("warning", f"Live data unavailable — showing cached analysis. ({err})")
                    if err
                    else ("info", f"No new data found. Analysis is current as of {today}.")
                )
                st.session_state[f"notice_{ticker}"] = notice

            st.rerun()

        return  # wait for button click

    # ── Display ────────────────────────────────────────────────────────────────
    display_md = st.session_state.get(f"display_{ticker}")
    notice = st.session_state.get(f"notice_{ticker}")

    if notice:
        _notice(*notice)

    if display_md:
        st.markdown(strip_frontmatter(display_md), unsafe_allow_html=False)
        st.download_button(
            label=f"Download {ticker}.md",
            data=display_md,
            file_name=f"{ticker}.md",
            mime="text/markdown",
        )


if __name__ == "__main__":
    main()
