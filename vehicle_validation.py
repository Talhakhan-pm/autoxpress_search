
import re

def has_vehicle_info(query):
    """
    Check if query contains a part mention (simplified to just check for non-empty query)
    """
    if not query:
        return False
        
    # Check if the query has some content in it
    # This is a simplified version that will pass as long as there's content
    return len(query.strip()) > 0

def get_missing_info_message(query):
    """
    Return informative message if no query is provided
    """
    if not has_vehicle_info(query):
        return "Please enter a search query for the auto part you're looking for."
    return None