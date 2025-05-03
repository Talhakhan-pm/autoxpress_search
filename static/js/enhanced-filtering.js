/**
 * Enhanced Filtering System for AutoXpress
 * Now uses the unified filtering API from updated_products.js
 */

document.addEventListener('DOMContentLoaded', function() {
    // Log initialization
    console.log('Initializing enhanced filtering system with unified API');
    
    // Elements
    const filterCheckboxes = document.querySelectorAll('.filter-check');
    const resetFiltersButton = document.getElementById('resetFilters');
    const filterCountBadge = document.getElementById('filter-count');
    const activeFiltersContainer = document.getElementById('active-filters');
    
    // Store active filters (local copy for UI management)
    let activeFilters = {
        condition: [],
        type: [],
        shipping: [],
        source: ['eBay', 'Google Shopping'] // Default checked sources
    };
    
    // Check if we have the unified product display API
    const hasUnifiedAPI = window.productDisplay && typeof window.productDisplay.applyFilters === 'function';
    
    // If using unified API, synchronize local filters with central system
    if (hasUnifiedAPI) {
        console.log('Using unified filtering API from updated_products.js');
        
        // Get current filters from the central system
        try {
            const centralFilters = window.productDisplay.getActiveFilters();
            if (centralFilters) {
                // Merge with our local filters, preferring central values
                for (const [filterType, values] of Object.entries(centralFilters)) {
                    if (Array.isArray(values)) {
                        activeFilters[filterType] = [...values];
                    }
                }
                console.log('Synchronized filters with central system:', activeFilters);
            }
        } catch (e) {
            console.warn('Failed to get active filters from central system:', e);
        }
    } else {
        console.warn('Unified filtering API not found - using standalone mode');
    }
    
    // Initialize filter event handlers
    function initFilters() {
        // Set up filter checkbox listeners
        filterCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                const filterType = this.dataset.filter;
                const filterValue = this.dataset.value;
                
                console.log(`Filter checkbox changed: ${filterType}=${filterValue}, checked=${this.checked}`);
                
                if (this.checked) {
                    // Add to active filters
                    if (!activeFilters[filterType].includes(filterValue)) {
                        activeFilters[filterType].push(filterValue);
                        
                        // If using unified API, synchronize with central system
                        if (hasUnifiedAPI) {
                            window.productDisplay.addFilter(filterType, filterValue);
                        }
                        
                        console.log(`Added ${filterValue} to ${filterType} filters`);
                    }
                } else {
                    // Remove from active filters
                    activeFilters[filterType] = activeFilters[filterType].filter(v => v !== filterValue);
                    
                    // If using unified API, synchronize with central system
                    if (hasUnifiedAPI) {
                        window.productDisplay.removeFilter(filterType, filterValue);
                    }
                    
                    console.log(`Removed ${filterValue} from ${filterType} filters`);
                }
                
                // Update UI and apply filters
                console.log('Active filters after change:', JSON.stringify(activeFilters));
                updateActiveFiltersUI();
                applyFilters();
            });
        });
        
        // Reset filters button
        if (resetFiltersButton) {
            resetFiltersButton.addEventListener('click', resetFilters);
        }
        
        // Initial UI update
        updateActiveFiltersUI();
        
        // Synchronize checkbox states with active filters
        syncCheckboxesWithFilters();
    }
    
    // Update checkboxes to match filter state
    function syncCheckboxesWithFilters() {
        filterCheckboxes.forEach(checkbox => {
            const filterType = checkbox.dataset.filter;
            const filterValue = checkbox.dataset.value;
            
            // Set checkbox state based on filter values
            if (activeFilters[filterType] && activeFilters[filterType].includes(filterValue)) {
                checkbox.checked = true;
            } else {
                checkbox.checked = filterType === 'source'; // Source checkboxes default to checked
            }
        });
    }
    
    // Update the active filters UI display
    function updateActiveFiltersUI() {
        if (!activeFiltersContainer) return;
        
        // Clear the container
        activeFiltersContainer.innerHTML = '';
        
        // Count active filters (excluding source which is always active)
        let filterCount = 0;
        
        // Friendly names for filter types and values
        const filterNames = {
            condition: 'Condition',
            type: 'Type',
            shipping: 'Shipping',
            relevance: 'Relevance',
            match: 'Match',
            source: 'Source'
        };
        
        const valueNames = {
            new: 'New',
            used: 'Used',
            oem: 'OEM',
            premium: 'Premium',
            free: 'Free Shipping',
            high: 'Best Match',
            exact: 'Exact Match',
            'eBay': 'eBay',
            'Google Shopping': 'Google'
        };
        
        // Generate tags for each active filter
        for (const [filterType, values] of Object.entries(activeFilters)) {
            // Skip source filters in the count
            if (filterType !== 'source') {
                filterCount += values.length;
            }
            
            // Create tags for non-empty filter groups (except source)
            if (values.length > 0 && filterType !== 'source') {
                values.forEach(value => {
                    const tag = document.createElement('div');
                    tag.className = 'active-filter-tag';
                    tag.dataset.filterType = filterType;
                    tag.dataset.filterValue = value;
                    
                    // Use friendly names if available
                    const displayValue = valueNames[value] || value;
                    tag.innerHTML = `
                        ${displayValue}
                        <span class="filter-remove"><i class="fas fa-times"></i></span>
                    `;
                    
                    // Add click handler to remove filter
                    tag.addEventListener('click', function() {
                        const type = this.dataset.filterType;
                        const value = this.dataset.filterValue;
                        
                        // Update checkbox state
                        const checkbox = document.querySelector(`.filter-check[data-filter="${type}"][data-value="${value}"]`);
                        if (checkbox) {
                            checkbox.checked = false;
                        }
                        
                        // Remove from active filters locally
                        activeFilters[type] = activeFilters[type].filter(v => v !== value);
                        
                        // If using unified API, synchronize with central system
                        if (hasUnifiedAPI) {
                            window.productDisplay.removeFilter(type, value);
                        }
                        
                        // Update UI and apply filters
                        updateActiveFiltersUI();
                        applyFilters();
                    });
                    
                    activeFiltersContainer.appendChild(tag);
                });
            }
        }
        
        // Update the filter count badge
        if (filterCountBadge) {
            if (filterCount > 0) {
                filterCountBadge.textContent = filterCount;
                filterCountBadge.style.display = 'inline';
            } else {
                filterCountBadge.style.display = 'none';
            }
        }
    }
    
    // Apply filters to product cards
    let filterCallCount = 0;
    function applyFilters() {
        filterCallCount++;
        console.log(`Applying filters (call #${filterCallCount}) with activeFilters:`, JSON.stringify(activeFilters));
        
        // If the unified API is available, use it
        if (hasUnifiedAPI) {
            console.log('Delegating filtering to unified API');
            
            // The applyFilters call will handle the DOM updates
            window.productDisplay.applyFilters({
                debug: true  // Enable debug logging
            });
            
            return; // Exit early - filtering handled by unified API
        }
        
        // Legacy standalone filter implementation - only used if unified API is not available
        console.warn('Using legacy filter implementation (unified API not available)');
        
        const productCards = document.querySelectorAll('.product-card');
        if (!productCards.length) {
            console.log('No product cards found to filter');
            return;
        }
        
        // Filter cards by walking the DOM
        productCards.forEach(card => {
            const parent = card.closest('.col-md-4, .col-lg-3, .col-6');
            if (!parent) return;
            
            // Default to visible
            let isVisible = true;
            
            // Check each filter type
            for (const [filterType, activeValues] of Object.entries(activeFilters)) {
                // Skip empty filter groups
                if (activeValues.length === 0) continue;
                
                // Source filtering
                if (filterType === 'source') {
                    const sourceElement = card.querySelector('.product-source');
                    if (sourceElement) {
                        const source = sourceElement.textContent.trim();
                        if (!activeValues.includes(source)) {
                            isVisible = false;
                            break;
                        }
                    }
                }
                
                // Condition filtering
                else if (filterType === 'condition') {
                    const condition = card.textContent.toLowerCase();
                    
                    // For 'new' filter only
                    if (activeValues.includes('new') && !activeValues.includes('used')) {
                        if (!condition.includes('new') && !condition.includes('brand new')) {
                            isVisible = false;
                            break;
                        }
                    }
                    
                    // For 'used' filter only
                    else if (activeValues.includes('used') && !activeValues.includes('new')) {
                        if (!condition.includes('used') && !condition.includes('pre-owned')) {
                            isVisible = false;
                            break;
                        }
                    }
                    
                    // If both are selected, all products should pass this filter
                }
                
                // Type filtering (OEM, Premium)
                else if (filterType === 'type') {
                    // For 'oem' filter
                    if (activeValues.includes('oem')) {
                        // Check for OEM badge, tag or text
                        const hasOemBadge = card.querySelector('.badge-oem');
                        const hasOemTag = card.querySelector('.tag-oem');
                        const hasOemText = card.textContent.toLowerCase().includes('oem') || 
                                           card.textContent.toLowerCase().includes('original equipment');
                        
                        if (!hasOemBadge && !hasOemTag && !hasOemText) {
                            isVisible = false;
                            break;
                        }
                    }
                    
                    // For 'premium' filter
                    if (activeValues.includes('premium')) {
                        // Check for Premium tag, badge, attribute or text
                        const hasPremiumBadge = card.querySelector('.badge-premium');
                        const hasPremiumTag = card.querySelector('.tag-premium');
                        const hasPremiumAttr = card.getAttribute('data-premium') === 'true';
                        const productTitle = card.querySelector('.product-title')?.textContent?.toLowerCase() || '';
                        
                        // Premium text markers (same as in unified API)
                        const hasPremiumText = productTitle.includes('premium') || 
                                            productTitle.includes('performance') ||
                                            productTitle.includes('detroit') ||
                                            productTitle.includes('apf') ||
                                            productTitle.includes('bosch') ||
                                            productTitle.includes('brembo') ||
                                            productTitle.includes('drilled') ||
                                            productTitle.includes('slotted') ||
                                            productTitle.includes('ceramic') ||
                                            productTitle.includes('carbon ceramic') ||
                                            productTitle.includes('semi-metallic') ||
                                            productTitle.includes('semi metallic') ||
                                            productTitle.includes('sport') ||
                                            productTitle.includes('racing') ||
                                            productTitle.includes('heavy duty');
                        
                        if (!hasPremiumBadge && !hasPremiumTag && !hasPremiumAttr && !hasPremiumText) {
                            isVisible = false;
                            break;
                        }
                    }
                }
                
                // Shipping filtering
                else if (filterType === 'shipping') {
                    if (activeValues.includes('free')) {
                        const shippingInfo = card.textContent.toLowerCase();
                        if (!shippingInfo.includes('free shipping')) {
                            isVisible = false;
                            break;
                        }
                    }
                }
            }
            
            // Update visibility
            if (isVisible) {
                parent.style.display = '';
            } else {
                parent.style.display = 'none';
            }
        });
        
        // Update product count (legacy mode)
        updateFilteredProductCount();
    }
    
    // Update the filtered product count (legacy standalone mode)
    function updateFilteredProductCount() {
        const totalCountElement = document.getElementById('product-total-count');
        if (!totalCountElement) return;
        
        // Count visible product cards
        const visibleCards = document.querySelectorAll('.col-md-4:not([style*="display: none"]), .col-lg-3:not([style*="display: none"]), .col-6:not([style*="display: none"])').length;
        
        // Update the counter
        totalCountElement.textContent = visibleCards;
    }
    
    // Reset all filters to default state
    function resetFilters() {
        console.log('Resetting all filters to default state');
        
        // If using unified API, use its reset function
        if (hasUnifiedAPI && typeof window.productDisplay.resetFilters === 'function') {
            window.productDisplay.resetFilters();
            
            // Update our local state to match
            activeFilters = window.productDisplay.getActiveFilters();
        } else {
            // Legacy standalone reset
            // Reset checkboxes except source filters (keep them checked by default)
            filterCheckboxes.forEach(checkbox => {
                const isSourceFilter = checkbox.dataset.filter === 'source';
                checkbox.checked = isSourceFilter; // Only keep source filters checked
            });
            
            // Reset active filters
            for (const filterType in activeFilters) {
                if (filterType === 'source') {
                    // Maintain default source filters
                    activeFilters[filterType] = ['eBay', 'Google Shopping'];
                } else {
                    activeFilters[filterType] = [];
                }
            }
            
            // Apply local filters
            applyFilters();
        }
        
        // Update the UI to match the reset state
        updateActiveFiltersUI();
    }
    
    // Initialize on document load
    initFilters();
    
    // Also listen for the load more button clicks
    const loadMoreBtn = document.getElementById('load-more-btn');
    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', function() {
            console.log('Load more button clicked - filters will be reapplied after loading');
        });
    }
    
    // Listen for product display events to re-apply filters
    document.addEventListener('productsDisplayed', function() {
        console.log('productsDisplayed event triggered - preparing to reapply filters');
        
        // Apply filters after a short delay to ensure all products are rendered
        setTimeout(() => {
            // If using unified API, re-sync our local state with the central system
            if (hasUnifiedAPI) {
                try {
                    activeFilters = window.productDisplay.getActiveFilters();
                    updateActiveFiltersUI();
                } catch (e) {
                    console.warn('Failed to sync with unified filters:', e);
                }
            }
            
            // In standalone mode, we need to check for premium products
            else {
                // Re-check for products that should be premium but don't have the tag
                const productCards = document.querySelectorAll('.product-card');
                productCards.forEach(card => {
                    const title = card.querySelector('.product-title')?.textContent.toLowerCase() || '';
                    
                    // Premium brand check (same list as in unified API)
                    const premiumBrands = ['bosch', 'brembo', 'bilstein', 'koni', 'borla', 'kw', 'k&n', 'moog', 
                                         'akebono', 'stoptech', 'eibach', 'h&r', 'magnaflow', 'hawk', 'edelbrock',
                                         'detroit', 'apf', 'detroit diesel', 'detroit axle'];
                    
                    const isPremiumByBrand = premiumBrands.some(brand => title.includes(brand));
                    const isPremiumByKeywords = title.includes('premium') || 
                                             title.includes('performance') || 
                                             title.includes('pro');
                                             
                    if ((isPremiumByBrand || isPremiumByKeywords) && !card.querySelector('.tag-premium')) {
                        console.log('Adding missing premium tag to:', title);
                        
                        // Add premium tag if missing
                        const tagsContainer = card.querySelector('.product-tags');
                        if (tagsContainer) {
                            const premiumTag = document.createElement('span');
                            premiumTag.className = 'product-tag tag-premium';
                            premiumTag.textContent = 'Premium';
                            tagsContainer.appendChild(premiumTag);
                            
                            // Mark with data attribute for persistence
                            card.setAttribute('data-premium', 'true');
                        }
                    }
                });
            }
            
            // Apply filters (using unified API if available)
            applyFilters();
        }, 100);
    });
    
    // Listen for filter changes from the unified system
    document.addEventListener('filtersApplied', function(event) {
        // Only process if we have filter data and we're using the unified API
        if (hasUnifiedAPI && event.detail && event.detail.filters) {
            console.log('Received filtersApplied event from unified system');
            
            // Update our local filter state to match the unified system
            activeFilters = event.detail.filters;
            
            // Update the UI to reflect the new filter state
            updateActiveFiltersUI();
            syncCheckboxesWithFilters();
        }
    });
});