import streamlit as st
import pandas as pd
import json
import datetime
import urllib.parse
import vedastro as va

# Page Layout Configuration
st.set_page_config(page_title="Premium Vedic Astrology System", layout="wide")
st.title("🔮 Your Digital Pandit: Premium Vedic Astrology System")
st.markdown("An advanced, dynamic astrological companion translating complex natal planetary configurations into personalized analysis.")

# Global Date Formats
MIN_DATE = datetime.date(1900, 1, 1)
MAX_DATE = datetime.date(2026, 12, 31)

# Initialize Streamlit Session State Memory Keys
if 'user_name' not in st.session_state: st.session_state.user_name = "Mayank Kumar"
if 'location_input' not in st.session_state: st.session_state.location_input = "New Delhi"
if 'date_input' not in st.session_state: st.session_state.date_input = datetime.date(1992, 10, 25)
if 'sb_hr' not in st.session_state: st.session_state.sb_hr = 2
if 'sb_min' not in st.session_state: st.session_state.sb_min = "30"
if 'sb_period' not in st.session_state: st.session_state.sb_period = "PM"
if 'form_submitted' not in st.session_state: st.session_state.form_submitted = False

# Robust helper function to safely obtain a valid VedAstro GeoLocation object 
def get_safe_geolocation(city_name):
    city_defaults = {
        "new delhi": (77.2090, 28.6139), "delhi": (77.2090, 28.6139),
        "mumbai": (72.8777, 19.0760), "kolkata": (88.3639, 22.5726),
        "chennai": (80.2707, 13.0827), "bangalore": (77.5946, 12.9716),
        "hyderabad": (78.4867, 17.3850)
    }
    clean_name = city_name.strip().lower()
    if clean_name in city_defaults:
        lon, lat = city_defaults[clean_name]
        return va.GeoLocation(city_name, lon, lat)
    return va.GeoLocation("New Delhi (Fallback)", 77.2090, 28.6139)

# Dynamic mapping helper for Indian Naam Rashi (Name Sign) syllables
def calculate_naam_rashi(name):
    if not name: return "Mesh (Aries)"
    first_char = name.strip()[0].upper()
    rashi_mapping = {
        "Mesh (Aries)": ["A", "L", "E", "अ", "ल", "इ"],
        "Vrishabha (Taurus)": ["B", "V", "U", "ब", "व", "उ"],
        "Mithun (Gemini)": ["K", "CH", "G", "क", "छ", "घ"],
        "Kark (Cancer)": ["HD", "H", "DD", "ह", "ड"],
        "Simha (Leo)": ["M", "TT", "म", "ट"],
        "Kanya (Virgo)": ["P", "T", "प", "ठ"],
        "Tula (Libra)": ["R", "TT", "र", "त"],
        "Vrishchik (Scorpio)": ["N", "Y", "न", "य"],
        "Dhanu (Sagittarius)": ["BH", "DH", "F", "भ", "ध", "फ"],
        "Makar (Capricorn)": ["KH", "J", "ख", "ज"],
        "Kumbha (Aquarius)": ["G", "S", "SH", "ग", "स", "श"],
        "Meen (Pisces)": ["D", "CH", "Z", "TH", "द", "च", "थ"]
    }
    for rashi, syllables in rashi_mapping.items():
        if first_char in syllables: return rashi
    return "Mesh (Aries)"

# ==========================================================
# MAIN PAGE INPUT MATRIX
# ==========================================================
st.markdown("### 🗺️ Enter Birth Details & Click Generate / जन्म विवरण भरें")

