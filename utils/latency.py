import time

# Global list to store latency records (in seconds)
latency_records = []

# Function to record latency based on WebSocket message processing time
def record_latency(start_time):
    """
    Calculate latency as the time difference between when the WebSocket message
    was received and the time when it was processed.
    """
    end_time = time.time()  # Current time when processing is complete
    latency = end_time - start_time  # Latency is the difference in time
    latency_records.append(latency)  # Append the latency to the list

    return latency  # Return the calculated latency

# Optional: Function to get the latest latency from the recorded latencies
def get_latest_latency():
    """
    Return the most recent latency recorded. If no latency is recorded,
    it returns None.
    """
    if latency_records:
        return latency_records[-1]  # Return the most recent latency
    return None  # Return None if no latency records exist
