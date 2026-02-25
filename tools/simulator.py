from .emi import calculate_emi
from .affordability import check_affordability

def generate_scenarios(principal, rate):
    tenures = [3, 5, 10, 15]
    results = []

    for t in tenures:
        emi_data = calculate_emi(principal, rate, t)
        results.append({
            "tenure_years": t,
            "emi": emi_data["emi"],
            "total_interest": emi_data["total_interest"],
            "total_payment": emi_data["total_payment"],
        })

    return results


# ✅ Compatibility wrapper (so agent.py can import simulate_scenarios)
def simulate_scenarios(principal, rate, salary=None, monthly_expenses=0):
    scenarios = generate_scenarios(principal, rate)

    # If salary provided, enrich with risk info (optional)
    if salary:
        for s in scenarios:
            aff = check_affordability(salary, s["emi"], monthly_expenses)
            s["risk_level"] = aff["risk_level"]
            s["color"] = aff.get("color", "")
            s["recommended"] = False

        # Recommend: lowest interest among those that are not Risky
        safe_or_mod = [s for s in scenarios if s.get("risk_level") in ("Safe", "Moderate")]
        pick_from = safe_or_mod if safe_or_mod else scenarios
        best = min(pick_from, key=lambda x: x["total_interest"])
        best["recommended"] = True
    else:
        for s in scenarios:
            s["risk_level"] = ""
            s["color"] = ""
            s["recommended"] = False

    return scenarios