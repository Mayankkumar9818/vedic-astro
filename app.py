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
st.title("🔮 Aapka Apna Panditji: Personal Vedic Astrology System")
st.markdown("Easy language mein aapki kundli, career, aur marriage compatibility ki deep details.")

# Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🔮 Kundli & Soul Reading", 
    "💑 Guna Matching (Shaadi/Love)", 
    "💼 Career & Property Potentials",
    "📅 Aaj Ka Panchanga & Transits"
])

# Robust function to safely obtain a valid VedAstro GeoLocation object 
def get_safe_geolocation(city_name):
    city_defaults = {
        "new delhi": (77.2090, 28.6139),
        "delhi": (77.2090, 28.6139),
        "mumbai": (72.8777, 19.0760),
        "kolkata": (88.3639, 22.5726),
        "chennai": (80.2707, 13.0827),
        "bangalore": (77.5946, 12.9716),
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

# Time picker without slider UI
def non_slider_time_picker(key_prefix):
    st.markdown("**Birth Time Select Karein (AM/PM Selector)**")
    c1, c2, c3 = st.columns(3)
    with c1:
        hr = c1.selectbox("Ghanta (Hour)", list(range(1, 13)), index=2, key=f"{key_prefix}_hr")
    with c2:
        minute = c2.selectbox("Minute", [f"{i:02d}" for i in range(60)], index=30, key=f"{key_prefix}_min")
    with c3:
        period = c3.selectbox("AM/PM", ["AM", "PM"], index=1, key=f"{key_prefix}_period")
        
    hour_24 = int(hr)
    if period == "PM" and hour_24 < 12:
        hour_24 += 12
    elif period == "AM" and hour_24 == 12:
        hour_24 = 0
        
    return datetime.time(hour_24, int(minute))

MIN_DATE = datetime.date(1900, 1, 1)
MAX_DATE = datetime.date(2026, 12, 31)

# ==========================================
# TAB 1: KUNDLI & DEEP SOUL READING
# ==========================================
with tab1:
    st.header("✨ Aapki Kundli Ke Main Grah-Nakshatra")
    st.markdown("Aapki personality aur grahon ki original positions ka asaan prediction.")
    
    user_name = st.text_input("Aapka Naam", "Seeker")
    
    col1, col2 = st.columns(2)
    with col1:
        location_input = st.text_input("Birth Place / City (India)", "New Delhi")
        time_input = non_slider_time_picker("tab1")
    with col2:
        date_input = st.date_input(
            "Birth Date (Dropdown se year change karein)", 
            value=datetime.date(1992, 10, 25),
            min_value=MIN_DATE,
            max_value=MAX_DATE
        )
        tz_input = st.text_input("Timezone Offset", "+05:30", disabled=True)
        
    if st.button("Kundli Calculate Karein", key="calc_chart"):
        with st.spinner("Panditji calculation kar rahe hain..."):
            try:
                loc = get_safe_geolocation(location_input)
                formatted_time = time_input.strftime("%H:%M")
                formatted_date = date_input.strftime("%d/%m/%Y")
                time_str = f"{formatted_time} {formatted_date} +05:30"
                
                birth_time = Time(time_str, loc)
                
                all_planet_data = Calculate.AllPlanetData(PlanetName.Sun, birth_time)
                all_house_data = Calculate.AllHouseData(HouseName.House1, birth_time)
                
                planet_json = json.loads(Tools.AnyToJSON("", all_planet_data)) if all_planet_data else {}
                house_json = json.loads(Tools.AnyToJSON("", all_house_data)) if all_house_data else {}
                
                st.success(f"✅ Kundli tayaar hai, {user_name}!")
                
                calculated_house_sign = "Detected"
                if isinstance(house_json, dict):
                    calculated_house_sign = house_json.get("HouseBhavaChalitSign", {}).get("Name", "Detected")
                
                sun_house = "1"
                if isinstance(planet_json, dict):
                    sun_house = planet_json.get("HouseFromSignName", "1")
                
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric(label="☀️ Surya Dev Ki Position", value=f"House {sun_house}")
                with c2:
                    st.metric(label="🔮 Aapka Lagna Sign (Ascendant)", value=calculated_house_sign)
                with c3:
                    st.metric(label="🌌 D60 Past Karma State", value="Active")
                
                st.subheader(f"🗣️ Simple Language Mein Iska Matlab Kya Hai, {user_name}?")
                st.markdown(f"""
                * **Aapka Lagna {calculated_house_sign} hai:** Iska seedha matlab ye hai ki aapka natural behavior, health, aur look isi rashi se control hota hai. Log aapko isi nature se pehchante hain.
                * **Surya Dev House {sun_house} mein baithe hain:** Surya matlab aapki soul aur confidence. Ab chunki ye {sun_house} house mein hain, aapki poori life ka focus aur energy hamesha isi sector ke chakkar kaategi (jaise career, paisa ya relationships).
                """)
                    
                with st.expander("Raw Technical Data Dekhein"):
                    st.json(house_json)
                    
            except Exception as e:
                st.error(f"Calculation mein dikkat aayi: {e}.")

# ==========================================
# TAB 2: MARRIAGE & GUNA MATCHING
# ==========================================
with tab2:
    st.header("💑 Kundli Milan (Ashta Koota Guna Match)")
    st.markdown("Check karein ki dono ke kitne Guna milte hain (Total 36 mein se).")
    
    m_col, f_col = st.columns(2)
    with m_col:
        st.subheader("Boy / Partner A Details")
        m_name = st.text_input("Boy's Name", "Partner A")
        m_loc = st.text_input("Boy's Birth City", "New Delhi", key="m1")
        m_time = non_slider_time_picker("tab2_m")
        m_date = st.date_input("Boy's Birth Date", value=datetime.date(1992, 10, 25), min_value=MIN_DATE, max_value=MAX_DATE, key="m3")
    with f_col:
        st.subheader("Girl / Partner B Details")
        f_name = st.text_input("Girl's Name", "Partner B")
        f_loc = st.text_input("Girl's Birth City", "New Delhi", key="f1")
        f_time = non_slider_time_picker("tab2_f")
        f_date = st.date_input("Girl's Birth Date", value=datetime.date(1997, 6, 15), min_value=MIN_DATE, max_value=MAX_DATE, key="f3")
        
    if st.button("Guna Milan Score Nikalein"):
        with st.spinner("Kundli match ho rahi hai..."):
            try:
                b_geo = get_safe_geolocation(m_loc)
                boy_time_str = f"{m_time.strftime('%H:%M')} {m_date.strftime('%d/%m/%Y')} +05:30"
                boy_birth = Time(boy_time_str, b_geo)
                
                g_geo = get_safe_geolocation(f_loc)
                girl_time_str = f"{f_time.strftime('%H:%M')} {f_date.strftime('%d/%m/%Y')} +05:30"
                girl_birth = Time(girl_time_str, g_geo)
                
                matchReport = Calculate.MatchReport(boy_birth, girl_birth)
                match_json = json.loads(Tools.AnyToJSON("", matchReport)) if matchReport else {}
                
                percentage_score = match_json.get("KutaScore", 0.0) if isinstance(match_json, dict) else 0.0
                gunas_matched = round((percentage_score / 100) * 36, 1)
                gunas_not_matched = round(36 - gunas_matched, 1)
                
                st.subheader(f"📊 Final Scorecard: {m_name} ❤️ {f_name}")
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric(label="✅ Kitne Guna Mile", value=f"{gunas_matched} / 36")
                with c2:
                    st.metric(label="❌ Jo Guna Nahi Mile", value=f"{gunas_not_matched} / 36")
                with c3:
                    st.metric(label="📈 Compatibility Score", value=f"{int(percentage_score)}%")
                
                st.subheader("🗣️ Panditji Ka Verdict (Hinglish Mein):")
                if gunas_matched >= 25.0:
                    st.balloons()
                    st.success(f"🌟 **Shaandaar Match ({gunas_matched} Gunas):** Are boss ekdum kamaal match hai! Dono ki tuning, aapsi samajh, aur kismat ek doosre ke liye perfect bani hai. Go ahead!")
                elif gunas_matched >= 18.0:
                    st.info(f"⚖️ **Normal/Theek Match ({gunas_matched} Gunas):** Gaadi chal padegi! Shastron ke hisaab se minimum 18 milne chahiye, aur aapke usse upar hain. Thoda adjustments lagenge par shaadi badhiya rahegi.")
                else:
                    st.warning(f"⚠️ **Thoda Mushkil Hai ({gunas_matched} Gunas):** Guna score kaafi kam aaya hai boss. Iska matlab dono ke nature aur soch mein kaafi farak hoga. Shaadi chalane ke liye bohot patience aur compromises ki zaroorat padegi.")
                
                embeds = match_json.get("Embeddings", []) if isinstance(match_json, dict) else []
                if embeds and len(embeds) >= 8:
                    st.write("### 🔍 Category Wise Breakdown:")
                    metrics_df = pd.DataFrame({
                        "Astrological Category": [
                            "Varna (Ego & Work Sync)", "Vashya (Attraction & Control)", 
                            "Tara (Health & Destiny)", "Yoni (Physical Compatibility)", 
                            "Graha Maitram (Friendship & Mindset)", "Gana (Nature/Temperament)", 
                            "Bhakoot (Family & Love Connection)", "Nadi (Genetic Health & Kids)"
                        ],
                        "Max Score": [1, 2, 3, 4, 5, 6, 7, 8],
                        "Aapka Score": [embeds[0], embeds[1], embeds[2], embeds[3], embeds[4], embeds[5], embeds[6], embeds[7]]
                    }).set_index("Astrological Category")
                    
                    st.bar_chart(metrics_df["Aapka Score"])
                    st.table(metrics_df)
                    
            except Exception as e:
                st.error(f"Error occurred: {e}")

# ==========================================
# TAB 3: LIFE & MATERIAL DESIRES
# ==========================================
with tab3:
    st.header("💼 Career Job Yoga & 🏠 Apna Ghar / Property Potential")
    st.markdown("Kundli ke hisaab se career ki tarakki aur land/assets ka roadmap.")
    
    user_name_p = st.text_input("Naam", "Seeker", key="prop_name")
    loc_p = st.text_input("Birth Place Re-confirm Karein", "New Delhi", key="prop_loc")
    time_p = non_slider_time_picker("tab3_p")
    date_p = st.date_input("Birth Date Re-confirm Karein", value=datetime.date(1992, 10, 25), min_value=MIN_DATE, max_value=MAX_DATE, key="prop_date")
    
    if st.button("Career aur Property Status Dekhein"):
        with st.spinner("Material houses analyze ho rahe hain..."):
            try:
                p_geo = get_safe_geolocation(loc_p)
                p_time_str = f"{time_p.strftime('%H:%M')} {date_p.strftime('%d/%m/%Y')} +05:30"
                p_time_obj = Time(p_time_str, p_geo)
                
                h4_raw = Calculate.AllHouseData(HouseName.House4, p_time_obj)
                h10_raw = Calculate.AllHouseData(HouseName.House10, p_time_obj)
                
                h4_data = json.loads(Tools.AnyToJSON("", h4_raw)) if h4_raw else {}
                h10_data = json.loads(Tools.AnyToJSON("", h10_raw)) if h10_raw else {}
                
                arudha_4 = h4_data.get("ArudhaOfHouse", "House4") if isinstance(h4_data, dict) else "House4"
                arudha_10 = h10_data.get("ArudhaOfHouse", "House10") if isinstance(h10_data, dict) else "House10"
                
                st.subheader(f"💼 Career Aur Professional Life ({user_name_p})")
                st.markdown(f"""
                Aapke career ka faisla Kundli ka **10th House (Karma Sthana)** karta hai. Aapke chart mein ye link ho raha hai **{arudha_10}** ke saath.
                
                **Panditji Ki Advice:** Boss, iska matlab aapko aisi jagah kaam karna pasand hoga jahan clear targets aur responsibilities hon. Sahi dasha aane par career mein solid jump dikhega.
                """)
                
                st.subheader("🏠 Property, Land aur Gaadi Ka Sukh")
                st.markdown(f"""
                Ghar banana ya zameen kharidna Kundli ka **4th House (Sukha Sthana)** batata hai. Aapka property point **{arudha_4}** par active hai.
                
                **Panditji Ki Advice:** Chart badhiya hai! Assets aur apna khud ka ghar banane ka support aapki kundli ke setup mein poora dikh raha hai.
                """)
                
            except Exception as e:
                st.error(f"House calculations update failed: {e}")

# ==========================================
# TAB 4: DAILY PANCHANGA
# ==========================================
with tab4:
    st.header("📅 Aaj Ka Grah Gochar (Live Cosmic Transit)")
    st.markdown("Check karein ki aaj aasman mein grahon ki chaal aapke sheher par kaisi chal rahi hai.")
    t_loc = st.text_input("Aapki Current Location", "New Delhi", key="t_loc")
    
    if st.button("Aaj Ka Transit Formula Dekhein"):
        with st.spinner("Live transits scan ho rahe hain..."):
            try:
                today_geo = get_safe_geolocation(t_loc)
                now_datetime = datetime.datetime.now()
                now_time = now_datetime.strftime("%H:%M %d/%m/%Y +05:30")
                today_time_obj = Time(now_time, today_geo)
                
                tithi_data = Calculate.AllZodiacSignData(ZodiacName.Aries, today_time_obj)
                panchanga_json = json.loads(Tools.AnyToJSON("", tithi_data)) if tithi_data else {}
                
                st.success(f"Live planets loaded for timestamp: {now_time}")
                
                focal_house = panchanga_json.get('HouseFromSignName', 'House 11') if isinstance(panchanga_json, dict) else 'House 11'
                destiny_point = panchanga_json.get("DestinyPoint", "3") if isinstance(panchanga_json, dict) else '3'
                
                st.info(f"🌌 Aaj Ka Active House Vector: {focal_house}")
                st.metric(label="✨ Core Transit Point", value=destiny_point)
                
                st.subheader("🗣️ Aaj Ka Panditji Prediction:")
                st.write("""
                Aaj ke din grahon ka ishaara hai ki faltu ke pange ya bina soche samjhe impulsively koi bada paisa invest mat karna, varna nuksan ho sakta hai. 
                Puraane pending tasks ko clear karne ke liye din badhiya hai. Shaanti se plans banao!
                """)
            except Exception as e:
                st.error(f"Transit scan issue: {e}")
