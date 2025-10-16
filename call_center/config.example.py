"""
Call Center Configuration Example
Copy this file to config.py and update with your settings
"""

# SIP Server Configuration
SIP_CONFIG = {
    'domain': 'sip.example.com',  # Your SIP server domain
    'wss_port': 7443,  # WebSocket Secure port
    'transport': 'wss',  # Use WSS for secure WebSocket
    
    # STUN/TURN servers for NAT traversal
    'ice_servers': [
        {
            'urls': 'stun:stun.l.google.com:19302'
        },
        # Add TURN server if needed
        # {
        #     'urls': 'turn:turn.example.com:3478',
        #     'username': 'turnuser',
        #     'credential': 'turnpass'
        # }
    ]
}

# Call Center Settings
CALL_CENTER_CONFIG = {
    'max_simultaneous_calls': 5,  # Maximum calls per agent
    'auto_answer': False,  # Auto-answer incoming calls
    'ring_timeout': 30,  # Seconds before call timeout
    'wrap_up_time': 10,  # Seconds for after-call work
    'recording_enabled': True,  # Enable call recording
}

# Agent Idle States
IDLE_STATES = [
    'Break',
    'Lunch',
    'Training',
    'Meeting',
    'Technical Issue',
    'Other'
]

# Customer Data Integration
CRM_CONFIG = {
    'enabled': False,  # Enable CRM integration
    'api_url': 'https://your-crm.com/api',
    'api_key': 'your-api-key',
    'timeout': 5  # API timeout in seconds
}

# Call Disposition Codes
DISPOSITION_CODES = [
    'Resolved',
    'Follow-up Required',
    'Escalated',
    'Voicemail',
    'No Answer',
    'Wrong Number',
    'Other'
]

# Logging Configuration
LOGGING_CONFIG = {
    'log_calls': True,
    'log_agent_activity': True,
    'log_level': 'INFO',
    'log_file': 'logs/call_center.log'
}

# Security Settings
SECURITY_CONFIG = {
    'session_timeout': 3600,  # Session timeout in seconds
    'max_login_attempts': 5,
    'password_min_length': 8,
    'require_https': True  # Require HTTPS in production
}

