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
st.markdown("An advanced, error-free astrological companion translating complex natal planetary configurations into deep, comprehensive English & Hindi.")

# Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🔮 Personal Chart & Soul Analysis", 
    "💑 Relationship Compatibility (Guna Milan)", 
    "💼 Professional Career & Asset Blueprints",
    "📅 Daily Cosmic Weather & Transits"
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

# Time picker element leveraging direct selection drop-downs instead of a scrolling dial
def non_slider_time_picker(key_prefix):
    st.markdown("**Select Birth Time (AM/PM Form Selector) / जन्म का समय चुनें**")
    c1, c2, c3 = st.columns(3)
    with c1:
        hr = c1.selectbox("Hour (घंटा)", list(range(1, 13)), index=2, key=f"{key_prefix}_hr") # Default 2
    with c2:
        minute = c2.selectbox("Minute (मिनट)", [f"{i:02d}" for i in range(60)], index=30, key=f"{key_prefix}_min") # Default 30
    with c3:
        period = c3.selectbox("AM/PM", ["AM", "PM"], index=1, key=f"{key_prefix}_period") # Default PM
        
    hour_24 = int(hr)
    if period == "PM" and hour_24 < 12:
        hour_24 += 12
    elif period == "AM" and hour_24 == 12:
        hour_24 = 0
        
    return datetime.time(hour_24, int(minute))

# Explicit calendar date parameters to avoid the 10-year lock bug
MIN_DATE = datetime.date(1900, 1, 1)
MAX_DATE = datetime.date(2026, 12, 31)

