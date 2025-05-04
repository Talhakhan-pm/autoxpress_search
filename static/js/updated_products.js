/**
 * Product display and filtering functionality
 * This file should be imported in the main HTML after main.js
 * 
 * UPDATED: Now exposes key functions globally for better code reuse
 */

// Creates a unique ID for a product
function generateProductId(product) {
  // Create a unique ID based on title and price, handling non-ASCII characters
  try {
    return btoa(product.title.substring(0, 30) + product.price).replace(/[^a-zA-Z0-9]/g, '');
  } catch (e) {
    // Handle non-ASCII characters by using encodeURIComponent
    const safeString = encodeURIComponent(product.title.substring(0, 30) + product.price);
    return btoa(safeString).replace(/[^a-zA-Z0-9]/g, '');
  }
}

// Load favorites from localStorage
function loadFavorites() {
  const favoritesJson = localStorage.getItem('autoxpress_favorites');
  return favoritesJson ? JSON.parse(favoritesJson) : {};
}

// Make these functions globally available
window.generateProductId = generateProductId;
window.loadFavorites = loadFavorites;

// Empty placeholder functions that do nothing - we don't need their actual functionality
function attachFavoriteButtonListeners() {
  // We don't actually need to implement this for the product display
  // The event handlers are attached in main.js
}

function attachImagePreviewListeners() {
  // We don't actually need to implement this for the product display  
  // The event handlers are attached in main.js
}

// Product display configuration
const productConfig = {
  currentView: 'grid', // grid, list, or compact
  currentSort: 'relevance', // relevance, price-low, price-high
  pageSize: 16, // Number of products to show initially
  activeFilters: {
    condition: [],
    shipping: [],
    source: ['eBay', 'Google Shopping'], // Default: show all sources
    relevance: []
  },
  allProducts: [], // All products returned from API
  displayedProducts: [], // Products currently shown (after filtering)
  currentPage: 1
};

// DOM Elements - initialize as null
let productsContainer = null;
let sortDropdown = null;
let viewDropdown = null;
let sortLabel = null;
let viewLabel = null;
let productTotalCount = null;
let productsCount = null;
let loadMoreBtn = null;
let loadMoreContainer = null;
let resetFiltersBtn = null;
let filterCheckboxes = null;
let productFilters = null;
let productTab = null;
let analysisTab = null;

// Function to initialize DOM references
function initializeDOMReferences() {
  productsContainer = document.getElementById('products-container');
  sortDropdown = document.getElementById('sortDropdown');
  viewDropdown = document.getElementById('viewDropdown');
  sortLabel = document.getElementById('sort-label');
  viewLabel = document.getElementById('view-label');
  productTotalCount = document.getElementById('product-total-count');
  productsCount = document.getElementById('products-count');
  loadMoreBtn = document.getElementById('load-more-btn');
  loadMoreContainer = document.getElementById('load-more-container');
  resetFiltersBtn = document.getElementById('resetFilters');
  filterCheckboxes = document.querySelectorAll('.filter-check');
  productFilters = document.querySelectorAll('[data-filter]');
  productTab = document.getElementById('products-tab');
  analysisTab = document.getElementById('analysis-tab');
}

// Debugging helper function to inspect products
function debugInspectProducts() {
  console.group("Product Filtering Debug Information");
  console.log("Total products:", productConfig.allProducts.length);
  
  // Check bestMatch property distribution
  const bestMatchCount = productConfig.allProducts.filter(p => p.bestMatch === true).length;
  console.log(`Products with bestMatch=true: ${bestMatchCount}`);
  
  // Check exact match property distribution
  const exactMatchCount = productConfig.allProducts.filter(p => p.isExactMatch === true).length;
  console.log(`Products with isExactMatch=true: ${exactMatchCount}`);
  
  // Check shipping property distribution
  const freeShippingCount = productConfig.allProducts.filter(p => 
    String(p.shipping || '').toLowerCase().includes('free')).length;
  console.log(`Products with free shipping: ${freeShippingCount}`);
  
  // Sample of shipping texts
  const shippingTexts = productConfig.allProducts
    .map(p => p.shipping)
    .filter((v, i, a) => a.indexOf(v) === i) // unique values
    .slice(0, 10); // first 10
  
  console.log("Sample of shipping text values:", shippingTexts);
  console.groupEnd();
}

