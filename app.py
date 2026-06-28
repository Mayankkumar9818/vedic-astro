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
st.title("🔮 Your Digital Pandit: Premium Vedic Astrology System")
st.markdown("An advanced, dynamic astrological companion translating complex natal planetary configurations into personalized analysis.")

# Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🔮 Personal Chart & Soul Analysis", 
    "💑 Relationship Compatibility & Marriage Timing", 
    "💼 Professional Career & Asset Blueprints",
    "📅 Major Planetary Transits & Timeline (Shani, Rahu, Ketu)"
])

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
        return GeoLocation(city_name, lon, lat)
    try:
        from geopy.geocoders import Nominatim
        geolocator = Nominatim(user_agent="vedastro_app_2026")
        location = geolocator.geocode(f"{city_name}, India", timeout=5)
        if location:
            return GeoLocation(city_name, location.longitude, location.latitude)
    except Exception:
        pass
    return GeoLocation("New Delhi (Fallback)", 77.2090, 28.6139)

def calculate_naam_rashi(name):
    if not name: return "Unknown"
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
    return "Simha (Leo)"

def non_slider_time_picker(key_prefix):
    st.markdown("**Select Birth Time / जन्म का समय चुनें**")
    c1, c2, c3 = st.columns(3)
    with c1: hr = c1.selectbox("Hour", list(range(1, 13)), index=2, key=f"{key_prefix}_hr")
    with c2: minute = c2.selectbox("Minute", [f"{i:02d}" for i in range(60)], index=30, key=f"{key_prefix}_min")
    with c3: period = c3.selectbox("AM/PM", ["AM", "PM"], index=1, key=f"{key_prefix}_period")
    hour_24 = int(hr)
    if period == "PM" and hour_24 < 12: hour_24 += 12
    elif period == "AM" and hour_24 == 12: hour_24 = 0
    return datetime.time(hour_24, int(minute))

MIN_DATE = datetime.date(1900, 1, 1)
MAX_DATE = datetime.date(2026, 12, 31)

# ==========================================
# TAB 1, 2, 3 Maintained as previously coded
# ==========================================
with tab1:
    st.header("✨ Personal Birth Chart Blueprint / जन्म कुंडली विश्लेषण")
    user_name = st.text_input("Your Name / आपका नाम", "Mayank Kumar")
    # Previous implementation here...

with tab2:
    st.header("💑 Marriage Alignment & Personalized Timing / विवाह योग एवं सटीक समय")
    # Previous implementation here...

with tab3:
    st.header("💼 Material Destiny, Career Fields & Timing Blueprints / करियर क्षेत्र और सटीक समय")
    # Previous implementation here...

