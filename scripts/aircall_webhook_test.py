import requests
import base64
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Your Aircall API credentials from environment variables
api_id = os.environ.get("AIRCALL_API_ID")
api_token = os.environ.get("AIRCALL_API_TOKEN")

# Encode credentials for Basic Auth
credentials = f"{api_id}:{api_token}"
encoded_credentials = base64.b64encode(credentials.encode()).decode()

# Set up headers with authentication
headers = {
    "Authorization": f"Basic {encoded_credentials}",
    "Content-Type": "application/json"
}

# Call ID to update (replace with an active call ID for testing)
call_id = "your_call_id_here" # IMPORTANT: Replace this with an actual call ID

# Custom variables to attach
custom_data = {
    "badge": "111", # Example badge
    "pin": "11111"   # Example PIN
}

# Update the call with custom data
response = requests.post(
    f"https://api.aircall.io/v1/calls/{call_id}/metadata",
    headers=headers,
    json=custom_data
)

print(f"Status Code: {response.status_code}")
try:
    print(f"Response JSON: {response.json()}")
except json.JSONDecodeError:
    print(f"Response Text: {response.text}")