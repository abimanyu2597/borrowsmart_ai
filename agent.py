"""
Borrow Smart AI — Agent Orchestration (compatible with current tools)

Expected tool functions:
- tools.emi.calculate_emi(principal, annual_rate, tenure_years) -> dict: emi,total_payment,total_interest
- tools.affordability.check_affordability(salary, emi, expenses) -> dict: risk_level, disposable_income, emi_to_salary_ratio, summary
- tools.simulator.generate_scenarios(principal, rate) -> list[dict]: tenure_years, emi, total_interest, total_payment
- tools.stress_test.stress_test(principal, rate, tenure_years, salary=None, monthly_expenses=0) -> list[dict] with shocks (+ risk if salary passed)
- llm.get_llm_explanation(user_query, tool_outputs) -> str (optional, safe fallback if LLM unavailable)
"""

from tools.emi import calculate_emi
from tools.affordability import check_affordability
from tools.simulator import generate_scenarios

# stress_test wrapper should exist (we added it earlier). If not, import run_stress as fallback.
try:
    from tools.stress_test import stress_test
except ImportError:  # fallback
    from tools.stress_test import run_stress as stress_test  # type: ignore

# LLM is optional: app should still run even if Groq not set up
try:
    from llm import get_llm_explanation
except Exception:
    get_llm_explanation = None  # type: ignore


def _badge(risk_level: str) -> str:
    mapping = {"Safe": "🟢", "Moderate": "🟠", "Risky": "🔴"}
    return mapping.get(risk_level, "🟠")


def _format_emi_result(emi_result: dict, principal: float, annual_rate: float, tenure_years: int) -> str:
    return (
        f"• Loan Amount: ₹{principal:,.2f}\n"
        f"• Interest Rate: {annual_rate}% p.a.\n"
        f"• Tenure: {tenure_years * 12} months\n"
        f"• Monthly EMI: ₹{emi_result['emi']:,.2f}\n"
        f"• Total Interest: ₹{emi_result['total_interest']:,.2f}\n"
        f"• Total Payment: ₹{emi_result['total_payment']:,.2f}"
    )


def _format_affordability(aff: dict, salary: float, expenses: float, emi: float) -> str:
    risk = aff.get("risk_level", "Moderate")
    return "\n".join(
        [
            f"• Monthly Salary: ₹{salary:,.2f}",
            f"• Fixed Expenses: ₹{expenses:,.2f}",
            f"• Monthly EMI: ₹{emi:,.2f}",
            f"• EMI-to-Salary Ratio: {aff.get('emi_to_salary_ratio', 0)}%",
            f"• Disposable Income (after EMI + expenses): ₹{aff.get('disposable_income', 0):,.2f}",
            f"• Risk Level: {_badge(risk)} {risk}",
            f"• Summary: {aff.get('summary', '')}",
        ]
    )


def _enrich_scenarios_with_risk(scenarios: list[dict], salary: float, expenses: float) -> list[dict]:
    enriched = []
    for s in scenarios:
        aff = check_affordability(salary, s["emi"], expenses)
        risk = aff.get("risk_level", "Moderate")
        enriched.append(
            {
                **s,
                "risk_level": risk,
                "color": _badge(risk),
                "recommended": False,
            }
        )

    # Recommendation: among Safe/Moderate, pick lowest total_interest; else pick lowest total_interest overall
    safe_mod = [x for x in enriched if x["risk_level"] in ("Safe", "Moderate")]
    pool = safe_mod if safe_mod else enriched
    if pool:
        best = min(pool, key=lambda x: x["total_interest"])
        best["recommended"] = True

    return enriched


def _format_scenarios(scenarios: list[dict]) -> str:
    lines = []
    for s in scenarios:
        star = "⭐" if s.get("recommended") else ""
        risk = s.get("risk_level", "")
        color = s.get("color", "")
        risk_txt = f"{color} {risk}".strip()

        lines.append(
            f"• {s['tenure_years']}y: EMI ₹{s['emi']:,.2f}, "
            f"Interest ₹{s['total_interest']:,.2f}, "
            f"Total ₹{s['total_payment']:,.2f}"
            + (f", Risk {risk_txt} {star}".rstrip() if risk_txt or star else "")
        )
    return "\n".join(lines)


def _format_stress(stress_results: list[dict]) -> str:
    lines = []
    for r in stress_results:
        risk = r.get("risk_level", "")
        color = r.get("color", "")
        risk_txt = f" | {color} {risk}".strip() if risk else ""

        lines.append(
            f"• +{r['shock_percent']}%: Rate {r.get('original_rate', '')}→{r['shocked_rate']} | "
            f"EMI ₹{r['original_emi']:,.2f}→₹{r['shocked_emi']:,.2f} "
            f"(+₹{r['emi_increase']:,.2f}/mo){risk_txt}"
        )
    return "\n".join(lines)


def run_agent(
    user_query: str,
    salary: float,
    loan_amount: float,
    interest_rate: float,
    tenure_years: int,
    monthly_expenses: float = 0,
    run_stress_test: bool = True,
) -> dict:
    # Basic validation
    errors = []
    if salary <= 0:
        errors.append("Salary must be positive.")
    if loan_amount <= 0:
        errors.append("Loan amount must be positive.")
    if interest_rate < 0:
        errors.append("Interest rate cannot be negative.")
    if tenure_years <= 0:
        errors.append("Tenure must be at least 1 year.")
    if monthly_expenses < 0:
        errors.append("Expenses cannot be negative.")
    if errors:
        return {"success": False, "error": " ".join(errors)}

    # Core calculations
    emi_result = calculate_emi(loan_amount, interest_rate, tenure_years)
    affordability = check_affordability(salary, emi_result["emi"], monthly_expenses)

    scenarios = generate_scenarios(loan_amount, interest_rate)
    scenarios = _enrich_scenarios_with_risk(scenarios, salary, monthly_expenses)

    stress_results = None
    if run_stress_test:
        # Our wrapper supports salary/expenses; fallback run_stress may ignore them
        try:
            stress_results = stress_test(loan_amount, interest_rate, tenure_years, salary, monthly_expenses)
        except TypeError:
            stress_results = stress_test(loan_amount, interest_rate, tenure_years)

    # Tool output text (for LLM to explain)
    sections = [
        "=== EMI Calculation ===",
        _format_emi_result(emi_result, loan_amount, interest_rate, tenure_years),
        "=== Affordability ===",
        _format_affordability(affordability, salary, monthly_expenses, emi_result["emi"]),
        "=== Scenario Comparison ===",
        _format_scenarios(scenarios),
    ]
    if stress_results:
        sections.append("=== Stress Test (Rate Shocks) ===")
        sections.append(_format_stress(stress_results))

    tool_output_text = "\n\n".join(sections)

    # Explanation (LLM optional)
    if not user_query.strip():
        user_query = (
            f"I earn ₹{salary:,.0f}/month with ₹{monthly_expenses:,.0f} expenses. "
            f"I want a ₹{loan_amount:,.0f} loan at {interest_rate}% for {tenure_years} years. "
            f"Is it affordable and what tenure is best?"
        )

    if get_llm_explanation is None:
        explanation = affordability.get("summary", "Analysis generated.")
    else:
        try:
            explanation = get_llm_explanation(user_query, tool_output_text)
        except Exception:
            explanation = affordability.get("summary", "Analysis generated (LLM unavailable).")

    return {
        "success": True,
        "emi": emi_result,
        "affordability": affordability,
        "scenarios": scenarios,
        "stress_test": stress_results,
        "tool_output_text": tool_output_text,
        "explanation": explanation,
    }