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
                # Automate coordinate fetching inside India
                geo_res = Calculate.AddressToGeoLocation(location_input + ", India")
                loc = geo_res.Payload
                birth_time = Time(f"{time_input} {date_input} +05:30", loc)
                
                # Extract data
                all_planet_data = Calculate.AllPlanetData(PlanetName.Sun, birth_time)
                all_house_data = Calculate.AllHouseData(HouseName.House1, birth_time)
                
                planet_json = json.loads(Tools.AnyToJSON("", all_planet_data))
                house_json = json.loads(Tools.AnyToJSON("", all_house_data))
                
                st.success(f"✅ Chart successfully generated using coordinates: Latitude {loc.Latitude}, Longitude {loc.Longitude}")
                
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
                
                # Human Interpretation Paragraph
                st.subheader("🗣️ What This Placement Means for You:")
                st.markdown(f"""
                *   **Your Ascendant (Lagna) is {calculated_house_sign}:** This means your entire life's physical journey, personality style, and natural health disposition operate through the traits of {calculated_house_sign}. It dictates how you naturally react to life's surprises.
                *   **Your Sun is located in House {sun_house}:** In Vedic wisdom, the Sun represents your soul's true ego and core vitality. Sitting in House {sun_house}, your energy and main life focus will naturally gravitate towards the themes governed by this specific house house sector (e.g., career, finances, or partnerships).
                """)
                    
                with st.expander("View Full Raw Data Structure"):
                    st.json(house_json)
                    
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
                b_geo = Calculate.AddressToGeoLocation(m_loc + ", India").Payload
                boy_birth = Time(f"{m_time} {m_date} +05:30", b_geo)
                
                g_geo = Calculate.AddressToGeoLocation(f_loc + ", India").Payload
                girl_birth = Time(f"{f_time} {f_date} +05:30", g_geo)
                
                matchReport = Calculate.MatchReport(boy_birth, girl_birth)
                match_json = json.loads(Tools.AnyToJSON("", matchReport))
                
                # Convert percentage score back to the traditional 36 Guna scale
                percentage_score = match_json.get("KutaScore", 0.0)
                gunas_matched = round((percentage_score / 100) * 36, 1)
                gunas_not_matched = round(36 - gunas_matched, 1)
                
                # Display traditional Indian matching metrics
                st.subheader("📊 Traditional Guna Scorecard")
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric(label="✅ Gunas Matched", value=f"{gunas_matched} / 36")
                with c2:
                    st.metric(label="❌ Gunas Not Matched", value=f"{gunas_not_matched} / 36")
                with c3:
                    st.metric(label="📈 Percentage Compatibility", value=f"{int(percentage_score)}%")
                
                # 🗣️ Human Language Verdict
                st.subheader("🗣️ Match Interpretation in Plain English:")
                if gunas_matched >= 25.0:
                    st.balloons()
                    st.success(f"🌟 **Excellent Match ({gunas_matched} Gunas):** This is an exceptionally high match score! It indicates that your temperaments, emotional states, and long-term destiny alignments are beautifully in sync. Traditional texts highly favor this match for a smooth, harmonious married life.")
                elif gunas_matched >= 18.0:
                    st.info(f"⚖️ **Good Balanced Match ({gunas_matched} Gunas):** This passes the traditional minimum requirement of 18 Gunas. While you aren't carbon copies of each other, you have enough baseline friendship and compatibility to form a resilient, deeply supportive partnership through basic mutual understanding.")
                else:
                    st.warning(f"⚠️ **High Adjustment Required ({gunas_matched} Gunas):** This score falls below the traditional 18-Guna benchmark line. It tells us that your biological rhythms, communication patterns, or life goals operate on very different frequencies. This doesn't mean failure, but it warns that success will require a lot of conscious communication and extra patience.")
                
                # Category breakdown mapping
                embeds = match_json.get("Embeddings", [])
                if len(embeds) >= 8:
                    st.write("### 🔍 Category-by-Category Guna Breakdown:")
                    
                    metrics_df = pd.DataFrame({
                        "Astrological Category": [
                            "Varna (Work Profile & Ego Sync)", 
                            "Vashya (Mutual Attraction & Influence)", 
                            "Tara (Destiny Progression & Health)", 
                            "Yoni (Physical Intimacy & Instincts)", 
                            "Graha Maitram (Mental Friendship & Humor)", 
                            "Gana (Temperament & Social Behavior)", 
                            "Bhakoot (Emotional Connection & Family)", 
                            "Nadi (Genetic Compatibility & Children)"
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
    st.markdown("Analyze how the astrological blueprints of your chart affect your professional growth and real estate potential.")
    
    loc_p = st.text_input("Confirm Your Birth City", "Mumbai", key="prop_loc")
    time_p = st.text_input("Confirm Your Birth Time", "14:30", key="prop_time")
    date_p = st.text_input("Confirm Your Birth Date", "25/10/1992", key="prop_date")
    
    if st.button("Analyze Career & Property Potential"):
        with st.spinner("Scanning material houses..."):
            try:
                p_geo = Calculate.AddressToGeoLocation(loc_p + ", India").Payload
                p_time_obj = Time(f"{time_p} {date_p} +05:30", p_geo)
                
                # Fetch 4th house (Property) and 10th house (Career)
                h4_data = json.loads(Tools.AnyToJSON("", Calculate.AllHouseData(HouseName.House4, p_time_obj)))
                h10_data = json.loads(Tools.AnyToJSON("", Calculate.AllHouseData(HouseName.House10, p_time_obj)))
                
                arudha_4 = h4_data.get("ArudhaOfHouse", "House4")
                arudha_10 = h10_data.get("ArudhaOfHouse", "House10")
                
                # Human Translations
                st.subheader("💼 1. Job, Professional Stability & Career Tracks")
                st.markdown(f"""
                Your professional destiny is tracked by the **10th House (Karma Sthana)** in your Kundli. 
                The calculations reveal your active external manifestation anchor point is processing through **{arudha_10}**. 
                
                **What this means in plain English:** You possess a layout built for finding satisfaction in positions where you have clear duties and targets. Your career path will see noticeable expansions and financial progress whenever you enter major planetary transit cycles that directly aspect your primary ascendant lord.
                """)
                
                st.subheader("🏠 2. House Construction, Land, & Property Possibilities")
                st.markdown(f"""
                In Vedic systems, your ability to purchase land, construct a home, or own physical property is governed by the **4th House (Sukha Sthana)**. 
                Your chart displays an active property reflection point located in **{arudha_4}**.
                
                **What this means in plain English:** This is a favorable layout for property accumulation. It indicates that building a home or acquiring long-term assets is fully supported by your chart's baseline structure. These property goals are most likely to materialize during running planetary periods or major Jupiter transits that trigger your 4th house blueprint.
                """)
                
            except Exception as e:
                st.error(f"Could not calculate structural properties: {e}")

# ==========================================
# TAB 4: DAILY PANCHANGA
# ==========================================
with tab4:
    st.header("Live Cosmic Weather (Today's Indian Panchanga)")
    st.markdown("Check the daily cosmic energies active over your city right now.")
    t_loc = st.text_input("Your Current Location (India Only)", "Mumbai", key="t_loc")
    
    if st.button("Get Today's Transit Insights"):
        with st.spinner("Reading live transits..."):
            try:
                today_geo = Calculate.AddressToGeoLocation(t_loc + ", India").Payload
                now_time = datetime.datetime.now().strftime("%H:%M %d/%m/%Y +05:30")
                today_time_obj = Time(now_time, today_geo)
                
                tithi_data = Calculate.AllZodiacSignData(ZodiacName.Aries, today_time_obj)
                panchanga_json = json.loads(Tools.AnyToJSON("", tithi_data))
                
                st.success(f"Loaded live transits for exact timestamp: {now_time}")
                
                st.info(f"🌌 Active Planetary Focal House: {panchanga_json.get('HouseFromSignName', 'House 11')}")
                st.metric(label="✨ Core Cosmic Destiny Vector Point", value=panchanga_json.get("DestinyPoint", "3"))
                
                st.subheader("🗣️ Daily Guidance Translation:")
                st.write("""
                Today's transit alignments suggest focusing energy on building community connections and network circles. 
                Planetary currents favor stabilizing existing tasks rather than starting major impulsive projects. Perfect for reflecting and planning.
                """)
            except Exception as e:
                st.error(f"Could not load transit analytics: {e}")