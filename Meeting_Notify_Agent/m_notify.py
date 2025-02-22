from uagents import Agent, Context, Model
import asyncio
import os
from datetime import datetime, timedelta, timezone
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle

class Event(Model):
    summary: str
    start: datetime
    end: datetime

my_mnotify_agent = Agent(
    name='My m_notify Agent', 
    port=4040,
    endpoint=['http://localhost:4040/submit'], 
    seed='chorot 3 seed phrase'
)

# Define the OAuth 2.0 scopes.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_calendar_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)        
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('calendar', 'v3', credentials=creds)

async def fetch_calendar_events():
    service = get_calendar_service()
    now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    end_of_day = (datetime.utcnow().replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)).isoformat()
    
    events_result = service.events().list(
        calendarId='primary', timeMin=now, timeMax=end_of_day, singleEvents=True,
        orderBy='startTime').execute()
    events = events_result.get('items', [])
    
    event_list = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        # Convert to datetime objects if you need to do further manipulation
        start_time = datetime.fromisoformat(start.replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(end.replace('Z', '+00:00'))
        event_list.append(Event(summary=event['summary'], start=start_time, end=end_time))
    
    return event_list

def display_notification(message: str):
    os.system(f"""
              osascript -e 'display notification "{message}" with title "Daily Meetings"'
              """)
    print(f'Notification sent: {message}')

@my_mnotify_agent.on_event('startup')
async def startup_handler(ctx: Context):
    ctx.logger.info(f'My name is {ctx.agent.name} and my address is {ctx.agent.address}')
    events = await fetch_calendar_events()
    
    if events:
        for event in events:
            print(f"You have a meeting: {event.summary} from {event.start.strftime('%H:%M')} to {event.end.strftime('%H:%M')}")
            # Displaying a notification for each event
            display_notification(f"You have a meeting: {event.summary} from {event.start.strftime('%H:%M')} to {event.end.strftime('%H:%M')}")
    else:
        print("No meetings found for today.")

if __name__ == "__main__":
    my_mnotify_agent.run()