import streamlit as st
import pandas as pd
import datetime
from vedastro import *

# Initialize VedAstro API Connection
Calculate.SetAPIKey('FreeAPIUser')

# Page Layout Configuration
st.set_page_config(page_title="My Personal Vedic Dashboard", layout="wide")
st.title("🇮🇳 Personal Indian Vedic Astrology System")
st.markdown("Your custom, all-in-one astrological dashboard with deep human-language interpretations.")

# Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🔮 Personal Kundli & Profile", 
    "💑 Relationship & Guna Matching", 
    "💼 Life & Material Desires (Jobs/Property)",
    "📅 Today's Indian Panchanga"
])

# ==========================================
# TAB 1: KUNDLI & DEEP SOUL READING
# ==========================================
with tab1:
    st.header("Personal Birth Chart Details")
    st.markdown("Discover your core signs, ascendant profile, and divisional alignment translated into direct English.")
    
    col1, col2 = st.columns(2)
    with col1:
        location_input = st.text_input("Birth City/Town (India)", "Mumbai", key="t1_loc")
        time_input = st.text_input("Birth Time (24 Hr Format HH:MM)", "14:30", key="t1_time")
    with col2:
        date_input = st.text_input("Birth Date (DD/MM/YYYY)", "25/10/1992", key="t1_date")
        tz_input = st.text_input("Timezone Offset", "+05:30", disabled=True)
        
    if st.button("Calculate My Chart"):
        with st.spinner("Decoding your natal sky..."):
            try:
                # Automated Geolocation safe translation
                geo_res = Calculate.AddressToGeoLocation(location_input + ", India")
                loc = geo_res.get("Payload") if isinstance(geo_res, dict) else geo_res.Payload
                
                # Setup Time Object securely
                birth_time = Time(f"{time_input} {date_input} +05:30", loc)
                
                # Fetching direct calculations to bypass internal JSON issues
                sun_sign = Calculate.PlanetSignName(PlanetName.Sun, birth_time)
                moon_sign = Calculate.PlanetSignName(PlanetName.Moon, birth_time)
                ascendant_sign = Calculate.HouseSignName(HouseName.House1, birth_time)
                
                st.success("✅ Chart successfully generated!")
                
                # Display metrics cleanly
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric(label="☀️ Sun Zodiac Sign", value=str(sun_sign))
                with c2:
                    st.metric(label="🌙 Moon Zodiac Sign", value=str(moon_sign))
                with c3:
                    st.metric(label="🔮 Ascendant (Lagna) Sign", value=str(ascendant_sign))
                
                st.subheader("🗣️ What This Placement Means for You:")
                st.markdown(f"""
                *   **Your Ascendant (Lagna) is {ascendant_sign}:** This means your entire life's physical journey, core personality traits, and natural health patterns operate through this sign. It governs your immediate approach to challenges.
                *   **Your Sun is in {sun_sign}:** The Sun represents your soul's vitality, ego, and career visibility. Having it placed here indicates that your life energy flows best when focusing on the structural domains ruled by {sun_sign}.
                """)
                    
            except Exception as e:
                st.error(f"Calculation tracking error: {e}")

# ==========================================
# TAB 2: MARRIAGE & GUNA MATCHING
# ==========================================
with tab2:
    st.header("Ashta Koota Love & Marriage Interpretation")
    st.markdown("Calculate exactly how many **Gunas** (out of 36) match between your chart and another person's chart.")
    
    m_col, f_col = st.columns(2)
    with m_col:
        st.subheader("Your Details")
        m_loc = st.text_input("Your City", "Mumbai", key="m1")
        m_time = st.text_input("Your Time", "14:30", key="m2")
        m_date = st.text_input("Your Date", "25/10/1992", key="m3")
    with f_col:
        st.subheader("Other Person's Details")
        f_loc = st.text_input("Their City", "Delhi", key="f1")
        f_time = st.text_input("Their Time", "14:30", key="f2")
        f_date = st.text_input("Their Date", "15/06/1997", key="f3")
        
    if st.button("Calculate Guna Match Score"):
        with st.spinner("Evaluating relationship matching scores..."):
            try:
                b_geo_res = Calculate.AddressToGeoLocation(m_loc + ", India")
                b_geo = b_geo_res.get("Payload") if isinstance(b_geo_res, dict) else b_geo_res.Payload
                boy_birth = Time(f"{m_time} {m_date} +05:30", b_geo)
                
                g_geo_res = Calculate.AddressToGeoLocation(f_loc + ", India")
                g_geo = g_geo_res.get("Payload") if isinstance(g_geo_res, dict) else g_geo_res.Payload
                girl_birth = Time(f"{f_time} {f_date} +05:30", g_geo)
                
                # Fetching the compatibility components cleanly
                matchReport = Calculate.MatchReport(boy_birth, girl_birth)
                
                # Direct safe extraction
                if isinstance(matchReport, dict):
                    percentage_score = matchReport.get("KutaScore", 0.0)
                    embeds = matchReport.get("Embeddings", [0]*8)
                else:
                    percentage_score = getattr(matchReport, "KutaScore", 50.0)
                    embeds = getattr(matchReport, "Embeddings", [0]*8)
                
                gunas_matched = round((float(percentage_score) / 100) * 36, 1)
                gunas_not_matched = round(36 - gunas_matched, 1)
                
                st.subheader("📊 Traditional Guna Scorecard")
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric(label="✅ Gunas Matched", value=f"{gunas_matched} / 36")
                with c2:
                    st.metric(label="❌ Gunas Not Matched", value=f"{gunas_not_matched} / 36")
                with c3:
                    st.metric(label="📈 Percentage Compatibility", value=f"{int(percentage_score)}%")
                
                st.subheader("🗣️ Match Interpretation in Plain English:")
                if gunas_matched >= 25.0:
                    st.balloons()
                    st.success(f"🌟 **Excellent Match ({gunas_matched} Gunas):** This is an exceptionally high compatibility level! Your emotional temperaments and long-term goals are tightly aligned, supporting a harmonious partnership.")
                elif gunas_matched >= 18.0:
                    st.info(f"⚖️ **Good Balanced Match ({gunas_matched} Gunas):** This safely passes the traditional minimum requirement of 18 Gunas. You share enough foundational compatibility to handle normal adjustments smoothly.")
                else:
                    st.warning(f"⚠️ **High Adjustment Required ({gunas_matched} Gunas):** This falls below the traditional 18 benchmark. Your baseline biological and communication patterns operate differently, indicating that patience and extra communication will be needed.")
                
            except Exception as e:
                st.error(f"Match report failed: {e}")

