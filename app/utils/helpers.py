"""Helper Functions Module"""

import random
import string
from datetime import datetime, timedelta
from typing import Optional


def generate_referral_code(length: int = 8) -> str:
    """
    Generate random referral code
    
    Args:
        length: Code length
        
    Returns:
        Random referral code
    """
    characters = string.ascii_uppercase + string.digits
    return "".join(random.choice(characters) for _ in range(length))


def generate_coupon_code(prefix: str = "", length: int = 8) -> str:
    """
    Generate random coupon code
    
    Args:
        prefix: Code prefix
        length: Code length
        
    Returns:
        Random coupon code
    """
    characters = string.ascii_uppercase + string.digits
    code = "".join(random.choice(characters) for _ in range(length))
    return f"{prefix}{code}" if prefix else code


def format_file_size(size_bytes: int) -> str:
    """
    Format file size to human readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def get_time_ago(dt: datetime) -> str:
    """
    Get time difference in human readable format
    
    Args:
        dt: DateTime object
        
    Returns:
        Time difference string
    """
    now = datetime.utcnow()
    diff = now - dt

    seconds = diff.total_seconds()
    
    if seconds < 60:
        return f"{int(seconds)} seconds ago"
    elif seconds < 3600:
        return f"{int(seconds / 60)} minutes ago"
    elif seconds < 86400:
        return f"{int(seconds / 3600)} hours ago"
    elif seconds < 604800:
        return f"{int(seconds / 86400)} days ago"
    else:
        return f"{int(seconds / 604800)} weeks ago"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def paginate(total: int, page: int = 1, per_page: int = 20) -> dict:
    """
    Calculate pagination info
    
    Args:
        total: Total items
        page: Current page
        per_page: Items per page
        
    Returns:
        Pagination info dictionary
    """
    total_pages = (total + per_page - 1) // per_page
    offset = (page - 1) * per_page
    
    return {
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
        "offset": offset,
        "has_next": page < total_pages,
        "has_prev": page > 1,
    }


def merge_dicts(*dicts) -> dict:
    """
    Merge multiple dictionaries
    
    Args:
        *dicts: Dictionaries to merge
        
    Returns:
        Merged dictionary
    """
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result


def safe_get(dictionary: dict, key: str, default=None):
    """
    Safely get value from dictionary with dot notation support
    
    Args:
        dictionary: Dictionary to get from
        key: Key (supports dot notation like 'user.name')
        default: Default value
        
    Returns:
        Value or default
    """
    keys = key.split(".")
    value = dictionary
    
    for k in keys:
        if isinstance(value, dict):
            value = value.get(k)
        else:
            return default
    
    return value if value is not None else default
