/**
 * Filter Manager Module
 * Enhances the product filtering functionality with badge support and visual filter indicators
 */

const FilterManager = (function() {
  // DOM Elements
  let appliedFiltersContainer = null;
  
  // Filter configuration
  const FILTER_LABELS = {
    condition: {
      new: 'New Only'
    },
    shipping: {
      free: 'Free Shipping'
    },
    relevance: {
      high: 'Best Matches'
    },
    badge: {
      year: 'Exact Year Match',
      partType: 'Exact Part Match',
      oem: 'OEM Parts',
      brand: 'Premium Brand'
    },
    source: {
      'eBay': 'eBay',
      'Google Shopping': 'Google Shopping'
    }
  };
  
  // Badge styles for filters
  const FILTER_STYLES = {
    condition: 'badge-condition',
    shipping: 'badge-shipping',
    relevance: 'badge-best-match',
    badge: {
      year: 'badge-exact-year',
      partType: 'badge-part-match',
      oem: 'badge-oem',
      brand: 'badge-brand'
    },
    source: ''
  };
  
  /**
   * Initializes the filter manager
   */
  function initialize() {
    appliedFiltersContainer = document.getElementById('applied-filters');
    
    // Add counts to filter options based on current products
    updateFilterCounts();
    
    // Enhance filter checkboxes with visual indicators
    enhanceFilterCheckboxes();
    
    // Initialize active filter display
    updateAppliedFilters();
    
    // Listen for filter changes
    document.addEventListener('filters-changed', updateAppliedFilters);
    
    // Listen for new products
    document.addEventListener('products-rendered', () => {
      updateFilterCounts();
    });
  }
  
  /**
   * Updates the badges showing active filters
   */
  function updateAppliedFilters() {
    if (!appliedFiltersContainer) return;
    
    // Clear current filters
    appliedFiltersContainer.innerHTML = '';
    
    // Get active filters from product config
    const activeFilters = window.productConfig?.activeFilters;
    if (!activeFilters) return;
    
    // Create filter badges for each active filter
    Object.keys(activeFilters).forEach(filterType => {
      const values = activeFilters[filterType];
      
      if (!Array.isArray(values) || values.length === 0) return;
      
      // Handle source filters using SourceManager if available
      if (filterType === 'source') {
        if (window.SourceManager) {
          // Use SourceManager to create badges for sources
          const sourceBadges = window.SourceManager.createSourceBadges(values);
          if (sourceBadges) {
            const sourceTagsContainer = document.createElement('div');
            sourceTagsContainer.className = 'source-badges-container';
            sourceTagsContainer.innerHTML = sourceBadges;
            
            // Add click handlers to remove source filters
            sourceTagsContainer.querySelectorAll('.remove-filter').forEach(removeBtn => {
              removeBtn.addEventListener('click', function() {
                const sourceValue = this.closest('.source-badge').dataset.value;
                removeFilter('source', sourceValue);
              });
            });
            
            appliedFiltersContainer.appendChild(sourceTagsContainer);
          }
          return;
        }
        
        // Fall back to default behavior if SourceManager isn't available
        // Skip source if all sources are selected
        const allSources = window.productConfig?.availableSources?.map(s => s.id) || ['eBay', 'Google Shopping'];
        if (allSources.every(source => values.includes(source))) {
          return;
        }
      }
      
      values.forEach(value => {
        // Get label for this filter
        let label = '';
        if (filterType === 'badge') {
          label = FILTER_LABELS[filterType][value] || value;
        } else {
          label = FILTER_LABELS[filterType]?.[value] || value;
        }
        
        // Get style for this filter
        let styleClass = '';
        if (filterType === 'badge') {
          styleClass = FILTER_STYLES[filterType][value] || '';
        } else {
          styleClass = FILTER_STYLES[filterType] || '';
        }
        
        // Create filter tag
        const filterTag = document.createElement('div');
        filterTag.className = 'applied-filter-tag';
        filterTag.dataset.filterType = filterType;
        filterTag.dataset.filterValue = value;
        
        // Add inner HTML with close button
        filterTag.innerHTML = `
          <span class="${styleClass}">${label}</span>
          <i class="fas fa-times-circle"></i>
        `;
        
        // Add click handler to remove filter
        filterTag.querySelector('i').addEventListener('click', function() {
          removeFilter(filterType, value);
        });
        
        // Add to container
        appliedFiltersContainer.appendChild(filterTag);
      });
    });
  }
  
  /**
   * Removes a filter and updates the UI
   */
  function removeFilter(filterType, value) {
    // Get active filters from product config
    const activeFilters = window.productConfig?.activeFilters;
    if (!activeFilters || !activeFilters[filterType]) return;
    
    // Update the active filters
    activeFilters[filterType] = activeFilters[filterType].filter(v => v !== value);
    
    // Update filter checkbox state
    const checkbox = document.querySelector(`[data-filter="${filterType}"][data-value="${value}"]`);
    if (checkbox) {
      checkbox.checked = false;
    }
    
    // Apply filters
    if (window.applyFilters) {
      window.applyFilters();
    }
    
    // Update UI
    updateAppliedFilters();
  }
  
  /**
   * Updates the filter options with counts based on current products
   */
  function updateFilterCounts() {
    const products = window.productConfig?.allProducts || [];
    if (products.length === 0) return;
    
    // Count products matching each filter criteria
    const counts = {
      condition: { new: 0 },
      shipping: { free: 0 },
      badge: { year: 0, partType: 0, oem: 0, brand: 0 },
      source: { 'eBay': 0, 'Google Shopping': 0 }
    };
    
    // If SourceManager is available, let it handle source counts and display
    if (window.SourceManager) {
      // Update source display information
      window.SourceManager.updateSourceDisplay();
    }
    
    // Count matches in products
    products.forEach(product => {
      // Count condition
      if (product.condition.toLowerCase().includes('new')) {
        counts.condition.new++;
      }
      
      // Count shipping
      if (product.shipping.toLowerCase().includes('free')) {
        counts.shipping.free++;
      }
      
      // Count source (only when SourceManager not available)
      if (!window.SourceManager && counts.source[product.source] !== undefined) {
        counts.source[product.source]++;
      }
      
      // Count badges
      if (product.primaryBadge) {
        const badgeType = product.primaryBadge.type;
        if (counts.badge[badgeType] !== undefined) {
          counts.badge[badgeType]++;
        }
      }
      
      if (product.secondaryBadges && Array.isArray(product.secondaryBadges)) {
        product.secondaryBadges.forEach(badge => {
          const badgeType = badge.type;
          if (counts.badge[badgeType] !== undefined) {
            counts.badge[badgeType]++;
          }
        });
      }
    });
    
    // Update the filter options with counts
    Object.keys(counts).forEach(filterType => {
      Object.keys(counts[filterType]).forEach(value => {
        const count = counts[filterType][value];
        
        // Find the filter option
        let selector = `[data-filter="${filterType}"]`;
        if (filterType === 'badge') {
          selector = `[data-filter="badge"][data-value="${value}"]`;
        } else {
          selector = `[data-filter="${filterType}"][data-value="${value}"]`;
        }
        
        const checkbox = document.querySelector(selector);
        if (!checkbox) return;
        
        // Find or create the count badge
        const label = checkbox.nextElementSibling;
        if (!label) return;
        
        let countBadge = label.querySelector('.badge-count');
        if (!countBadge) {
          countBadge = document.createElement('span');
          countBadge.className = 'badge-count';
          label.appendChild(countBadge);
        }
        
        // Update the count
        countBadge.textContent = count;
        
        // Disable checkbox if count is 0
        checkbox.disabled = count === 0;
        if (count === 0) {
          label.classList.add('text-muted');
        } else {
          label.classList.remove('text-muted');
        }
      });
    });
  }
  
  /**
   * Makes filter checkboxes more visually appealing
   */
  function enhanceFilterCheckboxes() {
    const checkboxes = document.querySelectorAll('.filter-check');
    
    checkboxes.forEach(checkbox => {
      checkbox.addEventListener('change', function() {
        // Update the filter UI immediately
        updateAppliedFilters();
      });
    });
  }
  
  // Return public API
  return {
    initialize,
    updateAppliedFilters,
    updateFilterCounts
  };
})();

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
  // Initialize with a slight delay to ensure productConfig is loaded
  setTimeout(() => {
    FilterManager.initialize();
  }, 200);
});