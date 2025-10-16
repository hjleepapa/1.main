"""
Initialize Call Center Database Tables
Run this script to create the necessary database tables for the call center module.
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from extensions import db
from call_center.models import Agent, Call, AgentActivity

def init_database():
    """Initialize the call center database tables"""
    with app.app_context():
        print("Creating call center database tables...")
        
        # Create tables
        db.create_all()
        
        print("✓ Tables created successfully!")
        print("\nCreated tables:")
        print("  - cc_agents")
        print("  - cc_calls")
        print("  - cc_agent_activities")
        
        # Optionally create a test agent
        create_test = input("\nDo you want to create a test agent? (y/n): ").strip().lower()
        
        if create_test == 'y':
            test_agent = Agent(
                agent_id='agent001',
                name='Test Agent',
                email='test@example.com',
                sip_extension='1001',
                sip_username='agent001',
                sip_password='test123',
                sip_domain='sip.example.com',
                state='logged_out'
            )
            
            db.session.add(test_agent)
            db.session.commit()
            
            print("\n✓ Test agent created!")
            print(f"  Agent ID: {test_agent.agent_id}")
            print(f"  Username: {test_agent.sip_username}")
            print(f"  Extension: {test_agent.sip_extension}")
            print(f"  Password: test123")
            print("\nYou can use these credentials to login to the call center.")

if __name__ == '__main__':
    init_database()

