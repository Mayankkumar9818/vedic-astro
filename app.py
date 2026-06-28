"""
VedaStro Comprehensive Vedic Astrology Dashboard
=================================================
India-only (IST +05:30 hardcoded).

Methods used — ALL verified against the provided method list:
  va.Calculate.SetAPIKey
  va.Calculate.LagnaSignName
  va.Calculate.PlanetRasiD1Sign        <- replaces hallucinated PlanetZodiacSign
  va.Calculate.AllPlanetRasiSigns      <- fallback for signs
  va.Calculate.NorthIndianChart
  va.Calculate.MarriageByJupiter
  va.Calculate.KujaDosaScore
  va.Calculate.AllHouseData
  va.Calculate.PlanetNirayanaLongitude <- replaces hallucinated PlanetLongitude
  va.Calculate.AllPlanetStrength
  va.Calculate.DasaForNow
  va.Calculate.MoonConstellation

Run:  streamlit run vedastro_dashboard.py
"""

import streamlit as st
from datetime import date, time as dtime
import traceback

# ── library guard ─────────────────────────────────────────────────────────────
try:
    import vedastro as va
    IMPORT_OK = True
    IMPORT_ERR = None
except Exception as e:
    IMPORT_OK = False
    IMPORT_ERR = str(e)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Jyotish Dashboard",
    page_icon="🔱",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid #e94560;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.5rem;
    }
    .metric-label {
        color: #a0a0b0;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    .metric-value {
        color: #f5c518;
        font-size: 1.3rem;
        font-weight: 700;
        margin-top: 0.2rem;
    }
    .section-header {
        color: #e94560;
        font-size: 1rem;
        font-weight: 600;
        border-left: 3px solid #e94560;
        padding-left: 0.6rem;
        margin: 1rem 0 0.5rem 0;
    }
    .verdict-box {
        background: #0f0f1a;
        border: 1px solid #4a4a6a;
        border-radius: 8px;
        padding: 1rem;
        margin-top: 0.5rem;
        line-height: 1.7;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# IMPORT GUARD
# ─────────────────────────────────────────────────────────────────────────────
if not IMPORT_OK:
    st.error(
        f"Could not import `vedastro`. Run: `pip install vedastro`\n\n"
        f"```\n{IMPORT_ERR}\n```"
    )
    st.stop()

try:
    va.Calculate.SetAPIKey("FreeAPIUser")
except Exception as e:
    st.warning(f"SetAPIKey: {e}")

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
for key, default in {
    "submitted": False,
    "person": {},
    "tab1": {}, "tab2": {}, "tab3": {}, "tab4": {},
    "errors": {},
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def make_time(h, m, day, month, year, city, lon, lat):
    geo = va.GeoLocation(city, lon, lat)
    s   = f"{h:02d}:{m:02d} {day:02d}/{month:02d}/{year} +05:30"
    return va.Time(s, geo)


def safe_str(val):
    try:
        return val.ToString()
    except Exception:
        return str(val)


def render_chart(chart):
    if chart is None:
        st.info("Chart data not available.")
        return
    if isinstance(chart, str):
        if chart.strip().startswith("<"):
            st.components.v1.html(chart, height=520, scrolling=True)
        else:
            st.text(chart)
    elif hasattr(chart, "_repr_html_"):
        st.components.v1.html(chart._repr_html_(), height=520, scrolling=True)
    elif hasattr(chart, "to_svg"):
        st.components.v1.html(chart.to_svg(), height=520, scrolling=True)
    else:
        st.text(safe_str(chart))


# ─────────────────────────────────────────────────────────────────────────────
# CALCULATION FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────
def calc_tab1(t):
    out, errs = {}, {}

    try:
        out["lagna"] = safe_str(va.Calculate.LagnaSignName(t))
    except Exception as e:
        errs["LagnaSignName"] = str(e); out["lagna"] = "—"

    try:
        out["moon_sign"] = safe_str(va.Calculate.PlanetRasiD1Sign(va.PlanetName.Moon, t))
    except Exception as e:
        errs["PlanetRasiD1Sign(Moon)"] = str(e)
        try:
            raw = safe_str(va.Calculate.AllPlanetRasiSigns(t))
            out["moon_sign"] = raw
        except Exception:
            out["moon_sign"] = "—"

    try:
        out["sun_sign"] = safe_str(va.Calculate.PlanetRasiD1Sign(va.PlanetName.Sun, t))
    except Exception as e:
        errs["PlanetRasiD1Sign(Sun)"] = str(e); out["sun_sign"] = "—"

    try:
        out["nakshatra"] = safe_str(va.Calculate.MoonConstellation(t))
    except Exception as e:
        errs["MoonConstellation"] = str(e); out["nakshatra"] = "—"

    try:
        out["dasa"] = safe_str(va.Calculate.DasaForNow(t))
    except Exception as e:
        errs["DasaForNow"] = str(e); out["dasa"] = "—"

    try:
        out["chart"] = va.Calculate.NorthIndianChart(t)
    except Exception as e:
        errs["NorthIndianChart"] = str(e); out["chart"] = None

    return out, errs


def calc_tab2(t):
    out, errs = {}, {}

    try:
        out["marriage_jupiter"] = safe_str(va.Calculate.MarriageByJupiter(t))
    except Exception as e:
        errs["MarriageByJupiter"] = str(e); out["marriage_jupiter"] = "—"

    try:
        score = va.Calculate.KujaDosaScore(t)
        out["kuja_score"] = safe_str(score)
        try:
            out["kuja_num"] = float(safe_str(score).split()[0])
        except Exception:
            out["kuja_num"] = None
    except Exception as e:
        errs["KujaDosaScore"] = str(e)
        out["kuja_score"] = "—"; out["kuja_num"] = None

    try:
        out["venus_sign"] = safe_str(va.Calculate.PlanetRasiD1Sign(va.PlanetName.Venus, t))
    except Exception as e:
        errs["PlanetRasiD1Sign(Venus)"] = str(e); out["venus_sign"] = "—"

    try:
        out["house7"] = safe_str(va.Calculate.AllHouseData(va.HouseName.House7, t))
    except Exception as e:
        errs["AllHouseData(House7)"] = str(e); out["house7"] = "—"

    return out, errs


def calc_tab3(t):
    out, errs = {}, {}

    for key, house in [("house10", va.HouseName.House10),
                        ("house2",  va.HouseName.House2),
                        ("house11", va.HouseName.House11)]:
        try:
            out[key] = safe_str(va.Calculate.AllHouseData(house, t))
        except Exception as e:
            errs[f"AllHouseData({house})"] = str(e); out[key] = "—"

    try:
        out["strengths"] = safe_str(va.Calculate.AllPlanetStrength(t))
    except Exception as e:
        errs["AllPlanetStrength"] = str(e); out["strengths"] = "—"

    try:
        out["saturn_sign"] = safe_str(va.Calculate.PlanetRasiD1Sign(va.PlanetName.Saturn, t))
    except Exception as e:
        errs["PlanetRasiD1Sign(Saturn)"] = str(e); out["saturn_sign"] = "—"

    return out, errs


def calc_tab4(t):
    out, errs = {}, {}
    planets = {
        "Saturn": va.PlanetName.Saturn,
        "Rahu":   va.PlanetName.Rahu,
        "Ketu":   va.PlanetName.Ketu,
        "Jupiter":va.PlanetName.Jupiter,
        "Mars":   va.PlanetName.Mars,
    }
    lons = {}
    for pname, planet in planets.items():
        try:
            lons[pname] = safe_str(va.Calculate.PlanetNirayanaLongitude(planet, t))
        except Exception as e:
            errs[f"PlanetNirayanaLongitude({pname})"] = str(e)
            lons[pname] = "—"
    out["longitudes"] = lons

    for key, planet in [("rahu_sign", va.PlanetName.Rahu),
                         ("ketu_sign", va.PlanetName.Ketu),
                         ("saturn_sign", va.PlanetName.Saturn)]:
        try:
            out[key] = safe_str(va.Calculate.PlanetRasiD1Sign(planet, t))
        except Exception as e:
            errs[f"PlanetRasiD1Sign({key})"] = str(e); out[key] = "—"

    sat  = out.get("saturn_sign", "—")
    rahu = out.get("rahu_sign",   "—")
    ketu = out.get("ketu_sign",   "—")
    sat_lon  = lons.get("Saturn", "—")
    rahu_lon = lons.get("Rahu",   "—")
    ketu_lon = lons.get("Ketu",   "—")

    out["verdict_en"] = (
        f"Shani (Saturn) is currently in **{sat}** at longitude **{sat_lon}**, "
        f"indicating karmic lessons around discipline, responsibility, and endurance. "
        f"Rahu in **{rahu}** ({rahu_lon}) amplifies worldly desires and unconventional paths, "
        f"while Ketu in **{ketu}** ({ketu_lon}) pulls towards detachment and spiritual introspection. "
        f"The nodal axis {rahu}–{ketu} defines your primary karmic axis in this lifetime."
    )
    out["verdict_hi"] = (
        f"शनि (Saturn) इस समय **{sat}** राशि में **{sat_lon}** अंश पर स्थित है। "
        f"यह कर्म, अनुशासन और सहनशीलता की परीक्षा का संकेत देता है। "
        f"राहु **{rahu}** राशि ({rahu_lon}) में होने से सांसारिक इच्छाएं और नवीन मार्ग प्रबल होते हैं। "
        f"केतु **{ketu}** राशि ({ketu_lon}) में वैराग्य और आध्यात्मिक चिंतन की प्रेरणा देता है। "
        f"{rahu}–{ketu} अक्ष आपके इस जन्म का मुख्य कर्म-अक्ष है।"
    )
    return out, errs


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR — INPUT FORM
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔱 जन्म विवरण")
    st.caption("Birth Details · IST only")

    with st.form("birth_form", clear_on_submit=False):
        name       = st.text_input("Name / नाम", placeholder="Full name")
        city       = st.text_input("Birth City / जन्म स्थान", value="New Delhi")
        birth_date = st.date_input(
            "Date of Birth / जन्म तिथि",
            value=date(1990, 1, 1),
            min_value=date(1900, 1, 1),
            max_value=date.today(),
        )
        birth_time = st.time_input("Time of Birth / जन्म समय", value=dtime(6, 0))
        st.markdown("**Coordinates**")
        lon = st.number_input("Longitude °E", value=77.2090, format="%.4f")
        lat = st.number_input("Latitude °N",  value=28.6139, format="%.4f")
        submitted = st.form_submit_button("✨ Generate Chart", use_container_width=True)

    st.markdown("---")
    st.caption("🇮🇳 India only · IST +05:30")

# ─────────────────────────────────────────────────────────────────────────────
# ON SUBMIT
# ─────────────────────────────────────────────────────────────────────────────
if submitted:
    for k in ("submitted", "person", "tab1", "tab2", "tab3", "tab4", "errors"):
        st.session_state[k] = {} if k not in ("submitted",) else False

    try:
        t = make_time(
            birth_time.hour, birth_time.minute,
            birth_date.day, birth_date.month, birth_date.year,
            city, lon, lat,
        )
        st.session_state["person"] = {
            "name": name or "—", "city": city,
            "date": str(birth_date), "time": str(birth_time),
        }
        with st.spinner("Calculating — please wait…"):
            d1, e1 = calc_tab1(t)
            d2, e2 = calc_tab2(t)
            d3, e3 = calc_tab3(t)
            d4, e4 = calc_tab4(t)

        st.session_state.update({
            "tab1": d1, "tab2": d2, "tab3": d3, "tab4": d4,
            "errors": {**e1, **e2, **e3, **e4},
            "submitted": True,
        })
    except Exception:
        st.session_state["errors"] = {"__init__": traceback.format_exc()}
        st.session_state["submitted"] = True

# ─────────────────────────────────────────────────────────────────────────────
# MAIN DISPLAY
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("# 🔱 Jyotish Dashboard")
st.caption("Vedic Astrology · India Edition · IST +05:30")

if not st.session_state["submitted"]:
    st.info("👈 Fill in your birth details in the sidebar and click **Generate Chart**.")
    st.stop()

p = st.session_state["person"]
st.markdown(f"### {p.get('name','—')} · {p.get('city','—')} · {p.get('date','—')} {p.get('time','—')} IST")
st.divider()

errs = st.session_state["errors"]
if errs:
    with st.expander(f"⚠️ {len(errs)} calculation warning(s) — click to expand", expanded=False):
        for method, msg in errs.items():
            st.error(f"**{method}**\n```\n{msg}\n```")

tab1, tab2, tab3, tab4 = st.tabs([
    "🪐 Identity & Chart",
    "💍 Marriage & Relations",
    "💼 Profession & Assets",
    "🌀 Transits & Karma",
])

# ── TAB 1 ─────────────────────────────────────────────────────────────────────
with tab1:
    d = st.session_state["tab1"]

    def mcard(col, label, val):
        col.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-label">{label}</div>'
            f'<div class="metric-value">{val}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    c1, c2, c3, c4 = st.columns(4)
    mcard(c1, "Lagna / लग्न",        d.get("lagna",     "—"))
    mcard(c2, "Moon Sign / चंद्र",   d.get("moon_sign", "—"))
    mcard(c3, "Sun Sign / सूर्य",    d.get("sun_sign",  "—"))
    mcard(c4, "Nakshatra / नक्षत्र", d.get("nakshatra", "—"))

    st.markdown('<div class="section-header">Current Dasha Period</div>', unsafe_allow_html=True)
    st.code(d.get("dasa", "—"), language=None)

    st.markdown('<div class="section-header">North Indian Chart / उत्तर भारतीय कुंडली</div>',
                unsafe_allow_html=True)
    render_chart(d.get("chart"))

# ── TAB 2 ─────────────────────────────────────────────────────────────────────
with tab2:
    d = st.session_state["tab2"]
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">Marriage Timing — Jupiter / विवाह काल</div>',
                    unsafe_allow_html=True)
        st.markdown(f'<div class="verdict-box">{d.get("marriage_jupiter", "—")}</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="section-header">Venus Sign / शुक्र राशि</div>',
                    unsafe_allow_html=True)
        st.metric("Venus", d.get("venus_sign", "—"))

    with col2:
        st.markdown('<div class="section-header">Kuja Dosha Score / मंगल दोष</div>',
                    unsafe_allow_html=True)
        kuja_num = d.get("kuja_num")
        if kuja_num is not None:
            color = "#cc3333" if kuja_num > 50 else "#f5c518" if kuja_num > 25 else "#22bb66"
            st.markdown(
                f'<div class="metric-card">'
                f'<div class="metric-label">Score (0–100)</div>'
                f'<div class="metric-value" style="color:{color}">{kuja_num:.1f}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.progress(min(int(kuja_num), 100))
            if kuja_num > 50:
                st.warning("Significant Kuja Dosha detected. Remedies advised.")
            elif kuja_num > 25:
                st.info("Mild Kuja Dosha present.")
            else:
                st.success("Kuja Dosha is minimal.")
        else:
            st.metric("Kuja Dosha", d.get("kuja_score", "—"))

    st.markdown('<div class="section-header">7th House / सप्तम भाव</div>', unsafe_allow_html=True)
    st.code(d.get("house7", "—"), language=None)

# ── TAB 3 ─────────────────────────────────────────────────────────────────────
with tab3:
    d = st.session_state["tab3"]
    col1, col2 = st.columns([3, 2])

    with col1:
        for label, key in [
            ("10th House — Career / दशम भाव", "house10"),
            ("2nd House — Wealth / द्वितीय भाव", "house2"),
            ("11th House — Gains / एकादश भाव", "house11"),
        ]:
            st.markdown(f'<div class="section-header">{label}</div>', unsafe_allow_html=True)
            st.code(d.get(key, "—"), language=None)

    with col2:
        st.markdown('<div class="section-header">Saturn Sign / शनि राशि</div>',
                    unsafe_allow_html=True)
        st.metric("Saturn", d.get("saturn_sign", "—"))
        st.markdown('<div class="section-header">Planet Strengths</div>', unsafe_allow_html=True)
        st.code(d.get("strengths", "—"), language=None)

# ── TAB 4 ─────────────────────────────────────────────────────────────────────
with tab4:
    d = st.session_state["tab4"]

    st.markdown('<div class="section-header">Karmic Planet Longitudes (Nirayana)</div>',
                unsafe_allow_html=True)
    lons = d.get("longitudes", {})
    if lons:
        cols = st.columns(len(lons))
        for i, (pname, lon_val) in enumerate(lons.items()):
            cols[i].metric(pname, lon_val)

    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Saturn / शनि", d.get("saturn_sign", "—"))
    c2.metric("Rahu / राहु",  d.get("rahu_sign",  "—"))
    c3.metric("Ketu / केतु",  d.get("ketu_sign",  "—"))

    st.divider()
    st.markdown('<div class="section-header">Karmic Verdict / कर्म निर्णय</div>',
                unsafe_allow_html=True)
    v1, v2 = st.columns(2)
    with v1:
        st.markdown(f'<div class="verdict-box">{d.get("verdict_en","—")}</div>',
                    unsafe_allow_html=True)
    with v2:
        st.markdown(f'<div class="verdict-box">{d.get("verdict_hi","—")}</div>',
                    unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "Built with `vedastro` · India only (IST +05:30) · "
    "Methods: LagnaSignName · PlanetRasiD1Sign · AllPlanetRasiSigns · "
    "NorthIndianChart · MarriageByJupiter · KujaDosaScore · "
    "AllHouseData · PlanetNirayanaLongitude · AllPlanetStrength · "
    "DasaForNow · MoonConstellation"
)
