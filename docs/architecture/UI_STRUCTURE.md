# AutoXpress UI Structure

This document provides an overview of the AutoXpress application user interface structure, focusing on tab organization and navigation.

## Main Navigation Structure

The application has a primary navigation bar with:
- **Home** - Returns to the main application interface
- **Favorites** - Quick access to saved favorites 
- **Agent Activity** - Redirects to the Dialpad Dashboard page

## Main Tab Structure

The main application interface (`index.html`) is organized into the following tabs:

### 1. Search Tab (Default Active)
- Multi-field search form (year, make, model, part, engine)
- Single field search option (togglable)
- Field auto-complete functionality
- Key file: `field-based-search.js`

### 2. VIN Lookup Tab
- 17-character VIN input field
- Decodes vehicle information
- Key file: `modules/vin-decoder.js`

### 3. Favorites Tab
- Displays saved favorite parts
- Export and clear options
- Key file: `favorites-actions.js`

### 4. Location Tab
- ZIP code lookup functionality
- Displays city, state, county, timezone, area code
- Saved locations management
- Key file: `location-lookup.js`

### 5. Part Number Tab
- Direct part number search
- Options for including OEM terms, alternative part numbers
- AI-enhanced part information display
- Search history section
- Key files: `part-number-search.js`, `part-number-display.js` 

### 6. Chat Assistant Tab
- Interactive chatbot interface
- Quick response options
- Support for automotive part inquiries
- Key file: `chatbot.js`

### 7. Payment Link Tab
- Form to create payment links via Stripe
- Product name, description, amount fields
- Generates shareable payment links
- Key file: `payment-link.js`

## Results Display Tabs

After a search operation is completed, results are displayed using another set of tabs:

### 1. Analysis Tab
- Shows AI analysis of search query
- Presents extracted vehicle information
- Highlights identified parts
- Key file: `ai-analysis-formatter.js`

### 2. Products Tab
- Displays matching products 
- Filtering and sorting options
- Multiple view modes (grid, list, compact)
- Key file: `updated_products.js`

### 3. Vehicle Tab (for VIN results)
- Shows detailed vehicle information
- Specifications and compatibility information
- Appears only after VIN search

## Dialpad Dashboard (Separate Page)

The Dialpad Dashboard (`dialpad_dashboard.html`) has its own dedicated interface:
- Filters: date range, agent, call type, status
- Summary statistics section
- Call data table with status indicators
- Key file: `dialpad-dashboard.js`

## UI Design Patterns

The application employs consistent UI patterns throughout:
1. Bootstrap tabs for main feature organization
2. Card-based layouts for content grouping 
3. Responsive design with mobile optimization
4. Consistent icon usage across features
5. Common action patterns (save, clear, refresh)
6. Modal dialogs for expanded content (image preview)
7. Detailed filters for search refinement

## Tab Interaction Flow

```
┌──────────────────┐       ┌──────────────────┐        ┌──────────────────┐
│                  │       │                  │        │                  │
│  Feature Tab     │─────► │  API Processing  │──────► │  Results Tabs    │
│  (Search/VIN/etc)│       │                  │        │                  │
│                  │       │                  │        │                  │
└──────────────────┘       └──────────────────┘        └──────────────────┘
```

1. User selects and interacts with a feature tab
2. Input is validated and processed
3. API requests are made and data is returned
4. Results are displayed in the appropriate results tabs

## Tab State Management

Each tab maintains its own state:
- Search histories are preserved per-tab
- Form field values persist during tab switching
- Result sets are maintained until a new search is performed
- Global favorites are accessible across tabs

## Mobile Responsiveness

On smaller screens:
- Tabs transform into a more compact navigation
- Form elements stack vertically 
- Result displays adjust for smaller viewports
- Key file: `small-screen-aggressive.css`