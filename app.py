import streamlit as st
import requests
from datetime import datetime, timedelta, timezone

# -----------------------------
# API and Calendar Settings
# -----------------------------
API_BASE_URL = "https://rest.tsheets.com/api/v1"
# Fixed Schedule Calendar ID (as per requirement)
SCHEDULE_CALENDAR_ID = 563646  
# Reference: Rest.tsheets.com/api.v1/schedule_calenders id563646

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
    """
    Fetch schedule events between two ISO 8601 timestamps for the fixed Schedule Calendar ID.
    The timestamps must be in a valid ISO-8601 format (without microseconds).
    """
    url = f"{API_BASE_URL}/schedule_events"
    params = {
        "start": start,
        "end": end,
        "schedule_calendar_ids": str(SCHEDULE_CALENDAR_ID),
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
    Automatically sets the Schedule Calendar ID to the fixed value.
    """
    event_data["schedule_calendar_id"] = SCHEDULE_CALENDAR_ID
    url = f"{API_BASE_URL}/schedule_events"
    payload = {"data": [event_data], "team_events": "base"}
    response = requests.post(url, headers=HEADERS, json=payload)
    return response

def update_schedule_event(event_data):
    """
    Update an existing schedule event.
    Enforces the fixed Schedule Calendar ID.
    """
    event_data["schedule_calendar_id"] = SCHEDULE_CALENDAR_ID
    url = f"{API_BASE_URL}/schedule_events"
    payload = {"data": [event_data], "team_events": "base"}
    response = requests.put(url, headers=HEADERS, json=payload)
    return response

def delete_schedule_event(event_id):
    """
    "Delete" (deactivate) a schedule event by marking its 'active' flag as False.
    Uses the fixed Schedule Calendar ID.
    """
    data = {
        "id": event_id,
        "schedule_calendar_id": SCHEDULE_CALENDAR_ID,
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
    st.write("Welcome to the TSheets Schedule Manager app. This application manages schedule events using a fixed calendar ID.")
    st.markdown(f"**Schedule Calendar ID:** `{SCHEDULE_CALENDAR_ID}`")
    st.markdown("""
    **Features:**
    - **View Schedules:** Retrieve and display schedule events within a selected date range.
    - **Create Schedule:** Add a new schedule event to the fixed calendar.
    - **Update Schedule:** Modify details of an existing schedule event.
    - **Delete Schedule:** Deactivate (delete) an event.
    """)
    st.info("All operations are performed on the fixed Schedule Calendar ID.")

# -----------------------------
# View Schedules Page
# -----------------------------
elif page == "View Schedules":
    st.title("View Schedule Events")
    st.write(f"Viewing schedule events for Schedule Calendar ID: `{SCHEDULE_CALENDAR_ID}`")
    
    # Get start and end dates from the user.
    start_date = st.date_input("Start Date", datetime.today() - timedelta(days=7))
    end_date = st.date_input("End Date", datetime.today() + timedelta(days=30))
    
    if st.button("Fetch Schedules"):
        # Create timezone-aware datetime objects in UTC and remove microseconds.
        start_dt = datetime.combine(start_date, datetime.min.time()).replace(tzinfo=timezone.utc)
        end_dt = datetime.combine(end_date, datetime.max.time()).replace(tzinfo=timezone.utc)
        # Remove microseconds to ensure a valid ISO-8601 format.
        start_iso = start_dt.replace(microsecond=0).isoformat()  # e.g., "2025-02-21T00:00:00+00:00"
        end_iso = end_dt.replace(microsecond=0).isoformat()      # e.g., "2025-03-30T23:59:59+00:00"
        
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

# -----------------------------
# Create Schedule Page
# -----------------------------
elif page == "Create Schedule":
    st.title("Create Schedule Event")
    st.write(f"Creating a new schedule event for Schedule Calendar ID: `{SCHEDULE_CALENDAR_ID}`")
    st.info(f"Using fixed Schedule Calendar ID: `{SCHEDULE_CALENDAR_ID}`")
    
    start = st.text_input("Start Time (ISO 8601)", value=datetime.now(timezone.utc).replace(microsecond=0).isoformat())
    end = st.text_input("End Time (ISO 8601)", value=(datetime.now(timezone.utc) + timedelta(hours=2)).replace(microsecond=0).isoformat())
    title = st.text_input("Title")
    notes = st.text_area("Notes")
    assigned_user_ids = st.text_input("Assigned User IDs (comma-separated)")
    draft = st.checkbox("Draft", value=True)
    active = st.checkbox("Active", value=True)
    all_day = st.checkbox("All Day", value=False)
    jobcode_id = st.text_input("Job Code ID")
    color = st.text_input("Color (Hex Code)")
    
    if st.button("Create Event"):
        event_data = {
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
    st.write(f"Updating a schedule event for Schedule Calendar ID: `{SCHEDULE_CALENDAR_ID}`")
    
    event_id = st.text_input("Event ID to update")
    st.info(f"Using fixed Schedule Calendar ID: `{SCHEDULE_CALENDAR_ID}`")
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
            update_data["assigned_user_ids"] = [int(uid.strip()) for uid in new_assigned_user_ids.split(",") if uid.strip()]
        update_data["draft"] = new_draft
        update_data["active"] = new_active
        update_data["all_day"] = new_all_day
        if new_jobcode_id:
            update_data["jobcode_id"] = int(new_jobcode_id)
        if new_color:
            update_data["color"] = new_color
        
        update_data = {k: v for k, v in update_data.items() if v is not None}
        response = update_schedule_event(update_data)
        if response.status_code in [200, 201]:
            st.success("Schedule event updated successfully!")
            st.json(response.json())
        else:
            st.error(f"Failed to update event: {response.status_code} - {response.text}")

# -----------------------------
# Delete (Deactivate) Schedule Page
# -----------------------------
elif page == "Delete Schedule":
    st.title("Delete (Deactivate) Schedule Event")
    st.write(f"Deleting a schedule event for Schedule Calendar ID: `{SCHEDULE_CALENDAR_ID}`")
    
    event_id = st.text_input("Event ID to deactivate")
    
    if st.button("Deactivate Event"):
        if not event_id:
            st.error("Please provide the Event ID to deactivate.")
        else:
            response = delete_schedule_event(int(event_id))
            if response.status_code in [200, 201]:
                st.success("Schedule event deactivated successfully!")
                st.json(response.json())
            else:
                st.error(f"Failed to deactivate event: {response.status_code} - {response.text}")
