import streamlit as st
import requests
import json
from datetime import datetime, timedelta

# -----------------------------
# TSheets API Settings
# -----------------------------
API_BASE_URL = "https://rest.tsheets.com/api/v1"
API_TOKEN = "your_api_token_here"  # Replace with your actual API token
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

# -----------------------------
# API Helper Functions
# -----------------------------
def fetch_schedule_events(start, end):
    """
    Fetch schedule events between two ISO 8601 date/times.
    The API call uses the 'start' and 'end' parameters to filter events.
    """
    url = f"{API_BASE_URL}/schedule_events"
    params = {
        "start": start,
        "end": end,
        "supplemental_data": "yes"
    }
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error fetching schedules: {response.status_code} - {response.text}")
        return None

def create_schedule_event(event_data):
    """
    Create a new schedule event.
    event_data should be a dictionary with properties like:
      schedule_calendar_id, start, end, title, notes, assigned_user_ids, etc.
    """
    url = f"{API_BASE_URL}/schedule_events"
    payload = {"data": [event_data], "team_events": "base"}
    response = requests.post(url, headers=HEADERS, json=payload)
    return response

def update_schedule_event(event_data):
    """
    Update an existing schedule event.
    event_data should include the event 'id' and any fields to update.
    """
    url = f"{API_BASE_URL}/schedule_events"
    payload = {"data": [event_data], "team_events": "base"}
    response = requests.put(url, headers=HEADERS, json=payload)
    return response

def delete_schedule_event(event_id, schedule_calendar_id):
    """
    “Delete” a schedule event by marking it inactive.
    This function updates the event's 'active' flag to False.
    """
    data = {
        "id": event_id,
        "schedule_calendar_id": schedule_calendar_id,
        "active": False
    }
    url = f"{API_BASE_URL}/schedule_events"
    payload = {"data": [data], "team_events": "base"}
    response = requests.put(url, headers=HEADERS, json=payload)
    return response

# -----------------------------
# Streamlit Multi-Page Navigation
# -----------------------------
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Select Page", 
    ["Home", "View Schedules", "Create Schedule", "Update Schedule", "Delete Schedule"])

# -----------------------------
# Home Page
# -----------------------------
if page == "Home":
    st.title("TSheets Schedule Manager")
    st.write("Welcome to the TSheets Schedule Manager app. Use the sidebar to navigate:")
    st.markdown("""
    - **View Schedules:** Fetch and display schedule events within a date range.
    - **Create Schedule:** Add a new schedule event.
    - **Update Schedule:** Modify an existing schedule event.
    - **Delete Schedule:** Deactivate (delete) an event.
    """)
    
# -----------------------------
# View Schedules Page
# -----------------------------
elif page == "View Schedules":
    st.title("View Schedule Events")
    st.write("Select a date range to view schedule events.")
    # Default to one week ago and 30 days ahead
    start_date = st.date_input("Start Date", datetime.today() - timedelta(days=7))
    end_date = st.date_input("End Date", datetime.today() + timedelta(days=30))
    
    if st.button("Fetch Schedules"):
        start_iso = datetime.combine(start_date, datetime.min.time()).isoformat()
        end_iso = datetime.combine(end_date, datetime.max.time()).isoformat()
        data = fetch_schedule_events(start_iso, end_iso)
        if data:
            # TSheets returns schedule events in a dictionary keyed by event id
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

# -----------------------------
# Create Schedule Page
# -----------------------------
elif page == "Create Schedule":
    st.title("Create Schedule Event")
    st.write("Fill out the details to create a new schedule event.")
    schedule_calendar_id = st.text_input("Schedule Calendar ID")
    start = st.text_input("Start Time (ISO 8601)", value=datetime.now().isoformat())
    end = st.text_input("End Time (ISO 8601)", value=(datetime.now() + timedelta(hours=2)).isoformat())
    title = st.text_input("Title")
    notes = st.text_area("Notes")
    assigned_user_ids = st.text_input("Assigned User IDs (comma-separated)")
    draft = st.checkbox("Draft", value=True)
    active = st.checkbox("Active", value=True)
    all_day = st.checkbox("All Day", value=False)
    jobcode_id = st.text_input("Job Code ID")
    color = st.text_input("Color (Hex Code)")
    
    if st.button("Create Event"):
        # Build event data from form inputs
        event_data = {
            "schedule_calendar_id": int(schedule_calendar_id) if schedule_calendar_id else None,
            "start": start,
            "end": end,
            "title": title,
            "notes": notes,
            "assigned_user_ids": [int(uid.strip()) for uid in assigned_user_ids.split(",") if uid.strip()] if assigned_user_ids else [],
            "draft": draft,
            "active": active,
            "all_day": all_day,
            "jobcode_id": int(jobcode_id) if jobcode_id else 0,
            "color": color
        }
        # Remove None values from the payload
        event_data = {k: v for k, v in event_data.items() if v is not None}
        response = create_schedule_event(event_data)
        if response.status_code in [200, 201]:
            st.success("Schedule event created successfully!")
            st.json(response.json())
        else:
            st.error(f"Failed to create event: {response.status_code} - {response.text}")

