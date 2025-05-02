/**
 * Product Data Manager
 * Centralizes product data handling, caching, and unified data model
 */

const ProductDataManager = (function() {
  // Cache settings
  const CACHE_SETTINGS = {
    CACHE_EXPIRY: 30 * 60 * 1000, // 30 minutes
    STORAGE_KEY_PREFIX: 'autoxpress_product_cache_',
    ENABLED: true
  };
  
  // In-memory product cache
  const productCache = {
    // Structure: { queryHash: { data, timestamp } }
  };
  
  // Unified product data model fields
  const PRODUCT_MODEL_FIELDS = [
    'id',           // Unique identifier
    'title',        // Product title
    'brand',        // Brand name
    'partType',     // Type of part
    'condition',    // Condition (new, used, refurbished)
    'price',        // Price as number
    'originalPrice', // Original price if available
    'shipping',     // Shipping info
    'image',        // Primary image URL
    'fullImage',    // High-res image URL
    'link',         // Link to product
    'source',       // Source (eBay, Google, etc.)
    // Ranking data - added by ProductRanking module
    'relevanceScore', 
    'relevanceCategory',
    'primaryBadge',
    'secondaryBadges',
    // Extra metadata
    'metadata'      // Additional source-specific data
  ];
  
  /**
   * Generate a cache key for a query
   * @param {string} queryText - The search query
   * @param {Object} queryParams - Additional query parameters
   * @returns {string} Hash key for cache
   */
  function generateCacheKey(queryText, queryParams = {}) {
    // Sort params to ensure consistent order
    const sortedParams = Object.keys(queryParams)
      .sort()
      .map(key => `${key}:${queryParams[key]}`)
      .join('|');
    
    // Create composite key
    const compositeKey = `${queryText}__${sortedParams}`;
    
    // Simple hash function
    let hash = 0;
    for (let i = 0; i < compositeKey.length; i++) {
      const char = compositeKey.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32bit integer
    }
    
    return CACHE_SETTINGS.STORAGE_KEY_PREFIX + Math.abs(hash).toString(16);
  }
  
  /**
   * Check if cache entry is valid
   * @param {Object} cacheEntry - The cache entry to check
   * @returns {boolean} True if valid, false if expired
   */
  function isValidCache(cacheEntry) {
    if (!cacheEntry || !cacheEntry.timestamp) return false;
    
    const now = Date.now();
    const age = now - cacheEntry.timestamp;
    
    return age < CACHE_SETTINGS.CACHE_EXPIRY;
  }
  
  /**
   * Try to get products from cache first
   * @param {string} cacheKey - Cache key to look up
   * @returns {Array|null} Products if cached, null if not
   */
  function getFromCache(cacheKey) {
    // Check memory cache first (faster)
    if (productCache[cacheKey] && isValidCache(productCache[cacheKey])) {
      console.log('Cache hit (memory):', cacheKey);
      return productCache[cacheKey].data;
    }
    
    // Then check localStorage
    try {
      const cachedValue = localStorage.getItem(cacheKey);
      if (cachedValue) {
        const cacheEntry = JSON.parse(cachedValue);
        
        if (isValidCache(cacheEntry)) {
          console.log('Cache hit (localStorage):', cacheKey);
          
          // Update memory cache for faster access next time
          productCache[cacheKey] = cacheEntry;
          
          return cacheEntry.data;
        } else {
          // Remove expired cache
          localStorage.removeItem(cacheKey);
        }
      }
    } catch (error) {
      console.warn('Error reading from cache:', error);
    }
    
    return null;
  }
  
  /**
   * Save products to cache
   * @param {string} cacheKey - Cache key to store under
   * @param {Array} products - Products to cache
   */
  function saveToCache(cacheKey, products) {
    if (!CACHE_SETTINGS.ENABLED || !products) return;
    
    const cacheEntry = {
      data: products,
      timestamp: Date.now()
    };
    
    // Save to memory cache
    productCache[cacheKey] = cacheEntry;
    
    // Save to localStorage
    try {
      localStorage.setItem(cacheKey, JSON.stringify(cacheEntry));
    } catch (error) {
      console.warn('Error saving to cache:', error);
      
      // If storage is full, clear old cache entries
      if (error.name === 'QuotaExceededError') {
        clearOldCache();
        try {
          localStorage.setItem(cacheKey, JSON.stringify(cacheEntry));
        } catch (retryError) {
          console.error('Failed to save to cache after cleanup:', retryError);
        }
      }
    }
  }
  
  /**
   * Clear old/expired cache entries
   */
  function clearOldCache() {
    const now = Date.now();
    
    // Clear memory cache
    Object.keys(productCache).forEach(key => {
      if (!isValidCache(productCache[key])) {
        delete productCache[key];
      }
    });
    
    // Clear localStorage cache
    Object.keys(localStorage).forEach(key => {
      if (key.startsWith(CACHE_SETTINGS.STORAGE_KEY_PREFIX)) {
        try {
          const cacheEntry = JSON.parse(localStorage.getItem(key));
          if (!isValidCache(cacheEntry)) {
            localStorage.removeItem(key);
          }
        } catch (error) {
          // If entry can't be parsed, remove it
          localStorage.removeItem(key);
        }
      }
    });
  }
  
  /**
   * Normalizes product data to a consistent format
   * @param {Array} products - Raw products from different sources
   * @returns {Array} Normalized products
   */
  function normalizeProducts(products) {
    if (!Array.isArray(products)) return [];
    
    return products.map(product => {
      // Create a normalized product object with default values
      const normalizedProduct = {
        id: product.id || generateProductId(product),
        title: product.title || '',
        brand: product.brand || 'Unknown',
        partType: product.partType || extractPartType(product.title) || 'Part',
        condition: product.condition || 'Unknown',
        price: normalizePrice(product.price),
        originalPrice: normalizePrice(product.originalPrice || product.price),
        shipping: product.shipping || 'Standard Shipping',
        image: product.image || '/static/placeholder.png',
        fullImage: product.fullImage || product.image || '/static/placeholder.png',
        link: product.link || '#',
        source: product.source || 'Unknown',
        metadata: {}
      };
      
      // Copy over any existing ranking data
      if (product.relevanceScore !== undefined) {
        normalizedProduct.relevanceScore = product.relevanceScore;
      }
      
      if (product.relevanceCategory) {
        normalizedProduct.relevanceCategory = product.relevanceCategory;
      }
      
      if (product.primaryBadge) {
        normalizedProduct.primaryBadge = product.primaryBadge;
      }
      
      if (product.secondaryBadges) {
        normalizedProduct.secondaryBadges = product.secondaryBadges;
      }
      
      // Store any non-standard fields in metadata
      for (const key in product) {
        if (!PRODUCT_MODEL_FIELDS.includes(key)) {
          normalizedProduct.metadata[key] = product[key];
        }
      }
      
      return normalizedProduct;
    });
  }
  
  /**
   * Generate a product ID if none exists
   * @param {Object} product - Product to generate ID for
   * @returns {string} Generated ID
   */
  function generateProductId(product) {
    // Use existing function if available
    if (window.generateProductId) {
      return window.generateProductId(product);
    }
    
    // Fallback implementation
    try {
      return btoa(product.title.substring(0, 30) + product.price).replace(/[^a-zA-Z0-9]/g, '');
    } catch (e) {
      // Handle non-ASCII characters
      const safeString = encodeURIComponent(product.title.substring(0, 30) + product.price);
      return btoa(safeString).replace(/[^a-zA-Z0-9]/g, '');
    }
  }
  
  /**
   * Extract part type from product title
   * @param {string} title - Product title
   * @returns {string|null} Extracted part type or null
   */
  function extractPartType(title) {
    if (!title) return null;
    
    // Common part type keywords to look for
    const partTypes = [
      'alternator', 'battery', 'belt', 'brake pad', 'brake disc', 'brake rotor',
      'bumper', 'camshaft', 'carburetor', 'catalytic converter', 'clutch',
      'control arm', 'crankshaft', 'cv joint', 'cylinder head', 'differential',
      'door handle', 'drive shaft', 'engine', 'exhaust', 'fender', 'filter',
      'fuel pump', 'fuel injector', 'gasket', 'gearbox', 'grille', 'headlight',
      'ignition coil', 'mirror', 'muffler', 'o2 sensor', 'oil filter', 'oil pump',
      'piston', 'power steering', 'radiator', 'shock absorber', 'spark plug',
      'starter', 'strut', 'suspension', 'tail light', 'thermostat', 'timing belt',
      'transmission', 'water pump', 'wheel bearing', 'wheel hub', 'window regulator',
      'wiper blade'
    ];
    
    // Convert title to lowercase for case-insensitive matching
    const lowerTitle = title.toLowerCase();
    
    // Find the first matching part type
    for (const part of partTypes) {
      if (lowerTitle.includes(part)) {
        return part.charAt(0).toUpperCase() + part.slice(1); // Capitalize first letter
      }
    }
    
    return null;
  }
  
  /**
   * Normalize price to a number
   * @param {any} price - Price in various formats
   * @returns {number} Normalized price as a number
   */
  function normalizePrice(price) {
    if (typeof price === 'number') return price;
    
    if (typeof price === 'string') {
      // Strip currency symbols and other non-numeric characters
      const numericString = price.replace(/[^0-9.]/g, '');
      return parseFloat(numericString) || 0;
    }
    
    return 0;
  }
  
  /**
   * Format price to ensure it has a dollar sign
   * @param {string|number} price - Price to format
   * @returns {string} Price with dollar sign
   */
  function formatPrice(price) {
    if (price === undefined || price === null) return '$0.00';
    
    // Convert to string if it's a number
    const priceStr = price.toString();
    
    // If it already has a dollar sign, return as is
    if (priceStr.indexOf('$') === 0) return priceStr;
    
    // Add dollar sign
    return '$' + priceStr;
  }
  
  /**
   * Processes products through ranking and caching
   * @param {Array} products - Raw products from API
   * @param {Object} queryInfo - Query information
   * @returns {Array} Processed products
   */
  function processProducts(products, queryInfo = {}) {
    // Skip processing if no products
    if (!products || !Array.isArray(products) || products.length === 0) {
      return [];
    }
    
    // Normalize products to consistent format
    const normalizedProducts = normalizeProducts(products);
    
    // Apply ranking if available
    if (window.ProductRanking) {
      return window.ProductRanking.rankProducts(normalizedProducts, queryInfo.vehicleInfo || {});
    }
    
    return normalizedProducts;
  }
  
  /**
   * Get products with caching
   * @param {string} queryText - Search query text
   * @param {Object} queryParams - Additional query parameters
   * @param {Function} fetchFn - Function to fetch products if not cached
   * @returns {Promise<Array>} Products
   */
  async function getProducts(queryText, queryParams = {}, fetchFn) {
    if (!CACHE_SETTINGS.ENABLED || !fetchFn) {
      // If caching disabled or no fetch function, fetch directly
      const products = await fetchFn(queryText, queryParams);
      return processProducts(products, { queryText, ...queryParams });
    }
    
    // Generate cache key
    const cacheKey = generateCacheKey(queryText, queryParams);
    
    // Try to get from cache
    const cachedProducts = getFromCache(cacheKey);
    if (cachedProducts) {
      return cachedProducts;
    }
    
    // Fetch new products
    const products = await fetchFn(queryText, queryParams);
    
    // Process products
    const processedProducts = processProducts(products, { queryText, ...queryParams });
    
    // Save to cache
    saveToCache(cacheKey, processedProducts);
    
    return processedProducts;
  }
  
  /**
   * Clear all product cache
   */
  function clearCache() {
    // Clear memory cache
    Object.keys(productCache).forEach(key => {
      delete productCache[key];
    });
    
    // Clear localStorage cache
    Object.keys(localStorage).forEach(key => {
      if (key.startsWith(CACHE_SETTINGS.STORAGE_KEY_PREFIX)) {
        localStorage.removeItem(key);
      }
    });
    
    console.log('Product cache cleared');
  }
  
  /**
   * Extract vehicle info from query text
   * @param {string} queryText - Search query
   * @returns {Object} Vehicle info object
   */
  function extractVehicleInfo(queryText) {
    if (!queryText) return {};
    
    const vehicleInfo = {
      year: null,
      make: null,
      model: null,
      part: null
    };
    
    // Extract year - match 4 digit years starting with 19 or 20
    const yearMatch = queryText.match(/\b(19|20)\d{2}\b/);
    if (yearMatch) {
      vehicleInfo.year = yearMatch[0];
    }
    
    // Extract part - last word or phrase after last vehicle info
    const parts = queryText.split(' ');
    if (parts.length > 3 && vehicleInfo.year) {
      // Find position of year in query
      const yearIndex = parts.findIndex(part => part === vehicleInfo.year);
      if (yearIndex >= 0 && yearIndex + 2 < parts.length) {
        // Make is typically after year
        vehicleInfo.make = parts[yearIndex + 1];
        
        // Model is typically after make
        vehicleInfo.model = parts[yearIndex + 2];
        
        // Part is everything after model
        if (yearIndex + 3 < parts.length) {
          vehicleInfo.part = parts.slice(yearIndex + 3).join(' ');
        }
      }
    }
    
    return vehicleInfo;
  }
  
  // Public API
  return {
    getProducts,
    processProducts,
    normalizeProducts,
    clearCache,
    extractVehicleInfo,
    // Configuration access
    setCacheEnabled: function(enabled) {
      CACHE_SETTINGS.ENABLED = !!enabled;
    },
    isCacheEnabled: function() {
      return CACHE_SETTINGS.ENABLED;
    }
  };
})();

// Export globally
window.ProductDataManager = ProductDataManager;