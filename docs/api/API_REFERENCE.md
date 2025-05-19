# AutoXpress API Reference

This document provides a comprehensive reference for all API endpoints available in the AutoXpress application.

## Core API Endpoints

### 1. Query Processing and Analysis

#### 1.1 Parse Query

**Endpoint:** `/api/parse-query`  
**Method:** POST  
**Description:** Parses a search query and extracts vehicle and part information with confidence score.

**Request Parameters:**
```
prompt: string          // Natural language query to parse
structured_data: object // Optional structured data from multi-field form
```

**Response:**
```json
{
  "success": true,
  "parsed_data": {
    "vehicle_info": {
      "year": "2018",
      "make": "toyota",
      "model": "camry",
      "engine_specs": {
        "displacement": "2.5L",
        "type": "inline-4"
      },
      "position": ["front"],
      "part": "brake pads"
    },
    "confidence": 85
  }
}
```

#### 1.2 Analyze Query

**Endpoint:** `/api/analyze`  
**Method:** POST  
**Description:** Performs detailed analysis of a query, extracts information, and generates search terms.

**Request Parameters:**
```
prompt: string          // Natural language query to analyze
structured_data: object // Optional structured data from multi-field form
parsed_data: object     // Optional previously parsed data
local_pickup: boolean   // Optional flag for local pickup preference
```

**Response:**
```json
{
  "success": true,
  "questions": "HTML formatted analysis of the request",
  "search_terms": ["toyota camry brake pads 2018", "2018 camry front brakes"],
  "processed_locally": true,
  "vehicle_info": {
    "year": "2018",
    "make": "toyota",
    "model": "camry",
    "engine_specs": {
      "displacement": "2.5L",
      "type": "inline-4"
    },
    "position": ["front"],
    "part": "brake pads"
  }
}
```

### 2. Product Search

#### 2.1 Search Products

**Endpoint:** `/api/search-products`  
**Method:** POST  
**Description:** Searches for products using optimized search terms.

**Request Parameters:**
```
search_term: string     // Primary search term
original_query: string  // Original user query for context
structured_data: object // Optional structured data from form
local_pickup: boolean   // Optional flag for local pickup preference
```

**Response:**
```json
{
  "success": true,
  "listings": [
    {
      "title": "2018 Toyota Camry Front Brake Pads OEM",
      "price": "$49.99",
      "condition": "New",
      "shipping": "Free shipping",
      "image": "https://example.com/image.jpg",
      "link": "https://example.com/product",
      "source": "eBay"
    }
  ],
  "total_listings": 1
}
```

#### 2.2 Field-Based Search

**Endpoint:** `/api/field-search`  
**Method:** POST  
**Description:** Processes field-by-field search input to generate targeted search terms.

**Request Parameters:**
```
year: string     // Vehicle year
make: string     // Vehicle make
model: string    // Vehicle model
part: string     // Part name
engine: string   // Optional engine specifications
```

**Response:**
```json
{
  "success": true,
  "search_terms": ["toyota camry brake pads 2018", "2018 camry front brakes"],
  "analysis": "HTML formatted analysis of the fields",
  "vehicle_info": {
    "year": "2018",
    "make": "toyota",
    "model": "camry",
    "part": "brake pads",
    "engine_specs": {
      "displacement": "2.5L",
      "type": "inline-4"
    }
  }
}
```

### 3. VIN Decoding

#### 3.1 VIN Decode

**Endpoint:** `/api/vin-decode`  
**Method:** POST  
**Description:** Decodes a Vehicle Identification Number to extract detailed vehicle information.

**Request Parameters:**
```
vin: string      // 17-character Vehicle Identification Number
```

**Response:**
```json
{
  "success": true,
  "vehicle_info": {
    "year": "2018",
    "make": "Toyota",
    "model": "Camry",
    "trim": "LE",
    "engine": "2.5L I4",
    "transmission": "Automatic",
    "drive_type": "FWD",
    "body_style": "Sedan",
    "exterior_color": "Silver",
    "fuel_type": "Gasoline",
    "manufacturer": "Toyota Motor Corporation"
  },
  "original_vin": "4T1BF1FK5JU123456"
}
```

#### 3.2 VIN Decode (Render)

**Endpoint:** `/vin-decode`  
**Method:** POST  
**Description:** Server-side processing of VIN decode request, returns HTML page with results.

**Request Parameters:**
```
vin: string      // 17-character Vehicle Identification Number
```

**Response:**
- HTML page with VIN decode results rendered

### 4. Part Number Search

#### 4.1 Part Number Search

**Endpoint:** `/api/part-number-search`  
**Method:** POST  
**Description:** Searches for detailed information about a specific part number.

**Request Parameters:**
```
part_number: string     // Part number to search for
include_oem: boolean    // Whether to include OEM terms in search
include_alt_numbers: boolean  // Whether to look for alternative part numbers
exclude_wholesalers: boolean  // Whether to exclude wholesaler results
```

