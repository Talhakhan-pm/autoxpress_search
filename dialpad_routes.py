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
    - start_date: Start date in YYYY-MM-DD format
    - end_date: End date in YYYY-MM-DD format
    - days: Number of days to look back (default: 1) - used if start_date/end_date not provided
    - refresh: Whether to refresh data from Dialpad API (default: false)
    - max_pages: Maximum number of pages to fetch from API (default: 3)
    """
    # Initialize API client
    api = init_api()
    try:
        # Get query parameters for date range
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        refresh = request.args.get('refresh', 'false').lower() == 'true'
        
        # Get days parameter upfront so it's available in all code paths
        days = int(request.args.get('days', 1))  # Default to 1 day for quicker results
        
        # Current date and time (to avoid future dates)
        current_date = datetime.now()
        
        # If date range is provided, use that instead of days parameter
        if start_date_str and end_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                end_date_parsed = datetime.strptime(end_date_str, '%Y-%m-%d')
                
                # Ensure end_date is not in the future
                if end_date_parsed.date() > current_date.date():
                    end_date_parsed = current_date
                    logger.warning("End date was in the future, using current date instead")
                
                # Set end_date to end of day (23:59:59) but don't exceed current time
                end_date = min(
                    datetime.combine(end_date_parsed.date(), datetime.max.time()),
                    current_date
                )
                
                # Ensure start_date is not in the future
                if start_date.date() > current_date.date():
                    # Default to yesterday if start date is in the future
                    start_date = current_date - timedelta(days=1)
                    logger.warning("Start date was in the future, using yesterday instead")
                
                # Ensure start_date is before end_date
                if start_date > end_date:
                    start_date = end_date - timedelta(days=1)
                    logger.warning("Start date was after end date, using day before end date instead")
                
            except ValueError as e:
                logger.error(f"Invalid date format: {e}")
                return jsonify({
                    'success': False,
                    'error': f"Invalid date format: {e}"
                }), 400
        else:
            # Fall back to days parameter if no date range provided
            # Limit days to reasonable values
            if days < 1:
                days = 1
            elif days > 90:
                days = 90
                
            # Calculate date range based on days
            end_date = current_date
            start_date = end_date - timedelta(days=days)
        
        # Format dates for logging
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        logger.info(f"Getting agent activity from {start_date_str} to {end_date_str}")
        
        # Get max_pages (default to 2 for quick results)
        max_pages = int(request.args.get('max_pages', 2))
        
        # Get max_timeout (default to 600 seconds, 10 minutes)
        max_timeout = int(request.args.get('max_timeout', 600))
        
        # Calculate days between dates for the API call
        days_between = (end_date - start_date).days + 1
        
        # Get activity data directly from Dialpad API using date range
        activity_data = api.get_agent_activity_by_date_range(start_date, end_date, max_pages)
            
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
    - start_date: Start date in YYYY-MM-DD format
    - end_date: End date in YYYY-MM-DD format
    - days: Number of days to look back (default: 1) - used if start_date/end_date not provided
    - refresh: Whether to bypass cache (default: false)
    - max_pages: Maximum number of pages to fetch (default: 3)
    """
    # Initialize API client
    api = init_api()
    try:
        # Get query parameters for date range
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        refresh = request.args.get('refresh', 'false').lower() == 'true'
        max_pages = int(request.args.get('max_pages', 3))
        
        # Calculate date range based on provided parameters
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1)  # Default to 1 day ago
        
        # Get days parameter upfront so it's available in all code paths
        days = int(request.args.get('days', 1))
        
        # Current date and time (to avoid future dates)
        current_date = datetime.now()
        
        # If date range is provided, use that instead of days parameter
        if start_date_str and end_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                end_date_parsed = datetime.strptime(end_date_str, '%Y-%m-%d')
                
                # Ensure end_date is not in the future
                if end_date_parsed.date() > current_date.date():
                    end_date_parsed = current_date
                    logger.warning("End date was in the future, using current date instead")
                
                # Set end_date to end of day (23:59:59) but don't exceed current time
                end_date = min(
                    datetime.combine(end_date_parsed.date(), datetime.max.time()),
                    current_date
                )
                
                # Ensure start_date is not in the future
                if start_date.date() > current_date.date():
                    # Default to yesterday if start date is in the future
                    start_date = current_date - timedelta(days=1)
                    logger.warning("Start date was in the future, using yesterday instead")
                
                # Ensure start_date is before end_date
                if start_date > end_date:
                    start_date = end_date - timedelta(days=1)
                    logger.warning("Start date was after end date, using day before end date instead")
                
            except ValueError as e:
                logger.error(f"Invalid date format: {e}")
                return jsonify({
                    'success': False,
                    'error': f"Invalid date format: {e}"
                }), 400
        else:
            # Fall back to days parameter if no date range provided
            # Limit days to reasonable values
            if days < 1:
                days = 1
            elif days > 90:
                days = 90
                
            # Calculate date range based on days
            end_date = current_date
            start_date = end_date - timedelta(days=days)
        
        # Calculate days between dates for logging
        days_between = (end_date - start_date).days + 1
        
        # Fetch call data from Dialpad API using date range
        logger.info(f"Fetching Dialpad calls from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')} ({days_between} days, max_pages: {max_pages}, refresh: {refresh})")
        calls = api.fetch_department_calls_by_date_range(start_date, end_date, max_pages)
        
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
            'days': days_between,
            'date_range': {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d')
            }
        })
        
    except Exception as e:
        logger.error(f"Error fetching Dialpad calls: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500