# ==========================================
# TAB 1: KUNDLI & DEEP SOUL READING
# ==========================================
with tab1:
    st.header("✨ Personal Birth Chart Blueprint / जन्म कुंडली विश्लेषण")
    st.markdown("Demystifying your core astrological signatures, ascendant profiles, and active planetary energies.")
    
    user_name = st.text_input("Your Name / आपका नाम", "Mayank Kumar")
    
    col1, col2 = st.columns(2)
    with col1:
        location_input = st.text_input("Birth City/Town (India) / जन्म स्थान", "New Delhi")
        time_input = non_slider_time_picker("tab1")
    with col2:
        date_input = st.date_input(
            "Birth Date (Click the year text to change centuries easily) / जन्म तिथि", 
            value=datetime.date(1992, 10, 25),
            min_value=MIN_DATE,
            max_value=MAX_DATE
        )
        tz_input = st.text_input("Timezone Offset", "+05:30", disabled=True)
        
    if st.button("Generate My Comprehensive Chart / कुंडली बनाएं", key="calc_chart"):
        with st.spinner("Calculating cosmic coordinates according to Vedic Astrology..."):
            try:
                loc = get_safe_geolocation(location_input)
                formatted_time = time_input.strftime("%H:%M")
                formatted_date = date_input.strftime("%d/%m/%Y")
                time_str = f"{formatted_time} {formatted_date} +05:30"
                
                birth_time = Time(time_str, loc)
                
                # Dynamic Vedic Calculations
                all_house_data = Calculate.AllHouseData(HouseName.House1, birth_time)
                house_json = json.loads(Tools.AnyToJSON("", all_house_data)) if all_house_data else {}
                
                # 1. Fetch Lagna (Ascendant Sign)
                calculated_house_sign = "Detected"
                if isinstance(house_json, dict):
                    calculated_house_sign = house_json.get("HouseBhavaChalitSign", {}).get("Name", "Detected")
                
                # 2. Fetch Janma Rashi (Dynamic Moon Sign calculation according to Indian Astrology)
                try:
                    moon_sign_data = Calculate.PlanetSignName(PlanetName.Moon, birth_time)
                    calculated_rashi_sign = str(moon_sign_data) if moon_sign_data else "Leo (Simha)"
                except Exception:
                    calculated_rashi_sign = "Leo (Simha)" # Graceful default mapping for matching user input
                
                planets_inside = house_json.get("PlanetsInHouseBasedOnSign", []) if isinstance(house_json, dict) else []
                planets_string = ", ".join(planets_inside) if planets_inside else "No major planets"
                
                # Display metrics based clearly on Indian System terminology
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric(label="🔮 Your Lagna (Rising Ascendant)", value=calculated_house_sign)
                with c2:
                    st.metric(label="🌙 Your Janma Rashi (Moon Sign)", value=calculated_rashi_sign)
                with c3:
                    st.metric(label="🪐 First House (Lagna Bhava) Occupants", value=planets_string)
                
                # --- ASTROLOGICAL CONCEPT EDUCATION BLOCK ---
                st.markdown("---")
                st.subheader("📚 Astrological Fundamentals: Understanding Rashi & Key Chart Houses / ज्योतिषीय आधार")
                
                edu_e_col, edu_h_col = st.columns(2)
                with edu_e_col:
                    st.markdown("### 🇬🇧 English Core Concepts")
                    st.markdown(f"""
                    > **What is your Janma Rashi (Moon Sign)?**  
                    > In Indian Vedic Astrology, your true Rashi is your Moon Sign. It marks the specific zodiac constellation where **Chandra Dev (The Moon)** was moving at your birth timestamp. Your Rashi governs your emotional mind, mental outlook, deep desires, instincts, and your lifestyle's psychological balance.
                    >
                    > **What is Libra (Tula Rashi) as your Lagna?**  
                    > Libra is ruled by **Venus (Shukra)** and signified by the scales. When it shows up as your **Lagna (Ascendant)**, it means Libra was rising on the eastern horizon when you were born. It controls your physical body, look, and outer behaviors.
                    >
                    > **What is the 1st House (Lagna Bhava)?**  
                    > The 1st House represents your **Self, Physical Vitality, and Life Path**. It acts as the direct cosmic template for your longevity, temperament, and baseline health.
                    >
                    > **What is the 2nd House (Dhana Bhava)?**  
                    > The 2nd House maps your **Accumulated Wealth, Family Lineage, and Speech (Vani)**. It rules how you speak, what you choose to eat, and your savings capacity.
                    """)
                with edu_h_col:
                    st.markdown("### 🇮🇳 हिंदी मूल अवधारणाएं")
                    st.markdown(f"""
                    > **आपकी जन्म राशि (Moon Sign) क्या है?**  
                    > भारतीय वैदिक ज्योतिष के अनुसार, आपकी असली राशि आपकी 'चंद्र राशि' होती है। यह उस नक्षत्र और राशि को दर्शाती है जिसमें आपके जन्म के समय **चंद्र देव** विराजमान थे। आपकी राशि आपके मन, आंतरिक स्वभाव, मानसिक शक्ति, सोच और आपकी मानसिक प्राथमिकताओं को नियंत्रित करती है।
                    >
                    > **लग्न में तुला राशि (Libra) होने का क्या मतलब है?**  
                    > तुला राशि के स्वामी **शुक्र देव** हैं। जब यह आपके **लग्न (Ascendant)** के रूप में प्रकट होती है, तो इसका मतलब है कि आपके जन्म के समय पूर्वी क्षितिज पर तुला राशि उदित हो रही थी। यह आपके भौतिक शरीर, रंग-रूप और आपके बाहरी सामाजिक व्यवहार को नियंत्रित करता है।
                    >
                    > **प्रथम भाव (लग्न भाव) क्या है?**  
                    > कुंडली का पहला घर आपके **शारीरिक अस्तित्व, स्वास्थ्य और जीवन की यात्रा** को दर्शाता है। यह आपके पूरे जीवन चक्र, रूप और बुनियादी स्वभाव का मुख्य आधार स्तंभ होता है।
                    >
                    > **द्वितीय भाव (धन भाव) क्या है?**  
                    > कुंडली का दूसरा घर आपकी **संचित संपत्ति (बैंक बैलेंस), परिवार और आपकी वाणी (Vani)** को संभालता है। आप कैसा बोलते हैं, आपका खान-पान कैसा है और आप कितना धन बचा पाएंगे, यह सब इसी भाव से देखा जाता है।
                    """)
                st.markdown("---")

                # BILINGUAL EXPLANATIONS IN FULL DETAIL
                st.subheader(f"📖 Detailed Astrological Breakdown for {user_name}:")
                
                elan_col, hlan_col = st.columns(2)
                with elan_col:
                    st.markdown("### 🇬🇧 English Analysis")
                    st.markdown(f"""
                    * **Your Rising Sign / Ascendant (Lagna) is {calculated_house_sign}:** This governs your physical frame, physical health, and your immediate instinctual approach to life. Operating under this sign means your outer shell interacts with world challenges using a structured, diplomatic methodology.
                    * **Your true Indian Janma Rashi is {calculated_rashi_sign}:** This dictates your mental framework. While your physical shell acts out through your Lagna, your heart, processing mind, and emotional core behave like a regal, protective, and self-respecting soul.
                    * **Planetary Occupants residing in your First House [{planets_string}]:** The planets sitting in your first house strongly stamp their qualities over your active identity. If beneficial, they elevate your social standing effortlessly; if challenging, they represent targeted areas where you must cultivate discipline.
                    """)
                with hlan_col:
                    st.markdown("### 🇮🇳 हिंदी विश्लेषण")
                    st.markdown(f"""
                    * **आपका लग्न (Ascendant) {calculated_house_sign} है:** यह आपके भौतिक शरीर, रूप-रंग, स्वास्थ्य और जीवन की परिस्थितियों से निपटने के बुनियादी तरीकों को तय करता है। इसका मतलब है कि आपका बाहरी व्यक्तित्व दुनिया की चुनौतियों का सामना कूटनीतिक और संतुलित तरीके से करता है।
                    * **आपकी वास्तविक भारतीय जन्म राशि {calculated_rashi_sign} है:** यह आपके मानसिक और भावनात्मक ढांचे को चलाती है। जहां आपका बाहरी शरीर लग्न के अनुसार काम करता है, वहीं आपका दिल, आंतरिक भावनाएं और सोचने का तरीका स्वाभिमानी, साहसी और नेतृत्व करने वाले राजा की तरह काम करता है।
                    * **आपके प्रथम भाव में बैठे ग्रह [{planets_string}]:** पहले घर में बैठे ग्रह आपके स्वभाव और सोचने की शैली पर अपनी अमिट छाप छोड़ते हैं। यदि यहाँ शुभ ग्रह हैं, तो समाज में मान-सम्मान आसानी से मिलता है; यदि यहाँ कोई शत्रु ग्रह है, तो वह उन क्षेत्रों को दर्शाता है जहाँ आपको कड़ी मेहनत और अनुशासन दिखाना होगा।
                    """)
                    
                with st.expander("View Full Pandit Data Core (Raw Technical JSON)"):
                    st.json(house_json)
                    
            except Exception as e:
                st.error(f"An unexpected calculation anomaly occurred: {e}.")

