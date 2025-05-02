/**
 * Performance Monitor Module
 * Monitors and logs performance metrics to help optimize application
 */

const PerformanceMonitor = (function() {
  // Configuration
  const config = {
    enabled: true,
    detailedLogging: false,
    maxEntries: 100
  };
  
  // Store for performance marks and measures
  const performanceData = {
    marks: {},
    measures: []
  };
  
  // Key operations we want to monitor
  const MONITORED_OPERATIONS = [
    'productRendering',
    'productRanking',
    'productFiltering',
    'imageLazyLoading',
    'dataFetching',
    'badgeRendering',
    'searchProcessing'
  ];
  
  /**
   * Start timing an operation
   * @param {string} operationName - Name of operation to time
   * @param {Object} metadata - Additional data about the operation
   */
  function startMeasure(operationName, metadata = {}) {
    if (!config.enabled) return;
    
    const markName = `${operationName}_start_${Date.now()}`;
    
    // Record the start time
    performanceData.marks[markName] = {
      time: performance.now(),
      metadata
    };
    
    if (config.detailedLogging) {
      console.log(`Performance: Started measuring ${operationName}`, metadata);
    }
    
    return markName;
  }
  
  /**
   * End timing an operation
   * @param {string} startMarkName - Name returned from startMeasure
   * @param {Object} additionalData - Additional data to include
   */
  function endMeasure(startMarkName, additionalData = {}) {
    if (!config.enabled || !performanceData.marks[startMarkName]) return;
    
    const endTime = performance.now();
    const startData = performanceData.marks[startMarkName];
    const duration = endTime - startData.time;
    
    // Parse operation name from start mark
    const operationName = startMarkName.split('_start_')[0];
    
    // Create measure entry
    const measure = {
      operation: operationName,
      startTime: startData.time,
      endTime,
      duration,
      metadata: {
        ...startData.metadata,
        ...additionalData
      },
      timestamp: new Date().toISOString()
    };
    
    // Add to measures array
    performanceData.measures.push(measure);
    
    // Trim measures if needed
    if (performanceData.measures.length > config.maxEntries) {
      performanceData.measures = performanceData.measures.slice(
        performanceData.measures.length - config.maxEntries
      );
    }
    
    // Clean up the mark
    delete performanceData.marks[startMarkName];
    
    if (config.detailedLogging) {
      console.log(`Performance: ${operationName} took ${duration.toFixed(2)}ms`, measure.metadata);
    }
    
    return duration;
  }
  
  /**
   * Get statistics for a specific operation
   * @param {string} operationName - Operation to get stats for
   * @returns {Object} Statistics for the operation
   */
  function getStats(operationName) {
    const measures = performanceData.measures.filter(
      m => m.operation === operationName
    );
    
    if (measures.length === 0) {
      return {
        operation: operationName,
        count: 0,
        avgDuration: 0,
        minDuration: 0,
        maxDuration: 0,
        totalDuration: 0
      };
    }
    
    // Calculate statistics
    const totalDuration = measures.reduce((sum, m) => sum + m.duration, 0);
    const avgDuration = totalDuration / measures.length;
    const minDuration = Math.min(...measures.map(m => m.duration));
    const maxDuration = Math.max(...measures.map(m => m.duration));
    
    return {
      operation: operationName,
      count: measures.length,
      avgDuration,
      minDuration,
      maxDuration,
      totalDuration,
      lastMeasure: measures[measures.length - 1]
    };
  }
  
  /**
   * Get all performance statistics
   * @returns {Object} Statistics for all operations
   */
  function getAllStats() {
    const stats = {};
    
    // Get stats for all monitored operations
    MONITORED_OPERATIONS.forEach(operation => {
      stats[operation] = getStats(operation);
    });
    
    return stats;
  }
  
  /**
   * Measure an operation with automatic start/end
   * @param {string} operationName - Operation name
   * @param {Function} fn - Function to measure
   * @param {Object} metadata - Additional metadata
   * @returns Result of the function
   */
  async function measure(operationName, fn, metadata = {}) {
    const markName = startMeasure(operationName, metadata);
    
    try {
      const result = await fn();
      endMeasure(markName, { success: true });
      return result;
    } catch (error) {
      endMeasure(markName, { success: false, error: error.message });
      throw error;
    }
  }
  
  /**
   * Log current performance stats
   */
  function logStats() {
    if (!config.enabled) return;
    
    const stats = getAllStats();
    console.log('Performance Statistics:', stats);
    
    return stats;
  }
  
  /**
   * Reset all performance data
   */
  function reset() {
    performanceData.marks = {};
    performanceData.measures = [];
  }
  
  /**
   * Toggle detailed logging
   * @param {boolean} enabled - Whether to enable detailed logging
   */
  function setDetailedLogging(enabled) {
    config.detailedLogging = !!enabled;
  }
  
  /**
   * Toggle performance monitoring
   * @param {boolean} enabled - Whether to enable performance monitoring
   */
  function setEnabled(enabled) {
    config.enabled = !!enabled;
  }
  
  // Public API
  return {
    startMeasure,
    endMeasure,
    measure,
    getStats,
    getAllStats,
    logStats,
    reset,
    setDetailedLogging,
    setEnabled
  };
})();

// Export globally
window.PerformanceMonitor = PerformanceMonitor;