/**
 * Error Handler Module
 * Provides centralized error handling, reporting, and recovery
 */

const ErrorHandler = (function() {
  // Configuration
  const config = {
    enabled: true,
    logErrors: true,
    showUserFriendlyMessages: true,
    maxErrorsStored: 50,
    errorTypes: {
      NETWORK: 'network',
      DATA: 'data',
      RENDERING: 'rendering',
      MODULE: 'module',
      INITIALIZATION: 'initialization',
      UNKNOWN: 'unknown'
    }
  };
  
  // Storage for caught errors
  const errorLog = [];
  
  // Error count by type for analytics
  const errorCounts = {};
  
  // Element to display user-friendly errors
  let errorContainer = null;
  
  /**
   * Initialize the error handler
   */
  function initialize() {
    // Reset error counts
    Object.keys(config.errorTypes).forEach(key => {
      errorCounts[config.errorTypes[key]] = 0;
    });
    
    // Find or create error container for UI errors
    if (config.showUserFriendlyMessages) {
      errorContainer = document.getElementById('error-container');
      if (!errorContainer) {
        errorContainer = document.createElement('div');
        errorContainer.id = 'error-container';
        errorContainer.className = 'error-container';
        errorContainer.style.display = 'none';
        document.body.appendChild(errorContainer);
      }
    }
    
    // Set up global error handling
    if (config.enabled) {
      window.addEventListener('error', function(event) {
        handleError(event.error || new Error(event.message), config.errorTypes.UNKNOWN);
        
        // Prevent default browser error handling
        event.preventDefault();
        return true;
      });
      
      // Handle promise rejections
      window.addEventListener('unhandledrejection', function(event) {
        handleError(event.reason || new Error('Unhandled Promise Rejection'), config.errorTypes.UNKNOWN);
        
        // Prevent default browser error handling
        event.preventDefault();
        return true;
      });
      
      console.log('Error handler initialized');
    }
  }
  
  /**
   * Handle an error
   * @param {Error} error - The error object
   * @param {string} type - Type of error from config.errorTypes
   * @param {Object} metadata - Additional information about the error
   */
  function handleError(error, type = config.errorTypes.UNKNOWN, metadata = {}) {
    if (!config.enabled) return;
    
    // Ensure type is valid
    if (!Object.values(config.errorTypes).includes(type)) {
      type = config.errorTypes.UNKNOWN;
    }
    
    // Format error for logging
    const errorInfo = {
      message: error.message || 'Unknown error',
      stack: error.stack,
      type: type,
      timestamp: new Date().toISOString(),
      metadata: {
        url: window.location.href,
        userAgent: navigator.userAgent,
        ...metadata
      }
    };
    
    // Increment error count
    errorCounts[type] = (errorCounts[type] || 0) + 1;
    
    // Add to error log
    errorLog.push(errorInfo);
    
    // Trim error log if needed
    if (errorLog.length > config.maxErrorsStored) {
      errorLog.shift();
    }
    
    // Log to console if enabled
    if (config.logErrors) {
      console.error(`[${type.toUpperCase()}] ${errorInfo.message}`, metadata);
      if (error.stack) {
        console.error(error.stack);
      }
    }
    
    // Show user-friendly message if enabled
    if (config.showUserFriendlyMessages && errorContainer) {
      showUserFriendlyError(errorInfo);
    }
    
    // Dispatch error event for external handling
    document.dispatchEvent(new CustomEvent('app-error', {
      detail: { error: errorInfo }
    }));
    
    // Return formatted error info
    return errorInfo;
  }
  
  /**
   * Show a user-friendly error message
   * @param {Object} errorInfo - Error information
   */
  function showUserFriendlyError(errorInfo) {
    // Only show critical errors to user
    if (!shouldShowToUser(errorInfo)) return;
    
    // Create or update error message
    errorContainer.style.display = 'block';
    
    const message = getUserFriendlyMessage(errorInfo);
    
    // Create error notification
    const errorNotification = document.createElement('div');
    errorNotification.className = `error-notification error-${errorInfo.type}`;
    errorNotification.innerHTML = `
      <div class="error-icon"><i class="fas fa-exclamation-circle"></i></div>
      <div class="error-message">${message}</div>
      <button class="error-close">×</button>
    `;
    
    // Add close functionality
    const closeButton = errorNotification.querySelector('.error-close');
    if (closeButton) {
      closeButton.addEventListener('click', function() {
        errorNotification.remove();
        
        // Hide container if empty
        if (errorContainer.children.length === 0) {
          errorContainer.style.display = 'none';
        }
      });
    }
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
      if (errorNotification.parentNode) {
        errorNotification.remove();
        
        // Hide container if empty
        if (errorContainer.children.length === 0) {
          errorContainer.style.display = 'none';
        }
      }
    }, 5000);
    
    // Add to container
    errorContainer.appendChild(errorNotification);
  }
  
  /**
   * Determine if error should be shown to user
   * @param {Object} errorInfo - Error information
   * @returns {boolean} Whether to show to user
   */
  function shouldShowToUser(errorInfo) {
    // Hide minor errors or repetitive alerts
    return true;
  }
  
  /**
   * Get user-friendly message for error
   * @param {Object} errorInfo - Error information
   * @returns {string} User-friendly message
   */
  function getUserFriendlyMessage(errorInfo) {
    // Map technical errors to user-friendly messages
    switch (errorInfo.type) {
      case config.errorTypes.NETWORK:
        return 'There was a problem connecting to the server. Please check your internet connection.';
        
      case config.errorTypes.DATA:
        return 'There was a problem processing data. Please try refreshing the page.';
        
      case config.errorTypes.RENDERING:
        return 'There was a problem displaying content. Please try refreshing the page.';
        
      case config.errorTypes.MODULE:
        return 'A component failed to load properly. Please try refreshing the page.';
        
      case config.errorTypes.INITIALIZATION:
        return 'The application did not start properly. Please try refreshing the page.';
        
      default:
        return 'An unexpected error occurred. Please try again later.';
    }
  }
  
  /**
   * Clear all recorded errors
   */
  function clearErrors() {
    errorLog.length = 0;
    
    // Reset error counts
    Object.keys(errorCounts).forEach(key => {
      errorCounts[key] = 0;
    });
    
    // Clear UI
    if (errorContainer) {
      errorContainer.innerHTML = '';
      errorContainer.style.display = 'none';
    }
  }
  
  /**
   * Get error statistics
   * @returns {Object} Error stats by type
   */
  function getErrorStats() {
    return {
      totalErrors: errorLog.length,
      countByType: { ...errorCounts },
      recentErrors: errorLog.slice(-5)
    };
  }
  
  /**
   * Try to recover from common errors
   * @param {string} errorType - Type of error to recover from
   * @returns {boolean} Whether recovery was attempted
   */
  function attemptRecovery(errorType) {
    switch (errorType) {
      case config.errorTypes.NETWORK:
        // Retry network requests
        if (window.productDisplay && window.productDisplay.refreshData) {
          window.productDisplay.refreshData();
          return true;
        }
        break;
        
      case config.errorTypes.RENDERING:
        // Try to refresh the display
        if (window.productDisplay && window.productDisplay.displayProductsPage) {
          window.productDisplay.displayProductsPage();
          return true;
        }
        break;
        
      case config.errorTypes.MODULE:
        // Try to reinitialize modules
        if (window.LazyLoader) {
          window.LazyLoader.initialize();
        }
        return true;
    }
    
    return false;
  }
  
  /**
   * Creates a wrapped function with error handling
   * @param {Function} fn - Function to wrap
   * @param {string} errorType - Type of error
   * @param {Object} metadata - Additional metadata
   * @returns {Function} Wrapped function
   */
  function withErrorHandling(fn, errorType = config.errorTypes.UNKNOWN, metadata = {}) {
    return function(...args) {
      try {
        return fn.apply(this, args);
      } catch (error) {
        handleError(error, errorType, {
          arguments: args,
          ...metadata
        });
        return undefined;
      }
    };
  }
  
  /**
   * Handle network errors specifically
   * @param {Error} error - Network error
   * @param {string} url - URL that failed
   * @param {Object} options - Fetch options used
   */
  function handleNetworkError(error, url, options = {}) {
    handleError(error, config.errorTypes.NETWORK, {
      url,
      method: options.method || 'GET',
      status: error.status || 'unknown'
    });
  }
  
  /**
   * Handle data processing errors
   * @param {Error} error - Data error
   * @param {string} dataType - Type of data being processed
   * @param {Object} sampleData - Sample of problematic data
   */
  function handleDataError(error, dataType, sampleData = {}) {
    handleError(error, config.errorTypes.DATA, {
      dataType,
      sampleData: JSON.stringify(sampleData).substring(0, 200) // Truncate for log size
    });
  }
  
  // Initialize on load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
  } else {
    initialize();
  }
  
  // Public API
  return {
    // Error handling
    handleError,
    handleNetworkError,
    handleDataError,
    
    // Utility methods
    withErrorHandling,
    clearErrors,
    getErrorStats,
    attemptRecovery,
    
    // Configuration
    errorTypes: config.errorTypes,
    
    // Enable/disable
    setEnabled: function(enabled) {
      config.enabled = !!enabled;
    },
    
    // Control logging
    setLogErrors: function(logErrors) {
      config.logErrors = !!logErrors;
    }
  };
})();

// Export globally
window.ErrorHandler = ErrorHandler;