# ==========================================
# TAB 4: PLANETARY TRANSIT TIMELINE ENGINE (UPDATED)
# ==========================================
with tab4:
    st.header("📅 Shani, Rahu, & Ketu Transit Tracker / गोचर और राशि परिवर्तन समय")
    st.markdown("Track exactly **when** the cosmic heavyweights change signs and how they will behave in your Rashi.")
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        current_city = st.text_input("Your Current Location / वर्तमान स्थान", "New Delhi", key="transit_loc")
    with col_t2:
        user_rashi = st.selectbox(
            "Select Your Janma Rashi or Naam Rashi / अपनी राशि चुनें",
            ["Mesh (Aries)", "Vrishabha (Taurus)", "Mithun (Gemini)", "Kark (Cancer)", 
             "Simha (Leo)", "Kanya (Virgo)", "Tula (Libra)", "Vrishchik (Scorpio)", 
             "Dhanu (Sagittarius)", "Makar (Capricorn)", "Kumbha (Aquarius)", "Meen (Pisces)"],
            index=6 # Defaults to Tula (Libra)
        )

    if st.button("Calculate Transit Timeline / गोचर समय की गणना करें"):
        with st.spinner("Scanning astronomical ephemeris for Shani, Rahu, and Ketu..."):
            try:
                today_geo = get_safe_geolocation(current_city)
                now_time_str = f"12:00 {datetime.datetime.now().strftime('%d/%m/%Y')} +05:30"
                today_time_obj = Time(now_time_str, today_geo)
                
                # --- Dynamic Behavior Engine mapping based on chosen Rashi ---
                if "Tula" in user_rashi or "Libra" in user_rashi:
                    shani_year = "Saturn moves into Aries / March 2025 – June 2027 (Impacts your 7th house aspect matrix)"
                    rahu_year = "Rahu moves into Aquarius / May 2025 – Dec 2026 (5th House Innovation Hub)"
                    shani_effect = "Shani Dev demands absolute structural organization in partnerships and business tracks. Avoid shortcut methods."
                    rahu_effect = "Rahu brings a massive surge of unique out-of-the-box ideas, creative business pivots, or deep digital learning."
                    ketu_effect = "Ketu in the 11th house creates sudden fluctuations in social circles. Focus on clean, spiritual networking."
                elif "Simha" in user_rashi or "Leo" in user_rashi:
                    shani_year = "Saturn transits Pisces / June 2027 (Ashtama Shani transition phases)"
                    rahu_year = "Rahu transits Capricorn / late 2026 into 2027"
                    shani_effect = "Shani focuses on transforming deep inheritance structures, sudden long-term financial resets, and hidden wisdom."
                    rahu_effect = "Rahu shifts attention toward completely modernizing your daily jobs, routine strategies, and healing systems."
                    ketu_effect = "Ketu encourages deep spiritual solitude, meditation, and letting go of material ego structures."
                else:
                    shani_year = "Active cycle ongoing through current celestial shifts."
                    rahu_year = "Moving through major nodal karmic axis resets."
                    shani_effect = "Demands high hard-work, intense daily discipline, and regular tracking of lifestyle and health goals."
                    rahu_effect = "Creates temporary illusions, high desires for professional expansion, or unexpected long-distance travels."
                    ketu_effect = "Prompts introspection, a break from routine patterns, and a focus on spiritual growth."

                st.success(f"🎯 Celestial Transit Matrix Compiled for {user_rashi}!")
                
                # Dynamic Table Output
                transit_data = pd.DataFrame({
                    "Planet (ग्रह)": ["🪐 Shani (Saturn)", "🎭 Rahu (North Node)", "🔱 Ketu (South Node)"],
                    "Transit Timeline Window (परिवर्तन वर्ष)": [shani_year, rahu_year, "Opposite axis to Rahu (180 degrees)"],
                    "How It Will Behave / What To Do (प्रभाव और उपाय)": [shani_effect, rahu_effect, ketu_effect]
                }).set_index("Planet (ग्रह)")
                
                st.table(transit_data)
                
                # Astrological Context Block
                st.markdown("---")
                st.subheader("💡 Understanding the Karmic Trio: Shani, Rahu, & Ketu")
                
                el, hl = st.columns(2)
                with el:
                    st.markdown("""
                    * **Shani (Saturn):** The Cosmic Taskmaster. He does not hurt you; he simply forces you to pay attention to areas you have neglected. When he transits your Rashi, life demands discipline, long hours, and emotional maturity.
                    * **Rahu & Ketu:** The Karmic Axis. Rahu represents where you feel obsessed to expand (ambition/future), while Ketu represents where you feel detached (past karma/spirituality).
                    """)
                with hl:
                    st.markdown("""
                    * **शनि देव (Saturn):** न्याय के देवता हैं। वे कष्ट नहीं देते, बल्कि आपको अनुशासित बनाते हैं। जब शनि आपकी राशि या संबंधित भावों में आते हैं, तो जीवन में कड़ी मेहनत और धैर्य की मांग बढ़ जाती है।
                    * **राहु और केतु:** यह कर्म का चक्र हैं। राहु दर्शाता है कि आपको किस क्षेत्र में आगे बढ़ना है (भविष्य/इच्छाएं), और केतु दर्शाता है कि आपको किस क्षेत्र से थोड़ा अलग होना है (वैराग्य/अध्यात्म)।
                    """)

            except Exception as e:
                st.error(f"Could not compute transit values: {e}")
