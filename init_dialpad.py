"""
Initialize Dialpad API with key
"""
import os
import logging
from dialpad_api import DialpadAPI

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def init_dialpad_api(api_key):
    """Initialize Dialpad API with key and test connection"""
    # Set environment variable for Dialpad API key
    os.environ["DIALPAD_API_TOKEN"] = api_key
    
    # Create Dialpad API instance
    dialpad_api = DialpadAPI(api_key=api_key)
    
    # Test connection by fetching users
    users = dialpad_api.fetch_users()
    
    if users:
        logger.info(f"Dialpad API connection successful. Retrieved {len(users)} users.")
        logger.info(f"User cache now contains {len(dialpad_api.user_cache)} users.")
        return True
    else:
        logger.error("Failed to connect to Dialpad API. Check API key.")
        return False

if __name__ == "__main__":
    # If API key is passed as argument, use it
    import sys
    
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
        logger.info(f"Initializing Dialpad API with key from command line argument")
        success = init_dialpad_api(api_key)
    else:
        # Otherwise, try to get from environment variable or .env file
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.environ.get("DIALPAD_API_TOKEN", "")
        
        if api_key:
            logger.info(f"Initializing Dialpad API with key from environment variable")
            success = init_dialpad_api(api_key)
        else:
            logger.error("No API key provided. Please add DIALPAD_API_TOKEN to .env file or pass as argument.")
            success = False
    
    if success:
        logger.info("Dialpad API initialized successfully.")
    else:
        logger.error("Failed to initialize Dialpad API.")