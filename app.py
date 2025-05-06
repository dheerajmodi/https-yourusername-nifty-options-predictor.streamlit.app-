import streamlit as st
import numpy as np

st.title("Nifty Options Buyer/Seller Predictor")

Nifty_open = st.number_input("Nifty Opening Price (9:15)", value=24000)
Nifty_945 = st.number_input("Nifty Price at 9:45 AM", value=24080)
CE_open = st.number_input("ATM CE Premium at Open", value=100)
CE_945 = st.number_input("ATM CE Premium at 9:45", value=130)
PE_open = st.number_input("ATM PE Premium at Open", value=100)
PE_945 = st.number_input("ATM PE Premium at 9:45", value=80)
Theta_CE = st.number_input("CE Daily Theta", value=5)
Theta_PE = st.number_input("PE Daily Theta", value=5)
IV_open = st.number_input("IV at Open (%)", value=15.5)
IV_945 = st.number_input("IV at 9:45 (%)", value=17.0)

if st.button("Calculate Probability"):
    nifty_change = (Nifty_945 - Nifty_open) / Nifty_open * 100
    ce_premium_change = (CE_945 - CE_open) / CE_open * 100
    pe_premium_change = (PE_945 - PE_open) / PE_open * 100
    ce_theta_impact = (Theta_CE / 6.25) / CE_open * 100
    pe_theta_impact = (Theta_PE / 6.25) / PE_open * 100
    iv_change = (IV_945 - IV_open) / IV_open * 100

    premium_score = (ce_premium_change - pe_premium_change) * 0.4
    theta_score = -(ce_theta_impact + pe_theta_impact) * 0.3
    iv_score = iv_change * 0.3

    total_score = premium_score + theta_score + iv_score

    buyer_prob = np.clip(50 + total_score, 0, 100)
    seller_prob = 100 - buyer_prob
    decision = "Buyer" if buyer_prob > seller_prob else "Seller"

    st.subheader("Today's Trading Insight at 9:45 AM:")
    st.write(f"Nifty Change: {nifty_change:.2f}%")
    st.write(f"CE Premium Change: {ce_premium_change:.2f}%")
    st.write(f"PE Premium Change: {pe_premium_change:.2f}%")
    st.write(f"Theta Impact CE: {ce_theta_impact:.2f}%")
    st.write(f"Theta Impact PE: {pe_theta_impact:.2f}%")
    st.write(f"IV Change: {iv_change:.2f}%")
    st.markdown(f"### **Buyer Probability: {buyer_prob:.2f}%**")
    st.markdown(f"### **Seller Probability: {seller_prob:.2f}%**")
    st.markdown(f"### Decision: **{decision}’s Day**")
