/**
 * Source Adapter Interface
 * Defines the standard interface for all product data sources
 */

/**
 * Base Source Adapter class that all source implementations must extend
 * This provides a consistent interface for product data retrieval
 */
class SourceAdapter {
  /**
   * Constructor for the source adapter
   * @param {Object} config - Configuration options for the source
   */
  constructor(config = {}) {
    this.config = Object.assign({
      enabled: true,
      name: 'Unknown Source',
      id: 'unknown',
      priority: 10,
      maxResults: 50,
      timeout: 10000, // 10 seconds
      retryCount: 1,
      supportsRefinements: false
    }, config);
    
    this.isInitialized = false;
  }

  /**
   * Initialize the source adapter
   * @returns {Promise<boolean>} - Success status
   */
  async initialize() {
    if (this.isInitialized) return true;
    
    try {
      // Source-specific initialization logic should be implemented by subclasses
      this.isInitialized = true;
      return true;
    } catch (error) {
      console.error(`[${this.config.name}] Initialization failed:`, error);
      return false;
    }
  }

  /**
   * Search for products from this source
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
      // This should be implemented by specific source adapters
      throw new Error('searchProducts method must be implemented by subclass');
    } catch (error) {
      this._handleError(error, 'searchProducts');
      return [];
    }
  }

  /**
   * Format raw product data to match the application's unified data model
   * @param {Object} rawProduct - Raw product data from the source
   * @returns {Object} - Formatted product data
   */
  formatProduct(rawProduct) {
    try {
      // This should be implemented by specific source adapters
      throw new Error('formatProduct method must be implemented by subclass');
    } catch (error) {
      this._handleError(error, 'formatProduct');
      return null;
    }
  }

  /**
   * Get the source information object
   * @returns {Object} - Source metadata
   */
  getSourceInfo() {
    return {
      id: this.config.id,
      name: this.config.name,
      enabled: this.config.enabled,
      priority: this.config.priority,
      supportsRefinements: this.config.supportsRefinements
    };
  }

  /**
   * Handle source-specific errors
   * @param {Error} error - The error object
   * @param {string} methodName - The name of the method where the error occurred
   * @private
   */
  _handleError(error, methodName) {
    console.error(`[${this.config.name}] Error in ${methodName}:`, error);
    
    // Dispatch error event for central error handling
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('source-error', {
        detail: {
          source: this.config.id,
          method: methodName,
          message: error.message,
          error: error
        }
      }));
    }
  }

  /**
   * Set the enabled state of this source
   * @param {boolean} enabled - Whether the source is enabled
   */
  setEnabled(enabled) {
    this.config.enabled = !!enabled;
  }
}

// Export the SourceAdapter class
window.SourceAdapter = SourceAdapter;