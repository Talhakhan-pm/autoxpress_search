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
Include field-autocomplete.js in your frontend code
Create the necessary HTML elements for the search interface

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
search_terms = result["search_terms"]