// Initialize event listeners when the DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
  // Initialize DOM references
  initializeDOMReferences();

  // Skip initialization if essential elements don't exist
  if (!productsContainer) {
    console.warn("Products container not found - some functionality may be limited");
  }

  // Initialize view mode if possible
  if (productsContainer) {
    updateViewMode(productConfig.currentView);
  }

  // Event listener for sort options
  if (document.querySelectorAll('.sort-option').length > 0) {
    document.querySelectorAll('.sort-option').forEach(option => {
      option.addEventListener('click', function (e) {
        e.preventDefault();
        const sortValue = this.dataset.sort;
        productConfig.currentSort = sortValue;
        if (sortLabel) sortLabel.textContent = this.textContent;
        sortAndDisplayProducts();
      });
    });
  }

  // Event listener for view options
  if (document.querySelectorAll('.view-option').length > 0) {
    document.querySelectorAll('.view-option').forEach(option => {
      option.addEventListener('click', function (e) {
        e.preventDefault();
        const viewValue = this.dataset.view;
        updateViewMode(viewValue);
        if (viewLabel) viewLabel.textContent = this.textContent.trim();
      });
    });
  }

  // Event listener for filters
  if (filterCheckboxes && filterCheckboxes.length > 0) {
    filterCheckboxes.forEach(checkbox => {
      checkbox.addEventListener('change', function () {
        const filterType = this.dataset.filter;
        const filterValue = this.dataset.value;

        // Ensure the filter type exists in activeFilters
        if (!productConfig.activeFilters[filterType]) {
          productConfig.activeFilters[filterType] = [];
        }

        // Update active filters
        if (this.checked) {
          if (!productConfig.activeFilters[filterType].includes(filterValue)) {
            productConfig.activeFilters[filterType].push(filterValue);
          }
        } else {
          productConfig.activeFilters[filterType] = productConfig.activeFilters[filterType].filter(val => val !== filterValue);
        }

        // Reset to first page and apply filters
        productConfig.currentPage = 1;
        applyFilters();
      });
    });
  }

  // Event listener for reset filters
  if (resetFiltersBtn) {
    resetFiltersBtn.addEventListener('click', resetFilters);
  }

  // Event listener for load more button
  if (loadMoreBtn) {
    loadMoreBtn.addEventListener('click', loadMoreProducts);
  }

  // Event listener for product tab click
  if (productTab) {
    productTab.addEventListener('click', function () {
      // Make sure we're using relevance sorting when showing products tab
      if (productConfig.currentSort !== 'relevance') {
        productConfig.currentSort = 'relevance';
        if (sortLabel) sortLabel.textContent = 'Relevance';
      }
      
      // Re-render products when tab is shown
      if (productConfig.displayedProducts.length > 0) {
        sortAndDisplayProducts(); // Use sortAndDisplay instead of just displayProductsPage
      }
    });
  }
});

/**
 * Updates the view mode (grid, list, compact)
 */
function updateViewMode(viewMode) {
  if (!productsContainer) {
    console.error("Products container not found - cannot update view mode");
    return;
  }

  productConfig.currentView = viewMode;

  // Remove existing view classes
  productsContainer.classList.remove('grid-view', 'list-view', 'compact-view');

  // Add the new view class
  productsContainer.classList.add(viewMode + '-view');

  // Update column classes based on view mode
  if (productConfig.displayedProducts.length > 0) {
    displayProductsPage();
  }
}

/**
 * Resets all active filters
 */
function resetFilters() {
  // Reset filter state
  productConfig.activeFilters = {
    condition: [],
    shipping: [],
    source: ['eBay', 'Google Shopping'],
    relevance: []
  };

  // Reset checkbox UI
  if (filterCheckboxes && filterCheckboxes.length > 0) {
    filterCheckboxes.forEach(checkbox => {
      if (checkbox.dataset.filter === 'source') {
        checkbox.checked = true;
      } else {
        checkbox.checked = false;
      }
    });
  }

  // Reset to first page and apply filters
  productConfig.currentPage = 1;
  applyFilters();
}

/**
 * Applies current filters to the product list
 */
