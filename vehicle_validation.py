
def has_vehicle_info(query):
    """
    Modification: Always returns True to avoid rejecting any vehicle queries
    """
    return True

def get_missing_info_message(query):
    """
    Modification: Always returns None since we're not enforcing validation
    """
    return None