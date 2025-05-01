/**
 * Product Display Adapter
 * Connects the ranking and badge modules to the existing product display system
 */

const ProductDisplayAdapter = (function() {
  /**
   * Get current vehicle info from the UI
   * @returns {Object} Vehicle information
   */
  function getVehicleInfo() {
    return {
      make: document.getElementById('make-field')?.value || '',
      model: document.getElementById('model-field')?.value || '',
      year: document.getElementById('year-field')?.value || '',
      part: document.getElementById('part-field')?.value || ''
    };
  }
  
  /**
   * Process products through the ranking system
   * @param {Array} products - Raw product data
   * @returns {Array} Ranked products with badge data
   */
  function processProducts(products) {
    if (!products || !Array.isArray(products) || !products.length) {
      return [];
    }
    
    // Get current vehicle info for ranking
    const vehicleInfo = getVehicleInfo();
    
    // Use ranking module if available
    if (window.ProductRanking) {
      return window.ProductRanking.rankProducts(products, vehicleInfo);
    }
    
    // Otherwise return original products
    return products;
  }
  
  /**
   * Enhances the existing product display system
   * @param {Function} existingDisplayFn - The existing product display function
   * @returns {Function} Enhanced display function
   */
  function enhanceDisplayProducts(existingDisplayFn) {
    return function(products) {
      // Process products through ranking system
      const rankedProducts = processProducts(products);
      
      // Pass to existing function
      return existingDisplayFn(rankedProducts);
    };
  }
  
  /**
   * Initializes the adapter and connects it to existing systems
   */
  function initialize() {
    // Check if we have the original display function
    if (window.displayProducts) {
      // Store original function
      const originalDisplayProducts = window.displayProducts;
      
      // Replace with enhanced version
      window.displayProducts = enhanceDisplayProducts(originalDisplayProducts);
    }
    
    // Add badge styles to document if not already present
    if (!document.getElementById('badge-styles')) {
      const link = document.createElement('link');
      link.id = 'badge-styles';
      link.rel = 'stylesheet';
      link.href = '/static/css/badges.css';
      document.head.appendChild(link);
    }
    
    // Listen for product display event to apply badges to existing products
    document.addEventListener('productsDisplayed', updateExistingProductBadges);
  }
  
  /**
   * Updates badges on existing product cards in the DOM
   */
  function updateExistingProductBadges() {
    if (!window.ProductBadges) return;
    
    // Get all product cards
    const productCards = document.querySelectorAll('.product-card');
    
    productCards.forEach(card => {
      const productId = card.dataset.productId;
      if (!productId) return;
      
      // Find product data
      const product = findProductById(productId);
      if (!product) return;
      
      // Get next element after product source
      const sourceElement = card.querySelector('.product-source');
      if (!sourceElement) return;
      
      // Replace existing badge if any
      const existingBadge = card.querySelector('.product-primary-badge');
      if (existingBadge) {
        existingBadge.remove();
      }
      
      // Get badges HTML
      const badges = window.ProductBadges.renderBadges(product);
      
      // Skip creating primary badges since they're not being used
      
      // Add secondary badges to tags if present
      if (badges.secondary) {
        const tagsContainer = card.querySelector('.product-tags');
        if (tagsContainer) {
          // Clear ALL existing tags to prevent duplication with original tags
          tagsContainer.innerHTML = '';
          
          const tempDiv = document.createElement('div');
          tempDiv.innerHTML = badges.secondary;
          
          while (tempDiv.firstChild) {
            tagsContainer.appendChild(tempDiv.firstChild);
          }
        }
      }
      
      // Update relevance class
      if (product.relevanceScore) {
        card.classList.remove('product-relevance-high', 'product-relevance-medium');
        if (product.relevanceScore >= 80) {
          card.classList.add('product-relevance-high');
        } else if (product.relevanceScore >= 50) {
          card.classList.add('product-relevance-medium');
        }
      }
    });
  }
  
  /**
   * Find a product by its ID
   * @param {string} productId - Product ID to find
   * @returns {Object|null} Product data or null if not found
   */
  function findProductById(productId) {
    // Check in the product display config if available
    if (window.productDisplay && window.productDisplay.getProducts) {
      const products = window.productDisplay.getProducts();
      return products.find(p => generateProductId(p) === productId);
    }
    
    // Check in productConfig if available
    if (window.productConfig && window.productConfig.allProducts) {
      return window.productConfig.allProducts.find(p => generateProductId(p) === productId);
    }
    
    return null;
  }
  
  // Public API
  return {
    initialize,
    processProducts,
    updateExistingProductBadges
  };
})();

// Export globally
window.ProductDisplayAdapter = ProductDisplayAdapter;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  // Initialize the adapter with a slight delay to ensure all modules are loaded
  setTimeout(() => {
    ProductDisplayAdapter.initialize();
    console.log('ProductDisplayAdapter initialized');
  }, 100);
});

// Listen for tab changes to update badges
document.addEventListener('shown.bs.tab', function(event) {
  // If it's a product tab, update the badges
  if (event.target.id === 'products-tab') {
    // Give time for DOM to update
    setTimeout(() => {
      if (window.ProductDisplayAdapter && window.ProductDisplayAdapter.updateExistingProductBadges) {
        window.ProductDisplayAdapter.updateExistingProductBadges();
      }
    }, 50);
  }
});