function applyFilters() {
  const allProducts = productConfig.allProducts;
  let filteredProducts = [...allProducts];

  // Apply condition filter
  if (productConfig.activeFilters.condition.length > 0) {
    filteredProducts = filteredProducts.filter(product => {
      if (productConfig.activeFilters.condition.includes('new')) {
        return product.condition.toLowerCase().includes('new');
      }
      return true;
    });
  }

  // Apply shipping filter
  if (productConfig.activeFilters.shipping.length > 0) {
    // Log shipping values for debugging purposes
    console.log("Filtering for free shipping among these values:", 
      filteredProducts.map(p => p.shipping).slice(0, 5)); // Show first 5 for brevity
      
    filteredProducts = filteredProducts.filter(product => {
      if (productConfig.activeFilters.shipping.includes('free')) {
        // More robust check for free shipping
        const shippingText = String(product.shipping || '').toLowerCase();
        // Debug log for shipping values
        if (shippingText.includes('free')) {
          console.log("Found free shipping item:", product.title);
        }
        return shippingText.includes('free');
      }
      return true;
    });
    
    // Log how many products matched the free shipping filter
    console.log(`Found ${filteredProducts.length} products with free shipping`);
  }

  // Apply source filter
  if (productConfig.activeFilters.source.length > 0) {
    filteredProducts = filteredProducts.filter(product =>
      productConfig.activeFilters.source.includes(product.source)
    );
  }

  // Apply relevance filter (using bestMatch property)
  if (productConfig.activeFilters.relevance.length > 0) {
    filteredProducts = filteredProducts.filter(product => {
      if (productConfig.activeFilters.relevance.includes('high')) {
        // Check for bestMatch flag which is set in the backend
        return product.bestMatch === true;
      }
      return true;
    });
  }

  // Save filtered products and display first page
  productConfig.displayedProducts = filteredProducts;
  productConfig.currentPage = 1;
  displayProductsPage();

  // Update product counts
  updateProductCounts();
}

/**
 * Updates the product count displays
 */
function updateProductCounts() {
  const totalFilteredProducts = productConfig.displayedProducts.length;
  const totalProducts = productConfig.allProducts.length;

  // Update count elements if they exist
  if (productTotalCount) productTotalCount.textContent = totalFilteredProducts;
  if (productsCount) productsCount.textContent = totalFilteredProducts;

  // Show "no products" message if needed
  if (productsContainer && totalFilteredProducts === 0 && totalProducts > 0) {
    productsContainer.innerHTML = `
        <div class="col-12">
          <div class="no-products-message">
            <i class="fas fa-filter fa-3x mb-3"></i>
            <h5>No products match your filters</h5>
            <p>Try adjusting your filter criteria or <button id="in-content-reset" class="btn btn-link p-0">reset all filters</button></p>
          </div>
        </div>
      `;

    // Add event listener to the in-content reset button
    const inContentReset = document.getElementById('in-content-reset');
    if (inContentReset) {
      inContentReset.addEventListener('click', resetFilters);
    }

    // Hide load more button
    if (loadMoreContainer) loadMoreContainer.classList.add('d-none');
  }
}

/**
 * Displays the current page of products
 */
