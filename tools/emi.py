import math

def calculate_emi(principal: float, annual_rate: float, tenure_years: int) -> dict:
    """
    Returns a rich EMI payload so UI/agent can format without KeyErrors.

    Keys returned:
    - principal
    - annual_rate
    - tenure_years
    - tenure_months
    - monthly_rate
    - emi
    - total_payment
    - total_interest
    """
    if principal <= 0:
        raise ValueError("principal must be > 0")
    if annual_rate < 0:
        raise ValueError("annual_rate cannot be negative")
    if tenure_years <= 0:
        raise ValueError("tenure_years must be >= 1")

    n = int(tenure_years * 12)
    r = annual_rate / (12 * 100)

    # Handle 0% interest safely
    if r == 0:
        emi = principal / n
        total_payment = principal
        total_interest = 0.0
    else:
        emi = principal * r * (1 + r) ** n / ((1 + r) ** n - 1)
        total_payment = emi * n
        total_interest = total_payment - principal

    return {
        "principal": float(principal),
        "annual_rate": float(annual_rate),
        "tenure_years": int(tenure_years),
        "tenure_months": n,
        "monthly_rate": float(r),

        "emi": float(emi),
        "total_payment": float(total_payment),
        "total_interest": float(total_interest),
    }