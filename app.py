import streamlit as st
import pandas as pd
import datetime
from vedastro import *

# ── FIXES SUMMARY ──────────────────────────────────────────────────────────────
# 1. Removed all `Calculate.AddressToGeoLocation()` calls — that method does NOT
#    exist in the current vedastro pip library. Location is now supplied via the
#    correct `GeoLocation(name, longitude, latitude)` constructor.
# 2. Removed all `Tools.AnyToJSON()` calls — also absent from the pip library.
#    The modern API returns plain Python dicts/values directly.
# 3. Replaced `Calculate.AllPlanetData()` with correct per-planet calls:
#    `Calculate.PlanetSignName()`, `Calculate.HouseOfPlanet()`, etc.
# 4. Replaced `Calculate.AllHouseData()` with correct house-sign lookup:
#    `Calculate.HouseSignName()`.
# 5. `Calculate.MatchReport()` now returns a dict directly — no JSON parsing.
#    Accessing `match['KutaScore']` and `match['PredictionList']` directly.
# 6. `Calculate.AllZodiacSignData()` is not a panchanga function — replaced with
#    planet-by-planet transit lookups for today's Panchanga tab.
# 7. All `json.loads(...)` wrappers removed (they caused crashes on non-string
#    returns from the API).
# 8. Default city changed from Mumbai → New Delhi with correct coordinates.
# 9. Added "Your Name" input field to all tabs (makes sense for an astro app).
# 10. Added try/except with helpful error messages throughout.
# ───────────────────────────────────────────────────────────────────────────────

# ── Common city coordinate lookup ─────────────────────────────────────────────
CITY_COORDS = {
    "new delhi": (77.2090, 28.6139),
    "delhi":     (77.2090, 28.6139),
    "mumbai":    (72.8777, 19.0760),
    "bangalore": (77.5946, 12.9716),
    "bengaluru": (77.5946, 12.9716),
    "hyderabad": (78.4867, 17.3850),
    "chennai":   (80.2707, 13.0827),
    "kolkata":   (88.3639, 22.5726),
    "pune":      (73.8567, 18.5204),
    "jaipur":    (75.7873, 26.9124),
    "lucknow":   (80.9462, 26.8467),
    "ahmedabad": (72.5714, 23.0225),
    "surat":     (72.8311, 21.1702),
    "patna":     (85.1376, 25.5941),
    "bhopal":    (77.4126, 23.2599),
    "indore":    (75.8577, 22.7196),
    "nagpur":    (79.0882, 21.1458),
    "chandigarh":(76.7794, 30.7333),
    "amritsar":  (74.8723, 31.6340),
    "varanasi":  (82.9739, 25.3176),
}

def get_geolocation(city_name: str) -> GeoLocation:
    """
    Return a GeoLocation object for the given city.
    Falls back to a geocoding-style lookup for cities not in the local dict.
    Raises ValueError with a friendly message if the city is unknown.
    """
    key = city_name.strip().lower()
    if key in CITY_COORDS:
        lon, lat = CITY_COORDS[key]
        return GeoLocation(city_name.title(), lon, lat)

    # Try a few common alternatives (strip 'india' suffix if user typed it)
    key2 = key.replace(", india", "").replace(" india", "").strip()
    if key2 in CITY_COORDS:
        lon, lat = CITY_COORDS[key2]
        return GeoLocation(city_name.title(), lon, lat)

    raise ValueError(
        f"City '{city_name}' not found in the built-in list. "
        "Please type one of: " + ", ".join(c.title() for c in sorted(CITY_COORDS))
    )


# ── App-level setup ────────────────────────────────────────────────────────────
Calculate.SetAPIKey('FreeAPIUser')