function displayProductsPage() {
  if (!productsContainer) {
    console.error("Products container not found - cannot display products");
    return;
  }

  const displayedProducts = productConfig.displayedProducts;
  const startIndex = 0;
  const endIndex = productConfig.currentPage * productConfig.pageSize;
  const productsToShow = displayedProducts.slice(startIndex, endIndex);

  // Clear the container
  productsContainer.innerHTML = '';

  // Set column classes based on view mode
  let colClasses;
  switch (productConfig.currentView) {
    case 'grid':
      colClasses = 'col-md-4 col-lg-3';
      break;
    case 'list':
      colClasses = 'col-12';
      break;
    case 'compact':
      colClasses = 'col-6 col-md-3 col-lg-2';
      break;
    default:
      colClasses = 'col-md-4 col-lg-3';
  }

  // Display products
  productsToShow.forEach(product => {
    const productId = generateProductId(product);
    const sourceClass = product.source === 'eBay' ? 'source-ebay' : 'source-google';
    
    // Use multiple properties to determine high relevance/exact match status
    const isHighRelevance = product.bestMatch === true || 
                           (product.relevanceScore && product.relevanceScore > 50) || 
                           product.isExactMatch === true;
    
    // Add logging to understand which products are marked as bestMatch
    if (product.bestMatch === true) {
      console.log("Product marked as bestMatch:", product.title);
    }
    
    const exactMatchClass = isHighRelevance ? 'exact-match' : '';

    // Check if this product is a favorite
    const favorites = loadFavorites();
    const isFavorite = favorites[productId] !== undefined;

    // Create product HTML based on view mode
    let productHTML;

    if (productConfig.currentView === 'list') {
      // List view
      productHTML = createListViewProduct(product, productId, sourceClass, exactMatchClass, isFavorite);
    } else {
      // Grid or compact view
      productHTML = createGridViewProduct(product, productId, sourceClass, exactMatchClass, isFavorite);
    }

    // Create wrapper and append to container
    const productWrapper = document.createElement('div');
    productWrapper.className = colClasses;
    productWrapper.innerHTML = productHTML;
    productsContainer.appendChild(productWrapper);
  });

  // Show or hide "load more" button
  if (loadMoreContainer) {
    if (endIndex < displayedProducts.length) {
      loadMoreContainer.classList.remove('d-none');
    } else {
      loadMoreContainer.classList.add('d-none');
    }
  }

  // Add event listeners
  attachFavoriteButtonListeners();
  attachImagePreviewListeners();

  // Update product counts
  updateProductCounts();
  
  // Trigger a custom event to notify that products were displayed
  document.dispatchEvent(new CustomEvent('productsDisplayed'));
}

/**
 * Creates HTML for a product in grid view
 */
/**
* Creates HTML for a product in grid view with modern UI
*/

/**
 * Creates HTML for a product in grid view with proper condition and shipping styling
 */
