import os
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pickle

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

class GoogleCalendarService:
    def __init__(self, credentials_file: str = 'shared/credentials.json', token_file: str = 'shared/token.pickle'):
        """
        Initialize Google Calendar service.
        
        Args:
            credentials_file: Path to Google API credentials JSON file
            token_file: Path to store/load OAuth token
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Calendar API."""
        creds = None
        
        # The file token.pickle stores the user's access and refresh tokens.
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"Credentials file '{self.credentials_file}' not found. "
                        "Please download it from Google Cloud Console."
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('calendar', 'v3', credentials=creds)
    
    def create_event(self, title: str, description: str = None, 
                    start_time: datetime = None, end_time: datetime = None,
                    timezone: str = 'UTC') -> Optional[str]:
        """
        Create a Google Calendar event.
        
        Args:
            title: Event title
            description: Event description
            start_time: Start datetime
            end_time: End datetime
            timezone: Timezone string
            
        Returns:
            Google Calendar event ID if successful, None otherwise
        """
        try:
            if not start_time:
                start_time = datetime.utcnow()
            if not end_time:
                end_time = start_time + timedelta(hours=1)
            
            event = {
                'summary': title,
                'description': description or '',
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': timezone,
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': timezone,
                },
            }
            
            event = self.service.events().insert(
                calendarId='primary', body=event
            ).execute()
            
            return event.get('id')
        
        except HttpError as error:
            print(f'An error occurred: {error}')
            return None
    
    def update_event(self, event_id: str, title: str = None, 
                    description: str = None, start_time: datetime = None,
                    end_time: datetime = None, timezone: str = 'UTC') -> bool:
        """
        Update a Google Calendar event.
        
        Args:
            event_id: Google Calendar event ID
            title: New event title
            description: New event description
            start_time: New start datetime
            end_time: New end datetime
            timezone: Timezone string
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get existing event
            event = self.service.events().get(
                calendarId='primary', eventId=event_id
            ).execute()
            
            # Update fields
            if title:
                event['summary'] = title
            if description is not None:
                event['description'] = description
            if start_time:
                event['start']['dateTime'] = start_time.isoformat()
            if end_time:
                event['end']['dateTime'] = end_time.isoformat()
            
            self.service.events().update(
                calendarId='primary', eventId=event_id, body=event
            ).execute()
            
            return True
        
        except HttpError as error:
            print(f'An error occurred: {error}')
            return False
    
    def delete_event(self, event_id: str) -> bool:
        """
        Delete a Google Calendar event.
        
        Args:
            event_id: Google Calendar event ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.service.events().delete(
                calendarId='primary', eventId=event_id
            ).execute()
            return True
        
        except HttpError as error:
            print(f'An error occurred: {error}')
            return False
    
    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a Google Calendar event.
        
        Args:
            event_id: Google Calendar event ID
            
        Returns:
            Event data if found, None otherwise
        """
        try:
            event = self.service.events().get(
                calendarId='primary', eventId=event_id
            ).execute()
            return event
        
        except HttpError as error:
            print(f'An error occurred: {error}')
            return None

# Global instance for easy access
_calendar_service = None

def get_calendar_service() -> GoogleCalendarService:
    """Get or create the global Google Calendar service instance."""
    global _calendar_service
    if _calendar_service is None:
        _calendar_service = GoogleCalendarService()
    return _calendar_service 

if __name__ == "__main__":
    GoogleCalendarService() 