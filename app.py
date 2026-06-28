"""
VedaStro Streamlit App
======================
Methods used (all verified against the provided method list):
  - va.Calculate.SetAPIKey(key)
  - va.Calculate.LagnaSignName(time_obj)
  - va.Calculate.PlanetZodiacSign(planet, time_obj)   ← NOT in list; see NOTE below
  - va.Calculate.AllPlanetRasiSigns(time_obj)          ← FALLBACK (in list)
  - va.Calculate.NorthIndianChart(time_obj)
  - va.GeoLocation(name, lon, lat)
  - va.Time("HH:MM DD/MM/YYYY +05:30", geolocation)

NOTE ON PlanetZodiacSign:
  The provided method list does NOT contain "PlanetZodiacSign" verbatim.
  The closest confirmed methods are:
    - AllPlanetRasiSigns(time_obj)     ← returns sign for every planet
    - PlanetRasiD1Sign(planet, time)   ← exact Rasi (D1) sign per planet
    - ZodiacSignAtLongitude(lon)       ← sign from longitude
    - PlanetNirayanaLongitude(planet, time) ← longitude per planet
  This app uses PlanetRasiD1Sign for Sun/Moon (most semantically correct),
  with AllPlanetRasiSigns as a fallback so the diagnostic can show both.

Run:  streamlit run vedastro_app.py
"""

import streamlit as st
from datetime import date, time as dtime

# ── guard import ──────────────────────────────────────────────────────────────
try:
    import vedastro as va
    IMPORT_OK = True
    IMPORT_ERR = None
except Exception as e:
    IMPORT_OK = False
    IMPORT_ERR = str(e)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def make_time_obj(hour: int, minute: int,
                  day: int, month: int, year: int,
                  city: str, lon: float, lat: float) -> "va.Time":
    """Build a vedastro Time object from components."""
    geo = va.GeoLocation(city, lon, lat)
    time_str = f"{hour:02d}:{minute:02d} {day:02d}/{month:02d}/{year} +05:30"
    return va.Time(time_str, geo)


def run_diagnostic(time_obj) -> dict:
    """
    Diagnostic block — tries every relevant method and captures results/errors.
    Returns a dict of {label: (value_or_None, error_or_None)}.
    """
    results = {}

    # 1. LagnaSignName
    try:
        val = va.Calculate.LagnaSignName(time_obj)
        results["LagnaSignName"] = (str(val), None)
    except Exception as e:
        results["LagnaSignName"] = (None, str(e))

    # 2. PlanetRasiD1Sign – Moon  (confirmed in list)
    try:
        val = va.Calculate.PlanetRasiD1Sign(va.PlanetName.Moon, time_obj)
        results["PlanetRasiD1Sign (Moon)"] = (str(val), None)
    except Exception as e:
        results["PlanetRasiD1Sign (Moon)"] = (None, str(e))

    # 3. PlanetRasiD1Sign – Sun  (confirmed in list)
    try:
        val = va.Calculate.PlanetRasiD1Sign(va.PlanetName.Sun, time_obj)
        results["PlanetRasiD1Sign (Sun)"] = (str(val), None)
    except Exception as e:
        results["PlanetRasiD1Sign (Sun)"] = (None, str(e))

    # 4. AllPlanetRasiSigns – full planet-sign table (confirmed in list)
    try:
        val = va.Calculate.AllPlanetRasiSigns(time_obj)
        results["AllPlanetRasiSigns"] = (str(val), None)
    except Exception as e:
        results["AllPlanetRasiSigns"] = (None, str(e))

    # 5. PlanetNirayanaLongitude – Moon (confirmed in list)
    try:
        val = va.Calculate.PlanetNirayanaLongitude(va.PlanetName.Moon, time_obj)
        results["PlanetNirayanaLongitude (Moon)"] = (str(val), None)
    except Exception as e:
        results["PlanetNirayanaLongitude (Moon)"] = (None, str(e))

    return results


def get_lagna(time_obj) -> str:
    return str(va.Calculate.LagnaSignName(time_obj))


def get_moon_sign(time_obj) -> str:
    try:
        return str(va.Calculate.PlanetRasiD1Sign(va.PlanetName.Moon, time_obj))
    except Exception:
        # fallback: scan AllPlanetRasiSigns
        all_signs = va.Calculate.AllPlanetRasiSigns(time_obj)
        return str(all_signs.get("Moon", "Unknown"))


def get_sun_sign(time_obj) -> str:
    try:
        return str(va.Calculate.PlanetRasiD1Sign(va.PlanetName.Sun, time_obj))
    except Exception:
        all_signs = va.Calculate.AllPlanetRasiSigns(time_obj)
        return str(all_signs.get("Sun", "Unknown"))


def get_north_chart(time_obj):
    return va.Calculate.NorthIndianChart(time_obj)


