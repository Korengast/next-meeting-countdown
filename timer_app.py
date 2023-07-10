import os.path
import datetime
import pickle
import tkinter as tk

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build



class TimerApp:
    def __init__(self, root):
        self.root = root
        root.geometry("300x70")
        root.attributes('-topmost', 1)

        self.timer_label = tk.Label(root, font=("Helvetica", 32))
        self.timer_label.pack()

        self.creds = None
        self.service = None
        self.next_event = None
        self.last_updated = None
        self.next_event = None

        # Initialize Google Calendar API
        self.init_calendar_api()

        # Get the next event on start
        self.get_next_event()

        # Update the timer every second
        self.update_timer()

    def init_calendar_api(self):
        # If modifying these scopes, delete the file token.pickle.
        SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # credentials_path = resource_path('credentials.json')
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)

            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.creds = creds
        self.service = build('calendar', 'v3', credentials=creds)

    def get_next_event(self):
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time

        events_result = self.service.events().list(calendarId='primary', timeMin=now,
                                                   maxResults=10, singleEvents=True,
                                                   orderBy='startTime').execute()
        events = events_result.get('items', [])
        events = [e for e in events if 'dateTime' in e['start']]
        events = [e for e in events if e['start']['dateTime'] > datetime.datetime.now().isoformat()]

        if events:
            self.next_event = events[0]
        else:
            self.next_event = None

    def update_timer(self):

        if (self.last_updated is None) or (not self.next_event) or \
                (datetime.datetime.now(datetime.timezone.utc) - self.last_updated > datetime.timedelta(seconds=1)):
            self.get_next_event()
            self.last_updated = datetime.datetime.now(datetime.timezone.utc)

        if self.next_event:
            next_event_dt = datetime.datetime.fromisoformat(self.next_event['start'].get('dateTime'))
            remaining = next_event_dt - datetime.datetime.now(next_event_dt.tzinfo)
            self.root.title(self.next_event['summary'])
            self.timer_label.config(text=str(remaining)[:-7])
        else:
            self.timer_label.config(text="No upcoming events")

        # update the timer every second
        self.root.after(1000, self.update_timer)


if __name__ == "__main__":
    root = tk.Tk()
    app = TimerApp(root)
    root.mainloop()
