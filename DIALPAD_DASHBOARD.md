# Dialpad Dashboard Documentation

## Overview

The Dialpad Dashboard is a web-based interface for viewing and analyzing call activities of AutoXpress agents. It integrates directly with the Dialpad API to fetch call logs for individual agents, process the data, and present it in a user-friendly format. The dashboard allows for filtering by date range, agent, call type, and status.

## Architecture

The Dialpad Dashboard follows a client-server architecture:

1. **Backend (Python/Flask)**: 
   - Handles API requests from the frontend
   - Communicates with the Dialpad API
   - Processes and formats call data
   - Implements sophisticated call relationship tracking

2. **Frontend (HTML/JavaScript/CSS)**:
   - Presents the user interface for the dashboard
   - Sends requests to the backend API
   - Processes and displays the response data
   - Handles user interactions and filtering

## Backend Components

### DialpadClient Class (`direct_dialpad.py`)

The core component that handles communication with the Dialpad API.

#### Key Features:

- **Authentication**: Uses API key to authenticate with Dialpad
- **Agent Management**: Maintains a mapping of agent names to Dialpad user IDs
- **Pagination**: Implements proper cursor-based pagination for API calls
- **Call Relationship Tracking**: Sophisticated logic to track call relationships across agents
- **Call Status Determination**: Logic to determine if a call was completed, missed, or handled by another agent
- **Data Formatting**: Formats call data for frontend display

#### Important Methods:

1. **`get_calls(agent_id, limit, started_after, started_before)`**:
   - Fetches calls for a specific agent with filtering options
   - Handles pagination through the Dialpad API
   - Returns a list of raw call objects

2. **`get_all_agent_calls(started_after, started_before)`**:
   - Fetches calls for all agents with date filtering
   - Processes calls to establish relationships between them
   - Implements call deduplication based on entry_point_call_id
   - Tracks which agent answered each call and which other agents were affected
   - Returns a consolidated list of call objects with relationship data

3. **`format_call_for_display(call)`**:
   - Formats a raw call object for frontend display
   - Extracts customer information, duration, timestamps, etc.
   - Adds detailed status information for calls (e.g., which agent answered a call that was routed to multiple agents)
   - Returns a formatted call object ready for display

### Flask Routes (`app.py`)

1. **Dashboard Route**: `/dialpad-dashboard` (GET)
   - Renders the dashboard template with agent list and default date range (current day)
   - Initializes the DialpadClient
   - Does not load call data on initial page load

2. **API Endpoint**: `/api/dialpad-calls` (POST)
   - Accepts filter parameters: date_from, date_to, agent_id, call_type, call_status
   - Converts date strings to Unix timestamps (milliseconds)
   - Uses DialpadClient to fetch and process call data
   - Applies additional filtering based on request parameters
   - Returns formatted call data as JSON

## Frontend Components

### Dashboard Template (`dialpad_dashboard.html`)

The main UI template for the dashboard with the following sections:

1. **Dashboard Header**: Title and branding
2. **Filter Section**:
   - Date range inputs (from/to)
   - Agent selection dropdown
   - Call type filter (inbound/outbound)
   - Call status filter (completed/missed/handled elsewhere)
   - Apply filters button
3. **Summary Statistics**:
   - Total calls
   - Inbound calls count
   - Outbound calls count
   - Missed calls count
   - Average call duration
4. **Call Data Table**:
   - Date/Time
   - Agent
   - Customer
   - Phone
   - Call Type
   - Duration
   - Status (with color coding)
   - Recording link

### JavaScript Functionality

The dashboard includes client-side JavaScript for the following features:

1. **Data Loading**:
   - Fetches call data from the backend API endpoint (`/api/dialpad-calls`)
   - Handles loading states and errors
   - Displays "No data" message when appropriate

2. **Data Rendering**:
   - Renders call data in the table with proper formatting
   - Displays status details for calls that were handled elsewhere or missed
   - Creates recording links for calls that have recordings

3. **Summary Statistics**:
   - Calculates and displays summary statistics based on the loaded data
   - Updates when filters are applied

4. **Date Handling**:
   - Sets default date range to the current day
   - Formats dates properly for API requests

## Call Status Types

The dashboard implements a sophisticated status system for calls:

1. **Completed**: Calls that were successfully answered by the agent
2. **Missed**: Calls that rang but were not answered by any agent
3. **Handled Elsewhere**: Calls that rang to the agent but were answered by another agent

For "Handled Elsewhere" calls, the dashboard shows additional details about which agent answered the call, including:
- The name of the agent who answered the call
- Information about other agents the call was routed to

For "Missed" calls, the dashboard shows:
- Information about which agents the call was routed to but missed by all

