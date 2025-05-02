/**
 * Source Manager Module
 * Manages source filtering, visualization and statistics
 */

const SourceManager = (function() {
  // Config
  const config = {
    sourceTypes: {
      'eBay': {
        name: 'eBay',
        icon: 'fab fa-ebay',
        color: '#e53238',
        badgeClass: 'source-ebay-badge',
        countElement: 'ebay-count'
      },
      'Google Shopping': {
        name: 'Google Shopping',
        icon: 'fab fa-google',
        color: '#4285F4',
        badgeClass: 'source-google-badge',
        countElement: 'google-count'
      }
    },
    distributionElement: 'source-distribution',
    emptyWarningElement: 'empty-source-warning',
    minHeight: 6  // Minimum height of distribution bar in pixels
  };
  
  /**
   * Initialize the source manager
   */
  function initialize() {
    // Add event listener for when products are displayed
    document.addEventListener('productsDisplayed', updateSourceDisplay);
    
    // Add event listener for filter changes
    document.addEventListener('filters-changed', handleFilterChange);
    
    // Initialize source display if products already exist
    if (window.productDisplay && window.productDisplay.getProducts().length > 0) {
      updateSourceDisplay();
    }
    
    console.log('Source manager initialized');
  }
  
  /**
   * Update source counts and distribution visualization
   */
  function updateSourceDisplay() {
    if (!window.productDisplay) return;
    
    const sourceCounts = window.productDisplay.getSourceCounts();
    const totalProducts = window.productDisplay.getProducts().length;
    
    if (totalProducts === 0) return;
    
    // Update count displays
    Object.keys(config.sourceTypes).forEach(sourceId => {
      const sourceConfig = config.sourceTypes[sourceId];
      const countElement = document.getElementById(sourceConfig.countElement);
      if (countElement) {
        const count = sourceCounts[sourceId] || 0;
        countElement.textContent = `(${count})`;
        
        // Update checkbox state based on availability
        const checkbox = document.querySelector(`[data-filter="source"][data-value="${sourceId}"]`);
        if (checkbox) {
          if (count === 0) {
            checkbox.disabled = true;
            checkbox.parentElement.classList.add('disabled');
          } else {
            checkbox.disabled = false;
            checkbox.parentElement.classList.remove('disabled');
          }
        }
      }
    });
    
    // Update distribution visualization
    updateDistributionVisualization(sourceCounts, totalProducts);
  }
  
  /**
   * Handle source filter changes
   * @param {Event} event - filters-changed event
   */
  function handleFilterChange(event) {
    if (!event.detail || !event.detail.filters || !event.detail.filters.source) return;
    
    // Show warning if no sources are selected
    const selectedSources = event.detail.filters.source;
    const warningElement = document.getElementById(config.emptyWarningElement);
    
    if (warningElement) {
      if (selectedSources.length === 0) {
        warningElement.classList.add('visible');
      } else {
        warningElement.classList.remove('visible');
      }
    }
  }
  
  /**
   * Update the distribution visualization
   * @param {Object} sourceCounts - Counts by source
   * @param {number} totalProducts - Total number of products
   */
  function updateDistributionVisualization(sourceCounts, totalProducts) {
    const distributionElement = document.getElementById(config.distributionElement);
    if (!distributionElement) return;
    
    // Clear previous visualization
    distributionElement.innerHTML = '';
    
    // Create distribution bars
    Object.keys(config.sourceTypes).forEach(sourceId => {
      const sourceConfig = config.sourceTypes[sourceId];
      const count = sourceCounts[sourceId] || 0;
      const percentage = totalProducts > 0 ? (count / totalProducts) * 100 : 0;
      
      if (percentage > 0) {
        const barElement = document.createElement('div');
        barElement.className = `source-stat-bar source-${sourceId.toLowerCase().replace(/\s+/g, '-')}-bar`;
        barElement.style.width = `${percentage}%`;
        if (percentage < 5) {
          barElement.style.width = '5%'; // Minimum visible width
        }
        
        distributionElement.appendChild(barElement);
      }
    });
    
    // If distribution is empty, hide the element
    if (distributionElement.children.length === 0) {
      distributionElement.style.display = 'none';
    } else {
      distributionElement.style.display = 'flex';
    }
  }
  
  /**
   * Create source badges for applied filters display
   * @param {Array} sources - Active source filters
   * @returns {string} HTML for source badges
   */
  function createSourceBadges(sources) {
    if (!sources || sources.length === 0) return '';
    
    // Don't show badges if all sources are selected
    const allSourceIds = Object.keys(config.sourceTypes);
    if (sources.length === allSourceIds.length && 
        allSourceIds.every(id => sources.includes(id))) {
      return '';
    }
    
    // Create badges for selected sources
    return sources.map(sourceId => {
      const sourceConfig = config.sourceTypes[sourceId] || {
        name: sourceId,
        icon: 'fas fa-tag',
        badgeClass: ''
      };
      
      return `
        <span class="source-badge ${sourceConfig.badgeClass}" data-filter="source" data-value="${sourceId}">
          <i class="${sourceConfig.icon}"></i>
          ${sourceConfig.name}
          <i class="fas fa-times-circle ml-1 remove-filter"></i>
        </span>
      `;
    }).join('');
  }
  
  // Initialize source manager when DOM is loaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
  } else {
    initialize();
  }
  
  // Return public API
  return {
    updateSourceDisplay,
    createSourceBadges,
    getSourceConfig: function(sourceId) {
      return config.sourceTypes[sourceId] || null;
    }
  };
})();

// Export globally
window.SourceManager = SourceManager;