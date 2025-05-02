# AutoXpress Architecture Documentation

## Overview

AutoXpress is an application for searching and displaying auto parts from multiple sources. The application has a layered architecture with clear separation of concerns between different modules.

## Phase 2: Performance & Unification Implementation

Phase 2 focused on optimizing performance, implementing caching, adding lazy loading, and unifying the data model across the application.

### Module Structure

The application is organized into the following module types:

1. **Utility Modules** (No dependencies)
   - `formatPrice.js`: Price formatting utilities
   - `error-handler.js`: Centralized error handling
   - `performance-monitor.js`: Performance measurement and monitoring
   - `lazy-loader.js`: Image lazy loading

2. **Feature Modules** (May depend on utility modules)
   - `product-data-manager.js`: Data normalization and caching
   - `product-badges.js`: Badge rendering and management
   - `product-ranking.js`: Product relevance scoring
   - `product-renderer.js`: Product rendering utilities
   - `vin-decoder.js`: VIN lookup functionality
   - `image-modal.js`: Image preview functionality

3. **Core Application** (Depends on both utility and feature modules)
   - `updated_products.js`: Main product display logic
   - `main.js`: Core application functionality
   - `favorites-actions.js`: Favorites management
   - `field-autocomplete.js`: Search field autocomplete
   - `filter-manager.js`: Product filtering functionality
   - `location-lookup.js`: Location-based filtering

### Data Flow

1. User inputs search criteria
2. App sends search query to backend
3. Results are processed through `product-data-manager.js`
4. Products are ranked by `product-ranking.js`
5. UI is updated via `updated_products.js`
6. Images are lazy-loaded by `lazy-loader.js`

### Performance Optimizations

#### Caching
- Client-side caching in localStorage via `product-data-manager.js`
- In-memory caching for frequent operations
- Cache invalidation strategy based on TTL (time-to-live)

#### Lazy Loading
- Images are loaded only when they come into view
- Implemented using IntersectionObserver in `lazy-loader.js`
- Fallback mechanisms for older browsers

#### Performance Monitoring
- Key operations are measured using `performance-monitor.js`
- Timing for product rendering, filtering, and sorting
- Data collection for optimization insights

### Error Handling

The application implements a centralized error handling system in `error-handler.js` that:
- Captures and logs errors
- Provides user-friendly error messages
- Attempts to recover from common errors
- Records error statistics for troubleshooting

### Module Dependencies

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Utility Modules │     │ Feature Modules │     │  Core Application│
│                 │     │                 │     │                 │
│ formatPrice     │     │ product-data-   │     │ updated_products│
│ error-handler   │     │ manager         │     │ main            │
│ performance-    │◄────┤ product-badges  │◄────┤ favorites-      │
│ monitor         │     │ product-ranking │     │ actions         │
│ lazy-loader     │     │ vin-decoder     │     │ filter-manager  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Event System

The application uses a custom event system to communicate between modules:
- `productsDisplayed`: Fired when products are rendered
- `filters-changed`: Fired when filter criteria change
- `app-error`: Fired when an error occurs
- `favorites-changed`: Fired when favorites are modified

## Unified Data Model

Product data is normalized to a consistent format with the following fields:

```javascript
{
  id: String,             // Unique identifier
  title: String,          // Product title
  brand: String,          // Brand name
  partType: String,       // Type of part
  condition: String,      // Condition (new, used, refurbished)
  price: Number,          // Price as number
  originalPrice: Number,  // Original price if available
  shipping: String,       // Shipping info
  image: String,          // Primary image URL
  fullImage: String,      // High-res image URL
  link: String,           // Link to product
  source: String,         // Source (eBay, Google, etc.)
  
  // Ranking data (added by ProductRanking module)
  relevanceScore: Number, 
  relevanceCategory: String,
  primaryBadge: Object,
  secondaryBadges: Array,
  
  // Extra metadata
  metadata: Object        // Additional source-specific data
}
```

## Future Enhancements

1. **Testing Infrastructure**: Add comprehensive unit and integration tests
2. **Performance Dashboard**: Add UI for monitoring performance metrics
3. **Enhanced Caching**: Implement more sophisticated cache invalidation
4. **Offline Support**: Add service workers for offline functionality
5. **Analytics**: Add user behavior tracking and analysis