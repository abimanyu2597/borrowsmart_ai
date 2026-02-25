from .emi import calculate_emi
from .affordability import check_affordability

def run_stress(principal, rate, tenure_years):
    shocks = [1, 2]
    base = calculate_emi(principal, rate, tenure_years)

    results = []
    for shock in shocks:
        shocked_rate = rate + shock
        shocked = calculate_emi(principal, shocked_rate, tenure_years)

        results.append({
            "shock_percent": shock,
            "original_rate": rate,
            "shocked_rate": shocked_rate,
            "original_emi": base["emi"],
            "shocked_emi": shocked["emi"],
            "emi_increase": shocked["emi"] - base["emi"],
        })

    return results


# ✅ Compatibility wrapper so agent.py can import stress_test
def stress_test(principal, rate, tenure_years, salary=None, monthly_expenses=0):
    results = run_stress(principal, rate, tenure_years)

    # If salary provided, add risk labels after shock
    if salary:
        for r in results:
            aff = check_affordability(salary, r["shocked_emi"], monthly_expenses)
            r["risk_level"] = aff["risk_level"]
            r["color"] = aff.get("color", "")

    return results