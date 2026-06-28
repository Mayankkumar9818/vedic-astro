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

# User Input
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

        # CORRECTED API CALLS based on your provided list:
        # 1. Rising Sign
        lagna = va.Calculate.LagnaSignName(time_obj)
        
        # 2. Moon Sign (Using PlanetZodiacSign as per verified method list)
        moon_sign_obj = va.Calculate.PlanetZodiacSign(va.PlanetName.Moon, time_obj)
        moon_sign = moon_sign_obj.ToString() # Converts the object to string
        
        # 3. Sun Sign
        sun_sign_obj = va.Calculate.PlanetZodiacSign(va.PlanetName.Sun, time_obj)
        sun_sign = sun_sign_obj.ToString()

        # Display
        st.success("Calculations Complete")
        col1, col2, col3 = st.columns(3)
        col1.metric("Lagna", str(lagna))
        col2.metric("Moon Sign", str(moon_sign))
        col3.metric("Sun Sign", str(sun_sign))
        
        st.write(f"The analysis for {u_name} shows your rising sign is {lagna}, "
                 f"your emotional landscape is governed by the Moon in {moon_sign}, "
                 f"and your soul's expression is influenced by the Sun in {sun_sign}.")
        
    except Exception as e:
        st.error(f"Engine Error: {str(e)}")