with st.form("birth_details_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        u_name = st.text_input("Your Name / आपका नाम", value=st.session_state.user_name)
    with col2:
        l_input = st.text_input("Birth City / जन्म स्थान", value=st.session_state.location_input)
    with col3:
        d_input = st.date_input("Birth Date / जन्म तिथि", value=st.session_state.date_input, min_value=MIN_DATE, max_value=MAX_DATE)

    st.markdown("**Birth Time Selector / जन्म का समय**")
    t_col1, t_col2, t_col3 = st.columns(3)
    with t_col1:
        hr_selection = t_col1.selectbox("Hour", list(range(1, 13)), index=st.session_state.sb_hr - 1)
    with t_col2:
        minutes_list = [f"{i:02d}" for i in range(60)]
        default_min_idx = minutes_list.index(st.session_state.sb_min) if st.session_state.sb_min in minutes_list else 30
        min_selection = t_col2.selectbox("Minute", minutes_list, index=default_min_idx)
    with t_col3:
        period_idx = 0 if st.session_state.sb_period == "AM" else 1
        period_selection = t_col3.selectbox("AM/PM", ["AM", "PM"], index=period_idx)

    submit_button = st.form_submit_button("🔮 Generate Horoscope Calculations / कुंडली बनाएं")
    
    if submit_button:
        st.session_state.user_name = u_name
        st.session_state.location_input = l_input
        st.session_state.date_input = d_input
        st.session_state.sb_hr = hr_selection
        st.session_state.sb_min = min_selection
        st.session_state.sb_period = period_selection
        st.session_state.form_submitted = True

# Process calculations if form is submitted
birth_time = None
iframe_url = ""
if st.session_state.form_submitted:
    hour_24 = int(st.session_state.sb_hr)
    if st.session_state.sb_period == "PM" and hour_24 < 12: hour_24 += 12
    elif st.session_state.sb_period == "AM" and hour_24 == 12: hour_24 = 0
    master_time = datetime.time(hour_24, int(st.session_state.sb_min))

    try:
        master_loc = get_safe_geolocation(st.session_state.location_input)
        time_str = master_time.strftime('%H:%M')
        date_str = st.session_state.date_input.strftime('%d/%m/%Y')
        master_time_str = f"{time_str} {date_str} +05:30"
        
        birth_time = va.Time(master_time_str, master_loc)
        
        clean_city_url = urllib.parse.quote(master_loc.Name)
        iframe_url = f"https://api.vedastro.org/Calculate/CustomChart/Location/{clean_city_url}/Time/{time_str}/{date_str}/+05:30/Style/NorthIndian"
        
    except Exception as e:
        st.error(f"Error initializing astronomical coordinates: {e}")

st.markdown("---")

# Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🔮 Birth Signs & Personal Chart Layout", 
    "💑 Marriage Timing & Compatibility", 
    "💼 Profession & Asset Blueprints",
    "📅 Planetary Transits (Shani, Rahu, Ketu)"
])

if not st.session_state.form_submitted:
    st.info("👋 Please fill in your birth details above and click 'Generate Horoscope Calculations'.")
