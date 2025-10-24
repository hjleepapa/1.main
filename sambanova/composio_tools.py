"""
Composio Integration for Sambanova Project
Provides external tool integrations via Composio MCP
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from composio import ComposioToolSet, Action, ComposioClient

logger = logging.getLogger(__name__)

class ComposioManager:
    """Manages Composio integrations for external tools"""
    
    def __init__(self):
        """Initialize Composio client"""
        # Import environment config
        from .environment_config import config
        
        self.api_key = config.COMPOSIO_API_KEY
        self.project_id = config.COMPOSIO_PROJECT_ID
        
        try:
            self.client = ComposioClient(api_key=self.api_key)
            self.toolset = ComposioToolSet(api_key=self.api_key)
            logger.info("✅ Composio client initialized")
        except Exception as e:
            logger.error(f"❌ Composio initialization failed: {e}")
            self.client = None
            self.toolset = None
    
    def is_available(self) -> bool:
        """Check if Composio is available"""
        return self.client is not None and self.toolset is not None
    
    def get_slack_tools(self) -> List[Any]:
        """Get Slack integration tools"""
        try:
            if not self.is_available():
                return []
            
            slack_tools = self.toolset.get_tools(apps=["slack"])
            logger.info(f"✅ Loaded {len(slack_tools)} Slack tools")
            return slack_tools
        except Exception as e:
            logger.error(f"❌ Failed to load Slack tools: {e}")
            return []
    
    def get_github_tools(self) -> List[Any]:
        """Get GitHub integration tools"""
        try:
            if not self.is_available():
                return []
            
            github_tools = self.toolset.get_tools(apps=["github"])
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
            
            gmail_tools = self.toolset.get_tools(apps=["gmail"])
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
            
            notion_tools = self.toolset.get_tools(apps=["notion"])
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
            
            jira_tools = self.toolset.get_tools(apps=["jira"])
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
            
            # Get available apps from Composio
            apps = self.toolset.get_available_apps()
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
