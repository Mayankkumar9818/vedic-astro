import streamlit as st
import pandas as pd
import json
import datetime
from vedastro import *

# Initialize VedAstro API Connection safely
try:
    Calculate.SetAPIKey('FreeAPIUser')
except Exception as e:
    st.error(f"Failed to initialize VedAstro Engine: {e}")

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
        "Vrishabha (Taurus)": ["B", "V", "U", "ब", "в", "उ"],
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
# MAIN PAGE INPUT MATRIX (Wrapped inside a Secure Form)
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
if st.session_state.form_submitted:
    hour_24 = int(st.session_state.sb_hr)
    if st.session_state.sb_period == "PM" and hour_24 < 12: hour_24 += 12
    elif st.session_state.sb_period == "AM" and hour_24 == 12: hour_24 = 0
    master_time = datetime.time(hour_24, int(st.session_state.sb_min))

    try:
        master_loc = get_safe_geolocation(st.session_state.location_input)
        master_time_str = f"{master_time.strftime('%H:%M')} {st.session_state.date_input.strftime('%d/%m/%Y')} +05:30"
        birth_time = Time(master_time_str, master_loc)
    except Exception:
        st.error("Error setting astronomical time coordinates.")

st.markdown("---")

# Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🔮 Birth Signs & Soul Analysis", 
    "💑 Marriage Timing & Compatibility", 
    "💼 Profession & Asset Blueprints",
    "📅 Planetary Transits (Shani, Rahu, Ketu)"
])

if not st.session_state.form_submitted:
    st.info("👋 Please fill in your birth details above and click 'Generate Horoscope Calculations' to initialize your breakdown.")
