/**
 * Part Number Search Module
 * Handles part number lookups, Google search integration, and search history management
 */
document.addEventListener('DOMContentLoaded', function () {
    // DOM Elements
    const partNumberForm = document.getElementById('part-number-form');
    const partNumberInput = document.getElementById('part-number-input');
    const partNumberSearchBtn = document.getElementById('part-number-search-btn');
    const partNumberResult = document.getElementById('part-number-result');
    const noPartResults = document.getElementById('no-part-results');
    const partNumberLoading = document.getElementById('part-number-loading');
    const partNumberError = document.getElementById('part-number-error');
    const savePartNumberBtn = document.getElementById('save-part-number');
    const clearPartHistoryBtn = document.getElementById('clear-part-history');
    const partNumberDisplay = document.getElementById('part-number-display');
    const partTypeDisplay = document.getElementById('part-type-display');
    const partDetails = document.getElementById('part-details');
    const compatibilityList = document.getElementById('compatibility-list');
    const advancedSearchLinks = document.getElementById('advanced-search-links');
    const includeOEM = document.getElementById('include-oem');
    const includeAltNumbers = document.getElementById('include-alt-numbers');
    const excludeWholesalers = document.getElementById('exclude-wholesalers');
    const noPartHistory = document.getElementById('no-part-history');
    const partHistoryList = document.getElementById('part-history-list');
    
    // Quick search buttons - removed
    
    // Storage key for search history
    const PART_HISTORY_STORAGE_KEY = 'autoxpress_part_search_history';
    
    // Current part number state
    let currentPartNumber = '';
    let searchHistory = loadSearchHistory();
    
    // Initialize the UI
    initializeUI();
    
    // Event: Part number form submission
    if (partNumberForm) {
        partNumberForm.addEventListener('submit', function (e) {
            e.preventDefault();
            
            const partNumber = partNumberInput.value.trim();
            if (!partNumber) {
                showError('Please enter a valid part number');
                return;
            }
            
            // Save the part number to current state
            currentPartNumber = partNumber;
            
            // Show loading indicator
            startLoading();
            
            // Perform optimized Google search and extract information
            performPartNumberSearch(partNumber)
                .then(result => {
                    // Display the result
                    displayPartInfo(result);
                    
                    // Add to search history
                    addToSearchHistory(partNumber, result);
                    
                    // Update UI
                    stopLoading();
                })
                .catch(error => {
                    console.error('Error searching for part:', error);
                    showError('Failed to search for part information. Please try again.');
                    stopLoading();
                });
        });
    }
    
    // Event: Save part number button - integrate with existing favorites system
    if (savePartNumberBtn) {
        savePartNumberBtn.addEventListener('click', function() {
            if (!currentPartNumber) {
                showError('No part number to save');
                return;
            }
            
            // Create a product-like object that works with the existing favorites system
            const partInfo = {
                title: `Part #${currentPartNumber} - ${partTypeDisplay ? partTypeDisplay.textContent : 'Automotive Part'}`,
                price: 'Price varies',
                image: '/static/placeholder.png', // Default image
                condition: 'New/Used',
                shipping: 'Varies by retailer',
                link: getOptimizedGoogleSearchUrl(currentPartNumber),
                source: 'Part Search',
                notes: `Part Number: ${currentPartNumber}\nSearched on: ${new Date().toLocaleString()}`
            };
            
            // Generate a unique ID for the favorite
            const productId = 'part-' + currentPartNumber.replace(/[^a-zA-Z0-9]/g, '');
            
            // Access the main app's toggleFavorite function if available
            if (typeof window.toggleFavorite === 'function') {
                window.toggleFavorite(productId, partInfo);
                
                // Show success message
                const tempMessage = document.createElement('div');
                tempMessage.className = 'alert alert-success mt-3';
                tempMessage.textContent = 'Part saved to favorites!';
                
                // Insert after the error element
                if (partNumberError && partNumberError.parentNode) {
                    partNumberError.parentNode.insertBefore(tempMessage, partNumberError.nextSibling);
                    
                    // Remove after 3 seconds
                    setTimeout(() => {
                        tempMessage.remove();
                    }, 3000);
                }
            } else {
                // Fallback to using localStorage directly if the main function isn't available
                saveFavoriteDirectly(productId, partInfo);
            }
        });
    }
    
    /**
     * Save a favorite directly to localStorage if the main toggleFavorite function is not available
     */
    function saveFavoriteDirectly(productId, productData) {
        // Use the same storage key as the main favorites system
        const FAVORITES_STORAGE_KEY = 'autoxpress_favorites';
        
        // Load existing favorites
        let favorites = {};
        const savedFavorites = localStorage.getItem(FAVORITES_STORAGE_KEY);
        if (savedFavorites) {
            try {
                favorites = JSON.parse(savedFavorites);
            } catch (e) {
                console.error('Error parsing favorites:', e);
            }
        }
        
        // Add the new favorite
        favorites[productId] = {
            ...productData,
            savedAt: new Date().toISOString()
        };
        
        // Save back to localStorage
        localStorage.setItem(FAVORITES_STORAGE_KEY, JSON.stringify(favorites));
        
        // Show success message
        alert('Part saved to favorites!');
    }
    
    // Event: Clear history button
    if (clearPartHistoryBtn) {
        clearPartHistoryBtn.addEventListener('click', function() {
            if (confirm('Are you sure you want to clear your part search history?')) {
                clearSearchHistory();
            }
        });
    }
    
    // Events: Quick search buttons - removed
    
    /**
     * Initialize the UI elements and search history display
     */
    function initializeUI() {
        // Disable quick search buttons initially
        toggleQuickSearchButtons(false);
        
        // Display search history if available
        updateSearchHistoryDisplay();
    }
    
    /**
     * Toggle the quick search buttons enabled/disabled state - now removed
     */
    function toggleQuickSearchButtons(enabled) {
        // Function is kept for compatibility but no longer does anything 
        return;
    }
    
    /**
     * Start the loading indicator and hide other UI elements
     */
    function startLoading() {
        if (partNumberLoading) partNumberLoading.classList.remove('d-none');
        if (partNumberError) partNumberError.classList.add('d-none');
        if (partNumberSearchBtn) partNumberSearchBtn.disabled = true;
    }
    
    /**
     * Stop the loading indicator and restore UI elements
     */
    function stopLoading() {
        if (partNumberLoading) partNumberLoading.classList.add('d-none');
        if (partNumberSearchBtn) partNumberSearchBtn.disabled = false;
    }
    
    /**
     * Show an error message
     */
    function showError(message) {
        if (partNumberError) {
            partNumberError.textContent = message;
            partNumberError.classList.remove('d-none');
        }
    }
    
    /**
     * Perform an optimized part number search
     * This uses advanced Google search techniques to get the most relevant information
     */
    async function performPartNumberSearch(partNumber) {
        // Get search options from the UI
        const includeOemOption = includeOEM && includeOEM.checked;
        const includeAltOption = includeAltNumbers && includeAltNumbers.checked;
        const excludeWholesalersOption = excludeWholesalers && excludeWholesalers.checked;
        
        // Prepare form data for the API request
        const formData = new FormData();
        formData.append('part_number', partNumber);
        formData.append('include_oem', includeOemOption);
        formData.append('include_alt', includeAltOption);
        formData.append('exclude_wholesalers', excludeWholesalersOption);
        
        // Call our backend API
        const response = await fetch('/api/part-number-search', {
            method: 'POST',
            body: formData
        });
        
        // Parse the response
        const result = await response.json();
        
        // Check for errors
        if (!result.success) {
            throw new Error(result.error || 'Failed to search for part');
        }
        
        // Return the part information
        return result;
    }
    
    /**
     * Display part information in the UI
     */
    function displayPartInfo(partInfo) {
        if (!partInfo) return;
        
        // Update the part number display
        if (partNumberDisplay) {
            partNumberDisplay.textContent = `Part #${partInfo.partNumber}`;
        }
        
        // Update the part type display with the part name when available
        if (partTypeDisplay) {
            partTypeDisplay.textContent = partInfo.partName || partInfo.partType || 'Automotive Part';
        }
        
        // Update part details
        if (partDetails) {
            partDetails.innerHTML = `
                <div class="mb-2">
                    <span class="text-muted">Description:</span>
                    <span class="fw-bold">${partInfo.description || 'Not available'}</span>
                </div>
                <div class="mb-2">
                    <span class="text-muted">Manufacturer:</span>
                    <span class="fw-bold">${partInfo.manufacturer || 'Unknown'}</span>
                </div>
                ${partInfo.alternativeNumbers && partInfo.alternativeNumbers.length > 0 ? `
                <div class="mb-2">
                    <span class="text-muted">Alternative Part #:</span>
                    <span class="fw-bold">${partInfo.alternativeNumbers.join(', ')}</span>
                </div>
                ` : ''}
            `;
        }
        
        // Update compatibility list
        if (compatibilityList) {
            if (partInfo.compatibility && partInfo.compatibility.length > 0) {
                compatibilityList.innerHTML = partInfo.compatibility.map(vehicle => 
                    `<div class="mb-1"><i class="fas fa-check-circle text-success me-1"></i> ${vehicle}</div>`
                ).join('');
            } else {
                compatibilityList.innerHTML = '<div class="text-muted">No compatibility information available</div>';
            }
        }
        
        // Update advanced search links
        if (advancedSearchLinks) {
            advancedSearchLinks.innerHTML = `
                <a href="${partInfo.searchUrls.google}" target="_blank" class="btn btn-sm btn-outline-primary">
                    <i class="fab fa-google me-1"></i> Google
                </a>
                <a href="${partInfo.searchUrls.amazon}" target="_blank" class="btn btn-sm btn-outline-primary">
                    <i class="fab fa-amazon me-1"></i> Amazon
                </a>
                <a href="${partInfo.searchUrls.ebay}" target="_blank" class="btn btn-sm btn-outline-primary">
                    <i class="fab fa-ebay me-1"></i> eBay
                </a>
                <a href="${partInfo.searchUrls.rockauto}" target="_blank" class="btn btn-sm btn-outline-primary">
                    <i class="fas fa-tools me-1"></i> RockAuto
                </a>
            `;
        }
        
        // Show the result card and hide the placeholder
        if (partNumberResult) partNumberResult.classList.remove('d-none');
        if (noPartResults) noPartResults.classList.add('d-none');
        
        // Enable quick search buttons
        toggleQuickSearchButtons(true);
    }
    
    /**
     * Generate a clean Google search URL for a part number
     * Simply searches for the part number itself with no additional terms
     */
    function getOptimizedGoogleSearchUrl(partNumber) {
        // Just use the part number as-is, no additional terms or operators
        return `https://www.google.com/search?q=${encodeURIComponent(partNumber)}`;
    }
    
    /**
     * Generate an optimized Amazon search URL for a part number
     * Uses advanced Amazon search parameters to improve results:
     * - Restricts to automotive department
     * - Adds automotive keywords
     * - Includes OEM keywords if selected
     * - Focuses on new condition items
     * - Filters by top customer ratings
     */
    function getAmazonSearchUrl(partNumber) {
        // Start with the part number
        let searchTerms = partNumber;
        
        // Add the clean version if it's different (without symbols)
        const cleanPartNumber = partNumber.replace(/[^a-zA-Z0-9]/g, '');
        if (cleanPartNumber !== partNumber) {
            searchTerms += ` ${cleanPartNumber}`;
        }
        
        // Add automotive keywords
        searchTerms += ' auto part';
        
        // Add OEM if checked
        if (includeOEM && includeOEM.checked) {
            searchTerms += ' OEM';
        }
        
        // Encode for URL
        const encodedQuery = encodeURIComponent(searchTerms);
        
        // Construct URL with advanced parameters:
        // - i=automotive-intl-ship: automotive department
        // - rh=p_n_condition-type:6461716011: New condition
        // - rh=p_72:1248861011: 4+ star items
        return `https://www.amazon.com/s?k=${encodedQuery}&i=automotive-intl-ship&rh=p_n_condition-type:6461716011,p_72:1248861011`;
    }
    
    /**
     * Generate an optimized eBay search URL for a part number
     * Uses advanced eBay search parameters for better results:
     * - Restricts to eBay Motors category
     * - Adds options for exact part number matching
     * - Includes filters for item condition and location
     * - Sorts by most relevant (Best Match)
     */
    function getEbaySearchUrl(partNumber) {
        // Start with the part number
        let searchTerms = partNumber;
        
        // Add the clean version if it's different (without symbols)
        const cleanPartNumber = partNumber.replace(/[^a-zA-Z0-9]/g, '');
        if (cleanPartNumber !== partNumber) {
            searchTerms += ` ${cleanPartNumber}`;
        }
        
        // Add automotive specific terms
        if (includeOEM && includeOEM.checked) {
            searchTerms += ' OEM genuine';
        }
        
        // Encode for URL
        const encodedQuery = encodeURIComponent(searchTerms);
        
        // Advanced parameters:
        // - _sacat=6000: eBay Motors category
        // - LH_TitleDesc=1: Search in title and description
        // - LH_BIN=1: Buy It Now items only (no auctions)
        // - LH_ItemCondition=3: New items
        // - LH_PrefLoc=1: Items from US sellers (for US users)
        
        return `https://www.ebay.com/sch/i.html?_nkw=${encodedQuery}&_sacat=6000&LH_TitleDesc=1&LH_BIN=1&LH_ItemCondition=3&LH_PrefLoc=1`;
    }
    
    /**
     * Generate an optimized RockAuto search URL for a part number
     * RockAuto has specific search parameters for part number lookup
     * that are more effective than regular search
     */
    function getRockAutoSearchUrl(partNumber) {
        // Remove any spaces from the part number (RockAuto search works better without spaces)
        const cleanPartNumber = partNumber.replace(/\s+/g, '');
        
        // Use the special part number search endpoint
        return `https://www.rockauto.com/en/partsearch/?partnum=${encodeURIComponent(cleanPartNumber)}`;
    }
    
    /**
     * Load search history from localStorage
     */
    function loadSearchHistory() {
        const historyJson = localStorage.getItem(PART_HISTORY_STORAGE_KEY);
        if (!historyJson) return [];
        
        try {
            return JSON.parse(historyJson);
        } catch (e) {
            console.error('Error parsing search history:', e);
            return [];
        }
    }
    
    /**
     * Save search history to localStorage
     */
    function saveSearchHistory(history) {
        localStorage.setItem(PART_HISTORY_STORAGE_KEY, JSON.stringify(history));
    }
    
    /**
     * Add a part number search to history
     */
    function addToSearchHistory(partNumber, partInfo) {
        if (!partNumber) return;
        
        // Load current history
        const history = loadSearchHistory();
        
        // Check if this part number already exists in history
        const existingIndex = history.findIndex(item => 
            item.partNumber.toLowerCase() === partNumber.toLowerCase()
        );
        
        // Create history entry
        const historyEntry = {
            partNumber: partNumber,
            partType: partInfo ? partInfo.partType : 'Automotive Part',
            timestamp: new Date().toISOString(),
            searchCount: 1
        };
        
        // If exists, update it, otherwise add new entry
        if (existingIndex !== -1) {
            historyEntry.searchCount = (history[existingIndex].searchCount || 0) + 1;
            history.splice(existingIndex, 1);
        }
        
        // Add to the beginning of history
        history.unshift(historyEntry);
        
        // Limit history to 10 entries
        const limitedHistory = history.slice(0, 10);
        
        // Save updated history
        saveSearchHistory(limitedHistory);
        
        // Update UI
        updateSearchHistoryDisplay();
    }
    
    /**
     * Clear all search history
     */
    function clearSearchHistory() {
        localStorage.removeItem(PART_HISTORY_STORAGE_KEY);
        searchHistory = [];
        updateSearchHistoryDisplay();
    }
    
    /**
     * Update the search history display
     */
    function updateSearchHistoryDisplay() {
        // Load current history
        searchHistory = loadSearchHistory();
        
        // Check if history exists
        if (!searchHistory || searchHistory.length === 0) {
            if (noPartHistory) noPartHistory.classList.remove('d-none');
            if (partHistoryList) partHistoryList.classList.add('d-none');
            return;
        }
        
        // Show history list
        if (noPartHistory) noPartHistory.classList.add('d-none');
        if (partHistoryList) {
            partHistoryList.classList.remove('d-none');
            
            // Generate history items
            partHistoryList.innerHTML = '';
            
            searchHistory.forEach(item => {
                const historyItem = document.createElement('div');
                historyItem.className = 'col-md-6 col-lg-4';
                
                const date = new Date(item.timestamp);
                const formattedDate = `${date.toLocaleDateString()} ${date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}`;
                
                historyItem.innerHTML = `
                    <div class="card h-100">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <h6 class="mb-0 text-primary part-history-number">${item.partNumber}</h6>
                                <span class="badge bg-secondary small">${item.searchCount}x</span>
                            </div>
                            <p class="text-muted small mb-2">${item.partType || 'Automotive Part'}</p>
                            <div class="small text-muted mb-3">
                                <i class="fas fa-clock me-1"></i> ${formattedDate}
                            </div>
                            <div class="d-flex justify-content-between">
                                <button class="btn btn-sm btn-outline-primary search-again-btn" 
                                    data-part-number="${item.partNumber}">
                                    <i class="fas fa-search me-1"></i> Search Again
                                </button>
                                <button class="btn btn-sm btn-outline-secondary remove-history-btn"
                                    data-part-number="${item.partNumber}">
                                    <i class="fas fa-times me-1"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                `;
                
                partHistoryList.appendChild(historyItem);
            });
            
            // Add event listeners to history buttons
            addHistoryButtonListeners();
        }
    }
    
    /**
     * Add event listeners to search history buttons
     */
    function addHistoryButtonListeners() {
        // Search again buttons
        document.querySelectorAll('.search-again-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const partNumber = this.dataset.partNumber;
                if (partNumber) {
                    // Set the input value
                    if (partNumberInput) {
                        partNumberInput.value = partNumber;
                        
                        // Trigger the search
                        if (partNumberForm) {
                            partNumberForm.dispatchEvent(new Event('submit'));
                        }
                    }
                }
            });
        });
        
        // Remove history buttons
        document.querySelectorAll('.remove-history-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const partNumber = this.dataset.partNumber;
                if (partNumber) {
                    removeFromHistory(partNumber);
                }
            });
        });
    }
    
    /**
     * Remove a part number from search history
     */
    function removeFromHistory(partNumber) {
        if (!partNumber) return;
        
        // Load current history
        const history = loadSearchHistory();
        
        // Remove the entry
        const updatedHistory = history.filter(item => 
            item.partNumber.toLowerCase() !== partNumber.toLowerCase()
        );
        
        // Save updated history
        saveSearchHistory(updatedHistory);
        
        // Update UI
        updateSearchHistoryDisplay();
    }
    
    /**
     * Guess the part type based on the part number pattern
     * This is a simple implementation that could be enhanced
     */
    function guessPartType(partNumber) {
        const partNumberLower = partNumber.toLowerCase();
        
        // Some simple pattern matching
        if (/^ac\d/.test(partNumberLower)) return 'Air Conditioning Component';
        if (/^br[a-z]?\d/.test(partNumberLower)) return 'Brake Component';
        if (/^alt\d/.test(partNumberLower)) return 'Alternator';
        if (/^eng\d/.test(partNumberLower)) return 'Engine Component';
        if (/^oil\d/.test(partNumberLower)) return 'Oil System Component';
        if (/^tr[ans]?\d/.test(partNumberLower)) return 'Transmission Component';
        if (/^sus\d/.test(partNumberLower)) return 'Suspension Component';
        if (/^exh\d/.test(partNumberLower)) return 'Exhaust Component';
        if (/^int\d/.test(partNumberLower)) return 'Interior Component';
        if (/^ele\d/.test(partNumberLower)) return 'Electrical Component';
        
        // Default
        return 'Automotive Part';
    }
    
    /**
     * Guess the manufacturer based on the part number pattern
     * This is a simple implementation that could be enhanced
     */
    function guessManufacturer(partNumber) {
        const partNumberLower = partNumber.toLowerCase();
        
        // Some simple pattern matching
        if (/^toy/.test(partNumberLower)) return 'Toyota';
        if (/^hon/.test(partNumberLower)) return 'Honda';
        if (/^bmw/.test(partNumberLower)) return 'BMW';
        if (/^mer/.test(partNumberLower)) return 'Mercedes-Benz';
        if (/^for/.test(partNumberLower)) return 'Ford';
        if (/^gm/.test(partNumberLower)) return 'General Motors';
        if (/^mo/.test(partNumberLower)) return 'Mopar';
        if (/^vw/.test(partNumberLower)) return 'Volkswagen';
        if (/^nis/.test(partNumberLower)) return 'Nissan';
        if (/^sub/.test(partNumberLower)) return 'Subaru';
        
        // Default
        return 'OEM or Aftermarket';
    }
});