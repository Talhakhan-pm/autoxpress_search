/**
 * Enhanced Source Manager Module
 * Extends the existing Source Manager to work with the new source adapter system
 * while maintaining backward compatibility
 */

const EnhancedSourceManager = (function() {
  // Original source configuration
  const originalConfig = {
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
      },
      // Add the new source configuration
      'Amazon': {
        name: 'Amazon',
        icon: 'fab fa-amazon',
        color: '#FF9900',
        badgeClass: 'source-amazon-badge',
        countElement: 'amazon-count'
      }
    },
    distributionElement: 'source-distribution',
    emptyWarningElement: 'empty-source-warning',
    minHeight: 6
  };
  
  // Store the original source manager
  let originalSourceManager = null;
  
  /**
   * Initialize the enhanced source manager
   */
  function initialize() {
    // Store reference to original source manager if it exists
    if (window.SourceManager) {
      originalSourceManager = window.SourceManager;
      console.log('Original SourceManager found, enhancing capabilities');
    } else {
      console.warn('Original SourceManager not found, initializing from scratch');
    }
    
    // Add event listener for when sources are registered in the registry
    window.addEventListener('source-registered', handleSourceRegistered);
    
    // Add event listener for source state changes
    window.addEventListener('source-state-changed', handleSourceStateChanged);
    
    // Register existing sources with the registry if available
    registerExistingSources();
    
    // Update all product config with the new source types
    updateProductConfig();
    
    // Initialize original functionality for backward compatibility
    if (originalSourceManager && typeof originalSourceManager.updateSourceDisplay === 'function') {
      originalSourceManager.updateSourceDisplay();
    }
    
    console.log('Enhanced source manager initialized');
  }
  
  /**
   * Register existing sources with the registry
   */
  function registerExistingSources() {
    if (!window.SourceRegistry) return;
    
    // Get existing sources from product config
    const existingSources = window.productDisplay?.getProductConfig()?.availableSources || [];
    
    // Update source display counts
    updateSourceCounts();
    
    console.log('Existing sources registered with registry');
  }
  
  /**
   * Handle a new source being registered in the registry
   * @param {CustomEvent} event - Source registered event
   */
  function handleSourceRegistered(event) {
    if (!event || !event.detail || !event.detail.source) return;
    
    const sourceInfo = event.detail.source;
    
    // Add the source type to our configuration if it doesn't exist
    if (!originalConfig.sourceTypes[sourceInfo.id]) {
      const iconClass = getIconClassForSource(sourceInfo.id);
      
      originalConfig.sourceTypes[sourceInfo.id] = {
        name: sourceInfo.name,
        icon: iconClass,
        color: getColorForSource(sourceInfo.id),
        badgeClass: `source-${sourceInfo.id.toLowerCase().replace(/\s+/g, '-')}-badge`,
        countElement: `${sourceInfo.id.toLowerCase().replace(/\s+/g, '-')}-count`
      };
    }
    
    // Update product config with new source
    updateProductConfig();
    
    // Refresh UI to show new source
    updateSourceDisplay();
    
    console.log(`Source registered with enhanced manager: ${sourceInfo.name}`);
  }
  
  /**
   * Handle a source state change event
   * @param {CustomEvent} event - Source state changed event
   */
  function handleSourceStateChanged(event) {
    if (!event || !event.detail) return;
    
    const { source, enabled } = event.detail;
    
    // Update UI to reflect the state change
    updateSourceDisplay();
    
    console.log(`Source state changed: ${source} (enabled: ${enabled})`);
  }
  
  /**
   * Get an icon class for a source based on its ID
   * @param {string} sourceId - Source ID
   * @returns {string} Icon class
   */
  function getIconClassForSource(sourceId) {
    // Common mappings
    const iconMappings = {
      'eBay': 'fab fa-ebay',
      'Google Shopping': 'fab fa-google',
      'Amazon': 'fab fa-amazon',
      'Walmart': 'fab fa-walmart',
      'CarParts': 'fas fa-car',
      'AutoZone': 'fas fa-car-alt',
      'RockAuto': 'fas fa-tools',
      'NAPA': 'fas fa-oil-can'
    };
    
    return iconMappings[sourceId] || 'fas fa-shopping-cart';
  }
  
  /**
   * Get a color for a source based on its ID
   * @param {string} sourceId - Source ID
   * @returns {string} Color code
   */
  function getColorForSource(sourceId) {
    // Common mappings
    const colorMappings = {
      'eBay': '#e53238',
      'Google Shopping': '#4285F4',
      'Amazon': '#FF9900',
      'Walmart': '#0071ce',
      'CarParts': '#e31837',
      'AutoZone': '#d52b1e',
      'RockAuto': '#294ba1',
      'NAPA': '#3064b1'
    };
    
    return colorMappings[sourceId] || '#555555';
  }
  
  /**
   * Update the product configuration with the new source types
   */
  function updateProductConfig() {
    if (!window.productDisplay || !window.productDisplay.getProductConfig) return;
    
    const productConfig = window.productDisplay.getProductConfig();
    if (!productConfig) return;
    
    // Get a list of all registered sources from the registry
    let availableSources = [];
    
    if (window.SourceRegistry) {
      const sourcesInfo = window.SourceRegistry.getSourcesInfo();
      
      availableSources = sourcesInfo.map(source => ({
        id: source.id,
        name: source.name,
        icon: getIconClassForSource(source.id),
        color: getColorForSource(source.id)
      }));
    } else {
      // Fallback to original config
      availableSources = Object.keys(originalConfig.sourceTypes).map(id => ({
        id,
        name: originalConfig.sourceTypes[id].name,
        icon: originalConfig.sourceTypes[id].icon,
        color: originalConfig.sourceTypes[id].color
      }));
    }
    
    // Update the product config with the combined source list
    if (productConfig.availableSources) {
      // Preserve existing sources and add new ones
      const existingSourceIds = productConfig.availableSources.map(s => s.id);
      
      availableSources.forEach(source => {
        if (!existingSourceIds.includes(source.id)) {
          productConfig.availableSources.push(source);
        }
      });
    } else {
      productConfig.availableSources = availableSources;
    }
    
    // Ensure the active filters include all available sources by default
    if (productConfig.activeFilters && productConfig.activeFilters.source) {
      const availableSourceIds = availableSources.map(s => s.id);
      
      // Add any missing sources to active filters
      availableSourceIds.forEach(id => {
        if (!productConfig.activeFilters.source.includes(id)) {
          productConfig.activeFilters.source.push(id);
        }
      });
    }
    
    // Update UI elements
    updateSourceFilterUI();
  }
  
  /**
   * Update the source filter UI to include all available sources
   */
  function updateSourceFilterUI() {
    if (!window.productDisplay || !window.productDisplay.getProductConfig) return;
    
    const productConfig = window.productDisplay.getProductConfig();
    if (!productConfig || !productConfig.availableSources) return;
    
    // Find the source filter container
    const sourceFilterContainer = document.querySelector('.source-filters');
    if (!sourceFilterContainer) return;
    
    // Create checkboxes for each source
    productConfig.availableSources.forEach(source => {
      // Check if a filter for this source already exists
      const existingFilter = sourceFilterContainer.querySelector(`[data-filter="source"][data-value="${source.id}"]`);
      if (existingFilter) return;
      
      // Create a new source filter item
      const filterItem = document.createElement('div');
      filterItem.className = 'source-filter-item';
      
      // Create the checkbox
      const checkbox = document.createElement('input');
      checkbox.type = 'checkbox';
      checkbox.id = `source-${source.id.toLowerCase().replace(/\s+/g, '-')}`;
      checkbox.className = 'filter-check';
      checkbox.dataset.filter = 'source';
      checkbox.dataset.value = source.id;
      checkbox.checked = productConfig.activeFilters.source.includes(source.id);
      
      // Create the label
      const label = document.createElement('label');
      label.htmlFor = checkbox.id;
      label.innerHTML = `
        <i class="${source.icon}" style="color: ${source.color};"></i>
        ${source.name}
        <span class="badge-count" id="${source.id.toLowerCase().replace(/\s+/g, '-')}-count">(0)</span>
      `;
      
      // Add event listener to checkbox
      checkbox.addEventListener('change', function() {
        // Update active filters
        if (this.checked) {
          if (!productConfig.activeFilters.source.includes(source.id)) {
            productConfig.activeFilters.source.push(source.id);
          }
        } else {
          productConfig.activeFilters.source = productConfig.activeFilters.source.filter(
            val => val !== source.id
          );
        }
        
        // Apply filters
        if (window.applyFilters) {
          window.applyFilters();
        }
      });
      
      // Add to the filter item
      filterItem.appendChild(checkbox);
      filterItem.appendChild(label);
      
      // Add to the source filter container
      sourceFilterContainer.appendChild(filterItem);
    });
  }
  
  /**
   * Update source counts and distribution visualization
   */
  function updateSourceCounts() {
    if (!window.productDisplay) return;
    
    // Get product counts by source
    const sourceCounts = typeof window.productDisplay.getSourceCounts === 'function' ? 
                        window.productDisplay.getSourceCounts() : {};
    
    // Get all products
    const allProducts = typeof window.productDisplay.getProducts === 'function' ? 
                      window.productDisplay.getProducts() : [];
    
    const totalProducts = allProducts.length;
    
    if (totalProducts === 0) return;
    
    // Update count displays for each source
    Object.keys(originalConfig.sourceTypes).forEach(sourceId => {
      const sourceConfig = originalConfig.sourceTypes[sourceId];
      const countElementId = sourceConfig.countElement;
      
      const countElement = document.getElementById(countElementId);
      if (countElement) {
        const count = sourceCounts[sourceId] || 0;
        countElement.textContent = `(${count})`;
        
        // Update checkbox state based on availability
        const checkbox = document.querySelector(`[data-filter="source"][data-value="${sourceId}"]`);
        if (checkbox) {
          if (count === 0) {
            checkbox.disabled = true;
            if (checkbox.parentElement) {
              checkbox.parentElement.classList.add('disabled');
            }
          } else {
            checkbox.disabled = false;
            if (checkbox.parentElement) {
              checkbox.parentElement.classList.remove('disabled');
            }
          }
        }
      }
    });
    
    // Update distribution visualization
    updateDistributionVisualization(sourceCounts, totalProducts);
    
    // If original source manager exists, delegate to it
    if (originalSourceManager && typeof originalSourceManager.updateSourceDisplay === 'function') {
      originalSourceManager.updateSourceDisplay();
    }
  }
  
  /**
   * Update the distribution visualization
   * @param {Object} sourceCounts - Counts by source
   * @param {number} totalProducts - Total number of products
   */
  function updateDistributionVisualization(sourceCounts, totalProducts) {
    const distributionElement = document.getElementById(originalConfig.distributionElement);
    if (!distributionElement) return;
    
    // Clear previous visualization
    distributionElement.innerHTML = '';
    
    // Create distribution bars
    Object.keys(originalConfig.sourceTypes).forEach(sourceId => {
      const sourceConfig = originalConfig.sourceTypes[sourceId];
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
    
    // Get all available sources
    const allSourceIds = Object.keys(originalConfig.sourceTypes);
    
    // Don't show badges if all sources are selected
    if (sources.length === allSourceIds.length && 
        allSourceIds.every(id => sources.includes(id))) {
      return '';
    }
    
    // Create badges for selected sources
    return sources.map(sourceId => {
      const sourceConfig = originalConfig.sourceTypes[sourceId] || {
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
  
  /**
   * Update the source display (counts, distribution, filters)
   */
  function updateSourceDisplay() {
    // Update source counts and distribution
    updateSourceCounts();
    
    // Update filter UI
    updateSourceFilterUI();
    
    // Dispatch an event to notify of source display update
    window.dispatchEvent(new CustomEvent('source-display-updated'));
  }
  
  /**
   * Get source configuration for a specific source
   * @param {string} sourceId - Source ID to get config for
   * @returns {Object|null} Source configuration or null if not found
   */
  function getSourceConfig(sourceId) {
    return originalConfig.sourceTypes[sourceId] || null;
  }
  
  // Initialize when DOM is loaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
  } else {
    initialize();
  }
  
  // Return public API
  return {
    updateSourceDisplay,
    createSourceBadges,
    getSourceConfig,
    // The following methods are used to adapt to the new SourceRegistry system
    registerSource: function(sourceInfo) {
      // This is adapter method that simulates a source being registered
      // It will trigger the source-registered event
      window.dispatchEvent(new CustomEvent('source-registered', {
        detail: { source: sourceInfo }
      }));
    }
  };
})();

// Export globally
window.EnhancedSourceManager = EnhancedSourceManager;