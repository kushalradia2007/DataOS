"""Hashing utilities."""

def hash_data(data: str) -> str:
    """Hash string data.
    
    Args:
        data: String to hash
        
    Returns:
        Hashed string
    """
    import hashlib
    return hashlib.sha256(data.encode()).hexdigest()
