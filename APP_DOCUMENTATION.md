# AutoXpress Application Documentation

## Overview
This is a comprehensive Flask-based automotive parts search and management application. The app integrates multiple APIs and services to provide intelligent part searching, AI-powered assistance, payment processing, and call management through Dialpad.

## Application Structure

### Core Dependencies (Lines 1-21)
- **Flask**: Main web framework
- **OpenAI**: AI-powered analysis and chat functionality
- **SerpAPI**: Product search across eBay and Google Shopping
- **Stripe**: Payment link generation
- **Dialpad**: Call management and dashboard
- **NHTSA API**: VIN decoding

### Configuration & Setup (Lines 22-54)
- **Environment Variables**: Loaded via `python-dotenv`
- **API Keys**: OpenAI, SerpAPI, Stripe, Dialpad tokens
- **Flask App**: Static folder configuration and secret key
- **Validation**: API key format checking and error handling

---

## Core Functions & Utilities

### Query Processing (Lines 56-194)
**Location**: `clean_query()` function
**Purpose**: Enhanced query cleaning and optimization for automotive parts searches
- Handles structured data from field-based searches
- Normalizes part terminology (e.g., "engine wire harness" → "engine wiring harness oem")
- Manages year/make/model extraction and formatting
- Extensive part terms dictionary with 50+ automotive components

### VIN Decoding (Lines 196-227)
**Location**: `decode_vin()` function with LRU caching
**Purpose**: Decode Vehicle Identification Numbers using NHTSA API
- **Endpoint**: `https://vpic.nhtsa.dot.gov/api/vehicles/decodevinvaluesextended/{vin}`
- **Caching**: 500 VIN cache for performance
- **Error Handling**: Comprehensive request and parsing error management

### SerpAPI Integration (Lines 229-366)
**Location**: `get_serpapi_cached()`, cache management functions
**Purpose**: Cached API requests to SerpAPI for eBay and Google Shopping
- **Cache TTL**: 5 minutes with automatic cleanup
- **eBay Categories**: Mapped automotive part categories (33637, 33564, etc.)
- **Concurrent Requests**: ThreadPoolExecutor for new/used product searches

---

## Product Search System

### eBay Search Processing (Lines 368-985)
**Location**: `get_ebay_serpapi_results()`, `process_ebay_results()`
**Key Features**:
- **Vehicle Info Extraction**: Year, make, model, part, position parsing
- **Smart Filtering**: 
  - Position term mapping (left/right, front/rear variations)
  - Part term variations (caliper, strut, rotor, etc.)
  - Make alternatives (Mercedes-Benz/Mercedes/Benz)
- **Relevance Scoring**: Priority scoring system for exact matches
- **Debug Logging**: Extensive filtering statistics

### Google Shopping Integration (Lines 987-1176)
**Location**: `get_google_shopping_results()`, `process_google_shopping_results()`
**Features**:
- **Category Filtering**: Product category mapping for auto parts
- **Specialized Queries**: Enhanced queries for bumpers and engines
- **Link Validation**: Multiple fallback strategies for product links
- **Less Restrictive Filtering**: 25% term matching for broader results

### Vehicle Information Extraction (Lines 405-479)
**Location**: `extract_vehicle_info_from_query()`
**Purpose**: Standardized vehicle data extraction
- **Structured Data Priority**: Field-based search data takes precedence
- **Query Processor Fallback**: Uses `EnhancedQueryProcessor` for text analysis
- **Position Handling**: Front/rear/left/right qualifier extraction
- **Confidence Scoring**: Returns confidence level (90 for structured, variable for parsed)

---

## Flask Routes & API Endpoints

### Main Application Route (Lines 1178-1183)
```
GET/POST / - Main application page
```

### Part Number Search System (Lines 1319-1756)
```
POST /api/part-number-search - AI-enhanced part number lookup
POST /api/part-number-listings - Product listings for part numbers
```
**Features**:
- **AI Integration**: GPT-4o for part information extraction
- **Search URL Generation**: Google, Amazon, eBay, RockAuto links
- **Alternative Numbers**: Cross-reference part number generation
- **Manufacturer Guessing**: Pattern-based manufacturer identification