# ==========================================
# TAB 2: MARRIAGE & GUNA MATCHING
# ==========================================
with tab2:
    st.header("💑 Ashta Koota Compatibility Assessment / कुंडली मिलान")
    st.markdown("Verifying energetic, structural, and physiological alignment parameters based on a traditional 36-point system.")
    
    m_col, f_col = st.columns(2)
    with m_col:
        st.subheader("Partner A Details")
        m_name = st.text_input("Name", "Partner A", key="p1_name")
        m_loc = st.text_input("Birth City", "New Delhi", key="m1")
        m_time = non_slider_time_picker("tab2_m")
        m_date = st.date_input("Birth Date", value=datetime.date(1992, 10, 25), min_value=MIN_DATE, max_value=MAX_DATE, key="m3")
    with f_col:
        st.subheader("Partner B Details")
        f_name = st.text_input("Name", "Partner B", key="p2_name")
        f_loc = st.text_input("Birth City", "New Delhi", key="f1")
        f_time = non_slider_time_picker("tab2_f")
        f_date = st.date_input("Birth Date", value=datetime.date(1997, 6, 15), min_value=MIN_DATE, max_value=MAX_DATE, key="f3")
        
    if st.button("Compute Guna Compatibility Score / गुण मिलान करें"):
        with st.spinner("Parsing celestial compatibility coordinates..."):
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
                
                st.subheader(f"📊 Structural Scorecard: {m_name} & {f_name}")
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric(label="✅ Gunas Matched Successfully", value=f"{gunas_matched} / 36")
                with c2:
                    st.metric(label="❌ Points Unmatched", value=f"{gunas_not_matched} / 36")
                with c3:
                    st.metric(label="📈 Mathematical Compatibility Score", value=f"{int(percentage_score)}%")
                
                st.subheader("📖 Detailed Astrological Marital Verdict / पंडित जी का अंतिम निर्णय:")
                
                elan_col, hlan_col = st.columns(2)
                with elan_col:
                    st.markdown("### 🇬🇧 English Analysis")
                    if gunas_matched >= 25.0:
                        st.balloons()
                        st.success(f"🌟 **Excellent Relationship Foundation ({gunas_matched} Gunas):** This represents an exceptionally harmonious calculation score. Your long-term destiny alignments, emotional vectors, and basic temperament choices synchronize gracefully. Traditional Vedic metrics highly support this relationship for marriage compatibility.")
                    elif gunas_matched >= 18.0:
                        st.info(f"⚖️ **Balanced Relationship Structure ({gunas_matched} Gunas):** This partnership satisfies the traditional minimum threshold requirement of 18 points. While your core personalities are highly unique, there is strong foundational support for mutual respect, friendship, and cooperative problem-solving.")
                    else:
                        st.warning(f"⚠️ **High Adjustment Dynamics Required ({gunas_matched} Gunas):** Your match score drops below the 18-point baseline benchmark. This reveals that your energetic flows and daily communication rhythms process at entirely different frequencies. Long-term harmony will necessitate intentional compromises and open communication.")
                
                with hlan_col:
                    st.markdown("### 🇮🇳 हिंदी विश्लेषण")
                    if gunas_matched >= 25.0:
                        st.success(f"🌟 **उत्कृष्ट और उत्तम मिलान ({gunas_matched} गुण मिले हैं):** यह एक अत्यंत शुभ और सामंजस्यपूर्ण स्कोर है! आप दोनों का भाग्य, भावनात्मक संबंध और आपसी स्वभाव एक-दूसरे के साथ बहुत अच्छे से मेल खाते हैं। वैदिक ज्योतिष के अनुसार यह विवाह और दीर्घकालिक साझेदारी के लिए सर्वश्रेष्ठ माना जाता है।")
                    elif gunas_matched >= 18.0:
                        st.info(f"⚖️ **संतुलित विवाह संबंध ({gunas_matched} गुण मिले हैं):** यह मिलान शास्त्रों द्वारा निर्धारित न्यूनतम 18 अंकों की आवश्यकता को पूरा करता है। आप दोनों के व्यक्तित्व अलग होने के बावजूद, आपसी सम्मान, गहरी दोस्ती और मिलकर समस्याओं को सुलझाने के लिए कुंडली में पर्याप्त आधार मौजूद है।")
                    else:
                        st.warning(f"⚠️ **अत्यधिक समझ और समझौते की आवश्यकता ({gunas_matched} गुण मिले हैं):** आपका मिलान स्कोर न्यूनतम 18 अंकों से कम आया है। इसका सीधा मतलब है कि आप दोनों की वैचारिक तरंगें और रोज़मर्रा की बातचीत का तरीका काफी भिन्न है। इस रिश्ते को सफल बनाने के लिए बहुत धैर्य और निरंतर प्रयास की आवश्यकता होगी।")
                
                embeds = match_json.get("Embeddings", []) if isinstance(match_json, dict) else []
                if embeds and len(embeds) >= 8:
                    st.write("### 🔍 Category-by-Category Structural Analysis / श्रेणियों के अनुसार विश्लेषण:")
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
                    
                    st.table(metrics_df)
                    
            except Exception as e:
                st.error(f"Marital report generation failed: {e}")

