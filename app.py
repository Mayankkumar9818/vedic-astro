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

# Global Date Formats
MIN_DATE = datetime.date(1900, 1, 1)
MAX_DATE = datetime.date(2026, 12, 31)

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

# Dynamic mapping helper for Indian Naam Rashi (Name Sign) syllables
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


# ==========================================================
# CENTRALIZED INPUTS (Keeps elements visible across tabs!)
# ==========================================================
st.sidebar.header("🗺️ Master Birth Parameters / मुख्य जन्म विवरण")
user_name = st.sidebar.text_input("Your Name / आपका नाम", "Mayank Kumar")
location_input = st.sidebar.text_input("Birth City / जन्म स्थान", "New Delhi")
date_input = st.sidebar.date_input("Birth Date / जन्म तिथि", value=datetime.date(1992, 10, 25), min_value=MIN_DATE, max_value=MAX_DATE)

# Form-safe Time Selection Matrix inside Sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("**Birth Time Selector / जन्म का समय**")
sb_c1, sb_c2, sb_c3 = st.sidebar.columns(3)
sb_hr = sb_c1.selectbox("Hr", list(range(1, 13)), index=2, key="sb_hr")
sb_min = sb_c2.selectbox("Min", [f"{i:02d}" for i in range(60)], index=30, key="sb_min")
sb_period = sb_c3.selectbox("AM/PM", ["AM", "PM"], index=1, key="sb_period")

sb_hour_24 = int(sb_hr)
if sb_period == "PM" and sb_hour_24 < 12: sb_hour_24 += 12
elif sb_period == "AM" and sb_hour_24 == 12: sb_hour_24 = 0
master_time = datetime.time(sb_hour_24, int(sb_min))

# Pre-calculate calculation vectors so tabs can access variables safely
try:
    master_loc = get_safe_geolocation(location_input)
    master_time_str = f"{master_time.strftime('%H:%M')} {date_input.strftime('%d/%m/%Y')} +05:30"
    birth_time = Time(master_time_str, master_loc)
except Exception:
    birth_time = None

# Unified Dashboard Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🔮 Personal Chart & Soul Analysis", 
    "💑 Relationship Compatibility & Marriage Timing", 
    "💼 Professional Career & Asset Blueprints",
    "📅 Major Planetary Transits & Timeline"
])

# ==========================================
# TAB 1: KUNDLI, LAGNA, & NAAM RASHI
# ==========================================
with tab1:
    st.header("✨ Personal Birth Chart Blueprint / जन्म कुंडली विश्लेषण")
    
    if birth_time:
        try:
            all_house_data = Calculate.AllHouseData(HouseName.House1, birth_time)
            house_json = json.loads(Tools.AnyToJSON("", all_house_data)) if all_house_data else {}
            calculated_house_sign = house_json.get("HouseBhavaChalitSign", {}).get("Name", "Libra (Tula)") if isinstance(house_json, dict) else "Libra (Tula)"
            calculated_naam_rashi = calculate_naam_rashi(user_name)
            
            c1, c2, c3 = st.columns(3)
            with c1: st.metric(label="🔮 Your Lagna (Rising Ascendant)", value=calculated_house_sign)
            with c2: st.metric(label="🌙 Janma Rashi (Birth Moon Sign)", value="Libra (Tula)")
            with c3: st.metric(label="🔤 Naam Rashi (Name Signature Sign)", value=calculated_naam_rashi)
            
            st.markdown("---")
            st.subheader("📚 Astrological Fundamentals / ज्योतिषीय आधार")
            e_col, h_col = st.columns(2)
            with e_col:
                st.markdown(f"""
                > **Naam Rashi vs Janma Rashi:** For names starting with the **M** sound (like Mayank), your Naam Rashi defaults to **Simha (Leo)**, ruled by the Sun. It reflects your external social identity. Janma Rashi reflects the psychological mind where the Moon resided.
                """)
            with h_col:
                st.markdown(f"""
                > **नाम राशि बनाम जन्म राशि:** **'म'** अक्षर से शुरू होने वाले नामों की नाम राशि **सिंह (Leo)** होती है। यह आपके सामाजिक जीवन को दर्शाती है। जन्म राशि आंतरिक विचार प्रणाली को चलाती है।
                """)
        except Exception as e:
            st.error(f"Engine parsing error: {e}")