### Query Analysis & Search (Lines 1803-2796)
```
POST /api/parse-query - Parse queries into structured vehicle data
POST /api/analyze - GPT-4 powered query analysis and optimization
POST /api/search-products - Main product search with pagination
POST /api/search - Legacy combined analyze + search endpoint
```

**Advanced Features**:
- **AI Analysis**: GPT-4 for vehicle validation and fitment guidance
- **Price Range Analysis**: Market pricing insights
- **Search Optimization**: Multiple search strategies and fallbacks
- **Specialized Handling**: Enhanced logic for engines, bumpers, transmissions

### VIN Services (Lines 2799-2859)
```
POST /api/vin-decode - Modern VIN decoding API
POST /vin-decode - Legacy VIN decoding (backward compatibility)
```

### Chat & AI Services (Lines 2861-2865)
```
POST /api/chat - AI-powered chat responses (delegates to chatbot_handler.py)
```

### Payment Integration (Lines 2867-2930)
```
POST /api/create-payment-link - Stripe payment link creation
```
**Features**:
- **Product Creation**: Dynamic Stripe product and price creation
- **Address Collection**: US-only billing and shipping
- **Payment Methods**: Card payments only (Link disabled)

### Dialpad Dashboard (Lines 2934-3084)
```
GET /dialpad-dashboard - Call management dashboard
POST /api/dialpad-calls - Filtered call data retrieval
```
**Features**:
- **Date Filtering**: Configurable date ranges with UTC timestamp conversion
- **Agent Filtering**: Specific agent or all agents
- **Call Type/Status Filtering**: Inbound/outbound, completed/missed calls
- **Real-time Data**: Live call data from Dialpad API

---

## Key Helper Functions

### Input Sanitization (Lines 1768-1800)
**Location**: `sanitize_input()` function
**Security Features**:
- HTML tag removal
- XSS prevention through entity encoding
- Character whitelist (alphanumeric + safe punctuation)
- Control character removal

### Product Enhancement & Scoring (Lines 2071-2732)
**Location**: `prioritize_exact_part_matches()`, relevance scoring functions
**Features**:
- **Match Classification**: Exact complete, exact, related, other
- **Priority Scoring**: 150 for complete engines, 100 for exact complete matches
- **Special Handling**: Engine-specific indicators and part classifications

### Alternative Generation (Lines 1712-1755)
**Location**: `generate_alternative_numbers()`, `generate_compatibility_data()`
**Purpose**: Create plausible alternative part numbers and vehicle compatibility

---

## Application Configuration

### Environment Variables Required
```
OPENAI_API_KEY - GPT-4 access for AI features
SERPAPI_KEY - Product search across platforms  
STRIPE_SECRET_KEY - Payment processing
DIALPAD_API_TOKEN - Call management
FLASK_SECRET_KEY - Session security (optional, auto-generated)
```

### Port Configuration (Lines 3088-3090)
- **Default Port**: 5040
- **Host**: 0.0.0.0 (all interfaces)
- **Environment Override**: PORT environment variable

---

## Integration Points

### External APIs
1. **OpenAI GPT-4o/GPT-4-turbo**: Part analysis, chat responses, query optimization
2. **SerpAPI**: eBay and Google Shopping product searches
3. **NHTSA**: VIN decoding and vehicle validation
4. **Stripe**: Payment link generation
5. **Dialpad**: Call data retrieval and management

### Internal Modules
1. **chatbot_handler.py**: AI chat processing and conversation management
2. **query_processor.py**: Enhanced query parsing and vehicle extraction
3. **query_templates.py**: Message template matching
4. **vehicle_validation.py**: Vehicle information validation
5. **direct_dialpad.py**: Dialpad API client implementation

---

## Performance Optimizations

### Caching Strategy
- **VIN Decoding**: LRU cache (500 entries, permanent)
- **SerpAPI Results**: TTL cache (5 minutes, 200 entries max)
- **Concurrent Processing**: ThreadPoolExecutor for parallel API calls

### Search Optimization
- **Multiple Strategies**: Primary + fallback search terms
- **Smart Filtering**: Balanced relevance vs. coverage
- **Deduplication**: Title-based similarity matching
- **Pagination**: 24 items per page default

This application serves as a comprehensive automotive parts search platform with AI-enhanced capabilities, payment processing, and call management features.