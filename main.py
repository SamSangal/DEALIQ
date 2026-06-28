import yfinance as yf
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="DealIQ", layout="wide", page_icon="💼")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1c1f26; padding: 15px; border-radius: 10px; }
    .stButton>button { background-color: #00C4FF; color: black; font-weight: bold; border-radius: 8px; padding: 8px 20px; }
    </style>
""", unsafe_allow_html=True)

st.title("💼 DealIQ")
st.subheader("Financial Research & Deal Screening Platform")

view = st.radio("Select your role:", ["👤 Investor", "📊 IB Analyst", "🏦 Private Equity"], horizontal=True)
st.markdown("---")

ticker_input = st.text_input("🔍 Enter a stock ticker (e.g. AAPL, NVDA, MSFT)").upper()

def acquisition_score(info):
    score = 0
    pe = info.get("trailingPE", 0) or 0
    if pe < 15: score += 20
    elif pe < 25: score += 10
    growth = info.get("revenueGrowth", 0) or 0
    if growth > 0.20: score += 20
    elif growth > 0.10: score += 10
    margin = info.get("profitMargins", 0) or 0
    if margin > 0.20: score += 20
    elif margin > 0.10: score += 10
    dte = info.get("debtToEquity", 999) or 999
    if dte < 50: score += 20
    elif dte < 100: score += 10
    fcf = info.get("freeCashflow", 0) or 0
    if fcf > 5e9: score += 20
    elif fcf > 1e9: score += 10
    return score

def investment_verdict(info):
    reasons = []
    flags = []
    pe = info.get("trailingPE", 0) or 0
    growth = info.get("revenueGrowth", 0) or 0
    margin = info.get("profitMargins", 0) or 0
    dte = info.get("debtToEquity", 999) or 999
    fcf = info.get("freeCashflow", 0) or 0
    roe = info.get("returnOnEquity", 0) or 0
    if growth > 0.15: reasons.append("Strong revenue growth")
    if margin > 0.20: reasons.append("High profit margins")
    if fcf > 5e9: reasons.append("Strong free cash flow")
    if roe > 0.20: reasons.append("High return on equity")
    if pe < 20: reasons.append("Attractive valuation")
    if pe > 40: flags.append("Expensive valuation")
    if dte > 150: flags.append("High debt levels")
    if margin < 0: flags.append("Negative profit margins")
    if growth < 0: flags.append("Declining revenue")
    if fcf < 0: flags.append("Negative free cash flow")
    if len(reasons) >= 3 and len(flags) == 0:
        verdict = "BUY"
    elif len(flags) >= 2:
        verdict = "AVOID"
    else:
        verdict = "HOLD"
    return verdict, reasons, flags

if ticker_input:
    with st.spinner("Fetching data..."):
        stock = yf.Ticker(ticker_input)
        info = stock.info

    name = info.get("longName", ticker_input)
    sector = info.get("sector", "")
    industry = info.get("industry", "")
    country = info.get("country", "")
    market_cap = info.get("marketCap", 0)
    revenue = info.get("totalRevenue", 0)
    ebitda = info.get("ebitda", 0)
    pe = info.get("trailingPE", 0) or 0
    gross_margin = info.get("grossMargins", 0) or 0
    net_margin = info.get("profitMargins", 0) or 0
    rev_growth = info.get("revenueGrowth", 0) or 0
    fcf = info.get("freeCashflow", 0) or 0
    dte = info.get("debtToEquity", 0) or 0
    roe = info.get("returnOnEquity", 0) or 0
    ev_ebitda = info.get("enterpriseToEbitda", 0) or 0
    ev_revenue = info.get("enterpriseToRevenue", 0) or 0
    fcf_yield = (fcf / market_cap * 100) if market_cap else 0

    st.header(f"🏢 {name}")
    st.caption(f"📍 {sector} | {industry} | {country}")
    st.markdown("---")

    # ─── INVESTOR VIEW ───
    if view == "👤 Investor":
        verdict, reasons, flags = investment_verdict(info)

        if verdict == "BUY":
            st.success("## ✅ BUY")
            st.write("This company looks like a solid investment based on its financials.")
        elif verdict == "AVOID":
            st.error("## ❌ AVOID")
            st.write("This company has some concerning financial signals right now.")
        else:
            st.warning("## ⚠️ HOLD")
            st.write("This company is a mixed picture — not a clear buy or sell.")

        col1, col2, col3 = st.columns(3)
        col1.metric("Stock P/E Ratio", f"{pe:.1f}", help="How expensive the stock is vs earnings")
        col2.metric("Revenue Growth", f"{rev_growth*100:.1f}%", help="How fast the company is growing")
        col3.metric("Profit Margin", f"{net_margin*100:.1f}%", help="How much profit per dollar of revenue")

        st.subheader("📈 Stock Price — Last 12 Months")
        history = stock.history(period="1y")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=history.index, y=history["Close"], mode="lines", line=dict(color="#00C4FF", width=2), fill="tozeroy", fillcolor="rgba(0,196,255,0.1)"))
        fig.update_layout(template="plotly_dark", height=350, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)

        if reasons:
            st.write("**Why it looks good:**")
            for r in reasons: st.write(f"✓ {r}")
        if flags:
            st.write("**Things to watch out for:**")
            for f in flags: st.write(f"✗ {f}")

    # ─── IB ANALYST VIEW ───
    elif view == "📊 IB Analyst":
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Market Cap", f"${market_cap:,.0f}")
        col2.metric("Revenue", f"${revenue:,.0f}")
        col3.metric("EBITDA", f"${ebitda:,.0f}")
        col4.metric("P/E Ratio", f"{pe:.1f}")

        st.subheader("📈 Stock Price — Last 12 Months")
        history = stock.history(period="1y")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=history.index, y=history["Close"], mode="lines", line=dict(color="#00C4FF", width=2), fill="tozeroy", fillcolor="rgba(0,196,255,0.1)"))
        fig.update_layout(template="plotly_dark", height=350, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("🔢 Valuation Multiples")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("EV/EBITDA", f"{ev_ebitda:.1f}x")
        col2.metric("EV/Revenue", f"{ev_revenue:.1f}x")
        col3.metric("Gross Margin", f"{gross_margin*100:.1f}%")
        col4.metric("Net Margin", f"{net_margin*100:.1f}%")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Debt/Equity", f"{dte:.1f}")
        col2.metric("Free Cash Flow", f"${fcf:,.0f}")
        col3.metric("Return on Equity", f"{roe*100:.1f}%")
        col4.metric("Revenue Growth", f"{rev_growth*100:.1f}%")

        st.subheader("🔎 Peer Comparison")
        peer_input = st.text_input("Enter peer tickers (e.g. AMD, INTC, QCOM)").upper()
        if peer_input:
            tickers = [ticker_input] + [t.strip() for t in peer_input.split(",")]
            rows = []
            for t in tickers:
                i = yf.Ticker(t).info
                rows.append({
                    "Company": i.get("longName", t),
                    "Ticker": t,
                    "Market Cap ($B)": round(i.get("marketCap", 0) / 1e9, 1),
                    "Revenue ($B)": round(i.get("totalRevenue", 0) / 1e9, 1),
                    "EBITDA ($B)": round(i.get("ebitda", 0) / 1e9, 1),
                    "P/E": round(i.get("trailingPE", 0), 1),
                    "EV/EBITDA": round(i.get("enterpriseToEbitda", 0), 1),
                    "Gross Margin %": round(i.get("grossMargins", 0) * 100, 1),
                    "Net Margin %": round(i.get("profitMargins", 0) * 100, 1),
                    "Rev Growth %": round(i.get("revenueGrowth", 0) * 100, 1),
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True)

        st.subheader("🏆 Acquisition Score")
        score = acquisition_score(info)
        if score >= 70: label = "Strong Acquisition Candidate"
        elif score >= 40: label = "Moderate Acquisition Candidate"
        else: label = "Weak Acquisition Candidate"

        col1, col2 = st.columns(2)
        col1.metric("Score", f"{score}/100")
        col1.write(f"**{label}**")
        fig2 = go.Figure(go.Indicator(mode="gauge+number", value=score,
            gauge={"axis": {"range": [0,100]}, "bar": {"color": "#00C4FF"},
                   "steps": [{"range": [0,40], "color": "#ff4444"}, {"range": [40,70], "color": "#ffaa00"}, {"range": [70,100], "color": "#00cc44"}]},
            title={"text": "Acquisition Attractiveness"}))
        fig2.update_layout(height=300, template="plotly_dark")
        col2.plotly_chart(fig2, use_container_width=True)

    # ─── PRIVATE EQUITY VIEW ───
    elif view == "🏦 Private Equity":
        st.subheader("📊 Key Financials")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Market Cap", f"${market_cap/1e9:.1f}B")
        col2.metric("EBITDA", f"${ebitda/1e9:.1f}B")
        col3.metric("FCF Yield", f"{fcf_yield:.1f}%")
        col4.metric("Debt/Equity", f"{dte:.1f}")

        st.subheader("🏦 LBO Analysis")
        st.write("Estimate returns based on a leveraged buyout of this company.")

        col1, col2, col3 = st.columns(3)
        entry_multiple = col1.slider("Entry EV/EBITDA Multiple", 5.0, 20.0, float(round(ev_ebitda, 1)) if ev_ebitda else 10.0)
        exit_multiple = col2.slider("Exit EV/EBITDA Multiple", 5.0, 20.0, float(round(ev_ebitda * 1.1, 1)) if ev_ebitda else 11.0)
        debt_pct = col3.slider("Debt Financing %", 30, 80, 60)
        hold_years = st.slider("Hold Period (Years)", 3, 7, 5)

        if ebitda and ebitda > 0:
            entry_ev = entry_multiple * ebitda
            equity_invested = entry_ev * (1 - debt_pct / 100)
            exit_ev = exit_multiple * ebitda
            debt = entry_ev * (debt_pct / 100)
            exit_equity = exit_ev - debt
            moic = exit_equity / equity_invested
            irr = (moic ** (1 / hold_years) - 1) * 100

            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Entry Enterprise Value", f"${entry_ev/1e9:.1f}B")
            col2.metric("Equity Invested", f"${equity_invested/1e9:.1f}B")
            col3.metric("Exit Enterprise Value", f"${exit_ev/1e9:.1f}B")
            col4.metric("Exit Equity Value", f"${exit_equity/1e9:.1f}B")

            col1, col2 = st.columns(2)
            col1.metric("MOIC", f"{moic:.2f}x")
            col2.metric("Estimated IRR", f"{irr:.1f}%")

            if irr >= 20:
                st.success("✅ Strong LBO candidate — IRR above 20% threshold")
            elif irr >= 15:
                st.warning("⚠️ Moderate LBO candidate — IRR between 15-20%")
            else:
                st.error("❌ Weak LBO candidate — IRR below 15% hurdle rate")
        else:
            st.warning("EBITDA data not available for LBO analysis.")

        score = acquisition_score(info)
        if score >= 70: label = "Strong Acquisition Candidate"
        elif score >= 40: label = "Moderate Acquisition Candidate"
        else: label = "Weak Acquisition Candidate"
        st.metric("Acquisition Score", f"{score}/100 — {label}")

    st.markdown("---")
    st.caption("DealIQ | Built for investment banking, private equity, and corporate development professionals")