import random
import string


def generate_uid(prefix: str, length: int = 6) -> str:
    """Generate a unique identifier with the given prefix."""
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    return f"{prefix}_{suffix}"