function createGridViewProduct(product, productId, sourceClass, exactMatchClass, isFavorite) {
  // Determine condition class based on product condition
  let conditionClass = 'condition-unknown';
  let conditionValueClass = '';

  if (product.condition.toLowerCase().includes('new')) {
    conditionClass = 'condition-new';
    conditionValueClass = 'new-item';
  } else if (product.condition.toLowerCase().includes('used') ||
    product.condition.toLowerCase().includes('pre-owned') ||
    product.condition.toLowerCase().includes('preowned')) {
    conditionClass = 'condition-used';
    conditionValueClass = 'used-item';
  } else if (product.condition.toLowerCase().includes('refurbished')) {
    conditionClass = 'condition-refurbished';
    conditionValueClass = 'refurbished-item';
  }

  // Determine shipping class
  let shippingClass = '';
  let shippingValueClass = '';

  // Handle shipping safely with null/undefined check
  const shippingText = (product.shipping || '').toLowerCase();
  if (shippingText.includes('free')) {
    shippingClass = 'free-shipping';
    shippingValueClass = 'free-item';
  } else if (shippingText.includes('$')) {
    shippingValueClass = 'paid-shipping';
  }

  // Create tags
  let tags = '';
  if (product.condition.toLowerCase().includes('new')) {
    tags += `<span class="product-tag tag-new">New</span>`;
  } else if (product.condition.toLowerCase().includes('used') ||
    product.condition.toLowerCase().includes('pre-owned')) {
    tags += `<span class="product-tag tag-used">Pre-Owned</span>`;
  }

  if ((product.shipping || '').toLowerCase().includes('free')) {
    tags += `<span class="product-tag tag-free-shipping">Free Shipping</span>`;
  }
  
  // Check for OEM parts
  const productText = (product.title + ' ' + (product.description || '')).toLowerCase();
  
  // Log the product text for debugging
  console.log('Product text for analysis:', product.title);
  
  if (productText.includes('oem') || 
      productText.includes('original equipment') || 
      productText.includes('original')) {
    tags += `<span class="product-tag tag-oem">OEM</span>`;
  }
  
  // Check for Premium parts with multiple detection approaches
  // 1. Keyword-based detection
  const isPremiumByKeywords = productText.includes('premium') || 
      productText.includes('performance') || 
      productText.includes('pro') || 
      productText.includes('high quality') || 
      productText.includes('elite') || 
      productText.includes('advanced') || 
      productText.includes('upgraded') ||
      productText.includes('drilled') ||       // Drilled rotors are premium
      productText.includes('slotted') ||       // Slotted rotors are premium
      productText.includes('ceramic') ||       // Ceramic pads are premium
      productText.includes('carbon ceramic') || // Carbon ceramic is high-end
      productText.includes('semi-metallic') || // Semi-metallic is premium
      productText.includes('semi metallic') || // Semi-metallic (alt spelling)
      productText.includes('sport') ||         // Sport parts are premium
      productText.includes('racing') ||        // Racing parts are premium
      productText.includes('heavy duty');      // Heavy duty parts are premium
      
  // 2. Brand-based detection - list of premium brands
  const premiumBrands = ['bosch', 'brembo', 'bilstein', 'koni', 'borla', 'kw', 'k&n', 'moog', 
                         'akebono', 'stoptech', 'eibach', 'h&r', 'magnaflow', 'hawk', 'edelbrock',
                         'detroit', 'apf', 'detroit diesel', 'detroit axle', 'aisin', 'gear'];
  
  const isPremiumByBrand = premiumBrands.some(brand => productText.includes(brand));
  
  // Classify as premium if any detection method matches
  if (isPremiumByKeywords || isPremiumByBrand) {
    console.log('Found premium product by', 
                isPremiumByKeywords ? 'keywords' : 'brand',
                ':', product.title);
    tags += `<span class="product-tag tag-premium">Premium</span>`;
    
    // Add a data attribute to the product card to mark it as premium
    // This helps with persistence across redraws
    setTimeout(() => {
      try {
        const productCards = document.querySelectorAll('.product-card');
        productCards.forEach(card => {
          if (card.querySelector('.product-title') && 
              card.querySelector('.product-title').textContent === product.title) {
            card.setAttribute('data-premium', 'true');
            console.log('Marked product as premium with data attribute:', product.title);
          }
        });
      } catch (e) {
        console.error('Error setting premium data attribute:', e);
      }
    }, 100); // Small delay to ensure DOM is ready
  }

  // Badge removed as part of badge strategy redesign
  const relevanceBadge = '';

  return `
      <div class="product-card">
        <div class="product-source ${sourceClass}">${product.source}</div>
        ${relevanceBadge}
        <button class="favorite-btn ${isFavorite ? 'active' : ''}" data-product-id="${productId}">
          <i class="fas fa-heart"></i>
        </button>
        <div class="product-image-container" data-image="${product.image || '/static/placeholder.png'}">
          <img src="${product.image || '/static/placeholder.png'}" 
               class="product-image" 
               alt="${product.title || 'Product'}" 
               onerror="this.src='/static/placeholder.png'; this.onerror=null;">
        </div>
        <div class="product-details">
          <div class="product-title">${product.title}</div>
          <div class="product-tags mb-2">${tags}</div>
          <div class="product-meta justify-between">
            <span class="condition-label">Condition:</span>
            <span class="${conditionClass} ${conditionValueClass} condition-value">${product.condition}</span>
          </div>
          <div class="product-meta justify-between">
            <span class="shipping-label">Shipping:</span>
            <span class="${shippingClass} ${shippingValueClass} shipping-value">${product.shipping}</span>
          </div>
          <div class="d-flex justify-content-between align-items-center mt-3 mb-2">
            <span class="product-price">${product.price}</span>
          </div>
          <div class="product-actions">
            <a href="${product.link || '#'}" target="_blank" class="btn btn-danger view-details" style="padding: 0.4rem 0.8rem; font-size: 0.9rem;">View Details</a>
          </div>
        </div>
      </div>
    `;
}

/**
 * Creates HTML for a product in list view with proper condition and shipping styling
 */
