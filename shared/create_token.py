#!/usr/bin/env python3
import pickle
import json
from google.oauth2.credentials import Credentials

# OAuth2 data from oauth2l command
oauth_data = {
    "client_id": "624484441322-ali6jup0garnp9lkj4clklf5unkcf97o.apps.googleusercontent.com",
    "client_secret": "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",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "refresh_token": "1//06OSWFybvB4I-CgYIARAAGAYSNwF-L9IrM2nhAs9_AQyh6CQpqMuwvWNji_tftLOc4dcv0E0uT9QcoZcurT7h0oq8cn6r5CYrsdY",
    "type": "authorized_user"
}

# Create credentials object
creds = Credentials(
    token=None,  # Will be refreshed
    refresh_token=oauth_data["refresh_token"],
    token_uri=oauth_data["token_uri"],
    client_id=oauth_data["client_id"],
    client_secret=oauth_data["client_secret"]
)

# Save to token.pickle
with open('token.pickle', 'wb') as token_file:
    pickle.dump(creds, token_file)

print("token.pickle created successfully!")
print("You can now use the GoogleCalendarService class.")
