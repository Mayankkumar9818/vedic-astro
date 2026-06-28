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
    name = st.text_input("Name", "Mayank")
    city = st.text_input("City", "New Delhi")
    date = st.date_input("Date", datetime.date(1992, 10, 25))
    time_str = st.text_input("Time (HH:MM)", "14:30")
    submit = st.form_submit_button("Generate")

if submit:
    try:
        # 1. Setup Time/Location (Stable)
        geo = va.GeoLocation(city, 77.209, 28.613)
        time_obj = va.Time(f"{time_str} {date.strftime('%d/%m/%Y')} +05:30", geo)

        # 2. Stable Calculations
        # We use .Name property directly from the result of the calculation
        lagna = va.Calculate.RisingSignName(time_obj)
        moon_sign = va.Calculate.MoonSignName(time_obj)
        
        # 3. Display
        st.success("Calculations Complete")
        col1, col2 = st.columns(2)
        col1.metric("Lagna", str(lagna))
        col2.metric("Moon Sign", str(moon_sign))
        
        st.write(f"The analysis for {name} shows your core identity is rooted in {lagna} and your emotional landscape is governed by {moon_sign}.")
        
    except Exception as e:
        st.error(f"Engine Error: {str(e)}")