function createListViewProduct(product, productId, sourceClass, exactMatchClass, isFavorite) {
  // Determine condition class based on product condition
  let conditionClass = 'condition-unknown';
  let conditionValueClass = '';

  if (product.condition.toLowerCase().includes('new')) {
    conditionClass = 'condition-new';
    conditionValueClass = 'new-item';
  } else if (product.condition.toLowerCase().includes('used') ||
    product.condition.toLowerCase().includes('pre-owned') ||
    product.condition.toLowerCase().includes('preowned')) {
    conditionClass = 'condition-used';
    conditionValueClass = 'used-item';
  } else if (product.condition.toLowerCase().includes('refurbished')) {
    conditionClass = 'condition-refurbished';
    conditionValueClass = 'refurbished-item';
  }

  // Determine shipping class
  let shippingClass = '';
  let shippingValueClass = '';

  // Handle shipping safely with null/undefined check
  const shippingText = (product.shipping || '').toLowerCase();
  if (shippingText.includes('free')) {
    shippingClass = 'free-shipping';
    shippingValueClass = 'free-item';
  } else if (shippingText.includes('$')) {
    shippingValueClass = 'paid-shipping';
  }

  // Create tags
  let tags = '';
  if (product.condition.toLowerCase().includes('new')) {
    tags += `<span class="product-tag tag-new">New</span>`;
  } else if (product.condition.toLowerCase().includes('used') ||
    product.condition.toLowerCase().includes('pre-owned')) {
    tags += `<span class="product-tag tag-used">Pre-Owned</span>`;
  }

  if ((product.shipping || '').toLowerCase().includes('free')) {
    tags += `<span class="product-tag tag-free-shipping">Free Shipping</span>`;
  }
  
  // Check for OEM parts
  const productText = (product.title + ' ' + (product.description || '')).toLowerCase();
  
  // Log the product text for debugging
  console.log('Product text for analysis:', product.title);
  
  if (productText.includes('oem') || 
      productText.includes('original equipment') || 
      productText.includes('original')) {
    tags += `<span class="product-tag tag-oem">OEM</span>`;
  }
  
  // Check for Premium parts with multiple detection approaches
  // 1. Keyword-based detection
  const isPremiumByKeywords = productText.includes('premium') || 
      productText.includes('performance') || 
      productText.includes('pro') || 
      productText.includes('high quality') || 
      productText.includes('elite') || 
      productText.includes('advanced') || 
      productText.includes('upgraded') ||
      productText.includes('drilled') ||       // Drilled rotors are premium
      productText.includes('slotted') ||       // Slotted rotors are premium
      productText.includes('ceramic') ||       // Ceramic pads are premium
      productText.includes('carbon ceramic') || // Carbon ceramic is high-end
      productText.includes('semi-metallic') || // Semi-metallic is premium
      productText.includes('semi metallic') || // Semi-metallic (alt spelling)
      productText.includes('sport') ||         // Sport parts are premium
      productText.includes('racing') ||        // Racing parts are premium
      productText.includes('heavy duty');      // Heavy duty parts are premium
      
  // 2. Brand-based detection - list of premium brands
  const premiumBrands = ['bosch', 'brembo', 'bilstein', 'koni', 'borla', 'kw', 'k&n', 'moog', 
                         'akebono', 'stoptech', 'eibach', 'h&r', 'magnaflow', 'hawk', 'edelbrock',
                         'detroit', 'apf', 'detroit diesel', 'detroit axle', 'aisin', 'gear'];
  
  const isPremiumByBrand = premiumBrands.some(brand => productText.includes(brand));
  
  // Classify as premium if any detection method matches
  if (isPremiumByKeywords || isPremiumByBrand) {
    console.log('Found premium product by', 
                isPremiumByKeywords ? 'keywords' : 'brand',
                ':', product.title);
    tags += `<span class="product-tag tag-premium">Premium</span>`;
    
    // Add a data attribute to the product card to mark it as premium
    // This helps with persistence across redraws
    setTimeout(() => {
      try {
        const productCards = document.querySelectorAll('.product-card');
        productCards.forEach(card => {
          if (card.querySelector('.product-title') && 
              card.querySelector('.product-title').textContent === product.title) {
            card.setAttribute('data-premium', 'true');
            console.log('Marked product as premium with data attribute:', product.title);
          }
        });
      } catch (e) {
        console.error('Error setting premium data attribute:', e);
      }
    }, 100); // Small delay to ensure DOM is ready
  }

  // Badge removed as part of badge strategy redesign
  const relevanceBadge = '';

  return `
      <div class="product-card">
        <div class="product-source ${sourceClass}">${product.source}</div>
        ${relevanceBadge}
        <button class="favorite-btn ${isFavorite ? 'active' : ''}" data-product-id="${productId}">
          <i class="fas fa-heart"></i>
        </button>
        <div class="product-image-container" data-image="${product.image || '/static/placeholder.png'}">
          <img src="${product.image || '/static/placeholder.png'}" 
               class="product-image" 
               alt="${product.title || 'Product'}" 
               onerror="this.src='/static/placeholder.png'; this.onerror=null;">
        </div>
        <div class="product-details">
          <div class="product-title">${product.title}</div>
          <div class="product-tags">${tags}</div>
          <div class="d-flex justify-between my-2">
            <div class="d-flex flex-column">
              <div class="product-meta justify-between mb-1">
                <span class="condition-label me-2">Condition:</span>
                <span class="${conditionClass} ${conditionValueClass} condition-value">${product.condition}</span>
              </div>
              <div class="product-meta justify-between">
                <span class="shipping-label me-2">Shipping:</span>
                <span class="${shippingClass} ${shippingValueClass} shipping-value">${product.shipping}</span>
              </div>
            </div>
            <span class="product-price">${product.price}</span>
          </div>
          <div class="product-actions mt-auto">
            <a href="${product.link || '#'}" target="_blank" class="btn btn-danger view-details">View Details</a>
          </div>
        </div>
      </div>
    `;
}
/**
 * Loads the next page of products
 */