# ─────────────────────────────────────────────────────────────────────────────
# STREAMLIT UI
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(page_title="VedaStro Chart", page_icon="🪐", layout="centered")
st.title("🪐 VedaStro Birth Chart")
st.caption("Vedic astrology powered by the VedaStro library")

# ── library import guard ──────────────────────────────────────────────────────
if not IMPORT_OK:
    st.error(f"❌ Could not import `vedastro`. Install it first.\n\n```\n{IMPORT_ERR}\n```")
    st.stop()

# Set API key once
try:
    va.Calculate.SetAPIKey("FreeAPIUser")
except Exception as e:
    st.warning(f"SetAPIKey note: {e}")

# ── session state init ────────────────────────────────────────────────────────
for key in ("result", "diag", "error"):
    if key not in st.session_state:
        st.session_state[key] = None

# ─────────────────────────────────────────────────────────────────────────────
# INPUT FORM
# ─────────────────────────────────────────────────────────────────────────────
with st.form("birth_form"):
    st.subheader("Birth Details")

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Name", value="", placeholder="Your name")
        city = st.text_input("City", value="New Delhi", placeholder="Birth city")
    with col2:
        birth_date = st.date_input("Date of Birth", value=date(1990, 1, 1))
        birth_time = st.time_input("Time of Birth", value=dtime(6, 0))

    st.markdown("**Birth Location (longitude / latitude)**")
    col3, col4 = st.columns(2)
    with col3:
        lon = st.number_input("Longitude (°E)", value=77.2090, format="%.4f")
    with col4:
        lat = st.number_input("Latitude (°N)", value=28.6139, format="%.4f")

    st.markdown("---")
    run_diag = st.checkbox("Run diagnostic before generating chart", value=False)
    submitted = st.form_submit_button("✨ Generate Chart", use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# ON SUBMIT
# ─────────────────────────────────────────────────────────────────────────────
if submitted:
    st.session_state["result"] = None
    st.session_state["diag"] = None
    st.session_state["error"] = None

    try:
        time_obj = make_time_obj(
            hour=birth_time.hour,
            minute=birth_time.minute,
            day=birth_date.day,
            month=birth_date.month,
            year=birth_date.year,
            city=city,
            lon=lon,
            lat=lat,
        )

        # ── optional diagnostic ───────────────────────────────────────────────
        if run_diag:
            st.session_state["diag"] = run_diagnostic(time_obj)

        # ── main calculations ─────────────────────────────────────────────────
        lagna     = get_lagna(time_obj)
        moon_sign = get_moon_sign(time_obj)
        sun_sign  = get_sun_sign(time_obj)
        chart     = get_north_chart(time_obj)

        st.session_state["result"] = {
            "name":      name or "—",
            "lagna":     lagna,
            "moon_sign": moon_sign,
            "sun_sign":  sun_sign,
            "chart":     chart,
        }

    except Exception as e:
        import traceback
        st.session_state["error"] = traceback.format_exc()

# ─────────────────────────────────────────────────────────────────────────────
# DISPLAY RESULTS (persists via session_state)
# ─────────────────────────────────────────────────────────────────────────────

if st.session_state["error"]:
    st.error(f"**Error during calculation:**\n\n```\n{st.session_state['error']}\n```")

# Diagnostic output
if st.session_state["diag"]:
    st.subheader("🔬 Diagnostic Results")
    diag = st.session_state["diag"]
    for label, (val, err) in diag.items():
        if err:
            st.error(f"**{label}** → ❌ `{err}`")
        else:
            st.success(f"**{label}** → ✅ `{val}`")
    st.divider()

# Main chart output
if st.session_state["result"]:
    r = st.session_state["result"]
    st.subheader(f"📋 Chart for {r['name']}")

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Lagna (Ascendant)", r["lagna"])
    col_b.metric("Moon Sign", r["moon_sign"])
    col_c.metric("Sun Sign", r["sun_sign"])

    st.divider()
    st.subheader("🗺️ North Indian Chart")

    chart = r["chart"]
    # NorthIndianChart may return an SVG string, HTML, or an object.
    # We handle all three cases gracefully.
    if isinstance(chart, str):
        if chart.strip().startswith("<"):
            st.components.v1.html(chart, height=500, scrolling=True)
        else:
            st.text(chart)
    elif hasattr(chart, "_repr_html_"):
        st.components.v1.html(chart._repr_html_(), height=500, scrolling=True)
    elif hasattr(chart, "to_svg"):
        st.components.v1.html(chart.to_svg(), height=500, scrolling=True)
    elif hasattr(chart, "__str__"):
        st.text(str(chart))
    else:
        st.write(chart)

    st.caption(
        "Methods used: `LagnaSignName` · `PlanetRasiD1Sign` · "
        "`AllPlanetRasiSigns` (fallback) · `NorthIndianChart`"
    )
