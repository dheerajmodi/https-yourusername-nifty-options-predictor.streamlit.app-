import numpy as np
import pandas as pd

# Example data input for simplicity (Replace this with real-time data feed)
data = {
    "Nifty_open": 24000,
    "Nifty_945": 24080,
    "CE_open": 100,
    "CE_945": 130,
    "PE_open": 100,
    "PE_945": 80,
    "Theta_CE": 5,  # daily decay
    "Theta_PE": 5,
    "IV_open": 15.5,
    "IV_945": 17.0,
    "Days_to_expiry": 2
}

def calculate_probabilities(data):
    # Nifty Direction
    nifty_change = (data["Nifty_945"] - data["Nifty_open"]) / data["Nifty_open"] * 100

    # CE Premium Movement (%)
    ce_premium_change = (data["CE_945"] - data["CE_open"]) / data["CE_open"] * 100

    # PE Premium Movement (%)
    pe_premium_change = (data["PE_945"] - data["PE_open"]) / data["PE_open"] * 100

    # Theta effect per 30 minutes
    ce_theta_impact = (data["Theta_CE"] / 6.25) / data["CE_open"] * 100  # Assuming 6.25 hrs market
    pe_theta_impact = (data["Theta_PE"] / 6.25) / data["PE_open"] * 100

    # IV Change
    iv_change = (data["IV_945"] - data["IV_open"]) / data["IV_open"] * 100

    # Scoring logic (Weights: Premium 40%, Theta 30%, IV 30%)
    premium_score = (ce_premium_change - pe_premium_change) * 0.4
    theta_score = (- (ce_theta_impact + pe_theta_impact)) * 0.3
    iv_score = iv_change * 0.3

    total_score = premium_score + theta_score + iv_score

    # Convert to probability
    buyer_prob = np.clip(50 + total_score, 0, 100)
    seller_prob = 100 - buyer_prob

    decision = "Buyer" if buyer_prob > seller_prob else "Seller"

    return {
        "Nifty_change_%": round(nifty_change, 2),
        "CE_premium_change_%": round(ce_premium_change, 2),
        "PE_premium_change_%": round(pe_premium_change, 2),
        "Theta_impact_CE_%": round(ce_theta_impact, 2),
        "Theta_impact_PE_%": round(pe_theta_impact, 2),
        "IV_change_%": round(iv_change, 2),
        "Buyer_probability_%": round(buyer_prob, 2),
        "Seller_probability_%": round(seller_prob, 2),
        "Decision": decision
    }

result = calculate_probabilities(data)

print("Today's Trading Insight at 9:45 AM:\n")
for key, value in result.items():
    print(f"{key.replace('_', ' ')}: {value}")