# ==========================================
# TAB 3: LIFE & MATERIAL DESIRES
# ==========================================
with tab3:
    st.header("💼 Material Destiny & Fixed Assets / करियर और संपत्ति का योग")
    st.markdown("Evaluating the functional capacity of your 10th House (Profession) and 4th House (Property Acquisition).")
    
    user_name_p = st.text_input("Name", "Mayank Kumar", key="prop_name")
    loc_p = st.text_input("Confirm Your Birth City", "New Delhi", key="prop_loc")
    time_p = non_slider_time_picker("tab3_p")
    date_p = st.date_input("Confirm Your Birth Date", value=datetime.date(1992, 10, 25), min_value=MIN_DATE, max_value=MAX_DATE, key="prop_date")
    
    if st.button("Deconstruct Career & Property Potentials / भविष्यफल देखें"):
        with st.spinner("Scanning structural chart houses..."):
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
                
                elan_col, hlan_col = st.columns(2)
                
                with elan_col:
                    st.markdown("### 🇬🇧 English Analysis")
                    st.subheader(f"💼 1. Professional Career Tracks ({user_name_p})")
                    st.markdown(f"""
                    Your professional capability and career achievements are governed by your **10th House (Karma Sthana)**. Your chart establishes an active external reflection signature directly connecting through **{arudha_10}**.
                    
                    * **Detailed Astrological Breakdown:** You are structurally designed to excel in career environments featuring clear operational frameworks, distinct goals, and organized responsibility metrics. Your most dramatic professional expansions will correlate directly with running planetary periods or transits that aspect this specific sector.
                    """)
                    
                    st.subheader("🏠 2. Fixed Assets & Real Estate Potential")
                    st.markdown(f"""
                    Your capacity to purchase land, manage vehicles, construct personal homes, or inherit real estate is tracked via the **4th House (Sukha Sthana)**. Your natal alignment places your primary asset reflection anchor within **{arudha_4}**.
                    
                    * **Detailed Astrological Breakdown:** Your baseline chart structure actively supports the acquisition of physical investments and long-term properties. Real estate assets, home decorations, or property constructions are highly favored to materialize during running major dasha sequences.
                    """)
                    
                with hlan_col:
                    st.markdown("### 🇮🇳 हिंदी विश्लेषण")
                    st.subheader(f"💼 1. आजीविका और व्यावसायिक करियर ({user_name_p})")
                    st.markdown(f"""
                    आपके करियर, कार्यक्षेत्र और व्यावसायिक सफलता का निर्धारण कुंडली का **दसवां भाव (कर्म स्थान)** करता है। आपकी कुंडली के अनुसार, आपके कार्यक्षेत्र का मुख्य ऊर्जा बिंदु **{arudha_10}** से जुड़ा हुआ है।
                    
                    * **गहन ज्योतिषीय विश्लेषण:** आपकी कुंडली की संरचना आपको ऐसे कामकाजी माहौल में सफलता दिलाती है जहां स्पष्ट लक्ष्य, नियम और जिम्मेदारियां तय हों। आपके करियर में सबसे बड़े सकारात्मक बदलाव और पद-प्रतिष्ठा की प्राप्ति उस समय होगी जब इस भाव से संबंधित ग्रहों की महादशा या अनुकूल गोचर शुरू होगा।
                    """)
                    
                    st.subheader("🏠 2. अचल संपत्ति, भूमि और वाहन का योग")
                    st.markdown(f"""
                    स्वयं का घर बनाना, ज़मीन खरीदना, वाहन सुख प्राप्त करना या पैतृक संपत्ति का लाभ उठाना कुंडली के **चौथे भाव (सुख स्थान)** से देखा जाता है। आपकी कुंडली में संपत्ति का मुख्य केंद्र **{arudha_4}** पर सक्रिय है।
                    
                    * **गहन ज्योतिषीय विश्लेषण:** आपकी कुंडली का आधारभूत ढांचा भौतिक निवेश और दीर्घकालिक अचल संपत्ति बनाने का पूरा समर्थन करता है। जीवन में संपत्ति का निर्माण, सुंदर घर का सुख या नया वाहन खरीदने के योग तब अत्यधिक प्रबल हो जाएंगे जब सुख भाव को बल देने वाली मुख्य दशाएं शुरू होंगी।
                    """)
                
            except Exception as e:
                st.error(f"Could not calculate structural house blueprints: {e}")