## CSS Styling (`dialpad-dashboard.css`)

The dashboard includes dedicated CSS for styling:

1. **Status Styling**:
   - Color coding for different call statuses (green for completed, red for missed, amber for handled elsewhere)
   - Styling for status details section

2. **Call Type Styling**:
   - Visual differentiation between inbound and outbound calls
   - Border indicators for call types

3. **Layout**:
   - Responsive design adaptations for different screen sizes
   - Card-based layout for clear separation of sections

4. **Interactive Elements**:
   - Hover effects for table rows
   - Button styling for actions
   - Loading indicators

## Data Flow

1. User loads the dashboard page (`/dialpad-dashboard`)
2. Flask serves the template with empty initial data
3. User selects filters and clicks "Apply Filters"
4. Frontend JavaScript sends a POST request to `/api/dialpad-calls` with filter parameters
5. Backend processes the request:
   - Initializes DialpadClient
   - Converts date strings to timestamps
   - Calls appropriate DialpadClient methods based on agent selection
   - Formats and filters the results
   - Returns JSON response
6. Frontend receives the response:
   - Updates the UI with call data
   - Calculates and displays summary statistics
   - Handles any error states

## Security Considerations

1. **API Key**: The Dialpad API key is stored on the server side and never exposed to the client
2. **Input Validation**: The backend validates and sanitizes all input parameters
3. **Error Handling**: Proper error handling in both frontend and backend prevents exposure of sensitive information

## Performance Considerations

1. **Pagination**: The dashboard implements proper pagination for API calls to Dialpad
2. **Filtering**: Much of the filtering is done on the server side to reduce data transfer
3. **Loading States**: Clear loading indicators show when data is being fetched
4. **Result Limiting**: The system caps the maximum number of calls that can be retrieved per agent (200) to prevent excessive API calls

## Troubleshooting

Common issues and solutions:

1. **No Call Data Appears**:
   - Verify date range is correct
   - Check if selected agent has any calls in the specified period
   - Confirm API key is valid and has proper permissions
   - Check browser console for JavaScript errors

2. **Missing Call Information**:
   - Some calls may not have all metadata (e.g., no recording URL or customer name)
   - External numbers may be used as fallback when contact information is unavailable

3. **API Rate Limiting**:
   - The dashboard caps calls per agent to avoid hitting Dialpad API rate limits
   - If experiencing rate limiting, try narrowing the date range or selecting specific agents

## Future Enhancements

Potential improvements for future versions:

1. **Call Tagging**: Add ability to tag calls with custom labels
2. **Advanced Filtering**: Add more filter options like call duration, time of day, etc.
3. **Bulk Actions**: Allow operations on multiple calls at once
4. **Data Export**: Add options to export call data in various formats
5. **Real-time Updates**: Implement auto-refresh to show new calls without manual refresh
6. **Call Analytics**: Add more detailed analytics and charts for call patterns

---

## Technical Reference

### API Endpoint: `/api/dialpad-calls`

**Request Parameters:**

```json
{
  "date_from": "YYYY-MM-DD",      // Start date for filtering calls
  "date_to": "YYYY-MM-DD",        // End date for filtering calls
  "agent_id": "string",           // Optional agent ID (or "all" for all agents)
  "call_type": "string",          // Optional: "inbound", "outbound", or "all"
  "call_status": "string"         // Optional: "completed", "missed", "handled_elsewhere", or "all"
}
```

**Response Format:**

```json
{
  "success": true,
  "calls": [
    {
      "call_id": "string",
      "agent_name": "string",
      "agent_id": "string",
      "customer_name": "string",
      "customer_phone": "string",
      "call_type": "string",      // "inbound" or "outbound"
      "duration": number,         // Call duration in minutes
      "datetime": "string",       // Formatted timestamp
      "status": "string",         // "completed", "missed", or "handled_elsewhere"
      "status_details": "string", // Additional status information
      "recording_url": "string"   // URL to call recording if available
    },
    // ...more calls
  ],
  "total_calls": number
}
```

**Error Response:**

```json
{
  "success": false,
  "error": "Error message"
}
```

### Dialpad API Integration

The dashboard integrates with the Dialpad API v2, specifically the `/v2/call` endpoint with the following parameters:

- `target_type=user` - To specify we're looking for calls for a specific user
- `target_id` - The Dialpad user ID of the agent
- `started_after` - Unix timestamp in milliseconds for the start date
- `started_before` - Unix timestamp in milliseconds for the end date
- `limit` - Maximum number of results per page (default: 50)
- `cursor` - For pagination (provided by the Dialpad API response)

For more details on the Dialpad API, refer to the [official Dialpad API documentation](https://developers.dialpad.com/reference/call_read).