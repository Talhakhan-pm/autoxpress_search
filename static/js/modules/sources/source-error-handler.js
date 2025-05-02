/**
 * Source Error Handler
 * Centralizes error handling for different data sources
 */

const SourceErrorHandler = (function() {
  // Configuration
  const config = {
    displayTimeout: 5000, // How long to show error messages
    retryDelay: 2000,     // Delay before auto-retry
    maxRetries: 2,        // Maximum number of auto-retries
    errorContainer: 'source-error-container',  // ID of error container element
    errorLogLimit: 20     // Limit of errors to keep in history
  };
  
  // Store error history for debugging
  const errorLog = [];
  
  // Store retry counts by source
  const retryCounters = {};
  
  // Store circuit breaker state
  const circuitBreakers = {};
  
  /**
   * Initialize error handler
   */
  function initialize() {
    // Create error container if it doesn't exist
    createErrorContainer();
    
    // Listen for source error events
    window.addEventListener('source-error', handleSourceError);
    
    // Listen for page visibility changes to clear errors when user returns
    document.addEventListener('visibilitychange', function() {
      if (!document.hidden) {
        clearErrorDisplay();
      }
    });
    
    console.log('SourceErrorHandler initialized');
  }
  
  /**
   * Handle source errors dispatched as custom events
   * @param {CustomEvent} event - Source error event
   */
  function handleSourceError(event) {
    if (!event || !event.detail) return;
    
    const { source, method, message, error } = event.detail;
    
    // Log the error
    logError({
      source,
      method,
      message,
      timestamp: new Date().toISOString(),
      error: error || null
    });
    
    // Check if the circuit breaker is open for this source
    if (isCircuitOpen(source)) {
      console.warn(`Circuit open for source ${source}, error suppressed`);
      return;
    }
    
    // Increment retry counter
    if (!retryCounters[source]) {
      retryCounters[source] = 0;
    }
    retryCounters[source]++;
    
    // Trip circuit breaker if too many errors
    if (retryCounters[source] > config.maxRetries) {
      tripCircuit(source);
      displayError({
        source,
        message: `${getSourceName(source)} is currently unavailable. We've disabled it temporarily.`,
        level: 'warning',
        persistent: true
      });
      return;
    }
    
    // Display error to user based on error type
    if (method === 'searchProducts') {
      displayError({
        source,
        message: `Could not retrieve products from ${getSourceName(source)}. ${retryCounters[source] <= config.maxRetries ? 'Retrying...' : ''}`,
        level: 'info',
        persistent: false
      });
      
      // Attempt retry if we haven't exceeded max retries
      if (retryCounters[source] <= config.maxRetries) {
        scheduleRetry(source);
      }
    } else if (method === 'initialize') {
      displayError({
        source,
        message: `Could not initialize ${getSourceName(source)}. Some products may not be available.`,
        level: 'warning',
        persistent: false
      });
      
      // No retry for initialization errors
    } else {
      // Generic error handling for other methods
      if (isUserVisibleError(message)) {
        displayError({
          source,
          message: `Error from ${getSourceName(source)}: ${message}`,
          level: 'error',
          persistent: false
        });
      } else {
        // Just log the error without displaying for non-user-visible errors
        console.error(`[${source}] Error in ${method}:`, error || message);
      }
    }
  }
  
  /**
   * Log an error to the error history
   * @param {Object} errorInfo - Error information
   */
  function logError(errorInfo) {
    errorLog.unshift(errorInfo);
    
    // Keep error log under the limit
    if (errorLog.length > config.errorLogLimit) {
      errorLog.pop();
    }
    
    // Log to console for debugging
    console.error(`[${errorInfo.source}] Error in ${errorInfo.method}:`, errorInfo.message);
    
    // Notify any monitoring systems
    if (window.PerformanceMonitor) {
      window.PerformanceMonitor.measure('sourceError', async () => {
        // Just a placeholder function to track the error
        return null;
      }, {
        source: errorInfo.source,
        method: errorInfo.method,
        message: errorInfo.message
      });
    }
  }
  
  /**
   * Display an error message to the user
   * @param {Object} options - Error display options
   */
  function displayError(options) {
    const container = document.getElementById(config.errorContainer);
    if (!container) return;
    
    // Create error element
    const errorEl = document.createElement('div');
    errorEl.className = `source-error source-error-${options.level || 'info'} source-${options.source.toLowerCase().replace(/\s+/g, '-')}`;
    
    // Add source-specific icon if available
    let sourceIcon = '';
    if (window.SourceManager) {
      const sourceConfig = window.SourceManager.getSourceConfig(options.source);
      if (sourceConfig && sourceConfig.icon) {
        sourceIcon = `<i class="${sourceConfig.icon}"></i>`;
      }
    }
    
    // Add close button if not persistent
    const closeBtn = options.persistent ? '' : '<button class="source-error-close">&times;</button>';
    
    // Create error message content
    errorEl.innerHTML = `
      <div class="source-error-content">
        ${sourceIcon}
        <span class="source-error-message">${options.message}</span>
        ${closeBtn}
      </div>
    `;
    
    // Add click handler for close button
    if (!options.persistent) {
      const closeButton = errorEl.querySelector('.source-error-close');
      if (closeButton) {
        closeButton.addEventListener('click', function() {
          errorEl.classList.add('source-error-hiding');
          setTimeout(() => {
            container.removeChild(errorEl);
          }, 300); // Match transition time in CSS
        });
      }
      
      // Auto-remove after timeout
      setTimeout(() => {
        if (errorEl.parentNode === container) {
          errorEl.classList.add('source-error-hiding');
          setTimeout(() => {
            if (errorEl.parentNode === container) {
              container.removeChild(errorEl);
            }
          }, 300); // Match transition time in CSS
        }
      }, config.displayTimeout);
    }
    
    // Add to container
    container.appendChild(errorEl);
    
    // Animate in
    setTimeout(() => {
      errorEl.classList.add('source-error-visible');
    }, 10);
  }
  
  /**
   * Create the error container if it doesn't exist
   */
  function createErrorContainer() {
    let container = document.getElementById(config.errorContainer);
    
    if (!container) {
      container = document.createElement('div');
      container.id = config.errorContainer;
      container.className = 'source-error-container';
      
      // Append to body
      document.body.appendChild(container);
    }
  }
  
  /**
   * Clear all displayed errors
   */
  function clearErrorDisplay() {
    const container = document.getElementById(config.errorContainer);
    if (!container) return;
    
    // Remove non-persistent errors
    const errors = container.querySelectorAll('.source-error:not(.source-error-persistent)');
    errors.forEach(error => {
      error.classList.add('source-error-hiding');
      setTimeout(() => {
        if (error.parentNode === container) {
          container.removeChild(error);
        }
      }, 300); // Match transition time in CSS
    });
  }
  
  /**
   * Schedule a retry for a source
   * @param {string} sourceId - ID of the source to retry
   */
  function scheduleRetry(sourceId) {
    setTimeout(() => {
      // Find the source
      if (window.SourceRegistry) {
        const source = window.SourceRegistry.getSource(sourceId);
        if (source) {
          console.log(`Retrying source: ${sourceId}`);
          
          // Retry logic would depend on how searches are triggered
          // This could dispatch an event or call a method directly
          
          // Example: Dispatch a retry event
          window.dispatchEvent(new CustomEvent('source-retry', {
            detail: { source: sourceId }
          }));
        }
      }
    }, config.retryDelay);
  }
  
  /**
   * Check if a circuit breaker is open for a source
   * @param {string} sourceId - Source ID to check
   * @returns {boolean} Whether the circuit is open
   */
  function isCircuitOpen(sourceId) {
    if (!circuitBreakers[sourceId]) return false;
    
    const breaker = circuitBreakers[sourceId];
    
    // Check if enough time has passed to try again
    if (Date.now() - breaker.trippedAt > breaker.resetTimeout) {
      // Reset the circuit breaker
      resetCircuit(sourceId);
      return false;
    }
    
    return true;
  }
  
  /**
   * Trip the circuit breaker for a source
   * @param {string} sourceId - Source ID to trip
   */
  function tripCircuit(sourceId) {
    console.warn(`Tripping circuit breaker for source: ${sourceId}`);
    
    circuitBreakers[sourceId] = {
      trippedAt: Date.now(),
      resetTimeout: 60000, // 1 minute before trying again
      tripCount: (circuitBreakers[sourceId]?.tripCount || 0) + 1
    };
    
    // Disable the source if possible
    if (window.SourceRegistry) {
      window.SourceRegistry.setSourceEnabled(sourceId, false);
    }
    
    // Reset retry counter for this source
    retryCounters[sourceId] = 0;
  }
  
  /**
   * Reset a circuit breaker for a source
   * @param {string} sourceId - Source ID to reset
   */
  function resetCircuit(sourceId) {
    console.log(`Resetting circuit breaker for source: ${sourceId}`);
    
    delete circuitBreakers[sourceId];
    
    // Reset retry counter
    retryCounters[sourceId] = 0;
    
    // Re-enable the source if possible
    if (window.SourceRegistry) {
      window.SourceRegistry.setSourceEnabled(sourceId, true);
    }
  }
  
  /**
   * Get a user-friendly source name
   * @param {string} sourceId - Source ID
   * @returns {string} User-friendly source name
   */
  function getSourceName(sourceId) {
    // Try to get the source name from SourceRegistry
    if (window.SourceRegistry) {
      const source = window.SourceRegistry.getSource(sourceId);
      if (source) {
        return source.getSourceInfo().name;
      }
    }
    
    // Fallback to source ID with nice formatting
    return sourceId.replace(/([A-Z])/g, ' $1').trim();
  }
  
  /**
   * Check if an error message should be shown to users
   * @param {string} message - Error message
   * @returns {boolean} Whether the error should be shown
   */
  function isUserVisibleError(message) {
    // Don't show technical errors to users
    const technicalErrors = [
      'undefined is not a function',
      'cannot read property',
      'is not defined',
      'syntax error',
      'unexpected token',
      'failed to fetch',
      'cors',
      'network error'
    ];
    
    message = (message || '').toLowerCase();
    
    return !technicalErrors.some(term => message.includes(term));
  }
  
  /**
   * Reset all error counters and circuit breakers
   */
  function resetAll() {
    // Reset retry counters
    Object.keys(retryCounters).forEach(key => {
      retryCounters[key] = 0;
    });
    
    // Reset circuit breakers
    Object.keys(circuitBreakers).forEach(key => {
      resetCircuit(key);
    });
    
    // Clear error display
    clearErrorDisplay();
    
    console.log('All source error counters and circuit breakers reset');
  }
  
  /**
   * Get the error history for debugging
   * @returns {Array} Error history
   */
  function getErrorHistory() {
    return [...errorLog];
  }
  
  // Initialize when the DOM is loaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
  } else {
    initialize();
  }
  
  // Return public API
  return {
    displayError,
    clearErrorDisplay,
    resetAll,
    getErrorHistory,
    isCircuitOpen
  };
})();

// Export globally
window.SourceErrorHandler = SourceErrorHandler;