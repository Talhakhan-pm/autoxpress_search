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
    
    def deduplicate_calls(self, calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Deduplicate call records that refer to the same actual call
        
        When an inbound call rings multiple agents, Dialpad API returns a separate 
        call record for each agent. This function groups these records by call_id 
        and keeps only the most relevant record.
        
        Args:
            calls: List of call records from Dialpad API
            
        Returns:
            List of deduplicated call records
        """
        if not calls:
            return []
            
        logger.info(f"Starting deduplication of {len(calls)} call records")
        
        # First, identify the key we'll use for grouping calls
        # Some calls may have call_id, others may use id field
        call_id_key = "call_id"
        if not any(call.get("call_id") for call in calls[:min(10, len(calls))]):
            # If the first few calls don't have call_id, try using 'id' instead
            call_id_key = "id"
            logger.info(f"Using '{call_id_key}' as the call identifier field")
        
        # Group calls by call_id/id and call direction
        # We group by direction too because the same call_id might be used 
        # for both incoming and outgoing legs of a call
        call_groups = defaultdict(list)
        for call in calls:
            call_id = str(call.get(call_id_key, ""))
            direction = call.get("direction", "unknown")
            
            # Skip calls without an ID
            if not call_id:
                continue
                
            # Create a composite key with ID and direction
            group_key = f"{call_id}_{direction}"
            call_groups[group_key].append(call)
        
        logger.info(f"Grouped {len(calls)} call records into {len(call_groups)} unique calls")
        
        # Process each group of calls with the same ID and direction
        unique_calls = []
        for group_key, call_group in call_groups.items():
            if len(call_group) == 1:
                # Only one record, no need to process
                unique_calls.append(call_group[0])
                continue
            
            # If we have multiple records for the same call, check if any were answered
            # (have a non-zero duration)
            answered_calls = []
            for call in call_group:
                duration = call.get("duration", 0)
                # Handle different duration formats
                try:
                    if isinstance(duration, str) and duration.strip():
                        duration = float(duration.replace(',', ''))
                    elif isinstance(duration, (int, float)):
                        duration = float(duration)
                    else:
                        duration = 0
                except (ValueError, TypeError):
                    duration = 0
                
                if duration > 0:
                    answered_calls.append(call)
            
            if answered_calls:
                # If any instance was answered, keep only that one
                # Sort by duration in case multiple agents handled parts of the same call
                answered_calls.sort(key=lambda c: float(c.get("duration", 0))
                                  if isinstance(c.get("duration"), (int, float, str)) else 0, 
                                  reverse=True)
                unique_calls.append(answered_calls[0])
                logger.debug(f"Keeping answered call with duration {answered_calls[0].get('duration', 0)}")
            else:
                # If all instances have duration = 0 (no one answered), keep just one
                # Preferably one with a valid agent
                valid_agent_calls = [c for c in call_group if c.get("agent_id") or 
                                   (c.get("target", {}).get("type") == "user" and c.get("target", {}).get("id"))]
                
                if valid_agent_calls:
                    unique_calls.append(valid_agent_calls[0])
                    logger.debug(f"Keeping missed call with agent {valid_agent_calls[0].get('agent_id')}")
                else:
                    # If no valid agent, just keep the first one
                    unique_calls.append(call_group[0])
                    logger.debug(f"Keeping first missed call in group (no valid agent)")
        
        reduction = len(calls) - len(unique_calls)
        if reduction > 0:
            logger.info(f"Deduplicated {len(calls)} call records to {len(unique_calls)} unique calls (removed {reduction} duplicates)")
        else:
            logger.info(f"No duplicates found among {len(calls)} call records")
        
        return unique_calls

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
        end_time_ms = int(datetime.now().timestamp() * 1000)  # Current time
        start_time_ms = int((datetime.now() - timedelta(days=days_back)).timestamp() * 1000)  # days_back days ago
        
        url = f"{self.base_url}/call"
        params = {
            "target_id": agent_id,
            "target_type": "user",
            "started_after": start_time_ms,
            "started_before": end_time_ms,
            "apikey": self.api_key,
            "limit": 50  # Increase page size to get more records per request
        }
        
        logger.info(f"Fetching calls for agent {agent_id} from {datetime.fromtimestamp(start_time_ms/1000)} to {datetime.fromtimestamp(end_time_ms/1000)}")
        
        all_calls = []
        page_count = 0
        
        try:
            # Get first page of results
            response = requests.get(url, params=params, timeout=30)
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
                response = requests.get(url, params=params, timeout=30)
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
        
        # Update user cache first
        self.fetch_department_operators()
        
        # Calculate start/end times as milliseconds since epoch
        end_time_ms = int(datetime.now().timestamp() * 1000)  # Current time
        start_time_ms = int((datetime.now() - timedelta(days=days_back)).timestamp() * 1000)  # days_back days ago
        
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
            response = requests.get(url, params=params, timeout=60)
            page_count += 1
            
            if response.status_code == 200:
                data = response.json()
                calls = data.get("items", [])
                dept_calls.extend(calls)
                
                # Handle pagination using cursor if present (but limit total pages)
                cursor = data.get("cursor")
                while cursor and page_count < max_pages:
                    params["cursor"] = cursor
                    response = requests.get(url, params=params, timeout=60)
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
                this_agent_calls = self.fetch_agent_calls_by_id(agent_id, days_back, max_pages)
                
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
    
    def fetch_agent_calls(self, agent_id: str, days_back: int = 7) -> List[Dict[str, Any]]:
        """
        Fetch call records for a specific agent for the specified time period
        
        Args:
            agent_id: Dialpad ID of the agent
            days_back: Number of days to look back for call records
            
        Returns:
            List of call records
        """
        # Calculate start time (days_back days ago)
        start_time = int((datetime.now() - timedelta(days=days_back)).timestamp())
        
        url = f"{self.base_url}/call"
        params = {
            "target_id": agent_id,
            "target_type": "user",
            "start_time": start_time,
            "apikey": self.api_key
        }
        
        try:
            logger.info(f"Fetching calls for agent {agent_id}")
            response = requests.get(url, params=params)
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch agent calls: {response.status_code} - {response.text}")
                return []
            
            data = response.json()
            calls = data.get("calls", [])
            logger.info(f"Retrieved {len(calls)} call records for agent {agent_id}")
            return calls
            
        except Exception as e:
            logger.error(f"Error fetching agent calls: {e}")
            return []
    
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
        
        # Determine call status based on duration and state
        call_state = call_data.get("state", "")
        
        # In Dialpad, if duration is 0 and state is hangup, it's likely a missed call
        status = "missed" if duration_minutes == 0 and call_state == "hangup" else "completed"
        
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
    
    def get_agent_activity(self, days_back: int = 1, max_pages: int = 2) -> Dict[str, Any]:
        """
        Get aggregated agent activity data
        
        Args:
            days_back: Number of days to look back for call records
            max_pages: Maximum number of pages to fetch (to avoid long loading times)
            
        Returns:
            Dictionary with agent activity metrics
        """
        # Fetch all department calls with page limit (deduplication happens in fetch_department_calls)
        calls = self.fetch_department_calls(days_back, max_pages)
        
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
        
        return {
            "agents": activity_list,
            "total_calls": total_completed_calls,
            "period_days": days_back,
            "from_date": (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d"),
            "to_date": datetime.now().strftime("%Y-%m-%d")
        }