"""
Borrow Smart AI — Streamlit UI (v2: XAI, Stress Test, Budget-Aware, Enhanced Scenarios + Chat)
"""

import streamlit as st
import pandas as pd

from agent import run_agent
from llm import get_llm_explanation

# ───────────────────────── Page Config ─────────────────────────
st.set_page_config(
    page_title="Borrow Smart AI",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ───────────────────────── Custom CSS ─────────────────────────
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        color: white;
    }
    .main-header h1 { margin: 0; font-size: 2rem; font-weight: 700; }
    .main-header p  { margin: 0.4rem 0 0; opacity: 0.9; font-size: 1rem; }

    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 14px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        transition: transform 0.2s;
    }
    .metric-card:hover { transform: translateY(-3px); }
    .metric-card .label { font-size: 0.85rem; color: #555; font-weight: 500; }
    .metric-card .value { font-size: 1.6rem; font-weight: 700; color: #1a1a2e; margin-top: 0.3rem; }

    .badge { display:inline-block; padding:0.35rem 1rem; border-radius:999px; font-weight:700; font-size:0.9rem; }
    .badge-safe  { background:#d4edda; color:#155724; }
    .badge-mod   { background:#fff3cd; color:#856404; }
    .badge-risky { background:#f8d7da; color:#721c24; }

    .explanation-box {
        background: #f8f9fa;
        border-left: 6px solid #667eea;
        padding: 1.2rem 1.2rem;
        border-radius: 12px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.06);
        line-height: 1.55;
    }

    .stress-card {
        background: white;
        border-radius: 14px;
        padding: 1rem 1.2rem;
        box-shadow: 0 3px 12px rgba(0,0,0,0.08);
        border: 1px solid rgba(0,0,0,0.06);
    }
    .shock-label { font-weight: 800; color: #2c3e50; }

    .disclaimer {
        margin-top: 2rem;
        background: #fff3cd;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        border: 1px solid rgba(133,100,4,0.25);
        color: #856404;
    }

    /* Chat */
    .chat-hint { color:#6c757d; font-size:0.9rem; margin-top:0.25rem; }
</style>
""",
    unsafe_allow_html=True,
)

# ───────────────────────── Header ─────────────────────────
st.markdown(
    """
<div class="main-header">
  <h1>💰 Borrow Smart AI</h1>
  <p>Budget-aware loan planning with explainable risk + stress testing + interactive Q&A</p>
</div>
""",
    unsafe_allow_html=True,
)

# ───────────────────────── Sidebar Inputs ─────────────────────────
with st.sidebar:
    st.header("Your Details")
    salary = st.number_input("Monthly Salary (₹)", 1000, 10_000_000, 80_000, step=5_000)
    monthly_expenses = st.number_input("Fixed Monthly Expenses (₹)", 0, 10_000_000, 25_000, step=1_000)

    st.header("Loan Details")
    loan_amount = st.number_input("Loan Amount (₹)", 10_000, 100_000_000, 1_500_000, step=50_000)
    interest_rate = st.slider("Interest Rate (% p.a.)", 0.0, 25.0, 11.0, step=0.25)
    tenure_years = st.slider("Tenure (years)", 1, 30, 5)

    run_stress_test = st.checkbox("Enable Stress Test (+1% / +2%)", value=True)

    user_query = st.text_input(
        "Your main question (optional)",
        placeholder="Can I afford this loan? Which tenure is best?",
    )

    run_btn = st.button("🚀 Analyze", use_container_width=True)

# Session state for chat + last result
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_tool_output" not in st.session_state:
    st.session_state.last_tool_output = ""
if "last_summary" not in st.session_state:
    st.session_state.last_summary = ""

# ───────────────────────── Run Analysis ─────────────────────────
if run_btn:
    result = run_agent(
        user_query=user_query or "",
        salary=salary,
        loan_amount=loan_amount,
        interest_rate=interest_rate,
        tenure_years=tenure_years,
        monthly_expenses=monthly_expenses,
        run_stress_test=run_stress_test,
    )

    if not result["success"]:
        st.error(result["error"])
    else:
        st.session_state.last_tool_output = result.get("tool_output_text", "")
        st.session_state.last_summary = result.get("explanation", "")

        emi = result["emi"]
        aff = result["affordability"]

        # Metrics row
        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="label">Monthly EMI</div>
                    <div class="value">₹{emi['emi']:,.0f}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="label">Total Interest</div>
                    <div class="value">₹{emi['total_interest']:,.0f}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="label">Disposable / month</div>
                    <div class="value">₹{aff['disposable_income']:,.0f}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c4:
            badge_class = {
                "Safe": "badge-safe",
                "Moderate": "badge-mod",
                "Risky": "badge-risky",
            }.get(aff["risk_level"], "badge-mod")
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="label">Risk</div>
                    <div class="value"><span class="badge {badge_class}">{aff['color']} {aff['risk_level']}</span></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("### ✅ Affordability Verdict")
        st.write(aff["verdict"])

        # Scenarios table
        st.markdown("### 📊 Tenure Scenarios (Compare Options)")
        df = pd.DataFrame(result["scenarios"])
        display_df = pd.DataFrame(
            {
                "Tenure (years)": df["tenure_years"],
                "EMI (₹)": df["emi"].apply(lambda x: f"₹{x:,.0f}"),
                "Total Interest (₹)": df["total_interest"].apply(lambda x: f"₹{x:,.0f}"),
                "Total Payment (₹)": df["total_payment"].apply(lambda x: f"₹{x:,.0f}"),
                "Risk": df.apply(lambda r: f"{r['color']} {r['risk_level']}", axis=1),
                "": df["recommended"].apply(lambda r: "⭐ Recommended" if r else ""),
            }
        )
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        # Stress test cards
        if result.get("stress_test"):
            st.markdown("### ⚡ Stress Test — What If Rates Rise?")
            stress_cols = st.columns(len(result["stress_test"]))
            for i, sr in enumerate(result["stress_test"]):
                with stress_cols[i]:
                    risk_badge = {
                        "Safe": "badge-safe",
                        "Moderate": "badge-mod",
                        "Risky": "badge-risky",
                    }.get(sr["risk_level"], "badge-mod")

                    st.markdown(
                        f"""
                        <div class="stress-card">
                            <div class="shock-label">+{sr['shock_percent']}% Rate Shock</div>
                            <p style="margin:0.5rem 0 0.2rem; font-size:0.9rem;">
                                Rate: <b>{sr['original_rate']}% → {sr['shocked_rate']}%</b>
                            </p>
                            <p style="margin:0; font-size:0.9rem;">
                                EMI: <b>₹{sr['original_emi']:,.0f} → ₹{sr['shocked_emi']:,.0f}</b>
                                <span style="color:#c0392b; font-weight:700;"> (+₹{sr['emi_increase']:,.0f}/mo)</span>
                            </p>
                            <p style="margin:0.6rem 0 0;">
                                <span class="badge {risk_badge}">{sr['color']} {sr['risk_level']}</span>
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        # AI explanation
        st.markdown("### 🧠 AI Explanation")
        st.markdown(
            f'<div class="explanation-box">{result["explanation"]}</div>',
            unsafe_allow_html=True,
        )

        # Optional: show raw tool output for transparency
        with st.expander("🔎 Show Tool Outputs (Transparent / Debug)"):
            st.code(result.get("tool_output_text", ""), language="text")

        # Reset chat on new analysis (keeps it clean)
        st.session_state.messages = []

# ───────────────────────── Follow-up Chat ─────────────────────────
st.markdown("### 💬 Ask Follow-up Questions")
st.markdown('<div class="chat-hint">Example: “Should I reduce tenure or increase down payment?”</div>', unsafe_allow_html=True)

# Show chat history
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

chat_q = st.chat_input("Ask Borrow Smart AI…")

if chat_q:
    if not st.session_state.last_tool_output:
        st.warning("Run an analysis first (left sidebar → Analyze). Then ask follow-ups here.")
    else:
        st.session_state.messages.append({"role": "user", "content": chat_q})
        with st.chat_message("user"):
            st.write(chat_q)

        with st.chat_message("assistant"):
            answer = get_llm_explanation(chat_q, st.session_state.last_tool_output)
            st.write(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})

# ───────────────────────── Disclaimer ─────────────────────────
st.markdown(
    """
<div class="disclaimer">
    ⚠️ <strong>Disclaimer:</strong> Educational decision-support only — not professional financial advice.
</div>
""",
    unsafe_allow_html=True,
)