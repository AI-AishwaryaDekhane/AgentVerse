import os
import asyncio
import datetime
import subprocess
from uagents import Agent, Context
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_calendar_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)
    return service

async def check_schedule(service):
    while True:
        # Ensure proper time format
        now = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

        try:
            # Fetch upcoming events
            events_result = service.events().list(
                calendarId='primary', 
                timeMin=now,
                maxResults=10, 
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])
            print("Fetched events:", events)  # Debugging

            DND_active = False

            for event in events:
                start = event.get('start').get('dateTime')
                end = event.get('end').get('dateTime')
                if start and end:
                    start_time = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
                    end_time = datetime.datetime.fromisoformat(end.replace('Z', '+00:00'))
                    now_time = datetime.datetime.now(datetime.timezone.utc)

                    if start_time <= now_time <= end_time:
                        if not DND_active:
                            print("You have a meeting now. Turning on Do Not Disturb mode.")
                            set_do_not_disturb(True)
                            display_notification("Do Not Disturb mode activated for your meeting.")
                        DND_active = True
                        break

            if not DND_active:
                set_do_not_disturb(False)

        except Exception as e:
            print(f"Error occurred while checking schedule: {e}")

        await asyncio.sleep(60)

def set_do_not_disturb(enabled):
    command = f"defaults -currentHost write com.apple.notificationcenterui doNotDisturb -boolean {'true' if enabled else 'false'}"
    subprocess.run(command, shell=True)
    subprocess.run("killall NotificationCenter", shell=True)
    status = "activated" if enabled else "deactivated"
    print(f"Do Not Disturb {status} at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.")

def display_notification(message: str):
    os.system(f"""
              osascript -e 'display notification "{message}" with title "Meeting Reminder"'
              """)
    print(f'Notification sent: {message}')

dnd_agent = Agent(
    name='Do Not Disturb Agent',
    port=4040,
    endpoint=[],
    seed='do not disturb seed phrase'
)

@dnd_agent.on_event('startup')
async def startup_handler(ctx: Context):
    ctx.logger.info("Do Not Disturb Agent started.")
    service = get_calendar_service()
    asyncio.create_task(check_schedule(service))

if __name__ == "__main__":
    dnd_agent.run()