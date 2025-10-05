from datetime import datetime

def generate_snowflake_id(timestamp: datetime, node_id: int) -> int:
    """
    Generate a fake Snowflake ID based on a datetime timestamp and node ID.
    
    Args:
        timestamp: Datetime object representing the timestamp
        node_id: Node ID (0 to 1023, as it uses 10 bits)
    
    Returns:
        A 64-bit Snowflake ID
    """
    # Validate inputs
    if not (0 <= node_id <= 1023):
        raise ValueError("Node ID must be between 0 and 1023")
    
    # Convert datetime to milliseconds since epoch
    timestamp_ms: int = int(timestamp.timestamp() * 1000)
    if timestamp_ms < 0:
        raise ValueError("Timestamp must be non-negative")
    
    # Twitter's Snowflake epoch (January 1, 2010, in milliseconds)
    SNOWFLAKE_EPOCH: int = 1288834974657
    
    # Bit lengths for each component
    _TIMESTAMP_BITS: int = 41
    NODE_ID_BITS: int = 10
    SEQUENCE_BITS: int = 12
    
    # Masks for each component
    _MAX_NODE_ID: int = (1 << NODE_ID_BITS) - 1  # 1023
    MAX_SEQUENCE: int = (1 << SEQUENCE_BITS) - 1  # 4095
    
    # Generate a random sequence number (0 to 4095)
    import random
    sequence: int = random.randint(0, MAX_SEQUENCE)
    
    # Calculate timestamp relative to Snowflake epoch
    relative_timestamp: int = timestamp_ms - SNOWFLAKE_EPOCH
    
    if relative_timestamp < 0:
        raise ValueError("Timestamp is before Snowflake epoch")
    
    # Construct the Snowflake ID:
    # - 41 bits for timestamp (shifted left by 22 bits)
    # - 10 bits for node ID (shifted left by 12 bits)
    # - 12 bits for sequence number
    snowflake_id: int = (relative_timestamp << (NODE_ID_BITS + SEQUENCE_BITS)) | \
                        (node_id << SEQUENCE_BITS) | \
                        sequence
    
    return snowflake_id