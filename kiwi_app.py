import streamlit as st
from kiwi_connection import KiwiConnection
import datetime
from dateutil.parser import isoparse
def format_datetime(datetime_str):
    date_part, time_part = datetime_str.split("T")
    time_part = time_part[:-5]  # Removing the ".000Z" from the time
    return f"{date_part} {time_part}"

def add_bg_from_url():
    st.markdown(
         f"""
         <style>
         .stApp {{
             background-image: url("https://cdn.pixabay.com/photo/2019/09/05/15/25/airbus-4454338_1280.jpg");
             background-attachment: fixed;
             background-size: cover
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

st.set_page_config(layout="wide")
add_bg_from_url() 


st.title("Flight Search")
st.write("This is an online flight search system that implements Streamlit connection feature to access Kiwi API.")
conn = st.experimental_connection("kiwiapi", type=KiwiConnection, apikey=st.secrets["KIWI_API_KEY"])

#st.write("My cool secrets:", st.secrets["my_cool_secrets"]["things_i_like"])
#st.write("My Key:", st.secrets.KIWI_API_KEY)

flights = []
col1, col2 = st.columns([0.5, 0.5], gap='medium')
with col1:
    with st.form("my_form"):
        fly_from = st.text_input("**From airport**", "JFK")
        fly_to = st.text_input("To airport", "PRG")

        date_from = st.date_input("Departure date", value=datetime.date(2023, 9, 3))
        date_to = st.date_input("Return date", value=datetime.date(2023, 9, 9))
        date_from_str = date_from.strftime("%d/%m/%Y") 
        date_to_str = date_to.strftime("%d/%m/%Y")
        adults = st.number_input("Adults", min_value=1) 
        children = st.number_input("Children", min_value=0)
        infants = st.number_input("Infants", min_value=0)

        sort = st.selectbox("Sort by", ["price", "duration"])
        limit = st.number_input("Limit", min_value=10)

        submitted = st.form_submit_button("Submit")

        if submitted:
            # Call API with input parameters
            results = conn.query(
                fly_from=fly_from, 
                fly_to=fly_to,
                date_from=date_from_str,
                date_to=date_to_str,
                adults=adults,
                children=children,
                infants=infants,
                sort=sort,
                limit=limit
            )
            
            if results:
                flights = results['data']

with col2:
    for flight in flights:
        
        overall_departure_time = min(route["local_departure"] for route in flight["route"])
        overall_arrival_time = max(route["local_arrival"] for route in flight["route"])
        #total_duration = sum(route["total_duration"] for route in flight["route"].values())
        city_from = flight["cityFrom"]
        city_to = flight["cityTo"]
        fly_from = flight["flyFrom"]
        fly_to = flight["flyTo"]
        connection_number = len(flight["route"]) - 1
        price = flight["price"]
        
        overall_departure_time_fm = format_datetime(str(overall_departure_time))
        overall_arrival_time_fm = format_datetime(str(overall_arrival_time))

        utc_departure_time = flight["route"][0]["utc_departure"]
        utc_arrival_time = flight["route"][connection_number]["utc_arrival"]
        total_hours = (isoparse(utc_arrival_time) - isoparse(utc_departure_time)).total_seconds() / 3600

        with st.expander(f'{overall_departure_time_fm} - {overall_arrival_time_fm}, {city_from}/{fly_from} - {city_to}/{fly_to}, total_hours: {total_hours:.1f}, #Connects:{connection_number}, Price:{price}USD'):
            st.json(flight)
