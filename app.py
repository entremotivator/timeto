import streamlit as st
import requests
import json
from datetime import datetime, timedelta

# -----------------------------
# API Base URL
# -----------------------------
API_BASE_URL = "https://rest.tsheets.com/api/v1"

# -----------------------------
# Streamlit API Token Input
# -----------------------------
st.sidebar.title("Settings")
api_token = st.sidebar.text_input("Enter API Token", type="password")

if not api_token:
    st.sidebar.warning("Please enter your API token to continue.")
    st.stop()

HEADERS = {
    "Authorization": f"Bearer {api_token}",
    "Content-Type": "application/json"
}

# -----------------------------
# API Helper Functions
# -----------------------------
def fetch_schedule_events(start, end):
    url = f"{API_BASE_URL}/schedule_events"
    params = {"start": start, "end": end, "supplemental_data": "yes"}
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error fetching schedules: {response.status_code} - {response.text}")
        return None

# -----------------------------
# Streamlit Navigation
# -----------------------------
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Select Page", ["Home", "View Schedules"])

# -----------------------------
# Home Page
# -----------------------------
if page == "Home":
    st.title("TSheets Schedule Manager")
    st.write("Welcome to the TSheets Schedule Manager app. Use the sidebar to navigate.")

# -----------------------------
# View Schedules Page
# -----------------------------
elif page == "View Schedules":
    st.title("View Schedule Events")
    start_date = st.date_input("Start Date", datetime.today() - timedelta(days=7))
    end_date = st.date_input("End Date", datetime.today() + timedelta(days=30))
    
    if st.button("Fetch Schedules"):
        start_iso = datetime.combine(start_date, datetime.min.time()).isoformat()
        end_iso = datetime.combine(end_date, datetime.max.time()).isoformat()
        data = fetch_schedule_events(start_iso, end_iso)
        if data:
            schedules = data.get("results", {}).get("schedule_events", {})
            if schedules:
                st.success(f"Fetched {len(schedules)} schedule event(s).")
                for key, event in schedules.items():
                    st.markdown(f"### Event ID: {event.get('id', 'N/A')}")
                    st.write(f"**Title:** {event.get('title', 'N/A')}")
                    st.write(f"**Start:** {event.get('start', 'N/A')}")
                    st.write(f"**End:** {event.get('end', 'N/A')}")
                    st.write(f"**Notes:** {event.get('notes', '')}")
                    st.markdown("---")
            else:
                st.warning("No schedule events found for the selected range.")
