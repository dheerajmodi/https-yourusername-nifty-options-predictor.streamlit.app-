import streamlit as st
import numpy as np
import requests
from datetime import datetime, time
import pytz

# Cache data once fetched at 9:45 AM
@st.cache_data(ttl=60*60*8)  # Cache for 8 hours
def fetch_nse_data_at_945():
    IST = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(IST).time()

    # Check if current time is after 9:45 AM IST
    if current_time >= time(9, 45):
        # Fetch Nifty data
        url_nifty = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
        url_options = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
        headers = {'User-Agent': 'Mozilla/5.0'}

        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers)
        nifty_resp = session.get(url_nifty, headers=headers).json()
        nifty_open = float(nifty_resp['data'][0]['open'].replace(',', ''))
        nifty_945 = float(nifty_resp['data'][0]['lastPrice'].replace(',', ''))

        # Fetch ATM Options data at Nifty price at 9:45
        strike = round(nifty_945 / 50) * 50
        options_resp = session.get(url_options, headers=headers).json()
        ce_price = pe_price = ce_theta = pe_theta = ce_iv = pe_iv = None

        for record in options_resp['records']['data']:
            if record['strikePrice'] == strike:
                ce = record['CE']
                pe = record['PE']
                ce_price, pe_price = ce['lastPrice'], pe['lastPrice']
                ce_theta, pe_theta = ce['theta'], pe['theta']
                ce_iv, pe_iv = ce['impliedVolatility'], pe['impliedVolatility']
                break

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
