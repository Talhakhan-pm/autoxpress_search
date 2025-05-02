/**
 * Source Integration Module
 * Integrates the new source adapter system with the existing application
 */

const SourceIntegration = (function() {
  /**
   * Initialize the source integration
   */
  function initialize() {
    // Listen for key events
    setupEventListeners();
    
    // Update the product search function to use SourceRegistry if available
    enhanceProductSearch();
    
    // Replace or enhance the original SourceManager
    enhanceSourceManager();
    
    console.log('Source integration initialized');
  }
  
  /**
   * Set up event listeners for integration
   */
  function setupEventListeners() {
    // Handle original product search form
    const searchForm = document.getElementById('search-form');
    if (searchForm) {
      // Intercept form submission
      searchForm.addEventListener('submit', handleSearchFormSubmit);
    }
    
    // Listen for source-retry events
    window.addEventListener('source-retry', handleSourceRetry);
    
    // Listen for products displayed to refresh source information
    document.addEventListener('productsDisplayed', handleProductsDisplayed);
  }
  
  /**
   * Enhance or replace the original source manager
   */
  function enhanceSourceManager() {
    // If the enhanced source manager exists, use it as the main source manager
    if (window.EnhancedSourceManager) {
      // Store original source manager if it exists
      const originalSourceManager = window.SourceManager;
      
      // Replace with enhanced version
      window.SourceManager = window.EnhancedSourceManager;
      
      // Copy over any missing methods from the original
      if (originalSourceManager) {
        for (const key in originalSourceManager) {
          if (!window.SourceManager[key] && typeof originalSourceManager[key] === 'function') {
            window.SourceManager[key] = originalSourceManager[key];
          }
        }
      }
      
      console.log('SourceManager enhanced with new source adapter capabilities');
    }
  }
  
  /**
   * Handle search form submission to use the new source system
   * @param {Event} event - Form submission event
   */
  function handleSearchFormSubmit(event) {
    // Only intercept if the source registry is available
    if (!window.SourceRegistry) return;
    
    // Get form data
    const searchQuery = document.getElementById('search-input')?.value;
    if (!searchQuery) return;
    
    // Get vehicle information
    const vehicleInfo = typeof window.productDisplay?.getVehicleInfo === 'function' ? 
                      window.productDisplay.getVehicleInfo() : {};
    
    // Prevent default form submission (optional, depending on how your app works)
    // event.preventDefault();
    
    // Perform search using the source registry
    performSearch(searchQuery, vehicleInfo);
  }
  
  /**
   * Enhance the existing product search function
   */
  function enhanceProductSearch() {
    // If the global search function is available, enhance it
    if (typeof window.searchProducts === 'function') {
      const originalSearchFn = window.searchProducts;
      
      // Replace with enhanced version
      window.searchProducts = function(query, options) {
        // If SourceRegistry is available, use it
        if (window.SourceRegistry) {
          return performSearch(query, options?.vehicleInfo || {});
        }
        
        // Otherwise fall back to original implementation
        return originalSearchFn(query, options);
      };
      
      console.log('Product search function enhanced with source adapter support');
    }
  }
  
  /**
   * Perform a search using the source registry
   * @param {string} query - Search query
   * @param {Object} vehicleInfo - Vehicle information
   * @returns {Promise<Array>} - Search results
   */
  async function performSearch(query, vehicleInfo = {}) {
    if (!window.SourceRegistry) {
      console.error('SourceRegistry not available for search');
      return [];
    }
    
    try {
      // Start performance monitoring if available
      let performanceMark = null;
      if (window.PerformanceMonitor) {
        performanceMark = window.PerformanceMonitor.startMeasure('searchProcessing', {
          query,
          vehicleInfo: Object.keys(vehicleInfo).join(',')
        });
      }
      
      // Search all sources
      const searchResults = await window.SourceRegistry.searchAllSources(query, {
        vehicleInfo
      });
      
      // Process the results if a data manager is available
      let processedResults = searchResults.results;
      
      if (window.ProductDataManager) {
        processedResults = window.ProductDataManager.processProducts(searchResults.results, {
          queryText: query,
          vehicleInfo
        });
      }
      
      // End performance monitoring
      if (performanceMark && window.PerformanceMonitor) {
        window.PerformanceMonitor.endMeasure(performanceMark, {
          success: true,
          resultCount: processedResults.length,
          sourceCount: Object.keys(searchResults.sourceResults).length
        });
      }
      
      // Set the products for display
      if (window.productDisplay && typeof window.productDisplay.setProducts === 'function') {
        window.productDisplay.setProducts(processedResults);
      }
      
      return processedResults;
    } catch (error) {
      console.error('Error performing search with source registry:', error);
      
      // Try to fall back to original search if available
      if (typeof window.originalSearchProducts === 'function') {
        return window.originalSearchProducts(query, { vehicleInfo });
      }
      
      return [];
    }
  }
  
  /**
   * Handle source retry events
   * @param {CustomEvent} event - Source retry event
   */
  function handleSourceRetry(event) {
    if (!event || !event.detail || !event.detail.source) return;
    
    const sourceId = event.detail.source;
    
    // Get the current search query
    const searchInput = document.getElementById('search-input');
    if (!searchInput || !searchInput.value) return;
    
    const query = searchInput.value;
    
    // Get vehicle information
    const vehicleInfo = typeof window.productDisplay?.getVehicleInfo === 'function' ? 
                      window.productDisplay.getVehicleInfo() : {};
    
    // Get the source from the registry
    if (!window.SourceRegistry) return;
    
    const source = window.SourceRegistry.getSource(sourceId);
    if (!source) return;
    
    // Perform search specifically for this source
    source.searchProducts(query, { vehicleInfo })
      .then(results => {
        if (!results || results.length === 0) {
          console.log(`Retry for source ${sourceId} returned no results`);
          return;
        }
        
        console.log(`Retry for source ${sourceId} returned ${results.length} results`);
        
        // Get existing products
        const existingProducts = window.productDisplay?.getProducts() || [];
        
        // Filter out existing products from this source
        const filteredProducts = existingProducts.filter(p => p.source !== sourceId);
        
        // Add the new results
        const combinedProducts = [...filteredProducts, ...results];
        
        // Set the products for display
        if (window.productDisplay && typeof window.productDisplay.setProducts === 'function') {
          window.productDisplay.setProducts(combinedProducts);
        }
      })
      .catch(error => {
        console.error(`Error retrying source ${sourceId}:`, error);
      });
  }
  
  /**
   * Handle products displayed event
   */
  function handleProductsDisplayed() {
    // Update source display
    if (window.SourceManager && typeof window.SourceManager.updateSourceDisplay === 'function') {
      window.SourceManager.updateSourceDisplay();
    }
  }
  
  // Initialize when DOM is loaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
  } else {
    initialize();
  }
  
  // Return public API
  return {
    performSearch
  };
})();

// Export globally
window.SourceIntegration = SourceIntegration;