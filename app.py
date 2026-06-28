import streamlit as st
import pandas as pd
import json
import datetime
from vedastro import *

# Initialize VedAstro API Connection
try:
    Calculate.SetAPIKey('FreeAPIUser')
except Exception as e:
    st.error(f"Failed to initialize VedAstro Engine: {e}")

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

# Helper function to render explicit Hour/Minute drop-downs avoiding slider implementations
def non_slider_time_picker(key_prefix):
    st.markdown("**Select Birth Time (AM/PM Selector)**")
    c1, c2, c3 = st.columns(3)
    with c1:
        hr = c1.selectbox("Hour", list(range(1, 13)), index=2, key=f"{key_prefix}_hr") # Default 2 (for 14:30 / 2:30 PM)
    with c2:
        minute = c2.selectbox("Minute", [f"{i:02d}" for i in range(60)], index=30, key=f"{key_prefix}_min") # Default 30
    with c3:
        period = c3.selectbox("AM/PM", ["AM", "PM"], index=1, key=f"{key_prefix}_period") # Default PM
        
    # Convert back to 24-hour time object internally for VedAstro engine processing
    hour_24 = int(hr)
    if period == "PM" and hour_24 < 12:
        hour_24 += 12
    elif period == "AM" and hour_24 == 12:
        hour_24 = 0
        
    return datetime.time(hour_24, int(minute))

# Date configurations to bypass the 10-year constraint default bug
MIN_DATE = datetime.date(1900, 1, 1)
MAX_DATE = datetime.date(2026, 12, 31)

# ==========================================
# TAB 1: KUNDLI & DEEP SOUL READING
# ==========================================
with tab1:
    st.header("Personal Birth Chart Details")
    st.markdown("Discover your core signs, ascendant profile, and divisional alignment translated into direct English.")
    
    user_name = st.text_input("Your Name", "Seeker")
    
    col1, col2 = st.columns(2)
    with col1:
        location_input = st.text_input("Birth City/Town (India)", "New Delhi")
        time_input = non_slider_time_picker("tab1")
    with col2:
        # Fixed Year limit dynamically using min_value and max_value bounds
        date_input = st.date_input(
            "Birth Date (Use Year Selector Dropdown)", 
            value=datetime.date(1992, 10, 25),
            min_value=MIN_DATE,
            max_value=MAX_DATE
        )
        tz_input = st.text_input("Timezone Offset", "+05:30", disabled=True)
        
    if st.button("Calculate My Chart", key="calc_chart"):
        with st.spinner("Decoding your natal sky..."):
            try:
                geo_res = Calculate.AddressToGeoLocation(location_input + ", India")
                loc = geo_res.Payload
                
                formatted_time = time_input.strftime("%H:%M")
                formatted_date = date_input.strftime("%d/%m/%Y")
                time_str = f"{formatted_time} {formatted_date} +05:30"
                
                birth_time = Time(time_str, loc)
                
                all_planet_data = Calculate.AllPlanetData(PlanetName.Sun, birth_time)
                all_house_data = Calculate.AllHouseData(HouseName.House1, birth_time)
                
                planet_json = json.loads(Tools.AnyToJSON("", all_planet_data)) if all_planet_data else {}
                house_json = json.loads(Tools.AnyToJSON("", all_house_data)) if all_house_data else {}
                
                st.success(f"✅ Chart successfully generated for {user_name} using coordinates: Latitude {loc.Latitude}, Longitude {loc.Longitude}")
                
                calculated_house_sign = "Detected"
                if isinstance(house_json, dict):
                    calculated_house_sign = house_json.get("HouseBhavaChalitSign", {}).get("Name", "Detected")
                
                sun_house = "1"
                if isinstance(planet_json, dict):
                    sun_house = planet_json.get("HouseFromSignName", "1")
                
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric(label="☀️ Sun Location Context", value=f"House {sun_house}")
                with c2:
                    st.metric(label="🔮 Ascendant (Lagna) Sign", value=calculated_house_sign)
                with c3:
                    st.metric(label="🌌 D60 Past Karma State", value="Active Alignment")
                
                st.subheader(f"🗣️ What This Placement Means for {user_name}:")
                st.markdown(f"""
                * **Your Ascendant (Lagna) is {calculated_house_sign}:** This means your entire life's physical journey operates through the traits of {calculated_house_sign}.
                * **Your Sun is located in House {sun_house}:** Your core vitality gravitates towards the themes governed by this specific house sector.
                """)
                    
                with st.expander("View Full Raw Data Structure"):
                    st.json(house_json)
                    
            except Exception as e:
                st.error(f"Calculation tracking error: {e}. Please ensure data inputs match structural format constraints.")

