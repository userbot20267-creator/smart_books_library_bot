"""Validators Module"""

import re
from config.settings import settings


def validate_email(email: str) -> bool:
    """
    Validate email format
    
    Args:
        email: Email address
        
    Returns:
        True if valid
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_file_type(filename: str) -> bool:
    """
    Validate file type
    
    Args:
        filename: File name
        
    Returns:
        True if file type is allowed
    """
    allowed_extensions = settings.allowed_extensions
    file_extension = filename.rsplit(".", 1)[-1].lower()
    return file_extension in allowed_extensions


def validate_file_size(file_size: int) -> bool:
    """
    Validate file size
    
    Args:
        file_size: File size in bytes
        
    Returns:
        True if file size is within limit
    """
    return file_size <= settings.max_file_size


def validate_telegram_id(telegram_id: str) -> bool:
    """
    Validate telegram ID format
    
    Args:
        telegram_id: Telegram user ID
        
    Returns:
        True if valid
    """
    return telegram_id.isdigit() and len(telegram_id) > 0


def validate_rating(rating: int) -> bool:
    """
    Validate rating value
    
    Args:
        rating: Rating value
        
    Returns:
        True if valid (1-5)
    """
    return 1 <= rating <= 5


def validate_coupon_code(code: str) -> bool:
    """
    Validate coupon code format
    
    Args:
        code: Coupon code
        
    Returns:
        True if valid
    """
    pattern = r"^[A-Z0-9]{3,50}$"
    return re.match(pattern, code) is not None
