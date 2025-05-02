/**
 * Source Registry System
 * Manages registration and access to all product data sources
 */

const SourceRegistry = (function() {
  // Registry of all source adapters
  const sources = {};
  
  // Default source priority order (lower number = higher priority)
  const DEFAULT_PRIORITY = 10;
  
  // Configuration
  const config = {
    enableAllByDefault: true,
    defaultTimeout: 10000
  };
  
  /**
   * Register a source adapter with the registry
   * @param {SourceAdapter} sourceAdapter - The source adapter instance to register
   * @returns {boolean} - Success status
   */
  function registerSource(sourceAdapter) {
    if (!sourceAdapter || typeof sourceAdapter.getSourceInfo !== 'function') {
      console.error('Invalid source adapter provided to registerSource');
      return false;
    }
    
    try {
      const sourceInfo = sourceAdapter.getSourceInfo();
      
      if (!sourceInfo.id) {
        console.error('Source adapter must have an ID');
        return false;
      }
      
      // Check if source is already registered
      if (sources[sourceInfo.id]) {
        console.warn(`Source ${sourceInfo.id} is already registered and will be replaced`);
      }
      
      // Store the source adapter
      sources[sourceInfo.id] = sourceAdapter;
      
      // Log successful registration
      console.log(`Source registered: ${sourceInfo.name} (${sourceInfo.id})`);
      
      // Dispatch event for source registration
      window.dispatchEvent(new CustomEvent('source-registered', {
        detail: { source: sourceInfo }
      }));
      
      return true;
    } catch (error) {
      console.error('Error registering source:', error);
      return false;
    }
  }
  
  /**
   * Get a source adapter by ID
   * @param {string} sourceId - The ID of the source to retrieve
   * @returns {SourceAdapter|null} - The source adapter instance or null if not found
   */
  function getSource(sourceId) {
    return sources[sourceId] || null;
  }
  
  /**
   * Get all registered source adapters
   * @param {boolean} enabledOnly - If true, return only enabled sources
   * @returns {Array} - Array of source adapter instances
   */
  function getAllSources(enabledOnly = false) {
    const sourceList = Object.values(sources);
    
    if (enabledOnly) {
      return sourceList.filter(source => {
        const info = source.getSourceInfo();
        return info.enabled;
      });
    }
    
    return sourceList;
  }
  
  /**
   * Get source info for all registered sources
   * @param {boolean} enabledOnly - If true, return only enabled sources
   * @returns {Array} - Array of source info objects
   */
  function getSourcesInfo(enabledOnly = false) {
    return getAllSources(enabledOnly).map(source => source.getSourceInfo());
  }
  
  /**
   * Enable or disable a specific source
   * @param {string} sourceId - The ID of the source
   * @param {boolean} enabled - Whether to enable or disable the source
   */
  function setSourceEnabled(sourceId, enabled) {
    const source = getSource(sourceId);
    
    if (source) {
      source.setEnabled(enabled);
      
      // Dispatch event for source state change
      window.dispatchEvent(new CustomEvent('source-state-changed', {
        detail: { 
          source: sourceId, 
          enabled: enabled 
        }
      }));
    }
  }
  
  /**
   * Initialize all registered sources
   * @returns {Promise<Array>} - Results of initialization
   */
  async function initializeAllSources() {
    const initPromises = Object.values(sources).map(async (source) => {
      try {
        const result = await source.initialize();
        return { 
          source: source.getSourceInfo().id, 
          success: result 
        };
      } catch (error) {
        console.error(`Error initializing source ${source.getSourceInfo().id}:`, error);
        return { 
          source: source.getSourceInfo().id, 
          success: false, 
          error: error.message 
        };
      }
    });
    
    return Promise.all(initPromises);
  }
  
  /**
   * Search for products using all enabled sources
   * @param {string} query - Search query text
   * @param {Object} options - Additional search options
   * @returns {Promise<Object>} - Object with results from each source
   */
  async function searchAllSources(query, options = {}) {
    // Get all enabled sources
    const enabledSources = getAllSources(true);
    
    if (enabledSources.length === 0) {
      console.warn('No enabled sources found for search');
      return { results: [], sourceResults: {} };
    }
    
    // Track performance if the module is available
    let performanceMark = null;
    if (window.PerformanceMonitor) {
      performanceMark = window.PerformanceMonitor.startMeasure('sourceSearch', {
        query,
        sourceCount: enabledSources.length
      });
    }
    
    // Create a map to store results by source
    const sourceResults = {};
    
    // Search each source in parallel
    const searchPromises = enabledSources.map(async (source) => {
      const sourceInfo = source.getSourceInfo();
      
      try {
        // Track source-specific performance
        let sourcePerformanceMark = null;
        if (window.PerformanceMonitor) {
          sourcePerformanceMark = window.PerformanceMonitor.startMeasure('sourceSearch_' + sourceInfo.id, {
            query,
            source: sourceInfo.id
          });
        }
        
        // Execute the search
        const results = await source.searchProducts(query, options);
        
        // End source-specific performance tracking
        if (sourcePerformanceMark && window.PerformanceMonitor) {
          window.PerformanceMonitor.endMeasure(sourcePerformanceMark, {
            success: true,
            resultCount: results.length
          });
        }
        
        // Store the results
        sourceResults[sourceInfo.id] = {
          success: true,
          source: sourceInfo,
          results: results || []
        };
        
        return results;
      } catch (error) {
        console.error(`Error searching source ${sourceInfo.id}:`, error);
        
        // End source-specific performance tracking with error
        if (sourcePerformanceMark && window.PerformanceMonitor) {
          window.PerformanceMonitor.endMeasure(sourcePerformanceMark, {
            success: false,
            error: error.message
          });
        }
        
        // Store the error
        sourceResults[sourceInfo.id] = {
          success: false,
          source: sourceInfo,
          error: error.message,
          results: []
        };
        
        return [];
      }
    });
    
    // Wait for all searches to complete
    await Promise.all(searchPromises);
    
    // Combine all results
    const allResults = [];
    Object.values(sourceResults).forEach(sourceResult => {
      if (sourceResult.success && Array.isArray(sourceResult.results)) {
        allResults.push(...sourceResult.results);
      }
    });
    
    // End overall performance tracking
    if (performanceMark && window.PerformanceMonitor) {
      window.PerformanceMonitor.endMeasure(performanceMark, {
        success: true,
        totalResultCount: allResults.length,
        sourceCount: Object.keys(sourceResults).length
      });
    }
    
    // Return combined results and source-specific results
    return {
      results: allResults,
      sourceResults: sourceResults
    };
  }
  
  /**
   * Reset the registry (mainly for testing)
   */
  function resetRegistry() {
    Object.keys(sources).forEach(key => {
      delete sources[key];
    });
  }
  
  // Listen for events
  document.addEventListener('DOMContentLoaded', function() {
    // Initialize all sources when the page loads
    initializeAllSources()
      .then(results => {
        console.log('Source initialization completed:', results);
      })
      .catch(error => {
        console.error('Error during source initialization:', error);
      });
  });
  
  // Public API
  return {
    registerSource,
    getSource,
    getAllSources,
    getSourcesInfo,
    setSourceEnabled,
    initializeAllSources,
    searchAllSources,
    resetRegistry,
    // Export configuration
    getConfig: () => ({ ...config })
  };
})();

// Export globally
window.SourceRegistry = SourceRegistry;