# -----------------------------
# Update Schedule Page
# -----------------------------
elif page == "Update Schedule":
    st.title("Update Schedule Event")
    st.write("Fill out the details to update an existing schedule event.")
    event_id = st.text_input("Event ID to update")
    schedule_calendar_id = st.text_input("Schedule Calendar ID (required)")
    new_title = st.text_input("New Title")
    new_start = st.text_input("New Start Time (ISO 8601)")
    new_end = st.text_input("New End Time (ISO 8601)")
    new_notes = st.text_area("New Notes")
    new_assigned_user_ids = st.text_input("New Assigned User IDs (comma-separated)")
    new_draft = st.checkbox("Draft")
    new_active = st.checkbox("Active")
    new_all_day = st.checkbox("All Day")
    new_jobcode_id = st.text_input("New Job Code ID")
    new_color = st.text_input("New Color (Hex Code)")
    
    if st.button("Update Event"):
        update_data = {
            "id": int(event_id) if event_id else None,
            "schedule_calendar_id": int(schedule_calendar_id) if schedule_calendar_id else None,
        }
        if new_title:
            update_data["title"] = new_title
        if new_start:
            update_data["start"] = new_start
        if new_end:
            update_data["end"] = new_end
        if new_notes:
            update_data["notes"] = new_notes
        if new_assigned_user_ids:
            update_data["assigned_user_ids"] = [int(uid.strip()) for uid in new_assigned_user_ids.split(",") if uid.strip()]\n        update_data["draft"] = new_draft\n        update_data["active"] = new_active\n        update_data["all_day"] = new_all_day\n        if new_jobcode_id:\n            update_data["jobcode_id"] = int(new_jobcode_id)\n        if new_color:\n            update_data["color"] = new_color\n        \n        # Remove keys with None values\n        update_data = {k: v for k, v in update_data.items() if v is not None}\n        \n        response = update_schedule_event(update_data)\n        if response.status_code in [200, 201]:\n            st.success(\"Schedule event updated successfully!\")\n            st.json(response.json())\n        else:\n            st.error(f\"Failed to update event: {response.status_code} - {response.text}\")\n\n# -----------------------------\n# Delete (Deactivate) Schedule Page\n# -----------------------------\nelif page == \"Delete Schedule\":\n    st.title(\"Delete (Deactivate) Schedule Event\")\n    st.write(\"Enter the Event ID and Schedule Calendar ID to deactivate (delete) an event.\")\n    event_id = st.text_input(\"Event ID to deactivate\")\n    schedule_calendar_id = st.text_input(\"Schedule Calendar ID (required)\")\n    if st.button(\"Deactivate Event\"):\n        if not event_id or not schedule_calendar_id:\n            st.error(\"Please provide both Event ID and Schedule Calendar ID.\")\n        else:\n            response = delete_schedule_event(int(event_id), int(schedule_calendar_id))\n            if response.status_code in [200, 201]:\n                st.success(\"Schedule event deactivated successfully!\")\n                st.json(response.json())\n            else:\n                st.error(f\"Failed to deactivate event: {response.status_code} - {response.text}\")\n```

### How It Works

- **Home:** An introduction with navigation instructions.
- **View Schedules:** Select a start and end date. The app retrieves events from the TSheets API and displays key details.
- **Create Schedule:** A form to enter details for a new schedule event. On submission, a POST request creates the event.
- **Update Schedule:** A form to update an existing event (by ID). The app sends a PUT request with the new values.
- **Delete Schedule:** A form that “deactivates” an event (sets its active flag to False).

Run this app with `streamlit run tsheets_app.py`. Adjust any fields or parameters to suit your requirements. Enjoy building your TSheets Schedule Manager!