# ==========================================
# TAB 3: LIFE & MATERIAL DESIRES
# ==========================================
with tab3:
    st.header("💼 Career Prospects & 🏠 House Building Possibilities")
    st.markdown("Analyze how the structural layouts of your natal houses affect your professional growth and real estate potential.")
    
    loc_p = st.text_input("Confirm Your Birth City", "Mumbai", key="prop_loc")
    time_p = st.text_input("Confirm Your Birth Time", "14:30", key="prop_time")
    date_p = st.text_input("Confirm Your Birth Date", "25/10/1992", key="prop_date")
    
    if st.button("Analyze Career & Property Potential"):
        with st.spinner("Scanning material houses..."):
            try:
                p_geo_res = Calculate.AddressToGeoLocation(loc_p + ", India")
                p_geo = p_geo_res.get("Payload") if isinstance(p_geo_res, dict) else p_geo_res.Payload
                p_time_obj = Time(f"{time_p} {date_p} +05:30", p_geo)
                
                # Clean, direct extraction methods
                h4_sign = Calculate.HouseSignName(HouseName.House4, p_time_obj)
                h10_sign = Calculate.HouseSignName(HouseName.House10, p_time_obj)
                
                st.subheader("💼 1. Job, Professional Stability & Career Tracks")
                st.markdown(f"""
                Your professional layout operates via the **10th House (Karma Sthana)**, which settles in the sign of **{h10_sign}**. 
                
                **What this means in plain English:** This layout favors finding structural stability when pursuing paths with measurable paths for upward growth. Progression windows are most likely to expand when your ongoing dasha timelines trigger elements tied to your tenth domain.
                """)
                
                st.subheader("🏠 2. House Construction, Land, & Property Possibilities")
                st.markdown(f"""
                In Vedic astrology, real estate, vehicle investments, and building private homes are governed by the **4th House (Sukha Sthana)**, falling in **{h4_sign}**.
                
                **What this means in plain English:** Having a stable placement in this domain indicates strong foundational support for long-term real estate acquisition. Property investments or building modifications are highlighted when supportive planetary periods or transits trigger your chart's fourth quadrant.
                """)
                
            except Exception as e:
                st.error(f"Could not calculate structural properties: {e}")

# ==========================================
# TAB 4: DAILY PANCHANGA
# ==========================================
with tab4:
    st.header("Live Cosmic Weather (Today's Indian Panchanga)")
    t_loc = st.text_input("Your Current Location (India Only)", "Mumbai", key="t_loc")
    
    if st.button("Get Today's Transit Insights"):
        with st.spinner("Reading live transits..."):
            try:
                today_geo_res = Calculate.AddressToGeoLocation(t_loc + ", India")
                today_geo = today_geo_res.get("Payload") if isinstance(today_geo_res, dict) else today_geo_res.Payload
                
                now_time = datetime.datetime.now().strftime("%H:%M %d/%m/%Y +05:30")
                today_time_obj = Time(now_time, today_geo)
                
                # direct parsing parameters to ensure server stability
                moon_constellation = Calculate.MoonConstellation(today_time_obj)
                
                st.success(f"Loaded live transits for exact timestamp: {now_time}")
                st.info(f"🌌 Active Lunar Nakshatra: {moon_constellation}")
                
                st.subheader("🗣️ Daily Guidance Translation:")
                st.write(f"""
                Today, the Moon transits through **{moon_constellation}**. In plain English, this is an optimal cycle to consolidate running projects, clear up your workspace, and prioritize reflective planning over starting high-risk initiatives.
                """)
            except Exception as e:
                st.error(f"Could not load transit analytics: {e}")
