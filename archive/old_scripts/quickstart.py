import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]


def main():
  """Shows basic usage of the Google Calendar API.
  Prints the start and name of the next 10 events on the user's calendar.
  """
  creds = None
  
  # Check if we have service account credentials
  if os.path.exists("credentials.json"):
    try:
      # Try to load as service account first
      creds = service_account.Credentials.from_service_account_file(
          "credentials.json", scopes=SCOPES
      )
      print("✅ Using service account credentials")
    except Exception as e:
      print(f"⚠️  Service account failed: {e}")
      creds = None
  
  # Fallback to OAuth2 flow if service account doesn't work
  if not creds:
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
      creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
      if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
      else:
        # Check if we have OAuth2 credentials file
        if os.path.exists("oauth_credentials.json"):
          flow = InstalledAppFlow.from_client_secrets_file(
              "oauth_credentials.json", SCOPES
          )
          creds = flow.run_local_server(port=0)
        else:
          print("❌ No valid credentials found. Please set up OAuth2 credentials.")
          return
      # Save the credentials for the next run
      with open("token.json", "w") as token:
        token.write(creds.to_json())

  try:
    service = build("calendar", "v3", credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
    print("Getting the upcoming 10 events")
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    if not events:
      print("No upcoming events found.")
      return

    # Prints the start and name of the next 10 events
    for event in events:
      start = event["start"].get("dateTime", event["start"].get("date"))
      print(start, event["summary"])

  except HttpError as error:
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()