"""
Helper functions and utilities
"""
import logging
from typing import Dict, Any


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Setup logging configuration.
    
    Args:
        log_level: Logging level
    
    Returns:
        Logger instance
    """
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)


def format_bytes(bytes_value: float, unit: str = "MB") -> str:
    """
    Format bytes to readable format.
    
    Args:
        bytes_value: Bytes value
        unit: Target unit (KB, MB, GB)
    
    Returns:
        Formatted string
    """
    units = {"KB": 1024, "MB": 1024**2, "GB": 1024**3}
    
    if unit in units:
        converted = bytes_value / units[unit]
        return f"{converted:.2f} {unit}"
    
    return str(bytes_value)


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Format percentage value.
    
    Args:
        value: Value as percentage
        decimals: Number of decimal places
    
    Returns:
        Formatted percentage string
    """
    return f"{value:.{decimals}f}%"


def create_response(success: bool, data: Any = None, error: str = None) -> Dict:
    """
    Create standardized API response.
    
    Args:
        success: Whether operation was successful
        data: Response data
        error: Error message if unsuccessful
    
    Returns:
        Response dictionary
    """
    response = {"success": success}
    
    if data is not None:
        response["data"] = data
    
    if error is not None:
        response["error"] = error
    
    return response


def validate_captcha_id(captcha_id: str) -> bool:
    """
    Validate CAPTCHA ID format.
    
    Args:
        captcha_id: CAPTCHA ID to validate
    
    Returns:
        True if valid, False otherwise
    """
    if not captcha_id or not isinstance(captcha_id, str):
        return False
    
    # CAPTCHA ID should be a hex string of 32 characters
    return len(captcha_id) == 32 and all(c in '0123456789abcdef' for c in captcha_id)


def validate_answer(answer: int) -> bool:
    """
    Validate CAPTCHA answer.
    
    Args:
        answer: User's answer
    
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(answer, int):
        return False
    
    # Answer should be between 1 and 100
    return 1 <= answer <= 100