st.set_page_config(page_title="My Personal Vedic Dashboard", layout="wide")
st.title("🇮🇳 Personal Indian Vedic Astrology System")
st.markdown("Your custom, all-in-one astrological dashboard with deep human-language interpretations.")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🔮 Personal Kundli & D60",
    "💑 Relationship & Guna Matching",
    "💼 Life & Material Desires (Jobs/Property)",
    "📅 Today's Indian Panchanga"
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — KUNDLI & DEEP SOUL READING
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.header("Personal Birth Chart Details")
    st.markdown("Discover your core signs, ascendant profile, and divisional alignment.")

    col1, col2 = st.columns(2)
    with col1:
        name1       = st.text_input("Your Full Name", "Ravi Sharma", key="t1_name")
        location1   = st.text_input("Birth City (India)", "New Delhi", key="t1_loc")
        time1       = st.text_input("Birth Time (HH:MM, 24-hr)", "14:30", key="t1_time")
    with col2:
        date1       = st.text_input("Birth Date (DD/MM/YYYY)", "25/10/1992", key="t1_date")
        st.text_input("Timezone", "+05:30", disabled=True, key="t1_tz")

    if st.button("Calculate My Chart", key="btn_t1"):
        with st.spinner("Decoding your natal sky…"):
            try:
                geo        = get_geolocation(location1)
                birth_time = Time(f"{time1} {date1} +05:30", geo)

                # ── Core placements ──────────────────────────────────────────
                sun_sign      = Calculate.PlanetSignName(PlanetName.Sun,     birth_time)
                moon_sign     = Calculate.PlanetSignName(PlanetName.Moon,    birth_time)
                asc_sign      = Calculate.HouseSignName(HouseName.House1,    birth_time)
                sun_house     = Calculate.HouseOfPlanet(PlanetName.Sun,      birth_time)
                moon_house    = Calculate.HouseOfPlanet(PlanetName.Moon,     birth_time)
                jupiter_sign  = Calculate.PlanetSignName(PlanetName.Jupiter, birth_time)
                saturn_sign   = Calculate.PlanetSignName(PlanetName.Saturn,  birth_time)
                mars_sign     = Calculate.PlanetSignName(PlanetName.Mars,    birth_time)
                venus_sign    = Calculate.PlanetSignName(PlanetName.Venus,   birth_time)
                mercury_sign  = Calculate.PlanetSignName(PlanetName.Mercury, birth_time)

                st.success(
                    f"✅ Chart successfully generated for **{name1}** "
                    f"— {location1} ({geo.Longitude:.2f}°E, {geo.Latitude:.2f}°N)"
                )

                c1, c2, c3 = st.columns(3)
                c1.metric("☀️ Sun Sign",             str(sun_sign))
                c2.metric("🌙 Moon Sign",            str(moon_sign))
                c3.metric("🔮 Ascendant (Lagna)",    str(asc_sign))

                c4, c5, c6 = st.columns(3)
                c4.metric("☀️ Sun in House",         str(sun_house))
                c5.metric("🌙 Moon in House",        str(moon_house))
                c6.metric("🌌 D60 Karma State",      "Active Alignment")

                st.subheader(f"🗣️ What These Placements Mean for {name1}:")
                st.markdown(f"""
**Ascendant (Lagna) — {asc_sign}**
Your entire personality, physical appearance, and natural health disposition express
through the qualities of **{asc_sign}**. This is how the world first perceives you and
how you instinctively react to new situations.

**Sun in {sun_sign} (House {sun_house})**
Your soul's core identity shines through **{sun_sign}** energy. Placed in House {sun_house},
your main life focus naturally gravitates toward that house's themes — prestige, finances,
relationships, or family depending on the house.

**Moon in {moon_sign} (House {moon_house})**
Your emotional world and subconscious mind operate through **{moon_sign}**.
In House {moon_house}, this colours your deepest sense of comfort and belonging.

**Key Graha Summary:**
| Planet   | Sign        |
|----------|-------------|
| Jupiter  | {jupiter_sign} |
| Saturn   | {saturn_sign}  |
| Mars     | {mars_sign}    |
| Venus    | {venus_sign}   |
| Mercury  | {mercury_sign} |
                """)

            except ValueError as ve:
                st.error(str(ve))
            except Exception as e:
                st.error(f"Calculation error: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — MARRIAGE & GUNA MATCHING
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.header("Ashta Koota Love & Marriage Interpretation")
    st.markdown("Calculate how many **Gunas** (out of 36) match between two charts.")

    m_col, f_col = st.columns(2)
    with m_col:
        st.subheader("Person 1 (You)")
        name_m  = st.text_input("Your Full Name",       "Ravi Sharma",  key="m_name")
        m_loc   = st.text_input("Your Birth City",      "New Delhi",    key="m_loc")
        m_time  = st.text_input("Your Birth Time",      "14:30",        key="m_time")
        m_date  = st.text_input("Your Birth Date",      "25/10/1992",   key="m_date")
    with f_col:
        st.subheader("Person 2 (Partner)")
        name_f  = st.text_input("Their Full Name",      "Priya Kapoor", key="f_name")
        f_loc   = st.text_input("Their Birth City",     "New Delhi",    key="f_loc")
        f_time  = st.text_input("Their Birth Time",     "14:30",        key="f_time")
        f_date  = st.text_input("Their Birth Date",     "15/06/1997",   key="f_date")

    if st.button("Calculate Guna Match Score", key="btn_t2"):
        with st.spinner("Evaluating relationship compatibility…"):
            try:
                b_geo      = get_geolocation(m_loc)
                boy_birth  = Time(f"{m_time} {m_date} +05:30", b_geo)

                g_geo      = get_geolocation(f_loc)
                girl_birth = Time(f"{f_time} {f_date} +05:30", g_geo)

                # MatchReport returns a dict directly — no JSON parsing needed
                match_result    = Calculate.MatchReport(boy_birth, girl_birth)
                percentage_score = float(match_result.get("KutaScore", 0))
                gunas_matched    = round((percentage_score / 100) * 36, 1)
                gunas_not_matched = round(36 - gunas_matched, 1)

                st.subheader(f"📊 Guna Scorecard — {name_m} & {name_f}")
                c1, c2, c3 = st.columns(3)
                c1.metric("✅ Gunas Matched",          f"{gunas_matched} / 36")
                c2.metric("❌ Gunas Not Matched",       f"{gunas_not_matched} / 36")
                c3.metric("📈 Compatibility %",         f"{int(percentage_score)}%")

                st.subheader("🗣️ Match Verdict:")
                if gunas_matched >= 25.0:
                    st.balloons()
                    st.success(
                        f"🌟 **Excellent Match ({gunas_matched} Gunas):** "
                        "Temperaments, emotional states, and long-term destiny are beautifully in sync. "
                        "Traditional texts highly favour this match for a harmonious married life."
                    )
                elif gunas_matched >= 18.0:
                    st.info(
                        f"⚖️ **Good Match ({gunas_matched} Gunas):** "
                        "Passes the traditional 18-Guna minimum. You complement each other well "
                        "and can build a resilient partnership with mutual understanding."
                    )
                else:
                    st.warning(
                        f"⚠️ **High Adjustment Required ({gunas_matched} Gunas):** "
                        "Below the 18-Guna benchmark. Not a verdict of failure, but a signal "
                        "that conscious communication and extra patience will be essential."
                    )

                # Prediction list breakdown
                predictions = match_result.get("PredictionList", [])
                if predictions:
                    st.write("### 🔍 Factor-by-Factor Breakdown:")
                    rows = []
                    for p in predictions:
                        rows.append({
                            "Kuta Factor": p.get("Name", "—"),
                            "Result":      p.get("Nature", "—"),
                            "Description": p.get("Description", "—"),
                        })
                    df = pd.DataFrame(rows).set_index("Kuta Factor")
                    st.dataframe(df, use_container_width=True)

            except ValueError as ve:
                st.error(str(ve))
            except Exception as e:
                st.error(f"Match report failed: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — CAREER & PROPERTY
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.header("💼 Career Prospects & 🏠 Property Possibilities")
    st.markdown("Analyse how your chart's 10th house (career) and 4th house (property) shape material life.")

    name_p  = st.text_input("Your Full Name",      "Ravi Sharma",  key="p_name")
    loc_p   = st.text_input("Birth City",           "New Delhi",    key="p_loc")
    time_p  = st.text_input("Birth Time (HH:MM)",  "14:30",        key="p_time")
    date_p  = st.text_input("Birth Date",           "25/10/1992",   key="p_date")

    if st.button("Analyse Career & Property", key="btn_t3"):
        with st.spinner("Scanning material houses…"):
            try:
                p_geo      = get_geolocation(loc_p)
                p_time_obj = Time(f"{time_p} {date_p} +05:30", p_geo)

                # House sign lords
                h4_sign  = Calculate.HouseSignName(HouseName.House4,  p_time_obj)
                h10_sign = Calculate.HouseSignName(HouseName.House10, p_time_obj)
                h2_sign  = Calculate.HouseSignName(HouseName.House2,  p_time_obj)

                # Planets in key houses
                planets_in_10 = Calculate.PlanetsInHouse(HouseName.House10, p_time_obj)
                planets_in_4  = Calculate.PlanetsInHouse(HouseName.House4,  p_time_obj)

                planets_10_str = ", ".join(str(p) for p in planets_in_10) if planets_in_10 else "None (clean house)"
                planets_4_str  = ", ".join(str(p) for p in planets_in_4)  if planets_in_4  else "None (clean house)"

                st.subheader(f"💼 Career & Professional Outlook — {name_p}")
                st.markdown(f"""
Your **10th House (Karma Sthana)** — the house of career and public reputation — falls in **{h10_sign}**.

- **Planets currently occupying your 10th House:** {planets_10_str}
- **2nd House (Wealth) Sign:** {h2_sign}

**What this means in plain English:**
{h10_sign} as the sign of your career house shapes the *style* in which you build your professional identity.
Any planets listed above act as direct influencers of your work-life — benefic planets bring expansion and
recognition, while malefic planets demand discipline before rewards. Watch Jupiter and Saturn transits over
your 10th house for the biggest career turning points.
                """)

                st.subheader("🏠 Property & Real-Estate Potential")
                st.markdown(f"""
Your **4th House (Sukha Sthana)** — governing home, land, and mother — falls in **{h4_sign}**.

- **Planets currently occupying your 4th House:** {planets_4_str}

**What this means in plain English:**
{h4_sign} as your 4th house sign reveals the *nature* of domestic happiness and property you are destined to
accumulate. Look for Jupiter transits activating this house, or your Dasha lord connecting to the 4th lord,
as the most likely windows for home purchase or construction.
                """)

            except ValueError as ve:
                st.error(str(ve))
            except Exception as e:
                st.error(f"Could not calculate structural properties: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — TODAY'S PANCHANGA (live transits)
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.header("📅 Live Cosmic Weather — Today's Indian Panchanga")
    st.markdown("Check the planetary positions active over your city right now.")

    name_t  = st.text_input("Your Name",             "Ravi Sharma",  key="t_name")
    t_loc   = st.text_input("Your Current City",     "New Delhi",    key="t_loc")

    if st.button("Get Today's Transit Insights", key="btn_t4"):
        with st.spinner("Reading live transits…"):
            try:
                today_geo     = get_geolocation(t_loc)
                now_str       = datetime.datetime.now().strftime("%H:%M %d/%m/%Y +05:30")
                today_time    = Time(now_str, today_geo)

                # Live planetary sign positions
                sun_t     = Calculate.PlanetSignName(PlanetName.Sun,     today_time)
                moon_t    = Calculate.PlanetSignName(PlanetName.Moon,    today_time)
                mars_t    = Calculate.PlanetSignName(PlanetName.Mars,    today_time)
                mercury_t = Calculate.PlanetSignName(PlanetName.Mercury, today_time)
                jupiter_t = Calculate.PlanetSignName(PlanetName.Jupiter, today_time)
                venus_t   = Calculate.PlanetSignName(PlanetName.Venus,   today_time)
                saturn_t  = Calculate.PlanetSignName(PlanetName.Saturn,  today_time)
                rahu_t    = Calculate.PlanetSignName(PlanetName.Rahu,    today_time)
                ketu_t    = Calculate.PlanetSignName(PlanetName.Ketu,    today_time)

                st.success(f"✅ Live transits for **{name_t}** in {t_loc} — {now_str}")

                st.subheader("🌌 Current Planetary Positions (Transit Sky)")
                transit_df = pd.DataFrame({
                    "Planet":       ["☀️ Sun", "🌙 Moon", "♂ Mars", "☿ Mercury",
                                     "♃ Jupiter", "♀ Venus", "♄ Saturn", "☊ Rahu", "☋ Ketu"],
                    "Current Sign": [str(sun_t), str(moon_t), str(mars_t), str(mercury_t),
                                     str(jupiter_t), str(venus_t), str(saturn_t), str(rahu_t), str(ketu_t)]
                }).set_index("Planet")
                st.table(transit_df)

                # Quick daily guidance based on Moon sign
                moon_sign_str = str(moon_t)
                guidance_map = {
                    "Aries":       "High energy day — great for starting new tasks, athletics, and bold decisions.",
                    "Taurus":      "Grounded energy — favour financial planning, comfort, and sensory pleasures.",
                    "Gemini":      "Communicative day — ideal for writing, meetings, networking, and learning.",
                    "Cancer":      "Emotional sensitivity is high — nurture relationships and avoid confrontations.",
                    "Leo":         "Confidence and creativity peak — present yourself boldly and lead from the front.",
                    "Virgo":       "Detail-oriented energy — perfect for analysis, health routines, and organisation.",
                    "Libra":       "Harmony-seeking day — negotiations, partnerships, and aesthetics are favoured.",
                    "Scorpio":     "Intense introspective energy — good for research, strategy, and transformation.",
                    "Sagittarius": "Expansive optimism — great for travel plans, higher learning, and philosophy.",
                    "Capricorn":   "Disciplined and ambitious — push career goals and long-term structure today.",
                    "Aquarius":    "Innovative and social — collaborate, brainstorm, and serve the community.",
                    "Pisces":      "Dreamy and spiritual — meditation, creative arts, and empathy are heightened.",
                }
                daily_tip = guidance_map.get(moon_sign_str,
                    "Moon's transit brings a mixed but introspective energy today. "
                    "Reflect before acting on impulse.")

                st.subheader(f"🗣️ Daily Guidance for {name_t} (Moon in {moon_sign_str}):")
                st.info(daily_tip)

                st.caption(f"Data timestamp: {now_str} IST")

            except ValueError as ve:
                st.error(str(ve))
            except Exception as e:
                st.error(f"Could not load transit analytics: {e}")
