# AutoXpress Smart Assistant

A comprehensive auto parts search and management platform with advanced AI-powered features.

## Overview

AutoXpress Smart Assistant is an intelligent web application designed to help users find the right auto parts for their vehicles and manage automotive service operations. The system uses advanced query processing to understand natural language requests and structured form data to accurately identify vehicle make, model, year, and part information.

The application combines multiple intelligent systems including:
- Natural language query processing for auto parts
- Field-based structured search
- Part number lookup and compatibility checking
- VIN decoding and vehicle identification
- Agent call activity dashboard
- Payment link generation
- Chatbot assistant for customer support

## Key Features

### Search & Parts Discovery
- **Natural Language Processing**: Understand queries like "2015 Ford F-150 headlight assembly"
- **Structured Data Handling**: Process form data with separate fields for make, model, year, and part
- **Vehicle Information Extraction**: Identify make, model, year, and engine specifications
- **Part Terminology Mapping**: Map common part names to standard terminology
- **Search Term Generation**: Create optimized search terms for finding parts
- **Multi-field Autocomplete**: Provide suggestions for vehicle makes, models, and years
- **Part Number Search**: Look up parts by their part number with AI-enhanced results
- **VIN Decoding**: Extract complete vehicle information from a VIN

### User Experience
- **Multiple View Modes**: Grid, list, and compact views for product listings
- **Enhanced Filtering**: Filter products by condition, type, shipping, and source
- **Image Previews**: View larger images of products
- **Product Favoriting**: Save and manage favorite products
- **Chat Assistant**: Get help and support through an integrated chatbot
- **Location Lookup**: Find shipping information based on ZIP code
- **Payment Link Generation**: Create payment links for transactions

### Management & Analytics
- **Dialpad Dashboard**: View and analyze agent call activity with filtering and statistics
- **Call Status Tracking**: Track completed, missed, and handled elsewhere calls
- **Call Relationship Tracking**: See how calls are routed between agents
- **API Integrations**: Seamless integration with Dialpad, Stripe, and other services

## Components

### Core Search Engine
1. **Query Processor** (`query_processor.py`)
   - Extracts vehicle information (make, model, year, engine specs)
   - Identifies part names and positions (front, rear, driver side, etc.)
   - Maps common terms to standardized part descriptions
   - Categorizes parts into systems (engine, transmission, brakes, etc.)
   - Generates optimized search terms for the inventory

2. **Field-Based Search** (`field_based_search.py`)
   - Processes structured field input (year, make, model, part, engine)
   - Creates targeted search queries based on available fields
   - Implements a more direct and effective search strategy

### Frontend Modules
1. **Product Display & Rendering**
   - `updated_products.js`: Primary product display with configurable views
   - `product-renderer.js`: Alternative rendering system with highlight support
   - `modules/image-modal.js`: Image preview functionality

2. **User Interface Components**
   - `field-autocomplete.js`: Enhanced autocomplete for vehicle fields
   - `enhanced-filtering.js`: Product filtering capabilities
   - `favorites-actions.js`: Favorite product management
   - `part-number-display.js`: Part number results display
   - `payment-link.js`: Payment link generation UI
   - `chatbot.js`: Customer support chat interface

3. **Utility Modules**
   - `user-context.js`: User preference and context management
   - `modules/vin-decoder.js`: VIN decoding functionality
   - `ai-analysis-formatter.js`: Formatting AI analysis results
   - `location-lookup.js`: ZIP code location services

### API & Backend Services
1. **Flask Routes** (`app.py`)
   - `/api/analyze`: Query analysis and search term generation
   - `/api/search-products`: Product search with filtering options
   - `/api/part-number-search`: Part number lookup and details
   - `/api/parse-query`: Real-time query parsing and extraction
   - `/api/vin-decode`: VIN decoding and vehicle information
   - `/api/chat`: Chatbot conversation endpoint
   - `/api/create-payment-link`: Payment link generation with Stripe
   - `/api/dialpad-calls`: Agent call activity data with filtering
   - `/dialpad-dashboard`: Dashboard for analyzing agent call activities

2. **Dialpad Integration** (`direct_dialpad.py`)
   - Connects to Dialpad API for call data
   - Processes call information and relationships
   - Tracks call routing between agents
   - Provides detailed call status information

## Recent Enhancements

### Vehicle Data Expansion
- Added complete US market vehicle makes and models
- Enhanced make-model relationships and synonym mapping
- Added support for legacy and discontinued models

### Part Data Expansion
- Added over 80 new part terms for better part recognition
- Enhanced existing part categories with more comprehensive terms
- Added new part categories including:
  - Chassis/Frame components
  - HVAC systems
  - Lighting components
  - Trim/appearance items
  - Belt/pulley systems

### Part Number Search AI Enhancement
- Added OpenAI and SerpAPI integration for real data
- Extracts structured part information from search results
- Provides vehicle compatibility information
- Identifies alternative part numbers
- Improved part type and manufacturer recognition

### Dialpad Dashboard Implementation
- Added call activity tracking for agents
- Implemented call relationship detection
- Enhanced call status determination
- Added filtering by date, agent, call type, and status
- Included summary statistics with call analytics

### UI Improvements
- Added multiple view modes for product listings
- Enhanced filtering capabilities
- Improved image preview functionality
- Added favorites system with notes
- Implemented responsive design for all screen sizes

## Implementation

### Requirements
- Modern web browser with JavaScript support
- Server with Python 3.8+ for backend processing
- API keys for external services:
  - Dialpad API key
  - OpenAI API key (optional, for AI enhancements)
  - SerpAPI key (optional, for part number search)
  - Stripe API key (optional, for payment links)

### Setup
1. Install required Python packages: `pip install -r requirements.txt`
2. Configure environment variables for API keys in `.env` file
3. Run the application: `python app.py`
4. Access the application at http://localhost:5040

### Basic Usage

```python
# Backend
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
search_terms = result["search_terms"]
```

## Documentation

For more detailed information, see these documentation files:

- [ARCHITECTURE.md](ARCHITECTURE.md) - Detailed system architecture
- [FIELD_BASED_SEARCH.md](FIELD_BASED_SEARCH.md) - Field-based search implementation
- [IMPROVEMENT_GUIDE.md](IMPROVEMENT_GUIDE.md) - Guidelines for safe improvements
- [REFACTORING.md](REFACTORING.md) - Product rendering refactoring details
- [PART_NUMBER_AI_ENHANCEMENT.md](part_number_ai_enhancement.md) - Part number search AI enhancement
- [DIALPAD_DASHBOARD.md](DIALPAD_DASHBOARD.md) - Dialpad call dashboard documentation