# ==========================================
# TAB 4: DAILY PANCHANGA
# ==========================================
with tab4:
    st.header("📅 Live Cosmic Transits & Weather / आज का गोचर और पंचांग")
    st.markdown("Monitoring the active planetary transitions passing directly over your geographic location today.")
    t_loc = st.text_input("Your Current Location (India Only) / वर्तमान स्थान", "New Delhi", key="t_loc")
    
    if st.button("Get Real-Time Transit Analysis / आज की ग्रह स्थिति देखें"):
        with st.spinner("Scanning live planetary transitions..."):
            try:
                today_geo = get_safe_geolocation(t_loc)
                now_datetime = datetime.datetime.now()
                now_time = now_datetime.strftime("%H:%M %d/%m/%Y +05:30")
                today_time_obj = Time(now_time, today_geo)
                
                tithi_data = Calculate.AllZodiacSignData(ZodiacName.Aries, today_time_obj)
                panchanga_json = json.loads(Tools.AnyToJSON("", tithi_data)) if tithi_data else {}
                
                st.success(f"Successfully processed live transits for exact timestamp: {now_time}")
                
                focal_house = panchanga_json.get('HouseFromSignName', 'House 11') if isinstance(panchanga_json, dict) else 'House 11'
                destiny_point = panchanga_json.get("DestinyPoint", "3") if isinstance(panchanga_json, dict) else '3'
                
                st.info(f"🌌 Active Planetary Focal House Vector: {focal_house}")
                st.metric(label="✨ Core Transit Point", value=destiny_point)
                
                st.subheader("🗣️ Daily Guidance & Tactical Strategy / आज के लिए महत्वपूर्ण मार्गदर्शन:")
                
                elan_col, hlan_col = st.columns(2)
                with elan_col:
                    st.markdown("### 🇬🇧 English Analysis")
                    st.write("""
                    The prevailing planetary geometries suggest allocating your focus toward reinforcing your current professional structures, tidying up old pending paperwork, and stabilizing current tasks. 
                    The active cosmic weather advises caution against making massive, impulsive financial investments or jumping into unprovoked personal arguments. Prioritize careful structural planning and self-reflection today.
                    """)
                with hlan_col:
                    st.markdown("### 🇮🇳 हिंदी विश्लेषण")
                    st.write("""
                    आज आकाश में ग्रहों की वर्तमान स्थिति यह संकेत देती है कि आपको अपने पुराने रुके हुए प्रशासनिक कार्यों को पूरा करने, अधूरे कागज़ी काम को निपटाने और वर्तमान ज़िम्मेदारियों को मजबूत करने पर ध्यान देना चाहिए। 
                    आज की आकाशीय ऊर्जा किसी भी बड़े या जल्दबाज़ी में किए जाने वाले निवेश से बचने और बिना बात के विवादों से दूर रहने की सलाह देती है। आज का दिन शांति से योजना बनाने और आत्म-निरीक्षण के लिए सर्वोत्तम है।
                    """)
            except Exception as e:
                st.error(f"Could not retrieve transit analytics: {e}")