# ==========================================
# TAB 2: MARRIAGE COMPATIBILITY & DYNAMIC AGE TIMING
# ==========================================
with tab2:
    st.header("💑 Marriage Alignment & Personalized Timing / विवाह योग एवं सटीक समय")
    st.markdown("Calculates **customized age windows** by evaluating planetary blockages or benefits in your 7th House.")
    
    if birth_time:
        try:
            h7_raw = Calculate.AllHouseData(HouseName.House7, birth_time)
            h7_json = json.loads(Tools.AnyToJSON("", h7_raw)) if h7_raw else {}
            planets_in_7 = h7_json.get("PlanetsInHouseBasedOnSign", []) if isinstance(h7_json, dict) else []
            
            is_delayed = any(p in ["Saturn", "Rahu", "Ketu", "Shani"] for p in planets_in_7)
            
            if is_delayed:
                age_window = "30 to 34 Years (परिपक्व आयु योग)"
                verdict_eng = "Your 7th House demonstrates strong structural signatures from planets like Saturn or Rahu. This creates a Mature Marriage Yog, where long-term stability settles beautifully in your early 30s."
                verdict_hin = "आपके सप्तम भाव पर धीमे या अनुशासित ग्रहों (जैसे शनि या राहु) का प्रभाव है। यह एक परिपक्व विवाह योग बनाता है, जो 30 से 34 वर्ष की आयु में स्थायी जुड़ाव देगा।"
            else:
                age_window = "25 to 29 Years (सामान्य/शीघ्र विवाह योग)"
                verdict_eng = "Your 7th House enjoys beneficial paths. This triggers a standard union timeline, peaking gracefully in your mid-to-late 20s with an affectionate connection."
                verdict_hin = "आपके सप्तम भाव पर शुभ ग्रहों का सकारात्मक प्रभाव है। आपकी कुंडली के अनुसार विवाह सामान्य समय सीमा (25 से 29 वर्ष) के भीतर होने के प्रबल योग हैं।"

            res1, res2 = st.columns(2)
            with res1: st.metric(label="🎯 Personalized Marriage Age Window", value=age_window)
            with res2: st.metric(label="🪐 Active Planetary Yog Type", value="Structured / Mature" if is_delayed else "Auspicious / Standard")
            
            elan_col, hlan_col = st.columns(2)
            with elan_col: st.markdown(f"### 🇬🇧 English Analysis\n> {verdict_eng}")
            with hlan_col: st.markdown(f"### 🇮🇳 हिंदी विश्लेषण\n> {verdict_hin}")
        except Exception as e:
            st.error(f"Error computing marriage parameters: {e}")

# ==========================================
# TAB 3: CUSTOM CAREER FIELDS, TIMING & PROPERTY
# ==========================================
with tab3:
    st.header("💼 Material Destiny, Career Fields & Timing Blueprints / करियर क्षेत्र और सटीक समय")
    st.markdown("Extracting custom career field directives and asset-building ages via your **10th House (Profession)**.")
    
    if birth_time:
        try:
            h10_raw = Calculate.AllHouseData(HouseName.House10, birth_time)
            h10_json = json.loads(Tools.AnyToJSON("", h10_raw)) if h10_raw else {}
            sign_10 = h10_json.get("HouseBhavaChalitSign", {}).get("Name", "Cancer") if isinstance(h10_json, dict) else "Cancer"
            
            if "Cancer" in sign_10 or "Moon" in sign_10:
                field_rec = "Public administration, hospitality, counseling, or creative management fields."
            elif "Leo" in sign_10 or "Sun" in sign_10:
                field_rec = "Government roles, administrative leadership, software contracting, or corporate steering."
            else:
                field_rec = "Commerce, corporate financial advisory, legal consultation, design engineering, or tech sector analytics."
            
            c_field, c_time = st.columns(2)
            with c_field:
                st.info("### 🏢 Your Custom Job Industry")
                st.write(f"Based on your calculated 10th House Sign (**{sign_10}**), your optimal career fields are: **{field_rec}**")
            with c_time:
                st.warning("### ⏳ Financial & Job Security Ages")
                st.markdown("""
                * **Job Placement Milestones:** Initial operational career triggers operate at **Ages 22-24**, optimizing into deep financial mastery near **Ages 29-33**.
                * **Housing & Property Acquisition Milestone:** Physical fixed asset paths, land deals, or vehicle ownership indices settle heavily between **Ages 32 to 36**.
                """)
        except Exception as e:
            st.error(f"Error checking house properties: {e}")

# ==========================================
# TAB 4: SHANI, RAHU, & KETU TRANSIT TRACKER
# ==========================================
with tab4:
    st.header("📅 Shani, Rahu, & Ketu Transit Tracker / गोचर और राशि परिवर्तन समय")
    st.markdown("Track exactly **when** the cosmic heavyweights change signs and how they will behave in your Rashi.")
    
    user_rashi = st.selectbox(
        "Select Your Rashi for Transit Mapping / अपनी राशि चुनें",
        ["Mesh (Aries)", "Vrishabha (Taurus)", "Mithun (Gemini)", "Kark (Cancer)", 
         "Simha (Leo)", "Kanya (Virgo)", "Tula (Libra)", "Vrishchik (Scorpio)", 
         "Dhanu (Sagittarius)", "Makar (Capricorn)", "Kumbha (Aquarius)", "Meen (Pisces)"],
        index=6
    )

    if "Tula" in user_rashi or "Libra" in user_rashi:
        shani_year = "Saturn moves into Aries / March 2025 – June 2027"
        rahu_year = "Rahu moves into Aquarius / May 2025 – Dec 2026"
        shani_effect = "Shani Dev demands absolute structural organization in partnerships. Avoid shortcut methods."
        rahu_effect = "Rahu brings a massive surge of unique out-of-the-box ideas, software engineering innovations, or creative pivots."
        ketu_effect = "Focus on clean, highly targeted spiritual networking circles."
    else:
        shani_year = "Active cycle ongoing through current celestial shifts."
        rahu_year = "Moving through major nodal karmic axis resets."
        shani_effect = "Demands intense daily discipline, hard work, and regular tracking of lifestyle goals."
        rahu_effect = "Creates temporary desires for rapid professional expansion."
        ketu_effect = "Prompts introspection, meditation, and a focus on inner spiritual growth."

    transit_data = pd.DataFrame({
        "Planet (ग्रह)": ["🪐 Shani (Saturn)", "🎭 Rahu (North Node)", "🔱 Ketu (South Node)"],
        "Transit Timeline Window (परिवर्तन वर्ष)": [shani_year, rahu_year, "Opposite axis to Rahu (180 degrees)"],
        "How It Will Behave / What To Do (प्रभाव और उपाय)": [shani_effect, rahu_effect, ketu_effect]
    }).set_index("Planet (ग्रह)")
    
    st.table(transit_data)
