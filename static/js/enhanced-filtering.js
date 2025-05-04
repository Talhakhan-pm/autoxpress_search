/**
 * Enhanced Filtering System for AutoXpress
 * Supports OEM/premium/used product filtering without modifying core logic
 */

document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const filterCheckboxes = document.querySelectorAll('.filter-check');
    const resetFiltersButton = document.getElementById('resetFilters');
    const filterCountBadge = document.getElementById('filter-count');
    const activeFiltersContainer = document.getElementById('active-filters');
    
    // Store active filters
    let activeFilters = {
        condition: [],
        type: [],
        shipping: [],
        source: ['eBay', 'Google Shopping'] // Default checked sources
    };
    
    // Initialize filters in global productConfig if it exists
    if (window.productConfig && window.productConfig.activeFilters) {
        // Ensure all required filter types exist in productConfig
        const requiredFilterTypes = Object.keys(activeFilters);
        
        for (const filterType of requiredFilterTypes) {
            if (!window.productConfig.activeFilters[filterType]) {
                // Initialize missing filter types
                window.productConfig.activeFilters[filterType] = filterType === 'source' ? 
                    ['eBay', 'Google Shopping'] : [];
            }
        }
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
                        console.log(`Added ${filterValue} to ${filterType} filters`);
                    }
                } else {
                    // Remove from active filters
                    activeFilters[filterType] = activeFilters[filterType].filter(v => v !== filterValue);
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
                        
                        // Remove from active filters
                        activeFilters[type] = activeFilters[type].filter(v => v !== value);
                        
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
        
        // FORCE TRIGGER: Add an alert so we can see if this function is being called
        // alert('Filter is being applied with: ' + JSON.stringify(activeFilters));
        
        const productCards = document.querySelectorAll('.product-card');
        if (!productCards.length) {
            console.log('No product cards found to filter');
            return;
        }
        
        // Log all product cards for debugging
        console.log('Found', productCards.length, 'product cards to filter');
        productCards.forEach((card, index) => {
            const title = card.querySelector('.product-title')?.textContent || 'Unknown';
            console.log(`Product ${index+1}: ${title}`);
        });
        
        productCards.forEach(card => {
            const parent = card.closest('.col-md-4, .col-lg-3');
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
                    // For 'new' filter
                    if (activeValues.includes('new')) {
                        const condition = card.textContent.toLowerCase();
                        if (!condition.includes('new') && !condition.includes('brand new')) {
                            isVisible = false;
                            break;
                        }
                    }
                    
                    // For 'used' filter
                    if (activeValues.includes('used')) {
                        const condition = card.textContent.toLowerCase();
                        if (!condition.includes('used') && !condition.includes('pre-owned')) {
                            isVisible = false;
                            break;
                        }
                    }
                }
                
                // Type filtering (OEM, Premium)
                else if (filterType === 'type') {
                    // For 'oem' filter
                    if (activeValues.includes('oem')) {
                        // Check for OEM badge or text
                        const hasOemBadge = card.querySelector('.badge-oem');
                        const hasOemText = card.textContent.toLowerCase().includes('oem') || 
                                          card.textContent.toLowerCase().includes('original equipment');
                        
                        if (!hasOemBadge && !hasOemText) {
                            isVisible = false;
                            break;
                        }
                    }
                    
                    // For 'premium' filter
                    if (activeValues.includes('premium')) {
                        // FORCE TEST - Mark all products as passing premium filter for testing
                        const forceAllProductsAsPremium = false;
                        
                        if (forceAllProductsAsPremium) {
                            console.log('FORCE TEST: All products set to pass premium filter');
                            // Skip filtering - all products will show
                        } else {
                            // Check for Premium tag, badge, attribute or text
                            const hasPremiumBadge = card.querySelector('.badge-premium');
                            const hasPremiumTag = card.querySelector('.tag-premium');
                            const hasPremiumAttr = card.getAttribute('data-premium') === 'true';
                            const productTitle = card.querySelector('.product-title')?.textContent?.toLowerCase() || '';
                            const hasPremiumText = productTitle.includes('premium') || 
                                                productTitle.includes('performance') ||
                                                productTitle.includes('detroit') ||
                                                productTitle.includes('apf') ||
                                                productTitle.includes('bosch') ||
                                                productTitle.includes('brembo') ||
                                                productTitle.includes('drilled') ||     // Drilled rotors are premium
                                                productTitle.includes('slotted') ||     // Slotted rotors are premium
                                                productTitle.includes('ceramic') ||     // Ceramic pads are premium
                                                productTitle.includes('carbon ceramic') || // Carbon ceramic is high-end
                                                productTitle.includes('semi-metallic') ||  // Semi-metallic is premium
                                                productTitle.includes('semi metallic') ||  // Semi-metallic (alt spelling)
                                                productTitle.includes('sport') ||       // Sport parts are premium
                                                productTitle.includes('racing') ||      // Racing parts are premium
                                                productTitle.includes('heavy duty');    // Heavy duty parts are premium
                            
                            // Enhanced debugging - log the state of each check
                            console.log('Premium filter check for:', productTitle);
                            console.log({
                                hasPremiumBadge: !!hasPremiumBadge,
                                hasPremiumTag: !!hasPremiumTag,
                                hasPremiumAttr: !!hasPremiumAttr,
                                hasPremiumText: hasPremiumText,
                                productTitle: productTitle,
                                isPremium: !!(hasPremiumBadge || hasPremiumTag || hasPremiumAttr || hasPremiumText)
                            });
                            
                            if (!hasPremiumBadge && !hasPremiumTag && !hasPremiumAttr && !hasPremiumText) {
                                console.log('Product failed premium filter:', productTitle);
                                isVisible = false;
                                break;
                            } else {
                                console.log('Product PASSED premium filter:', productTitle);
                            }
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
                
                // Future filtering extensions can be added here
            }
            
            // Update visibility
            if (isVisible) {
                parent.style.display = '';
            } else {
                parent.style.display = 'none';
            }
        });
        
        // Update product count
        updateFilteredProductCount();
    }
    
    // Update the filtered product count
    function updateFilteredProductCount() {
        const totalCountElement = document.getElementById('product-total-count');
        if (!totalCountElement) return;
        
        const visibleProducts = document.querySelectorAll('.product-card').length;
        const visibleCards = document.querySelectorAll('.col-md-4:not([style*="display: none"]), .col-lg-3:not([style*="display: none"])').length;
        
        totalCountElement.textContent = visibleCards;
    }
    
    // Reset all filters to default state
    function resetFilters() {
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
        
        // Update UI and apply filters
        updateActiveFiltersUI();
        applyFilters();
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
            // Re-check for products that should be premium but don't have the tag
            const productCards = document.querySelectorAll('.product-card');
            productCards.forEach(card => {
                const title = card.querySelector('.product-title')?.textContent.toLowerCase() || '';
                
                // Premium brand check
                const premiumBrands = ['bosch', 'brembo', 'bilstein', 'koni', 'borla', 'kw', 'k&n', 'moog', 
                                     'akebono', 'stoptech', 'eibach', 'h&r', 'magnaflow', 'hawk', 'edelbrock',
                                     'detroit', 'apf', 'detroit diesel', 'detroit axle', 'aisin', 'gear'];
                
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
            
            // Apply filters
            applyFilters();
        }, 100);
    });
});