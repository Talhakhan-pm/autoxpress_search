/**
 * Amazon Source Adapter
 * Implements a source adapter for Amazon auto parts search
 */

class AmazonAdapter extends SourceAdapter {
  /**
   * Constructor for the Amazon source adapter
   * @param {Object} config - Configuration options
   */
  constructor(config = {}) {
    // Set up the default configuration for Amazon
    const defaultConfig = {
      id: 'Amazon',
      name: 'Amazon',
      priority: 3, // Priority level (lower numbers = higher priority)
      maxResults: 50,
      timeout: 12000, // 12 seconds
      retryCount: 2,
      supportsRefinements: true
    };
    
    // Call parent constructor with merged config
    super(Object.assign({}, defaultConfig, config));
    
    // Amazon-specific properties
    this.apiEndpoint = '/amazon-search-proxy'; // This would be set up on the backend
    this.departmentId = 'auto-parts';
    this.cachedVehicleInfo = {};
  }
  
  /**
   * Initialize the adapter
   * @returns {Promise<boolean>} Success status
   */
  async initialize() {
    if (this.isInitialized) return true;
    
    try {
      // Since this is a new source, we'll just do a simple check to see
      // if the backend supports this endpoint
      const checkResponse = await this._checkEndpointAvailability();
      
      if (!checkResponse) {
        console.warn('[AmazonAdapter] Amazon search endpoint is not available');
        this.config.enabled = false;
        return false;
      }
      
      this.isInitialized = true;
      return true;
    } catch (error) {
      this._handleError(error, 'initialize');
      this.config.enabled = false;
      return false;
    }
  }
  
  /**
   * Check if the Amazon search endpoint is available
   * @returns {Promise<boolean>} Whether the endpoint is available
   * @private
   */
  async _checkEndpointAvailability() {
    try {
      // This is a mock implementation - in a real system, you'd check
      // if the endpoint is actually available
      
      // For this implementation, we'll assume the endpoint is available
      // but limit results to not overload the real sources
      return true;
    } catch (error) {
      return false;
    }
  }
  
  /**
   * Search for products from Amazon
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
      
      // This is a mock implementation - in a real system, you'd make an
      // actual API call to your backend proxy
      const results = await this._fetchMockResults(query, options);
      
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
   * Mock implementation of Amazon search
   * @param {string} query - Search query
   * @param {Object} options - Search options
   * @returns {Promise<Array>} - Mock results
   * @private
   */
  async _fetchMockResults(query, options = {}) {
    // Get vehicle information
    const vehicleInfo = this.cachedVehicleInfo;
    
    // Create a deterministic but variable set of results
    const seed = query.length + (vehicleInfo.year ? parseInt(vehicleInfo.year) : 0);
    const resultCount = 5 + (seed % 10); // Between 5-15 results
    
    // Build mock results
    const results = [];
    
    for (let i = 0; i < resultCount; i++) {
      const id = `amazon-${vehicleInfo.make || 'auto'}-${i}-${Date.now()}`;
      
      // Generate a product title based on search query and vehicle info
      let title = '';
      if (vehicleInfo.year && vehicleInfo.make && vehicleInfo.model) {
        title = `${vehicleInfo.year} ${vehicleInfo.make} ${vehicleInfo.model} `;
      }
      
      title += query;
      
      if (i % 3 === 0) {
        title += ' - Genuine OEM Part';
      } else if (i % 3 === 1) {
        title += ' - Premium Replacement';
      } else {
        title += ' - New Aftermarket';
      }
      
      // Generate a price
      const basePrice = 20 + (i * 15) + (seed % 30);
      const price = basePrice.toFixed(2);
      
      // Determine condition
      let condition;
      if (i % 4 === 0) {
        condition = 'Used - Like New';
      } else if (i % 4 === 1) {
        condition = 'Refurbished';
      } else {
        condition = 'New';
      }
      
      // Determine shipping
      let shipping;
      if (i % 3 === 0) {
        shipping = 'Free Shipping';
      } else if (i % 3 === 1) {
        shipping = 'Free with Prime';
      } else {
        shipping = '$5.99 Shipping';
      }
      
      results.push({
        id,
        title,
        price,
        condition,
        shipping,
        // Use a placeholder image based on the index
        image: `/static/placeholder-${(i % 3) + 1}.jpg`,
        link: `https://www.amazon.com/dp/${id}`,
        // Amazon-specific fields that will be stored in metadata
        prime: i % 3 === 1,
        rating: 3 + (i % 3),
        reviews: 10 + (i * 12),
        seller: i % 2 === 0 ? 'Amazon.com' : 'AutoPartsExpress',
        arrival: `Delivery by ${new Date(Date.now() + (2 + i % 3) * 86400000).toLocaleDateString()}`
      });
    }
    
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 800 + Math.random() * 1000));
    
    return results;
  }
  
  /**
   * Format Amazon product data to match the application's unified data model
   * @param {Object} rawProduct - Raw product data from Amazon
   * @returns {Object} - Formatted product data
   */
  formatProduct(rawProduct) {
    try {
      // Create a normalized product with required fields
      const formattedProduct = {
        id: rawProduct.id || `amazon-${Date.now()}-${Math.random().toString(36).substring(2, 10)}`,
        title: rawProduct.title || '',
        brand: rawProduct.brand || this.extractBrand(rawProduct.title || ''),
        partType: rawProduct.partType || this.extractPartType(rawProduct.title || ''),
        condition: rawProduct.condition || 'New',
        price: this.normalizePrice(rawProduct.price),
        originalPrice: this.normalizePrice(rawProduct.originalPrice || rawProduct.price),
        shipping: rawProduct.shipping || 'Standard Shipping',
        image: rawProduct.image || '/static/placeholder.png',
        fullImage: rawProduct.fullImage || rawProduct.image || '/static/placeholder.png',
        link: rawProduct.link || '#',
        source: 'Amazon',
        metadata: {
          prime: rawProduct.prime || false,
          rating: rawProduct.rating || 0,
          reviews: rawProduct.reviews || 0,
          seller: rawProduct.seller || '',
          arrival: rawProduct.arrival || ''
        }
      };
      
      // Copy any additional properties to metadata
      for (const key in rawProduct) {
        if (!formattedProduct.hasOwnProperty(key) && 
            !formattedProduct.metadata.hasOwnProperty(key)) {
          formattedProduct.metadata[key] = rawProduct[key];
        }
      }
      
      return formattedProduct;
    } catch (error) {
      this._handleError(error, 'formatProduct');
      // Return the raw product as a fallback
      return {
        ...rawProduct,
        source: 'Amazon'
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
    
    // Common Amazon auto part brands
    const commonBrands = [
      'ACDelco', 'Bosch', 'Motorcraft', 'Mopar', 'Genuine', 'OEM',
      'ECCPP', 'Dorman', 'Spectra Premium', 'Denso', 'Beck Arnley',
      'Replacement', 'TRQ', 'Monroe', 'KYB', 'Cardone', 'Moog',
      'Delphi', 'Standard Motor Products', 'Gates', 'Continental',
      'MotoRad', 'Dayco', 'NGK', 'Duralast', 'FRAM', 'Wagner'
    ];
    
    for (const brand of commonBrands) {
      if (title.toLowerCase().includes(brand.toLowerCase())) {
        return brand;
      }
    }
    
    if (title.toLowerCase().includes('genuine')) {
      return 'Genuine OEM';
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
  window.SourceRegistry.registerSource(new AmazonAdapter());
}

// Export globally
window.AmazonAdapter = AmazonAdapter;