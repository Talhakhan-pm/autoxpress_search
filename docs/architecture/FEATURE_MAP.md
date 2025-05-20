# AutoXpress Feature Map

This document provides a comprehensive mapping between features, their code files, and API endpoints. It serves as a reference to quickly locate all components related to a specific feature when making changes or debugging.

## 1. Search & Field-Based Search

The core search functionality that powers product discovery through natural language or structured field inputs.

### Files

**Backend**:
- `query_processor.py` - Main query processing and analysis
- `field_based_search.py` - Field-by-field search implementation

**Frontend**:
- `static/js/field-based-search.js` - Form handling and API integration
- `static/js/field-autocomplete.js` - Field autocompletion functionality
- `static/js/ai-analysis-formatter.js` - Formats AI analysis results

**Templates**:
- `templates/index.html` - Contains search form and results tabs

### API Routes in `app.py`

- `/api/parse-query` - Parses natural language queries
- `/api/analyze` - Analyzes queries and generates search terms
- `/api/search-products` - Searches for products using optimized terms
- `/api/search` - General search API
- `/api/field-search` - Field-by-field search processing

### Documentation

- `docs/features/FIELD_BASED_SEARCH.md` - Detailed feature documentation

## 2. VIN Lookup

Allows users to decode Vehicle Identification Numbers (VINs) to get detailed vehicle information.

### Files

**Backend**:
- `vehicle_validation.py` - VIN validation and processing

**Frontend**:
- `static/js/modules/vin-decoder.js` - Handles VIN form and results

**Templates**:
- `templates/index.html` - Contains VIN lookup tab

### API Routes in `app.py`

- `/api/vin-decode` - API endpoint for VIN decoding
- `/vin-decode` - Server-side rendering for VIN results

### Documentation

- VIN lookup is covered in the core architecture docs but lacks a dedicated feature doc

## 3. Location Lookup

Enables users to look up location information based on ZIP codes and save frequently used locations.

### Files

**Backend**:
- No specific backend (uses external Zippopotam.us API directly)

**Frontend**:
- `static/js/location-lookup.js` - ZIP lookup and location management
- `static/css/variables.css` - Contains styling variables used by location feature

**Templates**:
- `templates/index.html` - Contains location lookup tab

### API Routes

- No specific backend routes (uses external API directly from frontend)

### Documentation

- `docs/features/LOCATION_LOOKUP.md` - Detailed feature documentation

## 4. Part Number Search

Allows searching for specific part numbers with detailed information and compatible vehicles.

### Files

**Backend**:
- Part of `app.py` (part number processing functions)

**Frontend**:
- `static/js/part-number-search.js` - Handles search form and requests
- `static/js/part-number-display.js` - Formats and displays part information

**Templates**:
- `templates/index.html` - Contains part number search tab

### API Routes in `app.py`

- `/api/part-number-search` - Searches for part number information
- `/api/part-number-listings` - Gets product listings for a part number

### Documentation

- `docs/features/PART_NUMBER_AI_ENHANCEMENT.md` - Detailed feature documentation

## 5. Chat Assistant

An AI-powered chat interface that provides automotive expertise and part recommendations.

### Files

**Backend**:
- `chatbot_handler.py` - Processes chat messages and generates responses
- `query_templates.py` - Templates for different query types

**Frontend**:
- `static/js/chatbot.js` - Chat interface and message handling
- `static/css/chatbot.css` - Chat interface styling

**Templates**:
- `templates/index.html` - Contains chat assistant tab

### API Routes in `app.py`

- `/api/chat` - Processes chat messages and returns AI responses

### Documentation

- Currently lacks dedicated feature documentation
- Brief descriptions in `docs/architecture/ARCHITECTURE.md` and `docs/architecture/UI_STRUCTURE.md`

## 6. Payment Link

Allows agents to generate payment links through Stripe for customer transactions.

### Files

**Backend**:
- Part of `app.py` (payment link generation functions)

**Frontend**:
- `static/js/payment-link.js` - Form handling and link generation
- `static/css/payment-link.css` - Payment link feature styling

**Templates**:
- `templates/index.html` - Contains payment link tab

### API Routes in `app.py`

- `/api/create-payment-link` - Creates Stripe payment links

### Documentation

- `docs/features/PAYMENT_LINK.md` - Detailed feature documentation

## 7. Dialpad Dashboard

Provides analytics and management for call data from the Dialpad API.

### Files

**Backend**:
- `direct_dialpad.py` - Dialpad API integration and call data processing

**Frontend**:
- `static/js/dialpad-dashboard.js` - Dashboard interface and data display
- `static/css/dialpad-dashboard.css` - Dashboard styling

**Templates**:
- `templates/dialpad_dashboard.html` - Dedicated dashboard page

### API Routes in `app.py`

- `/dialpad-dashboard` - Dashboard page (GET)
- `/api/dialpad-calls` - API for call data retrieval (POST)

### Documentation

- `docs/features/DIALPAD_DASHBOARD.md` - Detailed feature documentation

## 8. Favorites Management

Allows users to save and manage favorite products across sessions.

### Files

**Backend**:
- No specific backend (client-side only)

**Frontend**:
- `static/js/favorites-actions.js` - Favorites management logic
- `static/css/favorites-actions.css` - Favorites UI styling

**Templates**:
- `templates/index.html` - Contains favorites tab

### API Routes

- No specific backend routes (client-side localStorage only)

### Documentation

- Favorites is covered in the core architecture docs but lacks a dedicated feature doc

## Global Components

These components serve multiple features across the application.

### Files

**Backend**:
- `app.py` - Main Flask application and route definitions

**Frontend**:
- `static/js/main.js` - Core application logic
- `static/js/updated_products.js` - Product display system
- `static/js/enhanced-filtering.js` - Product filtering system
- `static/css/styles.css` - Core application styling
- `static/css/small-screen-aggressive.css` - Mobile responsiveness styles

**Templates**:
- `templates/index.html` - Main application template
- `templates/callbacks.html` - Callbacks page
- `templates/orders.html` - Orders page

### API Routes in `app.py`

- `/` - Main application page (GET, POST)
- `/callbacks.html` - Callbacks page (GET)
- `/orders.html` - Orders page (GET)

### Documentation

- `docs/architecture/ARCHITECTURE.md` - Overall architecture documentation
- `docs/architecture/UI_STRUCTURE.md` - UI structure documentation
- `docs/api/API_REFERENCE.md` - API reference documentation