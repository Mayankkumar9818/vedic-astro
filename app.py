import streamlit as st
import datetime
import vedastro as va

# Configuration
st.set_page_config(layout="wide")

# Initialize API
try:
    va.Calculate.SetAPIKey('FreeAPIUser')
except:
    pass

st.title("🔮 Your Digital Pandit")

# Use session state to keep the results on screen after clicking
if 'results' not in st.session_state:
    st.session_state.results = None

with st.form("birth_data"):
    u_name = st.text_input("Name", "Mayank")
    city = st.text_input("City", "New Delhi")
    date = st.date_input("Date", datetime.date(1992, 10, 25))
    time_str = st.text_input("Time (HH:MM)", "14:30")
    submit = st.form_submit_button("Generate")

    if submit:
        try:
            # Setup Time/Location
            geo = va.GeoLocation(city, 77.209, 28.613)
            time_obj = va.Time(f"{time_str} {date.strftime('%d/%m/%Y')} +05:30", geo)

            # Calculation
            lagna = str(va.Calculate.LagnaSignName(time_obj))
            moon_sign = str(va.Calculate.PlanetZodiacSign(va.PlanetName.Moon, time_obj).ToString())
            sun_sign = str(va.Calculate.PlanetZodiacSign(va.PlanetName.Sun, time_obj).ToString())
            
            # Store in session state
            st.session_state.results = {
                "lagna": lagna,
                "moon": moon_sign,
                "sun": sun_sign,
                "name": u_name
            }
        except Exception as e:
            st.session_state.results = {"error": str(e)}

# Display results if they exist in state
if st.session_state.results:
    res = st.session_state.results
    if "error" in res:
        st.error(f"Engine Error: {res['error']}")
    else:
        st.success("Calculations Complete!")
        col1, col2, col3 = st.columns(3)
        col1.metric("Lagna", res["lagna"])
        col2.metric("Moon Sign", res["moon"])
        col3.metric("Sun Sign", res["sun"])
        
        st.write(f"The analysis for {res['name']} shows your core identity is rooted in {res['lagna']}, "
                 f"your emotional landscape is governed by the Moon in {res['moon']}, "
                 f"and your soul's expression is influenced by the Sun in {res['sun']}.")