function loadMoreProducts() {
  console.log("Loading more products...");
  productConfig.currentPage++;
  displayProductsPage();

  // Scroll to show the newly loaded products
  if (productsContainer) {
    const lastVisibleProduct = productsContainer.lastElementChild;
    if (lastVisibleProduct) {
      lastVisibleProduct.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }
  
  // Manually trigger the productsDisplayed event to ensure filters are reapplied
  console.log("Triggering productsDisplayed event after loading more products");
  setTimeout(() => {
    document.dispatchEvent(new CustomEvent('productsDisplayed'));
  }, 100);
}

/**
 * Sets the products and initializes display
 */
function setProducts(products) {
  if (!products || !Array.isArray(products)) {
    return;
  }

  // Save products to state
  productConfig.allProducts = products;
  productConfig.displayedProducts = [...products];
  productConfig.currentPage = 1;

  // Make sure DOM references are initialized
  initializeDOMReferences();

  // Run debug inspection
  debugInspectProducts();
  
  // Explicitly set sort to relevance and apply sorting
  productConfig.currentSort = 'relevance';
  if (sortLabel) sortLabel.textContent = 'Relevance';
  sortAndDisplayProducts();

  // Show products tab if products exist
  if (products.length > 0 && productTab) {
    productTab.click();
  }
}

/**
 * Sorts and displays products according to current configuration
 */
function sortAndDisplayProducts() {
  if (!productConfig.displayedProducts || productConfig.displayedProducts.length === 0) return;

  let sortedProducts = [...productConfig.displayedProducts];

  switch (productConfig.currentSort) {
    case 'relevance':
      // Sort by relevance score (highest first)
      sortedProducts.sort((a, b) =>
        (b.relevanceScore || 0) - (a.relevanceScore || 0)
      );
      break;

    case 'price-low':
      // Sort by price (lowest first)
      sortedProducts.sort((a, b) => {
        const priceA = parseFloat(a.price.replace(/[^0-9.]/g, '')) || 0;
        const priceB = parseFloat(b.price.replace(/[^0-9.]/g, '')) || 0;
        return priceA - priceB;
      });
      break;

    case 'price-high':
      // Sort by price (highest first)
      sortedProducts.sort((a, b) => {
        const priceA = parseFloat(a.price.replace(/[^0-9.]/g, '')) || 0;
        const priceB = parseFloat(b.price.replace(/[^0-9.]/g, '')) || 0;
        return priceB - priceA;
      });
      break;
  }

  // Update the displayed products
  productConfig.displayedProducts = sortedProducts;
  displayProductsPage();
}

// Export the API
window.productDisplay = {
  setProducts,
  loadMoreProducts,
  resetFilters,
  updateViewMode,
  sortAndDisplayProducts
};