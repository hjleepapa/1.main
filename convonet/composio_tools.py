"""
Composio Integration for Convonet Project
Provides external tool integrations via Composio MCP
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from composio import ComposioToolSet, Action

logger = logging.getLogger(__name__)

class ComposioManager:
    """Manages Composio integrations for external tools"""
    
    def __init__(self):
        """Initialize Composio client"""
        # Import environment config (optional)
        try:
            from .environment_config import config
            self.api_key = config.COMPOSIO_API_KEY
            self.project_id = config.COMPOSIO_PROJECT_ID
        except ImportError:
            # Fallback to environment variables
            self.api_key = os.getenv('COMPOSIO_API_KEY', 'ak_68Xsj6WGv3Zl4ooBgkcD')
            self.project_id = os.getenv('COMPOSIO_PROJECT_ID', 'pr_bz7nkY2wflSi')
        
        try:
            self.toolset = ComposioToolSet(api_key=self.api_key)
            logger.info("✅ Composio client initialized")
        except Exception as e:
            logger.error(f"❌ Composio initialization failed: {e}")
            self.toolset = None
    
    def is_available(self) -> bool:
        """Check if Composio is available"""
        return self.toolset is not None
    
    def get_slack_tools(self) -> List[Any]:
        """Get Slack integration tools"""
        try:
            if not self.is_available():
                return []
            
            # Debug: Check what methods are available
            available_methods = [method for method in dir(self.toolset) if not method.startswith('_')]
            logger.info(f"🔍 Available ComposioToolSet methods: {available_methods[:10]}...")
            
            # Try to get Slack actions using the correct API
            try:
                # Use get_apps to find Slack app
                apps = self.toolset.get_apps()
                slack_app = None
                for app in apps:
                    if 'slack' in str(app).lower():
                        slack_app = app
                        break
                
                if slack_app:
                    # Get actions for Slack app
                    try:
                        slack_actions = self.toolset.get_action_schemas()
                        # Filter for Slack actions
                        slack_actions = [action for action in slack_actions if 'slack' in str(action).lower()]
                        logger.info(f"✅ Loaded {len(slack_actions)} Slack actions")
                        return slack_actions
                    except Exception as e:
                        logger.error(f"❌ Failed to get action schemas: {e}")
                        return []
                else:
                    logger.warning("⚠️ Slack app not found in available apps")
                    return []
                    
            except Exception as e:
                logger.error(f"❌ Failed to get Slack actions: {e}")
                return []
            
        except Exception as e:
            logger.error(f"❌ Failed to load Slack tools: {e}")
            return []
    
    def get_github_tools(self) -> List[Any]:
        """Get GitHub integration tools"""
        try:
            if not self.is_available():
                return []
            
            # Try different method names for getting tools
            if hasattr(self.toolset, 'get_tools'):
                github_tools = self.toolset.get_tools(apps=["github"])
            elif hasattr(self.toolset, 'get_actions'):
                github_tools = self.toolset.get_actions(apps=["github"])
            elif hasattr(self.toolset, 'list_tools'):
                github_tools = self.toolset.list_tools(apps=["github"])
            else:
                logger.warning("⚠️ No compatible method found for getting tools")
                return []
            
            logger.info(f"✅ Loaded {len(github_tools)} GitHub tools")
            return github_tools
        except Exception as e:
            logger.error(f"❌ Failed to load GitHub tools: {e}")
            return []
    
    def get_gmail_tools(self) -> List[Any]:
        """Get Gmail integration tools"""
        try:
            if not self.is_available():
                return []
            
            # Try different method names for getting tools
            if hasattr(self.toolset, 'get_tools'):
                gmail_tools = self.toolset.get_tools(apps=["gmail"])
            elif hasattr(self.toolset, 'get_actions'):
                gmail_tools = self.toolset.get_actions(apps=["gmail"])
            elif hasattr(self.toolset, 'list_tools'):
                gmail_tools = self.toolset.list_tools(apps=["gmail"])
            else:
                logger.warning("⚠️ No compatible method found for getting tools")
                return []
            
            logger.info(f"✅ Loaded {len(gmail_tools)} Gmail tools")
            return gmail_tools
        except Exception as e:
            logger.error(f"❌ Failed to load Gmail tools: {e}")
            return []
    
    def get_notion_tools(self) -> List[Any]:
        """Get Notion integration tools"""
        try:
            if not self.is_available():
                return []
            
            # Try different method names for getting tools
            if hasattr(self.toolset, 'get_tools'):
                notion_tools = self.toolset.get_tools(apps=["notion"])
            elif hasattr(self.toolset, 'get_actions'):
                notion_tools = self.toolset.get_actions(apps=["notion"])
            elif hasattr(self.toolset, 'list_tools'):
                notion_tools = self.toolset.list_tools(apps=["notion"])
            else:
                logger.warning("⚠️ No compatible method found for getting tools")
                return []
            
            logger.info(f"✅ Loaded {len(notion_tools)} Notion tools")
            return notion_tools
        except Exception as e:
            logger.error(f"❌ Failed to load Notion tools: {e}")
            return []
    
    def get_jira_tools(self) -> List[Any]:
        """Get Jira integration tools"""
        try:
            if not self.is_available():
                return []
            
            # Try different method names for getting tools
            if hasattr(self.toolset, 'get_tools'):
                jira_tools = self.toolset.get_tools(apps=["jira"])
            elif hasattr(self.toolset, 'get_actions'):
                jira_tools = self.toolset.get_actions(apps=["jira"])
            elif hasattr(self.toolset, 'list_tools'):
                jira_tools = self.toolset.list_tools(apps=["jira"])
            else:
                logger.warning("⚠️ No compatible method found for getting tools")
                return []
            
            logger.info(f"✅ Loaded {len(jira_tools)} Jira tools")
            return jira_tools
        except Exception as e:
            logger.error(f"❌ Failed to load Jira tools: {e}")
            return []
    
    def get_all_integration_tools(self) -> List[Any]:
        """Get all available integration tools"""
        all_tools = []
        
        # Add tools from different services
        all_tools.extend(self.get_slack_tools())
        all_tools.extend(self.get_github_tools())
        all_tools.extend(self.get_gmail_tools())
        all_tools.extend(self.get_notion_tools())
        all_tools.extend(self.get_jira_tools())
        
        logger.info(f"✅ Total integration tools loaded: {len(all_tools)}")
        return all_tools
    
    def get_available_apps(self) -> List[str]:
        """Get list of available Composio apps"""
        try:
            if not self.is_available():
                return []
            
            # Try different method names for getting apps
            if hasattr(self.toolset, 'get_available_apps'):
                apps = self.toolset.get_available_apps()
            elif hasattr(self.toolset, 'list_apps'):
                apps = self.toolset.list_apps()
            elif hasattr(self.toolset, 'get_apps'):
                apps = self.toolset.get_apps()
            else:
                logger.warning("⚠️ No compatible method found for getting apps")
                return []
            
            return apps
        except Exception as e:
            logger.error(f"❌ Failed to get available apps: {e}")
            return []
    
    def test_connection(self) -> bool:
        """Test Composio connection"""
        try:
            if not self.is_available():
                return False
            
            # Try to get available apps as a connection test
            apps = self.get_available_apps()
            logger.info(f"✅ Composio connection test successful. Available apps: {len(apps)}")
            return True
        except Exception as e:
            logger.error(f"❌ Composio connection test failed: {e}")
            return False
    
    def send_slack_message(self, channel: str, message: str) -> bool:
        """Send a message to a Slack channel"""
        try:
            if not self.is_available():
                logger.error("❌ Composio not available")
                return False
            
            # Use execute_action to send Slack message
            result = self.toolset.execute_action(
                action="SLACK_SEND_MESSAGE",
                params={
                    "channel": channel,
                    "text": message
                }
            )
            
            logger.info(f"✅ Slack message sent to {channel}: {message}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send Slack message: {e}")
            # Try alternative approach with different action name
            try:
                result = self.toolset.execute_action(
                    action="slack_send_message",
                    params={
                        "channel": channel,
                        "text": message
                    }
                )
                logger.info(f"✅ Slack message sent to {channel} (alternative method): {message}")
                return True
            except Exception as e2:
                logger.error(f"❌ Alternative Slack method also failed: {e2}")
                return False


# Global Composio manager instance
composio_manager = ComposioManager()

# Convenience functions
def get_slack_tools() -> List[Any]:
    """Get Slack tools"""
    return composio_manager.get_slack_tools()

def get_github_tools() -> List[Any]:
    """Get GitHub tools"""
    return composio_manager.get_github_tools()

def get_gmail_tools() -> List[Any]:
    """Get Gmail tools"""
    return composio_manager.get_gmail_tools()

def get_notion_tools() -> List[Any]:
    """Get Notion tools"""
    return composio_manager.get_notion_tools()

def get_jira_tools() -> List[Any]:
    """Get Jira tools"""
    return composio_manager.get_jira_tools()

def get_all_integration_tools() -> List[Any]:
    """Get all integration tools"""
    return composio_manager.get_all_integration_tools()

def test_composio_connection() -> bool:
    """Test Composio connection"""
    return composio_manager.test_connection()