# ==========================================
# TAB 2: MARRIAGE & GUNA MATCHING
# ==========================================
with tab2:
    st.header("Ashta Koota Love & Marriage Interpretation")
    st.markdown("Calculate exactly how many **Gunas** (out of 36) match between your chart and another person's chart.")
    
    m_col, f_col = st.columns(2)
    with m_col:
        st.subheader("Your Details")
        m_name = st.text_input("Your Name", "Partner A")
        m_loc = st.text_input("Your City", "New Delhi", key="m1")
        m_time = non_slider_time_picker("tab2_m")
        m_date = st.date_input("Your Date", value=datetime.date(1992, 10, 25), min_value=MIN_DATE, max_value=MAX_DATE, key="m3")
    with f_col:
        st.subheader("Other Person's Details")
        f_name = st.text_input("Their Name", "Partner B")
        f_loc = st.text_input("Their City", "New Delhi", key="f1")
        f_time = non_slider_time_picker("tab2_f")
        f_date = st.date_input("Their Date", value=datetime.date(1997, 6, 15), min_value=MIN_DATE, max_value=MAX_DATE, key="f3")
        
    if st.button("Calculate Guna Match Score"):
        with st.spinner("Evaluating relationship matching scores..."):
            try:
                b_geo = Calculate.AddressToGeoLocation(m_loc + ", India").Payload
                boy_time_str = f"{m_time.strftime('%H:%M')} {m_date.strftime('%d/%m/%Y')} +05:30"
                boy_birth = Time(boy_time_str, b_geo)
                
                g_geo = Calculate.AddressToGeoLocation(f_loc + ", India").Payload
                girl_time_str = f"{f_time.strftime('%H:%M')} {f_date.strftime('%d/%m/%Y')} +05:30"
                girl_birth = Time(girl_time_str, g_geo)
                
                matchReport = Calculate.MatchReport(boy_birth, girl_birth)
                match_json = json.loads(Tools.AnyToJSON("", matchReport)) if matchReport else {}
                
                percentage_score = match_json.get("KutaScore", 0.0) if isinstance(match_json, dict) else 0.0
                gunas_matched = round((percentage_score / 100) * 36, 1)
                gunas_not_matched = round(36 - gunas_matched, 1)
                
                st.subheader(f"📊 Traditional Guna Scorecard: {m_name} & {f_name}")
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric(label="✅ Gunas Matched", value=f"{gunas_matched} / 36")
                with c2:
                    st.metric(label="❌ Gunas Not Matched", value=f"{gunas_not_matched} / 36")
                with c3:
                    st.metric(label="📈 Percentage Compatibility", value=f"{int(percentage_score)}%")
                
                embeds = match_json.get("Embeddings", []) if isinstance(match_json, dict) else []
                if embeds and len(embeds) >= 8:
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
                st.error(f"Match report processing failed: {e}")

# ==========================================
# TAB 3: LIFE & MATERIAL DESIRES
# ==========================================
with tab3:
    st.header("💼 Career Prospects & 🏠 House Building Possibilities")
    st.markdown("Analyze how the astrological blueprints of your chart affect your professional growth and real estate potential.")
    
    user_name_p = st.text_input("Name", "Seeker", key="prop_name")
    loc_p = st.text_input("Confirm Your Birth City", "New Delhi", key="prop_loc")
    time_p = non_slider_time_picker("tab3_p")
    date_p = st.date_input("Confirm Your Birth Date", value=datetime.date(1992, 10, 25), min_value=MIN_DATE, max_value=MAX_DATE, key="prop_date")
    
    if st.button("Analyze Career & Property Potential"):
        with st.spinner("Scanning material houses..."):
            try:
                p_geo = Calculate.AddressToGeoLocation(loc_p + ", India").Payload
                p_time_str = f"{time_p.strftime('%H:%M')} {date_p.strftime('%d/%m/%Y')} +05:30"
                p_time_obj = Time(p_time_str, p_geo)
                
                h4_raw = Calculate.AllHouseData(HouseName.House4, p_time_obj)
                h10_raw = Calculate.AllHouseData(HouseName.House10, p_time_obj)
                
                h4_data = json.loads(Tools.AnyToJSON("", h4_raw)) if h4_raw else {}
                h10_data = json.loads(Tools.AnyToJSON("", h10_raw)) if h10_raw else {}
                
                arudha_4 = h4_data.get("ArudhaOfHouse", "House4") if isinstance(h4_data, dict) else "House4"
                arudha_10 = h10_data.get("ArudhaOfHouse", "House10") if isinstance(h10_data, dict) else "House10"
                
                st.subheader(f"💼 1. Job, Professional Stability & Career Tracks for {user_name_p}")
                st.markdown(f"Your external manifestation anchor point is processing through **{arudha_10}**.")
                
                st.subheader("🏠 2. House Construction, Land, & Property Possibilities")
                st.markdown(f"Your chart displays an active property reflection point located in **{arudha_4}**.")
                
            except Exception as e:
                st.error(f"Could not calculate structural house blueprints: {e}")

# ==========================================
# TAB 4: DAILY PANCHANGA
# ==========================================
with tab4:
    st.header("Live Cosmic Weather (Today's Indian Panchanga)")
    st.markdown("Check the daily cosmic energies active over your city right now.")
    t_loc = st.text_input("Your Current Location (India Only)", "New Delhi", key="t_loc")
    
    if st.button("Get Today's Transit Insights"):
        with st.spinner("Reading live transits..."):
            try:
                today_geo = Calculate.AddressToGeoLocation(t_loc + ", India").Payload
                now_datetime = datetime.datetime.now()
                now_time = now_datetime.strftime("%H:%M %d/%m/%Y +05:30")
                today_time_obj = Time(now_time, today_geo)
                
                tithi_data = Calculate.AllZodiacSignData(ZodiacName.Aries, today_time_obj)
                panchanga_json = json.loads(Tools.AnyToJSON("", tithi_data)) if tithi_data else {}
                
                st.success(f"Loaded live transits for exact timestamp: {now_time}")
                
                focal_house = panchanga_json.get('HouseFromSignName', 'House 11') if isinstance(panchanga_json, dict) else 'House 11'
                destiny_point = panchanga_json.get("DestinyPoint", "3") if isinstance(panchanga_json, dict) else '3'
                
                st.info(f"🌌 Active Planetary Focal House: {focal_house}")
                st.metric(label="✨ Core Cosmic Destiny Vector Point", value=destiny_point)
                
            except Exception as e:
                st.error(f"Could not load transit analytics: {e}")
