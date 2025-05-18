"""
API routes for Dialpad integration
"""
import json
import logging
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, render_template
from dialpad_api import DialpadAPI

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create Blueprint for Dialpad API routes
dialpad_routes = Blueprint('dialpad_routes', __name__)

# We'll initialize the API client later to avoid circular imports
dialpad_api = None

def init_api():
    """Initialize API client if not already initialized"""
    global dialpad_api
    if dialpad_api is None:
        dialpad_api = DialpadAPI()
    return dialpad_api

# New route for agent activity page
@dialpad_routes.route('/agent_activity')
def agent_activity_page():
    """Render the agent activity page"""
    return render_template('agent_activity.html')

# New route for call tables page
@dialpad_routes.route('/call_tables')
def call_tables_page():
    """Render the call tables page"""
    return render_template('call_tables.html')

@dialpad_routes.route('/api/agent-activity', methods=['GET'])
def get_agent_activity():
    """
    Get agent activity metrics
    
    Query parameters:
    - days: Number of days to look back (default: 7)
    - refresh: Whether to refresh data from Dialpad API (default: false)
    - max_pages: Maximum number of pages to fetch from API (default: 3)
    """
    # Initialize API client
    api = init_api()
    try:
        # Get query parameters
        days = int(request.args.get('days', 1))  # Default to 1 day for quicker results
        refresh = request.args.get('refresh', 'false').lower() == 'true'
        
        # Limit days to reasonable values
        if days < 1:
            days = 1
        elif days > 90:
            days = 90
            
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Format dates for logging
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        logger.info(f"Getting agent activity from {start_date_str} to {end_date_str}")
        
        # Get max_pages (default to 2 for quick results)
        max_pages = int(request.args.get('max_pages', 2))
        
        # Get max_timeout (default to 60 seconds)
        max_timeout = int(request.args.get('max_timeout', 60))
        
        # Get activity data directly from Dialpad API
        activity_data = api.get_agent_activity(days, max_pages)
            
        # Create response data
        response_data = {
            'success': True,
            'activity': activity_data
        }
        
        # Log response data for debugging
        logger.info(f"Returning agent activity response with {len(activity_data.get('agents', []))} agents")
        logger.info(f"Total calls: {activity_data.get('total_calls', 0)}")
        
        # Return response
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error getting agent activity: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dialpad_routes.route('/api/dialpad-calls', methods=['GET'])
def get_dialpad_calls():
    """
    Get call records directly from Dialpad API
    
    Query parameters:
    - days: Number of days to look back (default: 1)
    - refresh: Whether to bypass cache (default: false)
    - max_pages: Maximum number of pages to fetch (default: 3)
    """
    # Initialize API client
    api = init_api()
    try:
        # Get query parameters
        days = int(request.args.get('days', 1))
        refresh = request.args.get('refresh', 'false').lower() == 'true'
        max_pages = int(request.args.get('max_pages', 3))
        
        # Limit days to reasonable values
        if days < 1:
            days = 1
        elif days > 90:
            days = 90
            
        # Fetch call data from Dialpad API
        logger.info(f"Fetching Dialpad calls for the past {days} days (max_pages: {max_pages}, refresh: {refresh})")
        calls = api.fetch_department_calls(days, max_pages)
        
        # Calculate basic stats
        inbound_count = len([c for c in calls if c.get('direction') == 'inbound'])
        outbound_count = len([c for c in calls if c.get('direction') == 'outbound'])
        
        # Calculate missed calls
        def is_missed(call):
            try:
                duration = call.get('duration', 0)
                # Handle different duration formats
                if isinstance(duration, str) and duration.strip():
                    duration = float(duration.replace(',', ''))
                elif isinstance(duration, (int, float)):
                    duration = float(duration)
                else:
                    duration = 0
                
                # A call is definitively completed only if it has date_connected
                # This is the most reliable indicator in Dialpad API
                #
                # Note: duration > 0 without date_connected is ambiguous and will
                # be considered missed to be conservative
                return not (call.get('date_connected') is not None)
            except:
                # If any error in parsing, assume not missed
                return False
        
        # Count calls as completed or missed
        missed_calls = [c for c in calls if is_missed(c)]
        completed_calls = [c for c in calls if not is_missed(c)]
        
        missed_count = len(missed_calls)
        completed_count = len(completed_calls)
        
        stats = {
            'total_count': len(calls),
            'inbound_count': inbound_count,
            'outbound_count': outbound_count,
            'missed_count': missed_count,
            'completed_count': completed_count
        }
        
        # Return response
        return jsonify({
            'success': True,
            'calls': calls,
            'stats': stats,
            'days': days
        })
        
    except Exception as e:
        logger.error(f"Error fetching Dialpad calls: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500