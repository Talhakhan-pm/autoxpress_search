# Dialpad Integration

This document provides an overview of the Dialpad API integration for AutoXpress, explaining how the system fetches call data, tracks agent activity, and displays this information in the UI.

## Overview

The integration uses Dialpad's API to fetch call records for the AutoXpress department and display agent performance metrics on a dashboard. The system processes this data to provide insights on agent activity, call types, duration, and status.

## API Integration

### Authentication

The integration uses a Dialpad API token for authentication, which is stored in the environment:

```
DIALPAD_API_TOKEN=<your_api_token>
```

### Key Endpoints Used

1. **Department Calls API**
   - Endpoint: `https://dialpad.com/api/v2/call`
   - Parameters:
     - `target_id`: The department ID
     - `target_type`: "department"
     - `started_after`: Timestamp for filtering calls by start date
     - `started_before`: Timestamp for filtering calls by end date
     - `apikey`: Your API token

2. **Department Operators API**
   - Endpoint: `https://dialpad.com/api/v2/departments/{department_id}/operators`
   - Used to get the list of agents in the department

## Data Processing

The system processes Dialpad API data in several steps:

1. **API Data Fetching**: Calls are retrieved from the Dialpad API with pagination support to handle large volumes of data.

2. **Call Data Processing**: Raw call data is processed to extract and format key information such as:
   - Call type (inbound/outbound)
   - Agent handling the call
   - Call duration
   - Call status (completed/missed)
   - Customer information

3. **Agent Activity Metrics**: The system calculates metrics for each agent including:
   - Total calls handled
   - Inbound vs. outbound call distribution
   - Average call duration
   - Call status distribution (completed vs. missed)

4. **Data Storage**: Processed call data and agent metrics are stored in the database for quick retrieval and historical analysis.

## Database Schema

The system uses two main models for Dialpad data:

1. **CallRecord**: Stores individual call records with fields including:
   - call_type (inbound/outbound)
   - date and time
   - agent information
   - customer information
   - call duration and status

2. **AgentActivity**: Stores aggregated agent metrics by date:
   - total_calls, inbound_calls, outbound_calls
   - missed_calls, completed_calls
   - total_duration, avg_duration
   - calls_by_day for historical tracking

## UI Components

The UI displays Dialpad data through several components:

1. **Stats Cards**: Shows overall metrics for the department:
   - Inbound calls count
   - Outbound calls count
   - Missed calls count
   - Total calls count

2. **Agent Activity Cards**: Displays individual agent performance:
   - Agent name
   - Total calls handled
   - Efficiency (percentage of completed calls)
   - Call type distribution
   - Average call duration

3. **Call Tables**: Lists individual call records with filtering options:
   - Inbound/outbound tabs
   - Date range filters
   - Agent filters
   - Status filters
   - Search functionality

## Implementation Details

### Performance Considerations

1. **API Pagination**: The system handles pagination to fetch large volumes of call data without timeouts.

2. **Configurable Timeouts**: API requests have configurable timeouts (default 60 seconds) to accommodate slower responses.

3. **Date Range Filtering**: Users can select date ranges (Today, Last 3 days, Last 7 days, Last 14 days) to balance data volume and loading times.

### API Rate Limiting

The Dialpad API has rate limits, so the implementation includes features to manage this:

1. **Caching Mechanism**: Agent information is cached to reduce API calls.
2. **Limited Page Fetching**: The system can be configured to limit the number of pages fetched to avoid excessive API usage.

## Key Files

- `dialpad_api.py`: Core API interaction class for fetching and processing Dialpad data
- `dialpad_routes.py`: Flask routes that serve Dialpad data to the UI
- `models.py`: Database models for storing call records and agent activity
- `templates/dialpad_calls.html`: UI template for displaying call data and agent activity

## Usage Notes

1. **API Token**: The Dialpad API token must be set in the environment or .env file.

2. **Department ID**: The system is configured for department ID "4869792674824192".

3. **Data Freshness**: The system fetches real-time data from Dialpad when requested, but also stores processed data for faster subsequent access.

4. **Long-Running Requests**: Some API calls may take 20-60 seconds for large departments with many calls.

## Troubleshooting

### Common Issues

1. **API Timeouts**: If the API takes too long to respond, try:
   - Reducing the date range (e.g., "Today" instead of "Last 14 days")
   - Increasing the timeout setting in `dialpad_api.py`

2. **Missing Agent Data**: If agent activity doesn't appear:
   - Check that the agents are correctly associated with the department in Dialpad
   - Verify the API token has sufficient permissions

3. **Database Connection**: If database errors occur:
   - Ensure the database file exists and is writable
   - Run `python models.py` to initialize the database schema if needed

## Future Enhancements

Potential improvements to the Dialpad integration:

1. **Real-time Updates**: Implement webhooks to receive call events in real-time instead of polling.

2. **Advanced Analytics**: Add more sophisticated analysis of call patterns, peak times, etc.

3. **Agent Performance Scoring**: Implement scoring algorithms for agent performance.

4. **Scheduled Reports**: Add functionality to generate and email periodic reports.

## API Response Format Reference

### Call Record Format

```json
{
  "call_id": "5782764944539648",
  "contact": {
    "email": "",
    "id": "5784965655216128",
    "name": "Example Customer",
    "phone": "+15127700269",
    "type": "local"
  },
  "date_ended": "1747503699031",
  "date_started": "1747503688095",
  "direction": "inbound",
  "duration": 10936.422,
  "target": {
    "email": "agent@example.com",
    "id": "5503393985740800",
    "name": "Agent Name",
    "phone": "+18583265696",
    "type": "user"
  }
}
```

### Operator Format

```json
{
  "company_id": "5311371869962240",
  "display_name": "Agent Name",
  "emails": ["agent@example.com"],
  "first_name": "Agent",
  "group_details": [
    {
      "group_id": "4869792674824192",
      "group_type": "department",
      "role": "operator"
    }
  ],
  "id": "5925466191249408",
  "phone_numbers": ["+12522830626"]
}
```