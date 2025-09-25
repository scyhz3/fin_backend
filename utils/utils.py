from typing import Optional

# --- Helper Functions ---
def safe_float_conversion(value: Optional[str]) -> Optional[float]:
    """
    A safe conversion function to convert API string responses to floats.
    It correctly handles 'None' strings and potential conversion errors.
    """
    if value is None or value == 'None':
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None
