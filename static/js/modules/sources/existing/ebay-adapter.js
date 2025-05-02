/**
 * eBay Source Adapter
 * Wraps the existing eBay search functionality into the SourceAdapter interface
 */

class EbayAdapter extends SourceAdapter {
  /**
   * Constructor for the eBay source adapter
   * @param {Object} config - Configuration options
   */
  constructor(config = {}) {
    // Set up the default configuration for eBay
    const defaultConfig = {
      id: 'eBay',
      name: 'eBay',
      priority: 1, // Give eBay high priority
      maxResults: 50,
      timeout: 15000, // 15 seconds
      retryCount: 1
    };
    
    // Call parent constructor with merged config
    super(Object.assign({}, defaultConfig, config));
    
    // Store information about the original implementation
    this.originalSearchFn = null;
    this.cachedVehicleInfo = {};
  }
  
  /**
   * Initialize the adapter
   * @returns {Promise<boolean>} Success status
   */
  async initialize() {
    if (this.isInitialized) return true;
    
    try {
      // Check if the original eBay search function exists
      // This might be a global function or part of another module
      if (typeof window.fetchEbayProducts === 'function') {
        this.originalSearchFn = window.fetchEbayProducts;
      } else if (typeof window.searchEbay === 'function') {
        this.originalSearchFn = window.searchEbay;
      } else {
        console.warn('[EbayAdapter] Could not find original eBay search function');
        // We'll fall back to a mock implementation if needed
      }
      
      this.isInitialized = true;
      return true;
    } catch (error) {
      console.error('[EbayAdapter] Initialization failed:', error);
      return false;
    }
  }
  
  /**
   * Search for products from eBay
   * @param {string} query - Search query text
   * @param {Object} options - Additional search options
   * @returns {Promise<Array>} - Array of product objects
   */
  async searchProducts(query, options = {}) {
    if (!this.isInitialized) {
      await this.initialize();
    }
    
    if (!this.config.enabled) {
      return [];
    }
    
    try {
      // Start performance monitoring if available
      let performanceMark = null;
      if (window.PerformanceMonitor) {
        performanceMark = window.PerformanceMonitor.startMeasure('dataFetching', {
          source: this.config.id,
          query
        });
      }
      
      // Store vehicle info for later use in formatting
      if (options.vehicleInfo) {
        this.cachedVehicleInfo = options.vehicleInfo;
      } else if (typeof window.productDisplay?.getVehicleInfo === 'function') {
        this.cachedVehicleInfo = window.productDisplay.getVehicleInfo();
      }
      
      let results = [];
      
      // Use the original search function if available
      if (this.originalSearchFn) {
        results = await this.originalSearchFn(query, options);
      } else {
        // Fall back to a mock implementation that gets products from productDisplay
        // This is just a fallback to not break functionality
        console.warn('[EbayAdapter] Using fallback eBay search implementation');
        if (window.productDisplay && typeof window.productDisplay.getProducts === 'function') {
          const allProducts = window.productDisplay.getProducts();
          results = allProducts.filter(product => product.source === 'eBay');
        }
      }
      
      // End performance monitoring
      if (performanceMark && window.PerformanceMonitor) {
        window.PerformanceMonitor.endMeasure(performanceMark, {
          success: true,
          resultCount: results.length
        });
      }
      
      // Format products to ensure they match our data model
      return results.map(product => this.formatProduct(product));
    } catch (error) {
      this._handleError(error, 'searchProducts');
      return [];
    }
  }
  