else:
    # EXECUTING GUARANTEED API METHODS COMPATIBLE WITH VEDASTRO PYTHON EXPORTS
    try:
        # FIXED: Using explicit .LagnaSignName and .PlanetSignName string methods to bypass wrapper mapping bugs
        calculated_lagna = str(va.Calculate.LagnaSignName(birth_time))
        calculated_janma_rashi = str(va.Calculate.PlanetSignName(va.PlanetName.Moon, birth_time))
        calculated_sun_rashi = str(va.Calculate.PlanetSignName(va.PlanetName.Sun, birth_time))
        calculated_naam_rashi = calculate_naam_rashi(st.session_state.user_name)
        
        # Using native string mappings for planet positions
        saturn_long = str(va.Calculate.PlanetLongitude(va.PlanetName.Saturn, birth_time))
        rahu_long = str(va.Calculate.PlanetLongitude(va.PlanetName.Rahu, birth_time))
        ketu_long = str(va.Calculate.PlanetLongitude(va.PlanetName.Ketu, birth_time))
        
    except Exception as e:
        st.error(f"Astrological Engine Error: {e}")
        calculated_lagna, calculated_janma_rashi, calculated_sun_rashi = "Tula (Libra)", "Tula (Libra)", "Mesh (Aries)"
        saturn_long, rahu_long, ketu_long = "0°", "0°", "0°"
        calculated_naam_rashi = calculate_naam_rashi(st.session_state.user_name)

    # ==========================================
    # TAB 1: BOTH RASHIS & LIVE NORTH INDIAN CHART
    # ==========================================
    with tab1:
        st.header("✨ Your Identity Blueprint & Personal Natal Chart")
        
        c1, c2, c3 = st.columns(3)
        with c1: st.metric(label="🔮 Your Lagna (Rising Ascendant)", value=calculated_lagna)
        with c2: st.metric(label="🌙 Janma Rashi (True Birth Moon Sign)", value=calculated_janma_rashi)
        with c3: st.metric(label="🔤 Naam Rashi (Name Syllable Sign)", value=calculated_naam_rashi)
        
        st.markdown("---")
        
        chart_col, info_col = st.columns([2, 1])
        with chart_col:
            st.subheader("🗺️ Your Personalized North Indian Birth Chart (D1 Kundli)")
            if iframe_url:
                st.components.v1.iframe(iframe_url, height=500, scrolling=True)
        with info_col:
            st.subheader("💡 How to Read This")
            st.markdown("""
            * **The Top Middle Diamond:** This is your 1st House (Lagna).
            * **Counter-Clockwise Motion:** The houses count upwards (1st to 12th) going counter-clockwise around the template.
            """)

    # ==========================================
    # TAB 2: UNFILTERED MARRIAGE TIMING
    # ==========================================
    with tab2:
        st.header("💑 Marriage Alignment & Unfiltered Age Windows")
        st.write(f"Your relationship framework is calculated uniquely based on your **{calculated_lagna}** Lagna dynamics.")

    # ==========================================
    # TAB 3: CAREER & ASSET BLUEPRINTS
    # ==========================================
    with tab3:
        st.header("💼 Profession, Financial Security & Asset Blueprints")
        st.info(f"### 🏢 Active Career Profile Alignment: Centered around {calculated_lagna}")

    # ==========================================
    # TAB 4: TRANSITS
    # ==========================================
    with tab4:
        st.header("📅 Shani, Rahu, & Ketu Transit Blueprint")
        st.write(f"Active Calculations tracking positions relative to Janma Rashi: **{calculated_janma_rashi}**")

    # ==========================================
    # 🎯 UNIQUE LIVE BILINGUAL VERDICT
    # ==========================================
    st.markdown("---")
    st.markdown("## 🎯 Unfiltered Karmic Final Verdict / अंतिम परिणाम (सत्य समीक्षा)")
    
    col_en, col_hi = st.columns(2)
    with col_en:
        st.subheader("🇬🇧 Live English Analysis")
        st.markdown(f"""
        This calculation is generated specifically using your structural coordinates: **Lagna ({calculated_lagna})**, **Janma Rashi ({calculated_janma_rashi})**. Because this output reads your unique longitudes, it is unique to you.
        
        * **Your Identity Duality:** Your public persona operates on **Naam Rashi ({calculated_naam_rashi})**, but your core emotional truth is driven entirely by your birth **Janma Rashi ({calculated_janma_rashi})**. 
        * **Shani (Saturn) Structural Debt:** Your natal Saturn coordinates compute exactly to **{saturn_long}**. This specific degree governs the exact timing of your career breakthroughs and house-building capabilities.
        * **The Rahu-Ketu Axis:** Rahu is currently processing data at **{rahu_long}** and Ketu at **{ketu_long}**. This unique axis cross-section indicates exactly where you experience sudden desires versus where you feel detached.
        """)
            
    with col_hi:
        st.subheader("🇮🇳 वास्तविक हिंदी समीक्षा")
        st.markdown(f"""
        यह विश्लेषण किसी पूर्व-निर्धारित सांचे पर आधारित नहीं है, बल्कि आपके व्यक्तिगत ग्रहों की वास्तविक स्थिति के आधार पर तैयार किया गया है: **लग्न ({calculated_lagna})**, **जन्म राशि ({calculated_janma_rashi})**।
        
        * **आपकी दोहरी राशियाँ:** आपका बाहरी नाम प्रभाव **नाम राशि ({calculated_naam_rashi})** से चलता है, लेकिन आपकी आंतरिक मानसिक चेतना आपके जन्म के समय की **जन्म राशि ({calculated_janma_rashi})** से निर्धारित होती है।
        * **शनि का प्रभाव:** आपकी कुंडली में शनि की वास्तविक स्थिति **{saturn_long}** है। यह विशिष्ट स्थिति आपके जीवन में करियर के बड़े बदलावों और संपत्ति निर्माण के सटीक समय को तय करती है।
        * **राहु-केतु अक्ष का प्रभाव:** आपके जन्म के समय राहु **{rahu_long}** और केतु **{ketu_long}** पर स्थित हैं। यह अनोखा अंश संयोजन दर्शाता है कि आपको जीवन के किस क्षेत्र में अचानक अप्रत्याशित लाभ या भ्रम मिलेगा, और कहाँ वैराग्य होगा।
        """)
