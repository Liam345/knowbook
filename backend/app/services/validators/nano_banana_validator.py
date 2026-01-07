"""
Nano Banana API key validator.

Educational Note: Validates Nano Banana (Image Gen) API keys.
"""
from typing import Tuple


def validate_nano_banana_key(api_key: str) -> Tuple[bool, str]:
    """
    Validate a Nano Banana API key.
    
    Args:
        api_key: The API key to validate
    
    Returns:
        Tuple of (is_valid, message)
    """
    if not api_key or api_key == '':
        return False, "API key is empty"
    
    try:
        # TODO: Implement actual Nano Banana validation
        # For now, just check if it looks like a valid key format
        if len(api_key) > 10:
            return True, "Valid Nano Banana API key (validation not fully implemented)"
        else:
            return False, "API key appears too short"
    except Exception as e:
        return False, f"Validation failed: {str(e)}"
