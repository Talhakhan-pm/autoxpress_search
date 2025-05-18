"""
Dialpad API integration for fetching call data and agent activity
"""
import os
import json
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DialpadAPI:
    """Class to handle all Dialpad API interactions"""
    
    def __init__(self, api_key=None, department_id=None):
        """Initialize with API key and department ID"""
        # Try to get API key from various sources
        if api_key:
            self.api_key = api_key
        else:
            # Try environment variable
            self.api_key = os.environ.get("DIALPAD_API_TOKEN", "")
            # If still empty, try direct import from app.py
            if not self.api_key:
                try:
                    from app import DIALPAD_API_TOKEN
                    self.api_key = DIALPAD_API_TOKEN
                except:
                    pass
        
        self.department_id = department_id or os.environ.get("AUTOXPRESS_DEPT_ID", "4869792674824192")
        
        # Define known agent IDs
        self.agent_ids = {
            "Khan": "5503393985740800",
            "Luis Gustavo": "5442156569247744",
            "Roy Davis": "5182373231869952",
            "Ayesha Malik": "5925466191249408", 
            "Murtaza Subhan": "5687535988817920",
            "Farhan Shabir": "6496921529696256"
        }
        
        if not self.api_key:
            logger.warning("No Dialpad API key provided. API calls will fail.")
        else:
            logger.info("Dialpad API initialized successfully.")
        
        self.base_url = "https://dialpad.com/api/v2"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Cache for user information (agent names)
        self.user_cache = {}
        
        # Track missed calls count from deduplication
        self.missed_calls_count = 0
    
    def deduplicate_calls(self, calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Deduplicate call records that refer to the same actual call
        
        When an inbound call rings multiple agents, Dialpad API returns a separate 
        call record for each agent. This function groups these records by entry_point_call_id
        and keeps only the most relevant call record from each group.
        
        Args:
            calls: List of call records from Dialpad API
            
        Returns:
            List of deduplicated call records
        """
        if not calls:
            return []
            
        logger.info(f"Starting deduplication of {len(calls)} call records")
        
        # Step 1: Filter out non-user targets
        user_calls = []
        for call in calls:
            target = call.get("target", {})
            if target.get("type") == "user":
                user_calls.append(call)
            
        if len(user_calls) < len(calls):
            logger.info(f"Filtered out {len(calls) - len(user_calls)} non-user-targeted calls")
        
        # Step 2: Group calls by entry_point_call_id
        call_groups = defaultdict(list)
        
        # Track calls with known entry_point_call_id
        calls_with_entry_point = []
        calls_without_entry_point = []
        
        for call in user_calls:
            # Try to use entry_point_call_id as the primary group key
            entry_point_id = call.get("entry_point_call_id")
            
            if entry_point_id:
                # Add to proper group and track
                call_groups[str(entry_point_id)].append(call)
                calls_with_entry_point.append(call)
            else:
                # Keep track of calls missing entry_point_id for secondary grouping
                calls_without_entry_point.append(call)
        
        logger.info(f"Found {len(calls_with_entry_point)} calls with entry_point_call_id and {len(calls_without_entry_point)} without")
        
        # Secondary grouping by customer contact and timestamp for calls without entry_point_id
        if calls_without_entry_point:
            # Group by customer phone number and timestamp window (within 3 minutes)
            customer_groups = defaultdict(list)
            
            for call in calls_without_entry_point:
                # Get direction and timestamp
                direction = call.get("direction", "unknown")
                timestamp_ms = call.get("date_started", 0)
                
                # Get customer phone number
                phone = None
                if call.get("contact") and call["contact"].get("phone"):
                    phone = call["contact"]["phone"]
                
                # Create group key if we have phone and timestamp
                if phone and timestamp_ms:
                    # Round timestamp to 3-minute window (180000 ms)
                    rounded_ts = int(int(timestamp_ms) / 180000) * 180000
                    group_key = f"{phone}_{direction}_{rounded_ts}"
                    
                    # Add to customer group
                    customer_groups[group_key].append(call)
            
            # Process each customer group and add to main call_groups dictionary
            for group_key, group_calls in customer_groups.items():
                if len(group_calls) > 1:
                    # If we have multiple calls in the same 3-minute window to the same customer
                    # treat them as part of the same interaction
                    fallback_group_id = f"fallback_{group_key}"
                    call_groups[fallback_group_id] = group_calls
                    logger.debug(f"Created fallback group {fallback_group_id} with {len(group_calls)} calls")
                else:
                    # For single calls, just add them directly using their call_id
                    call = group_calls[0]
                    call_id = call.get("call_id", call.get("id", ""))
                    if call_id:
                        call_groups[f"single_{call_id}"].append(call)
                    
        # Add any remaining calls (those without entry_point_id, phone, or timestamp)
        for call in calls_without_entry_point:
            if not any(call in group for group in call_groups.values()):
                call_id = call.get("call_id", call.get("id", "")) 
                if call_id:
                    call_groups[f"orphan_{call_id}"].append(call)
        
        logger.info(f"Grouped {len(user_calls)} call records into {len(call_groups)} unique call groups")
        
        # Function to normalize call duration
        def normalize_duration(duration_raw):
            try:
                if isinstance(duration_raw, str) and duration_raw.strip():
                    if duration_raw.replace('.', '', 1).isdigit():
                        return float(duration_raw)
                    else:
                        return 0
                elif isinstance(duration_raw, (int, float)):
                    return float(duration_raw)
                else:
                    return 0
            except (ValueError, TypeError):
                return 0
                
        # Step 3: For each group, find the best call to keep
        unique_calls = []
        missed_calls_count = 0
        
        for group_id, group_calls in call_groups.items():
            # If there's only one call in the group, just keep it
            if len(group_calls) == 1:
                unique_calls.append(group_calls[0])
                # Check if it's a missed call
                duration = normalize_duration(group_calls[0].get("duration", 0))
                date_connected = group_calls[0].get("date_connected", None)
                
                if duration == 0 and not date_connected:
                    missed_calls_count += 1
                continue
            
            # For multiple calls in a group, find the best one to keep
            # First, extract and normalize call attributes
            processed_calls = []
            for call in group_calls:
                duration = normalize_duration(call.get("duration", 0))
                date_connected = call.get("date_connected", None)
                date_started = call.get("date_started", 0)
                
                # Get agent information
                agent_name = "Unknown"
                target = call.get("target", {})
                if target.get("name"):
                    agent_name = target.get("name")
                if call.get("agent_name"):
                    agent_name = call.get("agent_name")
                
                # Store all processed data
                processed_calls.append({
                    "call": call,
                    "duration": duration,
                    "date_connected": date_connected,
                    "date_started": date_started,
                    "agent_name": agent_name,
                    "has_known_agent": agent_name != "Unknown"
                })
                
            # Check for calls with date_connected (definitively answered)
            # In Dialpad API, date_connected is the most reliable indicator that a call was answered
            connected_calls = [c for c in processed_calls if c["date_connected"]]
            
            if connected_calls:
                # 1. Primary sort: Prefer calls with named agents
                known_agent_answers = [c for c in connected_calls if c["has_known_agent"]]
                
                if known_agent_answers:
                    # 2. Secondary sort: Sort by duration (longest first)
                    known_agent_answers.sort(key=lambda c: c["duration"], reverse=True)
                    unique_calls.append(known_agent_answers[0]["call"])
                    logger.debug(f"Keeping answered call with known agent '{known_agent_answers[0]['agent_name']}' and duration {known_agent_answers[0]['duration']}")
                else:
                    # If no known agent answered, use longest duration call
                    connected_calls.sort(key=lambda c: c["duration"], reverse=True)
                    unique_calls.append(connected_calls[0]["call"])
                    logger.debug(f"Keeping answered call with unknown agent and duration {connected_calls[0]['duration']}")
            
            # Handle ambiguous case: duration > 0 but no date_connected
            # This is unusual in Dialpad API and might represent a call that was
            # picked up by the system but not properly connected to an agent
            elif any(c["duration"] > 0 for c in processed_calls):
                duration_calls = [c for c in processed_calls if c["duration"] > 0]
                
                # These calls have duration but no date_connected (ambiguous)
                # Still prefer calls with known agents for better display
                known_agent_duration = [c for c in duration_calls if c["has_known_agent"]]
                
                if known_agent_duration:
                    # Sort by duration (longest first)
                    known_agent_duration.sort(key=lambda c: c["duration"], reverse=True)
                    unique_calls.append(known_agent_duration[0]["call"])
                    logger.warning(f"Ambiguous call state: duration={known_agent_duration[0]['duration']} but no date_connected. Keeping best record with agent '{known_agent_duration[0]['agent_name']}'")
                else:
                    # No known agent, sort by duration
                    duration_calls.sort(key=lambda c: c["duration"], reverse=True)
                    unique_calls.append(duration_calls[0]["call"])
                    logger.warning(f"Ambiguous call state: duration={duration_calls[0]['duration']} but no date_connected. Keeping record with longest duration.")
                
                # Count this as a missed call since there's no date_connected
                missed_calls_count += 1
            
            else:
                # This is a missed call - keep one representative call
                # Prefer calls with known agent information
                known_agent_calls = [c for c in processed_calls if c["has_known_agent"]]
                
                if known_agent_calls:
                    # For missed calls, prefer the most recent one
                    known_agent_calls.sort(key=lambda c: c["date_started"], reverse=True)
                    unique_calls.append(known_agent_calls[0]["call"])
                    logger.debug(f"Keeping missed call with known agent '{known_agent_calls[0]['agent_name']}'")
                else:
                    # Sort by timestamp (newest first)
                    processed_calls.sort(key=lambda c: c["date_started"], reverse=True)
                    unique_calls.append(processed_calls[0]["call"])
                    logger.debug(f"Keeping missed call with no agent info, timestamp {processed_calls[0]['date_started']}")
                
                # Count this as a missed call
                missed_calls_count += 1
        
        reduction = len(user_calls) - len(unique_calls)
        
        if reduction > 0:
            logger.info(f"Deduplicated {len(user_calls)} call records to {len(unique_calls)} unique calls (removed {reduction} duplicates)")
            logger.info(f"Identified {missed_calls_count} unique missed calls")
        else:
            logger.info(f"No duplicates found among {len(user_calls)} call records")
            logger.info(f"Identified {missed_calls_count} unique missed calls")
        
        # Store the missed calls count for use in the response
        self.missed_calls_count = missed_calls_count
        
        return unique_calls

    def fetch_agent_calls_by_id_and_date_range(self, agent_id: str, start_date: datetime, end_date: datetime, max_pages: int = 2) -> List[Dict[str, Any]]:
        """
        Fetch call records for a specific agent by ID for the specified date range
        
        Args:
            agent_id: Dialpad ID of the agent
            start_date: Start date for fetching calls
            end_date: End date for fetching calls
            max_pages: Maximum number of pages to fetch (to avoid long loading times)
            
        Returns:
            List of call records
        """
        # Ensure dates are not in the future
        current_time = datetime.now()
        
        if end_date > current_time:
            end_date = current_time
            logger.warning(f"End date was in the future for agent {agent_id}, using current time instead")
            
        if start_date > current_time:
            start_date = current_time - timedelta(days=1)
            logger.warning(f"Start date was in the future for agent {agent_id}, using yesterday instead")
            
        # Ensure start_date is before end_date
        if start_date > end_date:
            start_date = end_date - timedelta(days=1)
            logger.warning(f"Start date was after end date for agent {agent_id}, using day before end date instead")
        
        # Calculate start/end times as milliseconds since epoch (which is what Dialpad API expects)
        end_time_ms = int(end_date.timestamp() * 1000)
        start_time_ms = int(start_date.timestamp() * 1000)
        
        logger.info(f"Fetching calls for agent {agent_id} from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        
        return self._fetch_agent_calls_by_timeframe(agent_id, start_time_ms, end_time_ms, max_pages)
    
    def fetch_agent_calls_by_id(self, agent_id: str, days_back: int = 7, max_pages: int = 2) -> List[Dict[str, Any]]:
        """
        Fetch call records for a specific agent by ID for the specified time period
        
        Args:
            agent_id: Dialpad ID of the agent
            days_back: Number of days to look back for call records
            max_pages: Maximum number of pages to fetch (to avoid long loading times)
            
        Returns:
            List of call records
        """
        # Calculate start/end times as milliseconds since epoch (which is what Dialpad API expects)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        return self.fetch_agent_calls_by_id_and_date_range(agent_id, start_date, end_date, max_pages)
    
    def _fetch_agent_calls_by_timeframe(self, agent_id: str, start_time_ms: int, end_time_ms: int, max_pages: int = 2) -> List[Dict[str, Any]]:
        """
        Fetch call records for a specific agent by ID for the specified time frame
        
        Args:
            agent_id: Dialpad ID of the agent
            start_time_ms: Start time in milliseconds since epoch
            end_time_ms: End time in milliseconds since epoch
            max_pages: Maximum number of pages to fetch (to avoid long loading times)
            
        Returns:
            List of call records
        """
        # Calculate start/end times as milliseconds since epoch (which is what Dialpad API expects)
        url = f"{self.base_url}/call"
        params = {
            "target_id": agent_id,
            "target_type": "user",
            "started_after": start_time_ms,
            "started_before": end_time_ms,
            "apikey": self.api_key,
            "limit": 50  # Increase page size to get more records per request
        }
        
        logger.info(f"Fetching calls for agent {agent_id} using timeframe")
        
        all_calls = []
        page_count = 0
        
        try:
            # Get first page of results
            response = requests.get(url, params=params, timeout=600)
            page_count += 1
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch agent calls: {response.status_code} - {response.text}")
                return []
            
            data = response.json()
            calls = data.get("items", [])
            all_calls.extend(calls)
            
            # Handle pagination using cursor if present (but limit total pages)
            cursor = data.get("cursor")
            while cursor and page_count < max_pages:
                # Add cursor to parameters for next page
                params["cursor"] = cursor
                
                # Get next page
                logger.info(f"Fetching page {page_count+1} for agent {agent_id} with cursor: {cursor}")
                response = requests.get(url, params=params, timeout=600)
                page_count += 1
                
                if response.status_code != 200:
                    logger.error(f"Failed to fetch page {page_count}: {response.status_code} - {response.text}")
                    break
                    
                data = response.json()
                calls = data.get("items", [])
                all_calls.extend(calls)
                
                # Update cursor for next page, or set to None to exit loop
                cursor = data.get("cursor")
                if not cursor or not calls:
                    break
            
            logger.info(f"Retrieved {len(all_calls)} call records for agent {agent_id}")
            return all_calls
            
        except Exception as e:
            logger.error(f"Error fetching agent calls: {e}")
            return []

    def fetch_department_calls_by_date_range(self, start_date: datetime, end_date: datetime, max_pages: int = 3) -> List[Dict[str, Any]]:
        """
        Fetch call records for the department for the specified date range
        
        This implementation attempts both methods:
        1. Getting calls for the entire department (with deduplication)
        2. Getting calls for each individual agent separately (as a backup)
        
        Args:
            start_date: Start date for fetching calls
            end_date: End date for fetching calls
            max_pages: Maximum number of pages to fetch (to avoid long loading times)
            
        Returns:
            List of call records
        """
        # Ensure dates are not in the future
        current_time = datetime.now()
        
        if end_date > current_time:
            end_date = current_time
            logger.warning("End date was in the future, using current time instead")
            
        if start_date > current_time:
            start_date = current_time - timedelta(days=1)
            logger.warning("Start date was in the future, using yesterday instead")
            
        # Ensure start_date is before end_date
        if start_date > end_date:
            start_date = end_date - timedelta(days=1)
            logger.warning("Start date was after end date, using day before end date instead")
        
        days_between = (end_date - start_date).days + 1
        logger.info(f"Fetching calls from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')} ({days_between} days) using optimized method")
        
        # Update user cache first
        self.fetch_department_operators()
        
        # Calculate start/end times as milliseconds since epoch
        end_time_ms = int(end_date.timestamp() * 1000)
        start_time_ms = int(start_date.timestamp() * 1000)
        
        # APPROACH 1: Get calls for the entire department
        logger.info(f"APPROACH 1: Fetching calls for department {self.department_id}")
        
        url = f"{self.base_url}/call"
        params = {
            "target_id": self.department_id,
            "target_type": "department",
            "started_after": start_time_ms,
            "started_before": end_time_ms,
            "apikey": self.api_key,
            "limit": 50  # Increase page size to get more records per request
        }
        
        dept_calls = []
        page_count = 0
        
        try:
            # Get first page of results
            response = requests.get(url, params=params, timeout=600)
            page_count += 1
            
            if response.status_code == 200:
                data = response.json()
                calls = data.get("items", [])
                dept_calls.extend(calls)
                
                # Handle pagination using cursor if present (but limit total pages)
                cursor = data.get("cursor")
                while cursor and page_count < max_pages:
                    params["cursor"] = cursor
                    response = requests.get(url, params=params, timeout=600)
                    page_count += 1
                    
                    if response.status_code != 200:
                        logger.error(f"Failed to fetch page {page_count}: {response.status_code}")
                        break
                        
                    data = response.json()
                    calls = data.get("items", [])
                    dept_calls.extend(calls)
                    
                    cursor = data.get("cursor")
                    if not cursor or not calls:
                        break
                
                logger.info(f"APPROACH 1: Retrieved {len(dept_calls)} raw department call records")
            else:
                logger.error(f"Failed to fetch department calls: {response.status_code}")
        except Exception as e:
            logger.error(f"Error fetching department calls: {e}")
        
        # APPROACH 2: Fetch calls for each agent separately
        logger.info("APPROACH 2: Fetching calls for individual agents")
        agent_calls = []
        
        for agent_name, agent_id in self.agent_ids.items():
            try:
                logger.info(f"Fetching calls for agent {agent_name} ({agent_id})")
                this_agent_calls = self.fetch_agent_calls_by_id_and_date_range(agent_id, start_date, end_date, max_pages)
                
                # Add agent info to each call
                for call in this_agent_calls:
                    if not call.get("agent_name"):
                        call["agent_name"] = agent_name
                    if not call.get("agent_id"):
                        call["agent_id"] = agent_id
                
                agent_calls.extend(this_agent_calls)
                logger.info(f"Added {len(this_agent_calls)} calls for agent {agent_name}")
            except Exception as e:
                logger.error(f"Error fetching calls for agent {agent_name}: {e}")
        
        logger.info(f"APPROACH 2: Retrieved {len(agent_calls)} raw agent call records")
        
        # Deduplicate each set of calls separately
        deduplicated_dept_calls = self.deduplicate_calls(dept_calls)
        deduplicated_agent_calls = self.deduplicate_calls(agent_calls)
        
        logger.info(f"Deduplicated calls: {len(deduplicated_dept_calls)} from department, {len(deduplicated_agent_calls)} from agents")
        
        # Choose the approach that found more unique calls
        if len(deduplicated_dept_calls) >= len(deduplicated_agent_calls):
            logger.info(f"Using APPROACH 1 (department calls) which found more unique calls")
            return deduplicated_dept_calls
        else:
            logger.info(f"Using APPROACH 2 (agent calls) which found more unique calls")
            return deduplicated_agent_calls
    
    def fetch_department_calls(self, days_back: int = 7, max_pages: int = 3) -> List[Dict[str, Any]]:
        """
        Fetch call records for the department for the specified time period
        
        This implementation attempts both methods:
        1. Getting calls for the entire department (with deduplication)
        2. Getting calls for each individual agent separately (as a backup)
        
        Args:
            days_back: Number of days to look back for call records
            max_pages: Maximum number of pages to fetch (to avoid long loading times)
            
        Returns:
            List of call records
        """
        logger.info(f"Fetching calls for the past {days_back} days using optimized method")
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        return self.fetch_department_calls_by_date_range(start_date, end_date, max_pages)
            
    def fetch_department_operators(self) -> List[Dict[str, Any]]:
        """
        Fetch operators in the department
        
        Returns:
            List of operator records
        """
        url = f"{self.base_url}/departments/{self.department_id}/operators"
        params = {
            "apikey": self.api_key
        }
        
        try:
            logger.info(f"Fetching operators for department {self.department_id}")
            response = requests.get(url, params=params)
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch department operators: {response.status_code} - {response.text}")
                return []
            
            data = response.json()
            users = data.get("users", [])
            
            # Update user cache
            for user in users:
                user_id = str(user.get("id"))
                user_name = user.get("display_name", "Unknown")
                self.user_cache[user_id] = user_name
                
            logger.info(f"Retrieved {len(users)} operators")
            return users
            
        except Exception as e:
            logger.error(f"Error fetching department operators: {e}")
            return []
    
    def fetch_operator_calls(self, operator_id: str, days_back: int = 7) -> List[Dict[str, Any]]:
        """
        Fetch call records for a specific operator
        
        Args:
            operator_id: Dialpad ID of the operator
            days_back: Number of days to look back for call records
            
        Returns:
            List of call records
        """
        # Generate synthetic call data for this operator
        return self._generate_synthetic_calls(operator_id, days_back)
    
    def _generate_synthetic_calls(self, operator_id: str, days_back: int = 7) -> List[Dict[str, Any]]:
        """
        Generate synthetic call data for demonstration purposes
        
        Args:
            operator_id: Dialpad ID of the operator
            days_back: Number of days to look back
            
        Returns:
            List of synthetic call records
        """
        import random
        import uuid
        
        # Get operator name from cache
        operator_name = self.user_cache.get(operator_id, "Unknown Operator")
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Generate random number of calls (3-15)
        num_calls = random.randint(3, 15)
        
        # List to store synthetic calls
        calls = []
        
        # Generate random calls
        for _ in range(num_calls):
            # Random call date in the specified range
            call_date = start_date + timedelta(days=random.randint(0, days_back))
            
            # Call properties
            call_id = str(uuid.uuid4().hex[:10])
            call_type = random.choice(["inbound", "outbound"])
            duration = random.randint(1, 900) if random.random() > 0.2 else 0  # 20% chance of missed call
            status = "completed" if duration > 0 else "missed"
            
            # Create synthetic call record
            call = {
                "call_id": call_id,
                "direction": call_type,
                "start_time": int(call_date.timestamp()),
                "duration": duration,
                "answered_by": operator_id,
                "contact_name": f"Test Customer {random.randint(1, 100)}",
                "caller_number": f"+1{random.randint(200, 999)}{random.randint(200, 999)}{random.randint(1000, 9999)}",
                "target_number": f"+1{random.randint(200, 999)}{random.randint(200, 999)}{random.randint(1000, 9999)}",
                "notes": f"Synthetic call for demonstration purposes"
            }
            
            calls.append(call)
        
        logger.info(f"Generated {len(calls)} synthetic calls for {operator_name}")
        return calls
    
    def fetch_users(self) -> List[Dict[str, Any]]:
        """
        Fetch all users from Dialpad API and update user cache
        
        Returns:
            List of user records
        """
        url = f"{self.base_url}/users"
        
        try:
            logger.info("Fetching Dialpad users")
            response = requests.get(url, headers=self.headers)
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch Dialpad users: {response.status_code} - {response.text}")
                return []
            
            data = response.json()
            users = data.get("users", [])
            
            # Update user cache
            for user in users:
                user_id = str(user.get("id"))
                user_name = user.get("display_name", "Unknown")
                self.user_cache[user_id] = user_name
                
            logger.info(f"Retrieved {len(users)} user records")
            return users
            
        except Exception as e:
            logger.error(f"Error fetching Dialpad users: {e}")
            return []
    
    def process_call_data(self, call_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a call record to extract and format key information
        
        Args:
            call_data: Raw call data from Dialpad API
            
        Returns:
            Processed call record with formatted fields
        """
        # Extract call_id
        call_id = str(call_data.get("call_id", ""))
        
        # Get agent information from target if it's a user, or use what was added by fetch_agent_calls_by_id
        agent_id = call_data.get("agent_id", "")
        agent_name = call_data.get("agent_name", "Unknown Agent")
        
        if not agent_id or not agent_name or agent_name == "Unknown Agent":
            target = call_data.get("target", {})
            target_type = target.get("type", "")
            
            # If target is a user, that's our agent
            if target_type == "user":
                agent_id = target.get("id", "")
                agent_name = target.get("name", "Unknown Agent")
                
                # Add to user cache
                if agent_id:
                    self.user_cache[agent_id] = agent_name
            
            # Try to look up agent name from our predefined list
            if agent_id and not agent_name or agent_name == "Unknown Agent":
                for name, id in self.agent_ids.items():
                    if id == agent_id:
                        agent_name = name
                        break
        
        # Convert epoch milliseconds to datetime
        start_time_epoch = call_data.get("date_started", 0)
        try:
            # API returns timestamps in milliseconds, convert to seconds for datetime
            call_datetime = datetime.fromtimestamp(int(start_time_epoch) / 1000)
            call_date = call_datetime.strftime("%Y-%m-%d")
            call_time = call_datetime.strftime("%H:%M")
        except:
            call_datetime = datetime.now()
            call_date = call_datetime.strftime("%Y-%m-%d")
            call_time = call_datetime.strftime("%H:%M")
            logger.warning(f"Could not parse date_started: {start_time_epoch}, using current time")
        
        # Determine call type (inbound/outbound) based on direction
        call_direction = call_data.get("direction", "")
        call_type = "inbound" if call_direction == "inbound" else "outbound"
        
        # Get contact information
        contact = call_data.get("contact", {})
        contact_name = contact.get("name", "")
        contact_phone = contact.get("phone", "")
        
        # Get internal and external numbers
        internal_number = call_data.get("internal_number", "")
        external_number = call_data.get("external_number", "")
        
        # Calculate duration in minutes
        duration_seconds = call_data.get("duration", 0)
        # Convert to minutes, handle scientific notation
        try:
            if isinstance(duration_seconds, str) and 'e' in duration_seconds.lower():
                duration_seconds = float(duration_seconds)
            duration_minutes = round(float(duration_seconds) / 60000, 1)  # Convert milliseconds to minutes
        except:
            duration_minutes = 0
            logger.warning(f"Could not parse duration: {duration_seconds}, using 0")
        
        # Determine call status based on duration and date_connected
        call_state = call_data.get("state", "")
        date_connected = call_data.get("date_connected")
        
        # A call is definitively completed only if it has date_connected
        # This is the most reliable indicator in Dialpad API
        # 
        # Note: duration > 0 without date_connected is ambiguous and might
        # represent a call that was picked up by the system but not by an agent
        is_completed = (date_connected is not None)
        status = "completed" if is_completed else "missed"
        
        # Create processed call record
        processed_call = {
            "id": f"dp_{call_id}",
            "dialpad_id": call_id,
            "call_type": call_type,
            "date": call_date,
            "time": call_time,
            "timestamp": call_datetime,
            "agent": agent_name,
            "agent_id": agent_id,
            "customer": contact_name or contact_phone or external_number,
            "phone": contact_phone or external_number,
            "duration": duration_minutes,
            "status": status,
            "notes": "",  # API doesn't provide notes
            "vehicle_info": "",  # To be filled later by agents
            "product": "",       # To be filled later by agents
            "followup_required": False,
        }
        
        return processed_call
    
    def get_agent_activity_by_date_range(self, start_date: datetime, end_date: datetime, max_pages: int = 2) -> Dict[str, Any]:
        """
        Get aggregated agent activity data for a specific date range
        
        Args:
            start_date: Start date for fetching calls
            end_date: End date for fetching calls
            max_pages: Maximum number of pages to fetch (to avoid long loading times)
            
        Returns:
            Dictionary with agent activity metrics
        """
        # Fetch all department calls with page limit (deduplication happens in fetch_department_calls)
        calls = self.fetch_department_calls_by_date_range(start_date, end_date, max_pages)
        
        # Process and format calls
        processed_calls = [self.process_call_data(call) for call in calls]
        
        # Filter out missed calls - we only want to show completed calls
        completed_calls = [call for call in processed_calls if call.get("status") != "missed"]
        
        # Aggregate activity by agent
        agent_activity = {}
        
        for call in completed_calls:
            agent_id = call.get("agent_id")
            agent_name = call.get("agent")
            
            if not agent_id:
                continue
                
            # Initialize agent stats if not exists
            if agent_id not in agent_activity:
                agent_activity[agent_id] = {
                    "agent_id": agent_id,
                    "agent_name": agent_name,
                    "inbound_calls": 0,
                    "outbound_calls": 0,
                    "completed_calls": 0,
                    "total_duration": 0,
                    "avg_duration": 0,
                    "calls_by_day": {}
                }
            
            # Update agent stats - only track completed calls
            stats = agent_activity[agent_id]
            stats["completed_calls"] += 1
            
            if call.get("call_type") == "inbound":
                stats["inbound_calls"] += 1
            else:
                stats["outbound_calls"] += 1
                
            stats["total_duration"] += call.get("duration", 0)
            
            # Track calls by day
            call_date = call.get("date")
            if call_date:
                if call_date not in stats["calls_by_day"]:
                    stats["calls_by_day"][call_date] = 0
                stats["calls_by_day"][call_date] += 1
        
        # Calculate average call duration for each agent
        for agent_id, stats in agent_activity.items():
            if stats["completed_calls"] > 0:
                stats["avg_duration"] = round(stats["total_duration"] / stats["completed_calls"], 1)
        
        # Convert to list for easier frontend processing
        activity_list = list(agent_activity.values())
        
        # Sort by completed calls (descending)
        activity_list.sort(key=lambda x: x["completed_calls"], reverse=True)
        
        # Calculate the total number of completed calls
        total_completed_calls = len(completed_calls)
        
        days_between = (end_date - start_date).days + 1
        
        return {
            "agents": activity_list,
            "total_completed_calls": total_completed_calls,
            "missed_calls": self.missed_calls_count,
            "total_calls": total_completed_calls + self.missed_calls_count,
            "period_days": days_between,
            "from_date": start_date.strftime("%Y-%m-%d"),
            "to_date": end_date.strftime("%Y-%m-%d")
        }
    
    def get_agent_activity(self, days_back: int = 1, max_pages: int = 2) -> Dict[str, Any]:
        """
        Get aggregated agent activity data
        
        Args:
            days_back: Number of days to look back for call records
            max_pages: Maximum number of pages to fetch (to avoid long loading times)
            
        Returns:
            Dictionary with agent activity metrics
        """
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        return self.get_agent_activity_by_date_range(start_date, end_date, max_pages)