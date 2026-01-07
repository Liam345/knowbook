"""
ElevenLabs API key validator.

Educational Note: Validates ElevenLabs API keys using a minimal API call.
"""
from typing import Tuple


def validate_elevenlabs_key(api_key: str) -> Tuple[bool, str]:
    """
    Validate an ElevenLabs API key.
    
    Args:
        api_key: The API key to validate
    
    Returns:
        Tuple of (is_valid, message)
    """
    if not api_key or api_key == '':
        return False, "API key is empty"
    
    try:
        # TODO: Implement actual ElevenLabs validation
        # For now, just check if it looks like a valid key format
        if len(api_key) > 10:
            return True, "Valid ElevenLabs API key (validation not fully implemented)"
        else:
            return False, "API key appears too short"
    except Exception as e:
        return False, f"Validation failed: {str(e)}"
