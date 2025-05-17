AutoXpress Smart Assistant
A smart auto parts finder application that helps users search for the correct parts for their vehicles.
Overview
AutoXpress Smart Assistant is an intelligent search system designed to help users find the right auto parts for their vehicles. The system uses advanced query processing to understand natural language requests and structured form data to accurately identify vehicle make, model, year, and part information.
The core of the system is the EnhancedQueryProcessor which analyzes user queries, extracts vehicle and part information, and generates optimized search terms to find the right parts in the inventory.
Key Features

Natural Language Processing: Understand queries like "2015 Ford F-150 headlight assembly"
Structured Data Handling: Process form data with separate fields for make, model, year, and part
Vehicle Information Extraction: Identify make, model, year, and engine specifications
Part Terminology Mapping: Map common part names to standard terminology
Search Term Generation: Create optimized search terms for finding parts
Multi-field Autocomplete: Provide suggestions for vehicle makes, models, and years
Dialpad Integration: Track and analyze agent call activity for better customer service

Components
1. Query Processor (query_processor.py)
The core of the system that processes queries and extracts structured information:

Extracts vehicle information (make, model, year, engine specs)
Identifies part names and positions (front, rear, driver side, etc.)
Maps common terms to standardized part descriptions
Categorizes parts into systems (engine, transmission, brakes, etc.)
Generates optimized search terms for the inventory

2. Field Autocomplete (field-autocomplete.js)
Provides an enhanced autocomplete experience for the multi-field search form:

Make, model, year, and part field suggestions
Dependency handling between fields (model depends on make)
Category-based suggestion display
Fuzzy matching for typo tolerance

3. Dialpad Integration (dialpad_api.py, dialpad_routes.py)
Integrates with the Dialpad API to track and analyze agent call activity:

Fetches call data from Dialpad's API for the company department
Processes call records to extract key metrics (duration, type, status)
Calculates agent performance metrics (efficiency, call volume, etc.)
Displays agent activity in a user-friendly dashboard
Provides filtering by date range for historical analysis

Recent Enhancements
Vehicle Data Expansion

Added complete US market vehicle makes and models
Enhanced make-model relationships and synonym mapping
Added support for legacy and discontinued models

Part Data Expansion

Added over 80 new part terms for better part recognition
Enhanced existing part categories with more comprehensive terms
Added new part categories including:

Chassis/Frame components
HVAC systems
Lighting components
Trim/appearance items
Belt/pulley systems

Dialpad Integration

Implemented real-time call tracking via Dialpad's API
Added agent activity dashboard for call performance monitoring
Included metrics for call efficiency, volume, and type distribution
Developed date range filtering for historical data analysis
Optimized API usage with pagination and caching


Query Processing Improvements

Enhanced year range recognition for better compatibility matching
Improved confidence scoring for extracted information
Better handling of multi-word part names

Implementation
Requirements

Modern web browser with JavaScript support
Server with Python for backend processing

Setup

Include query_processor.py in your backend code
Include field-autocomplete.js and field-based-search.js in your frontend code
Create the necessary HTML elements for the search interface
Set up your Dialpad API token in the environment or .env file:
```
DIALPAD_API_TOKEN=your_api_token
```

For detailed documentation on the Dialpad integration, see [DIALPAD_INTEGRATION.md](DIALPAD_INTEGRATION.md)

## Field-Based Search

This application includes a field-based search approach that builds targeted search queries from individual fields (year, make, model, part, engine) rather than trying to normalize a single search term.

Key benefits of this approach:
- More accurate part matching by prioritizing user-entered field values
- Flexible search patterns that work even with partial information
- Better handling of engine-specific parts when engine information is provided
- Search terms are already structured, requiring less normalization

For detailed documentation on the field-based search implementation, see [FIELD_BASED_SEARCH.md](FIELD_BASED_SEARCH.md).

Basic Usage
python# Backend
from query_processor import EnhancedQueryProcessor

# Create processor instance
processor = EnhancedQueryProcessor()

# Process a natural language query
result = processor.process_query("2019 Toyota Camry brake pads")

# Or process structured form data
form_data = {
    "year": "2019",
    "make": "Toyota",
    "model": "Camry",
    "part": "brake pads"
}
result = processor.process_structured_data(form_data)

# Get the structured information and search terms
vehicle_info = result["vehicle_info"]
search_terms = result["search_terms"]# autoxpress_search