  /**
   * Format eBay product data to match the application's unified data model
   * @param {Object} rawProduct - Raw product data from eBay
   * @returns {Object} - Formatted product data
   */
  formatProduct(rawProduct) {
    try {
      // If the product data already matches our format, return it as is
      if (rawProduct.source === 'eBay' && rawProduct.id) {
        return rawProduct;
      }
      
      // Create a normalized product with required fields
      const formattedProduct = {
        id: rawProduct.id || rawProduct.itemId || generateProductId(rawProduct),
        title: rawProduct.title || '',
        brand: rawProduct.brand || this.extractBrand(rawProduct.title || ''),
        partType: rawProduct.partType || this.extractPartType(rawProduct.title || ''),
        condition: rawProduct.condition || 'Used',
        price: this.normalizePrice(rawProduct.price),
        originalPrice: this.normalizePrice(rawProduct.originalPrice || rawProduct.price),
        shipping: rawProduct.shipping || 'Standard Shipping',
        image: rawProduct.image || '/static/placeholder.png',
        fullImage: rawProduct.fullImage || rawProduct.image || '/static/placeholder.png',
        link: rawProduct.link || rawProduct.url || '#',
        source: 'eBay',
        metadata: {}
      };
      
      // Copy any additional properties to metadata
      for (const key in rawProduct) {
        if (!formattedProduct.hasOwnProperty(key)) {
          formattedProduct.metadata[key] = rawProduct[key];
        }
      }
      
      return formattedProduct;
    } catch (error) {
      this._handleError(error, 'formatProduct');
      // Return the raw product as a fallback
      return {
        ...rawProduct,
        source: 'eBay'
      };
    }
  }
  
  /**
   * Extract brand from product title
   * @param {string} title - Product title
   * @returns {string} - Extracted brand
   * @private
   */
  extractBrand(title) {
    // Get the make from the cached vehicle info
    const make = this.cachedVehicleInfo.make || '';
    
    if (make && title.toLowerCase().includes(make.toLowerCase())) {
      return make;
    }
    
    // Common auto part brands
    const commonBrands = [
      'OEM', 'Genuine', 'Motorcraft', 'ACDelco', 'Mopar', 'Bosch', 'Denso',
      'NGK', 'Moog', 'Monroe', 'Fel-Pro', 'Wagner', 'Cardone', 'Dorman',
      'KYB', 'Beck/Arnley', 'Gates', 'Edelbrock', 'Holley', 'K&N', 'NOS'
    ];
    
    for (const brand of commonBrands) {
      if (title.toLowerCase().includes(brand.toLowerCase())) {
        return brand;
      }
    }
    
    return 'Unknown Brand';
  }
  
  /**
   * Extract part type from product title
   * @param {string} title - Product title
   * @returns {string} - Extracted part type
   * @private
   */
  extractPartType(title) {
    // Get the part from the cached vehicle info
    const part = this.cachedVehicleInfo.part || '';
    
    if (part && title.toLowerCase().includes(part.toLowerCase())) {
      return part;
    }
    
    // Common part types to look for
    const partTypes = [
      'engine', 'transmission', 'alternator', 'starter', 'brake', 'rotor',
      'caliper', 'shock', 'strut', 'spring', 'control arm', 'radiator',
      'condenser', 'compressor', 'pump', 'filter', 'sensor', 'switch',
      'light', 'lamp', 'mirror', 'door', 'window', 'handle', 'bumper',
      'grille', 'hood', 'fender', 'panel'
    ];
    
    for (const partType of partTypes) {
      if (title.toLowerCase().includes(partType)) {
        return partType.charAt(0).toUpperCase() + partType.slice(1);
      }
    }
    
    return 'Auto Part';
  }
  
  /**
   * Normalize price to a number
   * @param {any} price - Price in various formats
   * @returns {number} - Normalized price as a number
   * @private
   */
  normalizePrice(price) {
    if (typeof price === 'number') return price;
    
    if (typeof price === 'string') {
      // Strip currency symbols and other non-numeric characters
      const numericString = price.replace(/[^0-9.]/g, '');
      const parsedPrice = parseFloat(numericString);
      
      return isNaN(parsedPrice) ? 0 : parsedPrice;
    }
    
    return 0;
  }
}

// Register the adapter with the registry if available
if (window.SourceRegistry) {
  window.SourceRegistry.registerSource(new EbayAdapter());
}

// Export globally
window.EbayAdapter = EbayAdapter;