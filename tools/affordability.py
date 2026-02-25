def check_affordability(salary, emi, expenses):
    if salary <= 0:
        raise ValueError("salary must be positive")
    if emi < 0:
        raise ValueError("emi cannot be negative")
    if expenses < 0:
        raise ValueError("expenses cannot be negative")

    ratio = (emi / salary) * 100
    disposable = salary - emi - expenses

    if ratio < 30:
        risk = "Safe"
        color = "🟢"
        verdict = "Comfortable. EMI is within a healthy range."
    elif ratio < 50:
        risk = "Moderate"
        color = "🟠"
        verdict = "Manageable but watch your budget. Consider a longer tenure or higher down payment."
    else:
        risk = "Risky"
        color = "🔴"
        verdict = "High risk. EMI is too heavy relative to income; reduce loan amount or extend tenure."

    return {
        "risk_level": risk,
        "color": color,
        "verdict": verdict,
        "disposable_income": disposable,
        "emi_to_salary_ratio": round(ratio, 2),
        "summary": f"EMI uses {ratio:.1f}% of salary → {risk}. Disposable: ₹{disposable:,.0f}/mo",
    }