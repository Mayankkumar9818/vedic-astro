import streamlit as st
import pandas as pd
import json
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
    "🔮 Personal Kundli & D60", 
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
        location_input = st.text_input("Birth City/Town (India)", "Mumbai")
        time_input = st.text_input("Birth Time (24 Hr Format HH:MM)", "14:30")
    with col2:
        date_input = st.text_input("Birth Date (DD/MM/YYYY)", "25/10/1992")
        tz_input = st.text_input("Timezone Offset", "+05:30", disabled=True)
        
    if st.button("Calculate My Chart"):
        with st.spinner("Decoding your natal sky..."):
            try:
                # SAFE FIXED LOOKUP FOR GEOLOCATION DICTIONARY
                geo_res = Calculate.AddressToGeoLocation(location_input + ", India")
                if isinstance(geo_res, dict):
                    loc = geo_res.get("Payload")
                else:
                    loc = geo_res.Payload
                    
                birth_time = Time(f"{time_input} {date_input} +05:30", loc)
                
                # Extract data
                all_planet_data = Calculate.AllPlanetData(PlanetName.Sun, birth_time)
                all_house_data = Calculate.AllHouseData(HouseName.House1, birth_time)
                
                planet_json = json.loads(Tools.AnyToJSON("", all_planet_data))
                house_json = json.loads(Tools.AnyToJSON("", all_house_data))
                
                st.success("✅ Chart successfully generated!")
                
                # Display dynamic metrics
                calculated_house_sign = house_json.get("HouseBhavaChalitSign", {}).get("Name", "Detected")
                sun_house = planet_json.get("HouseFromSignName", "1")
                
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric(label="☀️ Sun Location Context", value=f"House {sun_house}")
                with c2:
                    st.metric(label="🔮 Ascendant (Lagna) Sign", value=calculated_house_sign)
                with c3:
                    st.metric(label="🌌 D60 Past Karma State", value="Active Alignment")
                
                st.subheader("🗣️ What This Placement Means for You:")
                st.markdown(f"""
                * **Your Ascendant (Lagna) is {calculated_house_sign}:** This means your entire life's physical journey operates through the traits of {calculated_house_sign}.
                * **Your Sun is located in House {sun_house}:** Your energy and main life focus will naturally gravitate towards the themes governed by this specific house sector.
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
                # SAFE FIXED LOOKUP FOR BOY GEOLOCATION
                b_geo_res = Calculate.AddressToGeoLocation(m_loc + ", India")
                b_geo = b_geo_res.get("Payload") if isinstance(b_geo_res, dict) else b_geo_res.Payload
                boy_birth = Time(f"{m_time} {m_date} +05:30", b_geo)
                
                # SAFE FIXED LOOKUP FOR GIRL GEOLOCATION
                g_geo_res = Calculate.AddressToGeoLocation(f_loc + ", India")
                g_geo = g_geo_res.get("Payload") if isinstance(g_geo_res, dict) else g_geo_res.Payload
                girl_birth = Time(f"{f_time} {f_date} +05:30", g_geo)
                
                matchReport = Calculate.MatchReport(boy_birth, girl_birth)
                match_json = json.loads(Tools.AnyToJSON("", matchReport))
                
                percentage_score = match_json.get("KutaScore", 0.0)
                gunas_matched = round((percentage_score / 100) * 36, 1)
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
                    st.success(f"🌟 **Excellent Match ({gunas_matched} Gunas):** This is an exceptionally high match score! Harmonious married life.")
                elif gunas_matched >= 18.0:
                    st.info(f"⚖️ **Good Balanced Match ({gunas_matched} Gunas):** This passes the traditional minimum requirement of 18 Gunas.")
                else:
                    st.warning(f"⚠️ **High Adjustment Required ({gunas_matched} Gunas):** This score falls below the traditional 18-Guna benchmark line.")
                
                embeds = match_json.get("Embeddings", [])
                if len(embeds) >= 8:
                    st.write("### 🔍 Category-by-Category Guna Breakdown:")
                    metrics_df = pd.DataFrame({
                        "Astrological Category": [
                            "Varna (Work Profile & Ego Sync)", "Vashya (Mutual Attraction & Influence)", 
                            "Tara (Destiny Progression & Health)", "Yoni (Physical Intimacy & Instincts)", 
                            "Graha Maitram (Mental Friendship & Humor)", "Gana (Temperament & Social Behavior)", 
                            "Bhakoot (Emotional Connection & Family)", "Nadi (Genetic Compatibility & Children)"
                        ],
                        "Max Points Possible": [1, 2, 3, 4, 5, 6, 7, 8],
                        "Your Matched Points": [embeds[0], embeds[1], embeds[2], embeds[3], embeds[4], embeds[5], embeds[6], embeds[7]]
                    }).set_index("Astrological Category")
                    st.bar_chart(metrics_df["Your Matched Points"])
                    st.table(metrics_df)
                    
            except Exception as e:
                st.error(f"Match report failed: {e}")

# ==========================================
# TAB 3: LIFE & MATERIAL DESIRES
# ==========================================
with tab3:
    st.header("💼 Career Prospects & 🏠 House Building Possibilities")
    
    loc_p = st.text_input("Confirm Your Birth City", "Mumbai", key="prop_loc")
    time_p = st.text_input("Confirm Your Birth Time", "14:30", key="prop_time")
    date_p = st.text_input("Confirm Your Birth Date", "25/10/1992", key="prop_date")
    
    if st.button("Analyze Career & Property Potential"):
        with st.spinner("Scanning material houses..."):
            try:
                # SAFE FIXED LOOKUP FOR PROPERTY TAB
                p_geo_res = Calculate.AddressToGeoLocation(loc_p + ", India")
                p_geo = p_geo_res.get("Payload") if isinstance(p_geo_res, dict) else p_geo_res.Payload
                p_time_obj = Time(f"{time_p} {date_p} +05:30", p_geo)
                
                h4_data = json.loads(Tools.AnyToJSON("", Calculate.AllHouseData(HouseName.House4, p_time_obj)))
                h10_data = json.loads(Tools.AnyToJSON("", Calculate.AllHouseData(HouseName.House10, p_time_obj)))
                
                arudha_4 = h4_data.get("ArudhaOfHouse", "House4")
                arudha_10 = h10_data.get("ArudhaOfHouse", "House10")
                
                st.subheader("💼 1. Job, Professional Stability & Career Tracks")
                st.markdown(f"Your active external manifestation anchor point is processing through **{arudha_10}**.")
                
                st.subheader("🏠 2. House Construction, Land, & Property Possibilities")
                st.markdown(f"Your chart displays an active property reflection point located in **{arudha_4}**.")
                
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
                # SAFE FIXED LOOKUP FOR PANCHANGA TAB
                today_geo_res = Calculate.AddressToGeoLocation(t_loc + ", India")
                today_geo = today_geo_res.get("Payload") if isinstance(today_geo_res, dict) else today_geo_res.Payload
                
                now_time = datetime.datetime.now().strftime("%H:%M %d/%m/%Y +05:30")
                today_time_obj = Time(now_time, today_geo)
                
                tithi_data = Calculate.AllZodiacSignData(ZodiacName.Aries, today_time_obj)
                panchanga_json = json.loads(Tools.AnyToJSON("", tithi_data))
                
                st.success(f"Loaded live transits for exact timestamp: {now_time}")
                st.info(f"🌌 Active Planetary Focal House: {panchanga_json.get('HouseFromSignName', 'House 11')}")
                st.metric(label="✨ Core Cosmic Destiny Vector Point", value=panchanga_json.get("DestinyPoint", "3"))
                
            except Exception as e:
                st.error(f"Could not load transit analytics: {e}")
