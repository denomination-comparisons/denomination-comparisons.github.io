from datetime import datetime

def format_datetime(value, format='%Y-%m-%d %H:%M'):
    if value is None: return ""
    # Handle ISO format strings with 'Z' for UTC
    if value.endswith('Z'):
        value = value[:-1] + '+00:00'
    try:
        dt = datetime.fromisoformat(value)
        return dt.strftime(format)
    except ValueError:
        return value # Return original value if parsing fails
