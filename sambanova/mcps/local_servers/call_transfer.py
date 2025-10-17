"""
Call Transfer Tool for LangGraph Voice AI
Enables transferring calls from the AI assistant to FreePBX call center agents/queues
"""

import os
from typing import Optional
from langchain_core.tools import tool
import logging

logger = logging.getLogger(__name__)

# FreePBX configuration
FREEPBX_DOMAIN = os.getenv('FREEPBX_DOMAIN', '34.26.59.14')

# Default extension mapping
EXTENSION_MAP = {
    'support': '2000',  # Support queue
    'sales': '2000',    # Sales queue
    'general': '2000',  # General queue
    'operator': '2000', # Main operator
}

@tool
def transfer_to_agent(
    department: str = "support",
    extension: Optional[str] = None,
    reason: Optional[str] = None
) -> str:
    """
    Transfer the current call to a FreePBX call center agent or queue.
    
    Use this tool when:
    - User explicitly asks to speak with a human agent
    - User requests transfer to a specific department
    - The AI cannot handle the request and human intervention is needed
    - User is frustrated and needs personalized assistance
    
    Args:
        department: Department to transfer to (support, sales, general, operator). Default: support
        extension: Specific FreePBX extension number (overrides department). Optional.
        reason: Reason for transfer (for logging). Optional.
    
    Returns:
        A message confirming the transfer initiation
        
    Examples:
        transfer_to_agent(department="support", reason="Customer needs technical help")
        transfer_to_agent(extension="201", reason="User requested human agent")
        transfer_to_agent(department="sales", reason="Purchase inquiry")
    """
    try:
        # Determine the target extension
        if extension:
            target_extension = extension
        else:
            target_extension = EXTENSION_MAP.get(department.lower(), EXTENSION_MAP['support'])
        
        # Log the transfer request
        log_message = f"TRANSFER_REQUEST: Extension={target_extension}, Department={department}"
        if reason:
            log_message += f", Reason={reason}"
        logger.info(log_message)
        
        # Return a special marker that the webhook handler will detect
        # The webhook handler will then redirect to the /transfer endpoint
        return f"TRANSFER_INITIATED:{target_extension}|{department}|{reason or 'User requested transfer'}"
        
    except Exception as e:
        logger.error(f"Error in transfer_to_agent tool: {e}")
        return f"Transfer request failed: {str(e)}"


@tool
def get_available_departments() -> str:
    """
    Get a list of available departments for call transfer.
    
    Returns:
        A formatted list of available departments and their descriptions
    """
    departments = """
    Available departments for transfer:
    - support: Technical support queue (Extension 2000)
    - sales: Sales team (Extension 2000)
    - general: General inquiries (Extension 2000)
    - operator: Main operator (Extension 2000)
    """
    return departments.strip()


def get_transfer_tools():
    """
    Returns a list of all call transfer tools.
    Use this to register transfer tools with the LangGraph agent.
    """
    return [transfer_to_agent, get_available_departments]


# For standalone testing
if __name__ == "__main__":
    # Test the tool
    result = transfer_to_agent(department="support", reason="Test transfer")
    print(f"Transfer result: {result}")
    
    departments = get_available_departments()
    print(f"\n{departments}")