**Response:**
```json
{
  "success": true,
  "part_info": {
    "part_number": "NGK 7090",
    "part_type": "Spark Plug",
    "manufacturer": "NGK",
    "description": "Laser Iridium Spark Plug",
    "compatibility": [
      "2018 Toyota Camry 2.5L",
      "2019 Toyota RAV4 2.5L"
    ],
    "alternative_numbers": [
      "DENSO 5617",
      "CHAMPION 9007"
    ]
  },
  "ai_enhanced": true
}
```

#### 4.2 Part Number Listings

**Endpoint:** `/api/part-number-listings`  
**Method:** POST  
**Description:** Searches for product listings matching a specific part number.

**Request Parameters:**
```
part_number: string     // Part number to search for
```

**Response:**
```json
{
  "success": true,
  "listings": [
    {
      "title": "NGK 7090 Laser Iridium Spark Plug - Set of 4",
      "price": "$32.99",
      "condition": "New",
      "shipping": "Free shipping",
      "image": "https://example.com/image.jpg",
      "link": "https://example.com/product",
      "source": "eBay"
    }
  ],
  "total_listings": 1
}
```

### 5. Chat Functionality

#### 5.1 Chat API

**Endpoint:** `/api/chat`  
**Method:** POST  
**Description:** Handles chat messages and generates AI-powered responses.

**Request Parameters:**
```
message: string         // User's chat message
chat_history: array     // Optional array of previous messages
```

**Response:**
```json
{
  "success": true,
  "response": "I'd recommend OEM brake pads for your 2018 Toyota Camry. They typically cost between $50-80 and should last around 30,000-50,000 miles depending on your driving habits.",
  "suggested_next_questions": [
    "Where can I find OEM brake pads?",
    "How difficult is it to replace brake pads?"
  ]
}
```

### 6. Payment Link Generation

#### 6.1 Create Payment Link

**Endpoint:** `/api/create-payment-link`  
**Method:** POST  
**Description:** Creates a Stripe payment link for a specified product and amount.

**Request Parameters:**
```json
{
  "agent_input": {
    "product_name": "2018 Toyota Camry Brake Pads",
    "product_description": "OEM brake pads for front wheels",
    "amount": 89.99,
    "currency": "usd"
  }
}
```

**Response:**
```json
{
  "success": true,
  "payment_link": "https://buy.stripe.com/example_payment_link",
  "product_details": {
    "name": "2018 Toyota Camry Brake Pads",
    "price": 89.99,
    "currency": "usd",
    "description": "OEM brake pads for front wheels"
  }
}
```

### 7. Dialpad Dashboard

#### 7.1 Dialpad Calls

**Endpoint:** `/api/dialpad-calls`  
**Method:** POST  
**Description:** Fetches call data from Dialpad API with filtering options.

**Request Parameters:**
```json
{
  "date_from": "2024-05-10",
  "date_to": "2024-05-18",
  "agent_id": "5503393985740800",  // Optional, "all" for all agents
  "call_type": "inbound",          // Optional, "all" for all types
  "call_status": "completed"       // Optional, "all" for all statuses
}
```

**Response:**
```json
{
  "success": true,
  "calls": [
    {
      "call_id": "5678901234",
      "agent_name": "John Smith",
      "agent_id": "5503393985740800",
      "customer_name": "Jane Doe",
      "customer_phone": "+1-555-123-4567",
      "call_type": "inbound",
      "duration": 5.3,
      "datetime": "2024-05-15 14:30:22",
      "status": "completed",
      "status_details": "",
      "recording_url": "https://dialpad.com/recording/123"
    }
  ],
  "total_calls": 1
}
```

## Page Routes

### 1. Main Application Pages

#### 1.1 Home Page

**Endpoint:** `/`  
**Method:** GET, POST  
**Description:** Main application page with search form and product results.

#### 1.2 Callbacks Page

**Endpoint:** `/callbacks.html`  
**Method:** GET  
**Description:** Callback management page.

#### 1.3 Orders Page

**Endpoint:** `/orders.html`  
**Method:** GET  
**Description:** Order management page.

### 2. Dashboard Pages

#### 2.1 Dialpad Dashboard

**Endpoint:** `/dialpad-dashboard`  
**Method:** GET  
**Description:** Dashboard for viewing and analyzing agent call activity.

**Response:**
- HTML page with Dialpad dashboard interface
- Includes filters for date range, agent, call type, and status
- Renders call data table and summary statistics

## Error Responses

All API endpoints follow a consistent error response format:

```json
{
  "success": false,
  "error": "Descriptive error message"
}
```

Common error status codes:
- **400 Bad Request**: Invalid input parameters
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server-side processing error

## Request Authentication

The AutoXpress API endpoints do not require authentication for local development and testing. In a production environment, appropriate authentication would be implemented.

## Usage Limits

- **Call Rate Limits**: The Dialpad API has rate limits that are respected by the application
- **Search Depth**: Product searches are limited to optimize performance
- **Payment Links**: Maximum amount is limited to $4,000

## Technical Requirements

- All date parameters should be in ISO format (YYYY-MM-DD)
- VIN must be a valid 17-character Vehicle Identification Number
- ZIP codes must be valid 5-digit US postal codes
- Part numbers should not contain special characters beyond hyphens and spaces