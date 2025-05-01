# Product Modules Documentation

This folder contains several JavaScript modules that provide a unified system for product ranking and badge display.

## Core Modules

### 1. ProductRanking (`/modules/product-ranking.js`)

This module provides a sophisticated algorithm for ranking products based on multiple factors:

- **Year matching**: Exact year or compatible range
- **Part type relevance**: Exact part, major component, standard part, or accessory
- **Brand tier**: Premium, standard, or unknown
- **Condition**: New, refurbished, used
- **Shipping**: Free or paid

Each product is assigned a relevance score and categorized as high, medium, or low relevance.

### 2. ProductBadges (`/modules/product-badges.js`)

The badge module provides a consistent visual system for displaying product attributes:

- **Primary badges**: A main badge showing the most important attribute (Best Match, Exact Year, OEM, etc.)
- **Secondary badges**: Smaller tags showing additional attributes (Free Shipping, New, Premium Brand)
- **Relevance highlighting**: Color-coded left borders for high and medium relevance products

Each badge type has defined styling including background color, text color, and an appropriate icon.

### 3. ProductRenderer (`/modules/product-renderer.js`)

This renderer is responsible for creating product card HTML with badge support. It handles:

- Creating formatted product cards with all relevant information
- Applying relevance highlighting to cards
- Displaying primary and secondary badges

### 4. ProductDisplayAdapter (`/modules/product-display-adapter.js`)

This adapter integrates the ranking and badge system with the existing product display:

- Processes products through the ranking system
- Updates existing product cards with badges and highlighting
- Handles dynamic product updates when tabs change

## CSS Styling

Badge styles are defined in `/static/css/badges.css` which includes:

- Primary badge styling with proper positioning
- Secondary badge/tag styles for consistent appearance
- Color definitions for different badge types
- Relevance highlighting with colored left borders

## Testing

Unit tests for these modules are available in the `/modules/tests/` directory:

- `test-product-ranking.js`: Tests for the ranking algorithm
- `test-product-badges.js`: Tests for badge rendering
- `test-product-renderer.js`: Tests for the product renderer

A visual test page is available at `/static/js/test-data/test-product-badges.html` which shows examples of all badge types in different view modes.

## Integration

These modules are integrated with the existing product display system. The key integration points are:

1. Product ranking is applied when products are initially loaded
2. Badges are rendered when product cards are created
3. The adapter ensures badges are updated when tab changes occur
4. Badge styling is applied consistently through the badge CSS file

## Usage Example

```javascript
// Get vehicle information
const vehicleInfo = {
  make: 'Toyota',
  model: 'Camry',
  year: '2018',
  part: 'Brake Pads'
};

// Process products through ranking system
const rankedProducts = ProductRanking.rankProducts(products, vehicleInfo);

// Display products with badges
ProductRenderer.renderProductList(rankedProducts, container);
```

This system ensures a consistent, unified approach to product relevance and badges throughout the application.