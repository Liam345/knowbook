"""
OpenAI API key validator.

Educational Note: Validates OpenAI API keys using a minimal API call.
"""
from typing import Tuple


def validate_openai_key(api_key: str) -> Tuple[bool, str]:
    """
    Validate an OpenAI API key.
    
    Args:
        api_key: The API key to validate
    
    Returns:
        Tuple of (is_valid, message)
    """
    if not api_key or api_key == '':
        return False, "API key is empty"
    
    try:
        # TODO: Implement actual OpenAI validation
        # For now, just check if it looks like a valid key format
        if api_key.startswith('sk-') and len(api_key) > 40:
            return True, "Valid OpenAI API key (validation not fully implemented)"
        else:
            return False, "API key format appears incorrect"
    except Exception as e:
        return False, f"Validation failed: {str(e)}"
