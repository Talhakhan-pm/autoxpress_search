import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any

class DialpadClient:
    """Directly implements Dialpad API client based on documentation."""
    
    # Agent IDs and names
    AGENTS = {
        "Khan": "5503393985740800",
        "Luis Gustavo": "5442156569247744",
        "Roy Davis": "5182373231869952",
        "Ayesha Malik": "5925466191249408",
        "Murtaza Subhan": "5687535988817920",
        "Farhan Shabir": "6496921529696256"
    }
    
    def __init__(self):
        self.api_key = "pZcxnhANRfWWwU9G754vaSQp3huh5bmtUmchFQusrpxBjxZJkzYPVuUHJGZGjT3Mrs8Cj58Dph4uLHMBRbW2pxEHpt2u8Tdv5Ny5"
        self.headers = {"accept": "application/json"}
    
    def get_calls(self, agent_id=None, limit=50, started_after=None, started_before=None):
        """
        Direct implementation based on documentation example with pagination and date filtering.
        
        Args:
            agent_id: Optional agent ID to filter results
            limit: Maximum number of results to get (default 50)
            started_after: Optional timestamp (in milliseconds) for filtering calls after this time
            started_before: Optional timestamp (in milliseconds) for filtering calls before this time
            
        Returns:
            List of calls or empty list
        """
        all_calls = []
        cursor = None
        
        while True:
            # Build base URL with parameters
            params = {
                "apikey": self.api_key,
                "limit": limit
            }
            
            if agent_id:
                params["target_id"] = agent_id
                params["target_type"] = "user"
                
            if started_after:
                params["started_after"] = started_after
                
            if started_before:
                params["started_before"] = started_before
                
            if cursor:
                params["cursor"] = cursor
                
            # Construct URL with params
            url_parts = []
            for key, value in params.items():
                url_parts.append(f"{key}={value}")
                
            url = f"https://dialpad.com/api/v2/call?{'&'.join(url_parts)}"
                
            try:
                response = requests.get(url, headers=self.headers)
                print(f"Response status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    # Dialpad API returns 'items', not 'calls'
                    items = data.get("items", [])
                    all_calls.extend(items)
                    
                    # Get cursor for next page
                    cursor = data.get("cursor")
                    print(f"Retrieved {len(items)} calls, total so far: {len(all_calls)}")
                    
                    # Break if no cursor or no more items
                    if not cursor or not items:
                        break
                else:
                    print(f"Error: {response.status_code} - {response.text}")
                    break
                    
                # Break after collecting 200 calls per agent to avoid excessive API calls
                if len(all_calls) >= 200:
                    print(f"Reached maximum call limit of 200 for agent")
                    break
                    
            except Exception as e:
                print(f"Exception: {str(e)}")
                break
                
        return all_calls

    def get_all_agent_calls(self, started_after=None, started_before=None):
        """
        Fetch calls for all agents with date filtering and enhanced call relationship tracking.
        
        Args:
            started_after: Optional timestamp (in milliseconds) for filtering calls after this time
            started_before: Optional timestamp (in milliseconds) for filtering calls before this time
        """
        all_calls = []
        
        # Step 1: Collect raw calls for all agents
        print("Step 1: Collecting raw call data for all agents...")
        raw_agent_calls = {}
        
        for agent_name, agent_id in self.AGENTS.items():
            print(f"Fetching calls for {agent_name}...")
            
            agent_calls = self.get_calls(
                agent_id=agent_id,
                started_after=started_after,
                started_before=started_before
            )
            
            # Add agent info to each call
            for call in agent_calls:
                call["agent_name"] = agent_name
                call["agent_id"] = agent_id
            
            raw_agent_calls[agent_id] = agent_calls
            print(f"Retrieved {len(agent_calls)} calls for {agent_name}")
        
        # Step 2: Process calls to establish relationships (which agent actually took each call)
        print("Step 2: Processing calls to establish relationships...")
        call_mapping = {}  # Maps entry_point_call_id to the agent who answered
        
        # First pass: identify which calls were answered and by whom
        for agent_id, calls in raw_agent_calls.items():
            agent_name = next((name for name, aid in self.AGENTS.items() if aid == agent_id), "Unknown")
            
            for call in calls:
                entry_point_id = call.get("entry_point_call_id")
                
                # If this agent connected to the call, they answered it
                if call.get("date_connected") and entry_point_id:
                    if entry_point_id not in call_mapping:
                        call_mapping[entry_point_id] = {
                            "answered_by": agent_id,
                            "answered_by_name": agent_name,
                            "date_connected": call.get("date_connected")
                        }
                    # If there are multiple connected calls with the same entry_point_id,
                    # keep the one with the earliest connection time
                    elif call.get("date_connected") < call_mapping[entry_point_id]["date_connected"]:
                        call_mapping[entry_point_id] = {
                            "answered_by": agent_id,
                            "answered_by_name": agent_name,
                            "date_connected": call.get("date_connected")
                        }
        
        # Step 3: Track missed calls at entry_point level
        print("Step 3: Tracking missed calls...")
        missed_call_entries = set()  # Set of entry_point_call_ids that were missed by everyone
        first_agent_for_missed = {}  # Maps entry_point_call_id to the first agent who received the missed call
        
        for agent_id, calls in raw_agent_calls.items():
            agent_name = next((name for name, aid in self.AGENTS.items() if aid == agent_id), "Unknown")
            
            for call in calls:
                entry_point_id = call.get("entry_point_call_id")
                
                # Only track inbound calls with entry_point_id and no date_connected
                if (entry_point_id and not call.get("date_connected") and 
                    call.get("direction") == "inbound" and
                    entry_point_id not in call_mapping):  # Not answered by anyone
                    
                    # Track this as a missed call
                    missed_call_entries.add(entry_point_id)
                    
                    # Remember the first agent who received this call
                    if entry_point_id not in first_agent_for_missed:
                        first_agent_for_missed[entry_point_id] = {
                            "agent_id": agent_id,
                            "agent_name": agent_name,
                            "call": call  # Keep reference to this call
                        }
        
        # Step 4: Determine call status based on relationships
        print("Step 4: Determining call status with consolidated missed calls...")
        processed_missed_calls = set()  # Track entry_point_ids we've already processed
        
        for agent_id, calls in raw_agent_calls.items():
            agent_name = next((name for name, aid in self.AGENTS.items() if aid == agent_id), "Unknown")
            
            for call in calls:
                entry_point_id = call.get("entry_point_call_id")
                
                # Determine call status
                if call.get("date_connected"):
                    # This agent answered the call
                    call["status"] = "completed"
                    call["answering_agent"] = agent_name
                    all_calls.append(call)
                    
                elif entry_point_id and entry_point_id in call_mapping:
                    # Someone else answered this call
                    call["status"] = "handled_elsewhere"
                    call["answering_agent"] = call_mapping[entry_point_id]["answered_by_name"]
                    call["routed_to_agent"] = agent_name  # Track which agent this call was routed to
                    
                    # Create or update a list of agents this call was routed to
                    if "routed_to_agents" not in call_mapping[entry_point_id]:
                        call_mapping[entry_point_id]["routed_to_agents"] = []
                    
                    # Add this agent to the list of agents who received this call
                    if agent_name not in call_mapping[entry_point_id]["routed_to_agents"]:
                        call_mapping[entry_point_id]["routed_to_agents"].append(agent_name)
                    
                    # Copy the list to this call instance
                    call["routed_to_agents"] = call_mapping[entry_point_id]["routed_to_agents"]
                    
                    all_calls.append(call)
                    
                elif entry_point_id and entry_point_id in missed_call_entries:
                    # This is a missed call that rang to multiple agents
                    
                    # Only include the first agent's version in the final list
                    # to avoid duplicate "missed" calls in the reporting
                    if entry_point_id not in processed_missed_calls:
                        call["status"] = "missed"
                        call["answering_agent"] = "Nobody"
                        call["is_consolidated_miss"] = True
                        call["affected_agents"] = []  # Will track who else received this call
                        processed_missed_calls.add(entry_point_id)
                        all_calls.append(call)
                        
                    # For subsequent agents, we'll skip adding their version
                    # but track that they also received this call
                    elif call.get("date_rang"):  # Make sure it actually rang for this agent
                        # Find the consolidated miss call
                        for c in all_calls:
                            if c.get("entry_point_call_id") == entry_point_id and c.get("is_consolidated_miss"):
                                if agent_name not in c.get("affected_agents", []):
                                    c.get("affected_agents", []).append(agent_name)
                                break
                
                elif call.get("direction") == "outbound":
                    # Outbound calls are always kept
                    if not call.get("date_connected"):
                        call["status"] = "missed"
                    else:
                        call["status"] = "completed"
                    all_calls.append(call)
                    
                else:
                    # Default case: if we can't determine it's a duplicate miss,
                    # include it anyway with "missed" status
                    call["status"] = "missed"
                    call["answering_agent"] = "Unknown"
                    all_calls.append(call)
        
        print(f"Processed {len(all_calls)} total calls")
        return all_calls
    
    def format_call_for_display(self, call):
        """Format call for display."""
        # Get customer name from contact
        customer_name = call.get("contact", {}).get("name", "")
        
        # Calculate duration in minutes
        duration_seconds = call.get("duration", 0)
        duration_minutes = round(duration_seconds / 60, 1) if duration_seconds else 0
        
        # Format date/time
        date_started = call.get("date_started", "")
        formatted_datetime = ""
        if date_started:
            # Convert from Unix timestamp (milliseconds) to datetime
            try:
                # First try treating it as a timestamp
                if isinstance(date_started, (int, float)) or (isinstance(date_started, str) and date_started.isdigit()):
                    timestamp_ms = float(date_started)
                    dt = datetime.fromtimestamp(timestamp_ms / 1000.0)
                    formatted_datetime = dt.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    # Fallback to ISO format
                    dt = datetime.fromisoformat(date_started.replace("Z", "+00:00"))
                    formatted_datetime = dt.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError as e:
                # If conversion fails, just use the raw value
                print(f"Could not convert timestamp: {date_started} - {str(e)}")
                formatted_datetime = f"Raw: {date_started}"
        
        # Get customer phone number - from contact
        customer_phone = call.get("contact", {}).get("phone", "")
        if not customer_phone:
            # Fallback to external number if contact phone is not available
            customer_phone = call.get("external_number", "")
        
        # Get recording URL - check admin_recording_urls first
        recording_url = ""
        admin_recording_urls = call.get("admin_recording_urls", [])
        if admin_recording_urls and len(admin_recording_urls) > 0:
            recording_url = admin_recording_urls[0]
        else:
            # Check recording_details
            recording_details = call.get("recording_details", [])
            if recording_details and len(recording_details) > 0:
                recording_url = recording_details[0].get("url", "")
        
        # Create base display format
        display_data = {
            "call_id": call.get("call_id", ""),
            "agent_name": call.get("agent_name", "Unknown Agent"),
            "agent_id": call.get("agent_id", ""),
            "customer_name": customer_name,
            "customer_phone": customer_phone,
            "call_type": call.get("direction", ""),
            "duration": duration_minutes,
            "datetime": formatted_datetime,
            "status": call.get("status", "unknown"),
            "recording_url": recording_url
        }
        
        # Add detailed status information
        if call.get("status") == "handled_elsewhere" and call.get("answering_agent"):
            # Basic info about who answered
            answering_msg = f"Answered by {call.get('answering_agent')}"
            
            # Add info about which other agents it was routed to
            if call.get("routed_to_agents") and len(call.get("routed_to_agents", [])) > 1:
                # Get all agents except the current one and the one who answered
                others = [agent for agent in call.get("routed_to_agents", []) 
                         if agent != call.get("routed_to_agent") and agent != call.get("answering_agent")]
                
                # If there are other agents it was routed to
                if others:
                    also_routed = ", ".join(others)
                    display_data["status_details"] = f"{answering_msg}. Also routed to: {also_routed}"
                else:
                    display_data["status_details"] = answering_msg
            else:
                display_data["status_details"] = answering_msg
        elif call.get("status") == "missed":
            if call.get("is_consolidated_miss") and call.get("affected_agents"):
                # This is a consolidated miss that affected multiple agents
                affected = call.get("affected_agents", [])
                if affected:
                    agents_str = ", ".join(affected)
                    display_data["status_details"] = f"Also missed by: {agents_str}"
                else:
                    display_data["status_details"] = "Not answered"
            else:
                display_data["status_details"] = "Not answered"
        else:
            display_data["status_details"] = ""
            
        return display_data