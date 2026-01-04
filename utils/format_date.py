from datetime import datetime

def convert_to_date_std(date_string: str) -> datetime:
    """
    Attempts to parse a date string using a list of common formats.
    """
    formats = [
        "%d/%m/%Y",  # 28/12/2025
        "%Y-%m-%d",  # 2025-12-28 (ISO)
        "%d-%m-%Y",  # 28-12-2025
        "%Y/%m/%d",  # 2025/12/28
        "%d %b %Y",  # 28 Dec 2025
        "%B %d, %Y", # December 28, 2025
    ]
    
    # Clean the string (remove extra whitespace)
    date_string = date_string.strip()
    
    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
            
    raise ValueError(f"Format not recognized for date: {date_string}")