else:
    # Gather structural parameters safely using verified API endpoints
    try:
        # Dynamic calculation of Lagna
        h1_raw = Calculate.AllHouseData(HouseName.House1, birth_time)
        h1_json = json.loads(Tools.AnyToJSON("", h1_raw)) if h1_raw else {}
        calculated_lagna = h1_json.get("HouseBhavaChalitSign", {}).get("Name", "Libra (Tula)")
        
        # Pulled Moon's Sign data from Planet Sign library logic
        moon_sign_data = Calculate.PlanetSign(PlanetName.Moon, birth_time)
        calculated_janma_rashi = str(moon_sign_data).strip() if moon_sign_data else "Tula (Libra)"
        calculated_naam_rashi = calculate_naam_rashi(st.session_state.user_name)
        
        # 7th House Processing for Marriage
        h7_raw = Calculate.AllHouseData(HouseName.House7, birth_time)
        h7_json = json.loads(Tools.AnyToJSON("", h7_raw)) if h7_raw else {}
        planets_in_7 = h7_json.get("PlanetsInHouseBasedOnSign", []) if isinstance(h7_json, dict) else []
        
        # 10th House Processing for Career
        h10_raw = Calculate.AllHouseData(HouseName.House10, birth_time)
        h10_json = json.loads(Tools.AnyToJSON("", h10_raw)) if h10_raw else {}
        sign_10 = h10_json.get("HouseBhavaChalitSign", {}).get("Name", "Cancer")
        
        # Extract dynamic numeric properties to avoid generic pre-typed outputs
        moon_deg = float(Calculate.PlanetLongitude(PlanetName.Moon, birth_time).ToDegrees())
        sun_deg = float(Calculate.PlanetLongitude(PlanetName.Sun, birth_time).ToDegrees())
        lagna_deg = float(Calculate.HouseStartLongitude(HouseName.House1, birth_time).ToDegrees())
        
    except Exception as e:
        st.error(f"Astrological Engine Error: {e}")
        calculated_lagna, calculated_janma_rashi, planets_in_7, sign_10 = "Libra (Tula)", "Tula (Libra)", [], "Cancer"
        calculated_naam_rashi = calculate_naam_rashi(st.session_state.user_name)
        moon_deg, sun_deg, lagna_deg = 15.0, 10.0, 20.0

    # ==========================================
    # TAB 1: BOTH RASHIS & ASCENDANT
    # ==========================================
    with tab1:
        st.header("✨ Your Identity Blueprint: Both Rashis & Lagna")
        
        c1, c2, c3 = st.columns(3)
        with c1: st.metric(label="🔮 Your Lagna (Rising Ascendant)", value=calculated_lagna)
        with c2: st.metric(label="🌙 Janma Rashi (True Birth Moon Sign)", value=calculated_janma_rashi)
        with c3: st.metric(label="🔤 Naam Rashi (Name Syllable Sign)", value=calculated_naam_rashi)
        
        st.markdown("---")
        st.subheader("📚 Detailed Duality Breakdown")
        st.markdown(f"""
        *   **Janma Rashi ({calculated_janma_rashi}):** This is calculated strictly from your exact Date, Time, and Place of birth. It rules your subconscious mind, emotional stability, and dictates your active planetary dasha cycles and gochar (transits). **This is the core foundation for accurate predictions.**
        *   **Naam Rashi ({calculated_naam_rashi}):** Calculated from the first letter of your name (**{st.session_state.user_name[:1].upper()}**). This dictates how the public perceives you and operates when your exact birth chart details are unavailable.
        """)

    # ==========================================
    # TAB 2: UNFILTERED MARRIAGE TIMING
    # ==========================================
    with tab2:
        st.header("💑 Marriage Alignment & Unfiltered Age Windows")
        
        has_malefic = any(p in ["Saturn", "Rahu", "Ketu", "Mars", "Shani", "Mangal"] for p in planets_in_7)
        has_benefic = any(p in ["Jupiter", "Venus", "Guru", "Shukra"] for p in planets_in_7)
        
        if has_malefic:
            age_window = "30 to 34 Years (Delayed / Mature Bond)"
            severity = "Heavy planetary configurations (such as Saturnian or Nodal influences) indicate lessons in patience. Marriage prior to age 28 could bring communication stress or legal friction. True stability manifests after maturity."
            verdict_status = "Negative/Challenging initially, turning highly stable after age 30."
        elif has_benefic:
            age_window = "24 to 28 Years (Auspicious / Early Union)"
            severity = "Beneficent energy profiles dominate. Indicates an emotionally supportive partner, timely alignment, and domestic growth shortly after starting a career."
            verdict_status = "Positive and harmonious."
        else:
            age_window = "27 to 29 Years (Standard Karmic Lifecycle)"
            severity = "No severe afflictions or heavy accelerations are noticed in the 7th house cusp. Marriage occurs at a standard psychological and societal age window."
            verdict_status = "Neutral and stable."

        m_col1, m_col2 = st.columns(2)
        with m_col1: st.metric(label="🎯 Predicted Marriage Age Window", value=age_window)
        with m_col2: st.metric(label="🪐 Structural Condition", value=verdict_status)
        
        st.markdown(f"""
        ### 📊 Unfiltered Relationship Analysis
        *   **Plated Configurations Found:** `{planets_in_7 if planets_in_7 else 'None Directly Occupying'}`
        *   **The Reality Check:** {severity}
        """)

    # ==========================================
    # TAB 3: CAREER & ASSET BLUEPRINTS
    # ==========================================
    with tab3:
        st.header("💼 Profession, Financial Security & Asset Blueprints")
        
        if any(x in sign_10 for x in ["Cancer", "Scorpio", "Pisces", "Moon", "Mars"]):
            industry = "Public Administration, Healthcare, Strategic Logistics, or Technical Engineering."
        elif any(x in sign_10 for x in ["Aries", "Leo", "Sagittarius", "Sun", "Jupiter"]):
            industry = "Corporate Executive Leadership, Government Contracting, Legal counsel, or Enterprise Management."
        else:
            industry = "Tech Sector Analytics, Fintech Advisory, Design Architecture, or Mass Media Consulting."
            
        c_col1, c_col2 = st.columns(2)
        with c_col1:
            st.info("### 🏢 Your Custom Job Industry")
            st.write(f"Based on your dynamic 10th House alignment (**{sign_10}**), your wealth-generation vectors point heavily toward: **{industry}**")
        with c_col2:
            st.warning("### ⏳ Asset Acquisition Timelines")
            st.markdown("""
            *   **Wealth Optimization Peak:** Your financial stabilizing phase initiates heavily between **Ages 29 and 33**.
            *   **Housing & Property Acquisition Milestone:** Heavy indicators point toward independent property acquisition or fixed family investments settling between **Ages 32 to 36**.
            """)

    # ==========================================
    # TAB 4: SHANI, RAHU, & KETU TRANSIT TRACKER
    # ==========================================
    with tab4:
        st.header("📅 Shani, Rahu, & Ketu Transit Blueprint")
        st.markdown(f"The transit engine has automatically locked onto your calculated **Janma Rashi ({calculated_janma_rashi})**.")

        if "Tula" in calculated_janma_rashi or "Libra" in calculated_janma_rashi:
            shani_window = "Saturn in Aries (7th from Moon) / Testing phase for relationships."
            rahu_window = "Rahu in Aquarius (5th from Moon) / Sudden unconventional gains or analytical pivots."
            ketu_window = "Ketu in Leo (11th from Moon) / Re-evaluating large social networks and friend circles."
            verdict_t = "Demands strict discipline in contractual agreements and partnerships. Do not cut corners."
        elif "Mesh" in calculated_janma_rashi or "Aries" in calculated_janma_rashi:
            shani_window = "Saturn in Aries (Sade Sati/Janma Shani) / High workload, physical fatigue."
            rahu_window = "Rahu in Aquarius (11th from Moon) / Huge financial windfalls, sudden international exposure."
            ketu_window = "Ketu in Leo (5th from Moon) / Deep spiritual inclination, gut-health vulnerabilities."
            verdict_t = "A massive transformation year. High performance is rewarded, but physical burnout risks are real."
        else:
            shani_window = "Saturn moving through active structural houses relative to your Moon."
            rahu_window = "Rahu processing major nodal adjustments."
            ketu_window = "Ketu operating on the reciprocal axis."
            verdict_t = "Standard operational transits apply. Focus on disciplined lifestyle routines and daily metrics."

        transit_df = pd.DataFrame({
            "Shadow/Karmic Planet": ["🪐 Shani (Saturn)", "🎭 Rahu (North Node)", "🔱 Ketu (South Node)"],
            "Transit Space Allocation": [shani_window, rahu_window, ketu_window],
            "Raw Actionable Guidance": [verdict_t, "Expect unexpected psychological urges; ground them with data.", "Isolate noise; focus purely on inner execution."]
        }).set_index("Shadow/Karmic Planet")
        
        st.table(transit_df)

    # ==========================================
    # 🎯 COMPLETELY DYNAMIC BILINGUAL VERDICT
    # ==========================================
    st.markdown("---")
    st.markdown("## 🎯 Unfiltered Karmic Final Verdict / अंतिम परिणाम (सत्य समीक्षा)")
    
    # Calculate a unique programmatic Karmic Score using raw degrees of Luminary points
    # This guarantees that the final layout changes dynamically for every single distinct birth hour/date.
    karmic_structural_coefficient = round(((moon_deg * 1.5) + (sun_deg * 0.8) + (lagna_deg * 1.2)) % 100, 2)
    
    col_en, col_hi = st.columns(2)
    
    with col_en:
        st.subheader("🇬🇧 Dynamic English Analysis")
        st.markdown(f"**Computed Chart Strength Index:** `{karmic_structural_coefficient}%`")
        
        # Context-aware conditional statements driven by structural variables
        if karmic_structural_coefficient < 40.0:
            st.error(f"""
            ⚠️ **Karmic Adjustment Path:** Your personalized birth chart layout yields a raw capacity coefficient of **{karmic_structural_coefficient}%**. 
            This configuration implies that your early developmental milestones require intense grinding. 
            Because your **Moon ({calculated_janma_rashi})** and **Lagna ({calculated_lagna})** align at these specific spatial configurations, 
            rapid shortcuts or unearned success will instantly collapse under planetary scrutiny. 
            
            💡 **True Outlook:** Marriage structures stabilize best through maturity. Do not force corporate investments before clearing your focal structural debts. Your chart rewards hyper-disciplined execution over blind faith.
            """)
        elif 40.0 <= karmic_structural_coefficient <= 75.0:
            st.warning(f"""
            ⚡ **Karmic Stabilization Path:** Your custom birth metrics establish an equilibrium quotient of **{karmic_structural_coefficient}%**. 
            This dictates an undulating progression profile. You will observe cycles of immense professional momentum alternating with unexpected periods of absolute stagnation. 
            Your **10th Cusp house sign ({sign_10})** shows that your professional assets remain directly locked to your emotional focus. 
            
            💡 **True Outlook:** Relationships require deliberate, analytical communication because of your current house placements (`{planets_in_7 if planets_in_7 else 'Empty Seventh Cusp'}`). Wealth accumulation accelerates naturally between age ranges 31-35.
            """)
        else:
            st.success(f"""
            🚀 **Karmic Acceleration Path:** Your specific spatial layout maps a structural optimization quotient of **{karmic_structural_coefficient}%**. 
            Your **Ascendant ({calculated_lagna})** and luminary vectors allow you to navigate major structural crises with relative ease compared to your peers. 
            
            💡 **True Outlook:** While partnership houses display high alignment potential, there's a risk of complacency. If you stop pushing your limits, you will suppress the natural abundance promised by your chart's positive indicators.
            """)
            
    with col_hi:
        st.subheader("🇮🇳 वास्तविक हिंदी समीक्षा")
        st.markdown(f"**कुंडली वास्तविक क्षमता सूचकांक:** `{karmic_structural_coefficient}%`")
        
        if karmic_structural_coefficient < 40.0:
            st.error(f"""
            ⚠️ **कर्म संशोधन मार्ग:** आपकी गणना की गई कुंडली का वास्तविक सूचकांक **{karmic_structural_coefficient}%** आया है। 
            यह दर्शाता है कि आपके जीवन के शुरुआती फैसले भारी संघर्ष और कड़े परिश्रम की मांग करेंगे। क्योंकि आपका **चंद्रमा ({calculated_janma_rashi})** और **लग्न ({calculated_lagna})** इस विशेष अंश पर स्थित हैं, 
            इसलिए बिना सोचे-समझे किए गए कार्य या शॉर्टकट तुरंत असफल हो जाएंगे।
            
            💡 **सटीक भविष्यफल:** आपकी कुंडली के अनुसार विवाह और करियर में स्थायित्व थोड़ी देर से आएगा। किसी भी बड़े निवेश में जल्दबाजी न करें। यह कुंडली केवल और केवल कड़े अनुशासन से ही फलित होगी।
            """)
        elif 40.0 <= karmic_structural_coefficient <= 75.0:
            st.warning(f"""
            ⚡ **कर्म संतुलन मार्ग:** आपकी जन्म कुंडली के ग्रहों के अनुसार आपका संतुलन सूचकांक **{karmic_structural_coefficient}%** है। 
            यह आपके जीवन में उतार-चढ़ाव वाले ग्राफ को दर्शाता है। आपको अचानक बड़ी सफलता मिलेगी और फिर अचानक सब कुछ रुक जाएगा। 
            आपका **दसवां करियर भाव ({sign_10})** दिखाता है कि आपकी आर्थिक उन्नति आपकी मानसिक एकाग्रता पर निर्भर करती है।
            
            💡 **सटीक भविष्यफल:** आपके सप्तम भाव (`{planets_in_7 if planets_in_7 else 'रिक्त सप्तम भाव'}`) के कारण रिश्तों में आपको बहुत सोच-समझकर बोलना होगा। 31 से 35 वर्ष की आयु के बीच आपका धन संचय तेजी से बढ़ेगा।
            """)
        else:
            st.success(f"""
            🚀 **कर्म गतिवर्धन मार्ग:** आपकी कुंडली के विशिष्ट ग्रहों के स्थान के कारण आपका सूचकांक **{karmic_structural_coefficient}%** प्राप्त हुआ है। 
            आपका **लग्न ({calculated_lagna})** और मुख्य ग्रह आपको जीवन के बड़े संकटों से आसानी से बाहर निकाल लेंगे।
            
            💡 **सटीक भविष्यफल:** यद्यपि आपकी कुंडली में सुख और तरक्की के बेहतरीन योग हैं, लेकिन इसका मतलब यह नहीं है कि आप प्रयास करना छोड़ दें। यदि आप आलस्य करेंगे, तो आपके अच्छे ग्रहों का प्रभाव भी निष्प्रभावी हो जाएगा।
            """)
