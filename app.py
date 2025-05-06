import streamlit as st
import numpy as np
from nsepython import *
from datetime import datetime, time
import pytz

@st.cache_data(ttl=60*60*8)  # Data cached for 8 hours
def fetch_nse_data_at_945():
    IST = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(IST).time()

    if current_time >= time(9, 45):
        nifty_open = float(nse_quote_ltp("NIFTY")['open'])
        nifty_945 = float(nse_quote_ltp("NIFTY")['lastPrice'])

        strike = round(nifty_945 / 50) * 50
        expiry_date = expiry_list("NIFTY")[0]

        ce_data = nse_optionchain_scrapper("NIFTY", expiry_date, strike, 'CE')
        pe_data = nse_optionchain_scrapper("NIFTY", expiry_date, strike, 'PE')

        ce_price = ce_data['lastPrice']
        pe_price = pe_data['lastPrice']
        ce_theta = ce_data['theta']
        pe_theta = pe_data['theta']
        ce_iv = ce_data['impliedVolatility']
        pe_iv = pe_data['impliedVolatility']

        fetched_at = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")

        return {
            'fetched_at': fetched_at,
            'nifty_open': nifty_open,
            'nifty_945': nifty_945,
            'ce_price': ce_price,
            'pe_price': pe_price,
            'ce_theta': ce_theta,
            'pe_theta': pe_theta,
            'ce_iv': ce_iv,
            'pe_iv': pe_iv
        }
    else:
        return None

st.title("Nifty Options Daily Predictor (Auto 9:45 AM Data)")

data = fetch_nse_data_at_945()

if data:
    st.subheader(f"✅ Data captured at: {data['fetched_at']} IST")

    nifty_change = (data['nifty_945'] - data['nifty_open']) / data['nifty_open'] * 100
    ce_premium_change = (data['ce_price'] - 100)
    pe_premium_change = (data['pe_price'] - 100)

    ce_theta_impact = (data['ce_theta'] / 6.25) / data['ce_price'] * 100
    pe_theta_impact = (data['pe_theta'] / 6.25) / data['pe_price'] * 100

    avg_iv = (data['ce_iv'] + data['pe_iv']) / 2
    iv_change = (avg_iv - 15)

    premium_score = (ce_premium_change - pe_premium_change) * 0.4
    theta_score = -(ce_theta_impact + pe_theta_impact) * 0.3
    iv_score = iv_change * 0.3

    total_score = premium_score + theta_score + iv_score

    buyer_prob = np.clip(50 + total_score, 0, 100)
    seller_prob = 100 - buyer_prob
    decision = "Buyer" if buyer_prob > seller_prob else "Seller"

    st.write(f"Nifty Change: {nifty_change:.2f}%")
    st.write(f"CE Premium Change: {ce_premium_change:.2f}%")
    st.write(f"PE Premium Change: {pe_premium_change:.2f}%")
    st.write(f"Theta Impact CE: {ce_theta_impact:.2f}%")
    st.write(f"Theta Impact PE: {pe_theta_impact:.2f}%")
    st.write(f"IV Change: {iv_change:.2f}%")

    st.markdown(f"### **Buyer Probability: {buyer_prob:.2f}%**")
    st.markdown(f"### **Seller Probability: {seller_prob:.2f}%**")
    st.markdown(f"### Decision: **{decision}'s Day**")
else:
    st.warning("⚠️ It's not yet 9:45 AM IST. Please check back after 9:45 AM.")
