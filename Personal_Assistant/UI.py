import streamlit as st
import requests
import datetime
from google_auth_oauthlib.flow import InstalledAppFlow
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="AI Smart Scheduler", page_icon="📅", layout="centered")

st.title("📅 AI-Powered Smart Scheduler")
st.subheader("Automate your Google Calendar with AI & Fetch.ai")

# --- USER AUTHENTICATION ---
st.write("### 🔑 Login with Google to schedule events")

# Check if credentials already exist in session state
if "credentials" in st.session_state:
    st.success("You are already logged in!")
else:
    # Allow the user to input Google OAuth credentials dynamically
    client_id = st.text_input("Enter your Google Client ID:", placeholder="Your Google Client ID")
    client_secret = st.text_input("Enter your Google Client Secret:", placeholder="Your Google Client Secret")
    redirect_uri = "http://localhost:8502"  # You can change this if needed

    # If the user enters client details and presses login, proceed with authentication
    if st.button("Login with Google"):
        if client_id and client_secret:
            st.write("Redirecting to Google login...")
            
            # OAuth2 Flow using google-auth-oauthlib
            flow = InstalledAppFlow.from_client_config(
                {
                    "installed": {
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "redirect_uris": [redirect_uri],
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "scope": "https://www.googleapis.com/auth/calendar.events",
                    }
                },
                scopes=["https://www.googleapis.com/auth/calendar.events"],
            )
            
            credentials = flow.run_local_server(port=0)  # Runs a local server for OAuth callback
            
            # Store credentials in a session (for re-use)
            st.session_state.credentials = credentials
            st.success("Logged in successfully!")
        else:
            st.error("Please fill in all fields with your Google Client details!")

st.divider()

# --- EVENT INPUT FORM ---
st.write("### 📌 Schedule a New Event")

event_title = st.text_input("Event Title", placeholder="Meeting with AI team")
event_date = st.date_input("Date", min_value=datetime.date.today())
event_time = st.time_input("Time")
event_description = st.text_area("Description", placeholder="Discuss AI integration with Fetch.ai")

if st.button("Schedule Event"):
    # Combine event_date and event_time to create event_datetime
    event_datetime = datetime.datetime.combine(event_date, event_time)

    # Prepare event payload
    event_payload = {
        "title": event_title,
        "datetime": event_datetime.isoformat(),  # Convert datetime to ISO format
        "description": event_description
    }

    # --- CALL FETCH.AI API ---
    fetch_ai_api_url = "https://api.fetch.ai/schedule_event"
    try:
        response = requests.post(fetch_ai_api_url, json=event_payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        st.success("✅ Event successfully scheduled with AI automation!")
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Failed to schedule event: {e}")

st.divider()
st.write("Powered by **Fetch.ai**, **Google Calendar API**, and **Streamlit** 🚀")
