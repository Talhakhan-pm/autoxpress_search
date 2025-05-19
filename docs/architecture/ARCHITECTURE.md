# AutoXpress Architecture Documentation

This document provides a comprehensive overview of the AutoXpress application architecture, detailing all major components, their interactions, and design patterns.

## System Architecture

AutoXpress follows a client-server architecture with a Flask backend and a JavaScript-heavy frontend. The system is organized into several functional modules that work together to provide a seamless user experience.

### High-Level Architecture

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│                 │      │                 │      │  External APIs  │
│    Frontend     │◄────►│     Backend     │◄────►│  - Dialpad API  │
│   (Browser JS)  │      │  (Flask/Python) │      │  - Stripe API   │
│                 │      │                 │      │  - ZIP API      │
└─────────────────┘      └─────────────────┘      └─────────────────┘
```

## Backend Components

### 1. Flask Application (`app.py`)

The main entry point and controller for the application, handling:
- HTTP route definitions
- Request processing
- Response formatting
- Integration of all backend services

Key routes include:
- `/`: Main application page
- `/api/analyze`: Query analysis endpoint
- `/api/search-products`: Product search endpoint
- `/api/vin-decode`: VIN decoding endpoint
- `/api/part-number-search`: Part number lookup endpoint
- `/api/chat`: Chatbot conversation endpoint
- `/api/create-payment-link`: Payment link generation endpoint
- `/api/dialpad-calls`: Call data retrieval endpoint
- `/dialpad-dashboard`: Dialpad dashboard page

### 2. Query Processing System

#### 2.1 Query Processor (`query_processor.py`)

Core information extraction and query understanding:
- Vehicle information extraction (make, model, year)
- Part terminology mapping
- Position identification (front, rear, driver-side, etc.)
- Confidence scoring
- Search term generation

#### 2.2 Field-Based Search (`field_based_search.py`)

Handles structured field inputs:
- Processes individual field data
- Generates optimized search terms
- Prioritizes search strategies based on available fields

### 3. External API Integrations

#### 3.1 Dialpad Integration (`direct_dialpad.py`)

Manages communication with the Dialpad API:
- API authentication
- Call data retrieval
- Advanced call relationship tracking
- Call status determination
- Data formatting for display

#### 3.2 Chatbot Handler (`chatbot_handler.py`)

Processes chat interactions:
- Message context management
- Response generation
- Question suggestion
- Input sanitization

### 4. Vehicle Validation (`vehicle_validation.py`)

Handles VIN and vehicle data validation:
- VIN format verification
- Checksum validation
- Vehicle data extraction
- Year/make/model compatibility checking

## Frontend Components

### 1. Core Application

#### 1.1 Main Application (`main.js`)

Coordinates the overall application flow:
- Form submission handling
- API communication
- UI updates
- Event coordination
- Global state management

#### 1.2 Search Processing

- `field-based-search.js`: Handles multi-field search interactions
- `field-autocomplete.js`: Provides field suggestions and completion
- `ai-analysis-formatter.js`: Formats AI analysis results for display

### 2. Product Display System

#### 2.1 Product Rendering

- `updated_products.js`: Primary product display system with configurable views (grid, list, compact)
- `product-renderer.js`: Alternative rendering system with badge and highlighting support
- `modules/image-modal.js`: Image preview functionality

#### 2.2 Filtering System

- `enhanced-filtering.js`: Advanced product filtering capabilities
- Condition/type/shipping/source filtering options

### 3. Feature-Specific Modules

#### 3.1 VIN Decoder (`modules/vin-decoder.js`)

Handles VIN lookup and display:
- Form validation
- API communication
- Result formatting
- Error handling

#### 3.2 Location Lookup (`location-lookup.js`)

ZIP code-based location services:
- ZIP validation
- API integration with Zippopotam.us
- Location data display
- Saved locations management

#### 3.3 Payment Link Generation (`payment-link.js`)

Stripe payment link creation:
- Form handling
- Input validation
- API communication
- Success/error handling
- Link sharing capabilities

#### 3.4 Chatbot Integration (`chatbot.js`)

Chat interface implementation:
- Message sending/receiving
- Chat history management
- Quick response buttons
- UI animations

#### 3.5 Favorites Management (`favorites-actions.js`)

Product favorites system:
- Save/remove favorites
- Notes management
- Local storage persistence
- List display and management

#### 3.6 Part Number Search (`part-number-search.js` & `part-number-display.js`)

Part number lookup functionality:
- Form handling
- Search options management
- Result display
- Part compatibility visualization

### 4. Utility Modules

- `user-context.js`: User preference and context management
- `modules/product-renderer.js`: Product card generation utilities

## Data Flow

### 1. Product Search Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ User inputs │     │  Frontend   │     │   Backend   │     │   Product   │
│  query or   │────►│ processes & │────►│  analyzes   │────►│   display   │
│   fields    │     │ sends to API│     │ & searches  │     │  & filtering│
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

1. **Input Processing**:
   - User enters search query or fills in fields
   - Frontend validates and prepares the data
   - Real-time query parsing provides feedback

2. **API Request**:
   - AJAX request sent to appropriate endpoint
   - Query parameters or JSON payload included

3. **Backend Processing**:
   - Query analysis and information extraction
   - Search term generation
   - Product search execution

4. **Result Display**:
   - Frontend receives and processes response
   - Products rendered in selected view mode
   - Filtering options applied
   - Summary information displayed

### 2. Dialpad Dashboard Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ User selects│     │ Frontend JS │     │ Flask API   │     │  Call data  │
│   filters   │────►│ sends AJAX  │────►│ processes & │────►│ display &   │
│ & timeframe │     │   request   │     │ calls API   │     │ statistics  │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

1. **Filter Selection**:
   - User selects date range, agent, call type, status
   - Frontend prepares the filtering parameters

2. **API Request**:
   - AJAX request sent to `/api/dialpad-calls`
   - Includes all filter parameters

3. **Backend Processing**:
   - Converts date strings to timestamps
   - Initializes Dialpad client
   - Fetches appropriate call data
   - Processes call relationships
   - Applies additional filtering

4. **Result Display**:
   - Renders call data in table format
   - Calculates and displays summary statistics
   - Applies status-specific styling
   - Shows relationship details for calls

### 3. Payment Link Generation Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│User provides│     │ Frontend JS │     │ Flask API   │     │ Payment link│
│product info │────►│ validates & │────►│ calls Stripe│────►│ display &   │
│  & amount   │     │ sends data  │     │    API      │     │sharing tools│
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

1. **Input Collection**:
   - User enters product name, description, amount
   - Frontend validates the input data

2. **API Request**:
   - AJAX request sent to `/api/create-payment-link`
   - Includes product details and amount

3. **Backend Processing**:
   - Creates product in Stripe
   - Creates price point
   - Configures payment link options
   - Generates payment link

4. **Result Display**:
   - Shows success message with link details
   - Provides copy/share/open functionality
   - Displays product summary

## State Management

### 1. Client-Side State

#### 1.1 Product Listings State

- `currentListings`: Current product listings array
- `sortMode`: Current sorting mode (relevance/price)
- `queryParseData`: Information extracted from the query

#### 1.2 Location State

- `currentLocation`: Current ZIP code location data
- `savedLocations`: Array of saved locations in localStorage

#### 1.3 Favorites State

- `favorites`: Object containing saved product favorites
- Persisted in `localStorage` under `autoxpress_favorites`

#### 1.4 User Context

- Saved filters and preferences
- View mode selection
- Recent searches

### 2. Server-Side State

The application is largely stateless on the server side, with session management limited to:
- Dialpad API authentication state
- Backend service instantiation

## Important Functions

### Frontend Core Functions

#### Product Display (`updated_products.js`)

- `setProducts(products)`: Initialize product display
- `applyFilters()`: Apply current filters to products
- `displayProductsPage()`: Render current page of products
- `createGridViewProduct()` / `createListViewProduct()`: Create product HTML

#### Search Processing (`main.js`)

- `constructQueryFromFields()`: Build query from multiple fields
- `parseQuery()`: Send query to API for parsing
- `updateQueryFeedback()`: Update UI with extracted info

#### Dialpad Dashboard (inline JS)

- `loadCallData()`: Fetch filtered call data from API
- `renderCallData(calls)`: Display calls in table format
- `updateSummaryStats(calls)`: Calculate and show statistics

#### Payment Link (`payment-link.js`)

- `createPaymentLink()`: Handle form submission and API call
- `showSuccess(data)`: Display success with link options
- `copyPaymentLink(url)`: Copy link to clipboard

#### Location Lookup (`location-lookup.js`)

- `lookupZipCode(zipCode)`: Fetch location data from API
- `updateLocationDisplay(data)`: Show location information
- `saveCurrentLocation()`: Save location to localStorage

### Backend Core Functions

#### Query Processor (`query_processor.py`)

- `process_query(query)`: Process natural language query
- `extract_vehicle_info(query)`: Extract year/make/model
- `generate_search_terms(vehicle_info, part)`: Create search terms

#### Dialpad Client (`direct_dialpad.py`)

- `get_calls(agent_id, started_after, started_before)`: Fetch agent calls
- `get_all_agent_calls(started_after, started_before)`: Fetch all agents' calls
- `format_call_for_display(call)`: Format call for frontend display

## Critical Dependencies

1. **DOM Structure**:
   - Product cards must follow expected HTML structure
   - Filter checkboxes must have data-filter and data-value attributes

2. **Event Handling**:
   - `attachFavoriteButtonListeners()`: Must be called after product rendering
   - `attachImagePreviewListeners()`: Must be called after product rendering

3. **Global Functions**:
   - `generateProductId()`: Creates unique product identifiers
   - `loadFavorites()`: Loads favorites from localStorage

4. **API Integrations**:
   - Dialpad API: Required for call dashboard functionality
   - Stripe API: Required for payment link generation
   - Zippopotam.us API: Used for ZIP code lookup

## Event System

The application uses custom events for communication between components:

- **productsDisplayed**: Triggered after products are rendered to the DOM
- **Filter change events**: Triggered when filter checkboxes are toggled
- **shown.bs.tab**: Bootstrap tab activation events

## Template Rendering

The application uses a combination of server-side and client-side rendering:

1. **Server-Side Rendering**:
   - Main application structure and layout
   - Initial page loading
   - Dialpad dashboard template

2. **Client-Side Rendering**:
   - Product listings and cards
   - Search result formatting
   - Call data display
   - Location information
   - Payment link results

## CSS Structure

The styling system is organized into several specialized files:

- `styles.css`: Core application styling
- `variables.css`: Design system variables
- `favorites-actions.css`: Favorites functionality styling
- `chatbot.css`: Chat interface styling
- `dialpad-dashboard.css`: Dialpad dashboard specific styling
- `payment-link.css`: Payment link feature styling
- `small-screen-aggressive.css`: Responsive design optimizations

## Known Issues and Considerations

1. **Duplicate Rendering Logic**:
   - Code for rendering products exists in multiple places
   - Changes to product cards must be made in both systems

2. **Event Timing**:
   - The order of events is critical for proper functionality
   - Filters rely on 'productsDisplayed' event to apply correctly

3. **Global State**:
   - The application relies on global state in window.productDisplay
   - Conflicts or race conditions can occur with concurrent operations

4. **API Rate Limits**:
   - Dialpad API has rate limits that must be respected
   - The dashboard caps calls per agent to avoid hitting limits

## Best Practices for Modifications

1. **Test Both Rendering Paths**:
   - Always test both the updated_products.js and product-renderer.js paths
   - Ensure changes work regardless of which system is used

2. **Preserve Event Flow**:
   - Maintain the 'productsDisplayed' event triggering
   - Keep event listeners in the same order

3. **Use Defensive Coding**:
   - Add null checks for DOM elements
   - Add null checks for product properties
   - Use fallbacks for missing values

4. **Incremental Changes**:
   - Make small, isolated changes
   - Test thoroughly after each change
   - Document any changes to the architecture

5. **API Integration Considerations**:
   - Keep API keys secure, never expose them to the frontend
   - Implement proper error handling for API failures
   - Consider rate limiting for external API calls