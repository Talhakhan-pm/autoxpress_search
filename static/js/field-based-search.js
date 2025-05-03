/**
 * Field-Based Search Implementation for AutoXpress
 * 
 * This module handles the field-by-field search approach rather than using
 * normalized search terms. It works with the existing API endpoints by:
 * 
 * 1. Building a structured query from individual fields (year, make, model, part, engine)
 * 2. Passing field values as structured data to the backend
 * 3. Using field-specific combinations for more accurate results
 * 
 * This approach provides more targeted search results since it:
 * - Uses the exact field values entered by the user
 * - Maintains individual field context for better matching
 * - Generates optimized search terms based on available fields
 */

document.addEventListener('DOMContentLoaded', function () {
    // DOM Elements
    const searchForm = document.getElementById('search-form');
    const searchButton = document.getElementById('search-button');
    const yearField = document.getElementById('year-field');
    const makeField = document.getElementById('make-field');
    const modelField = document.getElementById('model-field');
    const partField = document.getElementById('part-field');
    const engineField = document.getElementById('engine-field');
    const resultContainer = document.getElementById('result-container');
    const questionsContainer = document.getElementById('questions');
    const productsContainer = document.getElementById('products-container');
    const validationError = document.getElementById('validation-error');
    const analysisTimeSpan = document.getElementById('analysis-time');
    const searchLoading = document.getElementById('search-loading');
    const productsLoading = document.getElementById('products-loading');
    const productCountBadge = document.getElementById('products-count');
    const productTotalCount = document.getElementById('product-total-count');
    
    // Configure search form submission for field-based search
    if (searchForm) {
        searchForm.addEventListener('submit', async function (e) {
            e.preventDefault();
            
            // Check if we're in single-field mode
            const singleFieldContainer = document.getElementById('single-field-container');
            const isSingleFieldMode = !singleFieldContainer.classList.contains('d-none');
            
            // Handle different field modes
            let year, make, model, part, engine, fieldPrompt;
            
            if (isSingleFieldMode) {
                // Single-field mode - get the single query
                const singleFieldQuery = document.getElementById('prompt').value.trim();
                
                if (!singleFieldQuery) {
                    showValidationError("Please enter your search query.");
                    return;
                }
                
                // For single-field search, we'll skip the part validation
                // but still need variables for the API call
                year = "";
                make = "";
                model = "";
                part = "auto part"; // Set a dummy value to bypass validation
                engine = "";
                fieldPrompt = singleFieldQuery;
            } else {
                // Multi-field mode - get values from individual fields
                year = yearField.value.trim();
                make = makeField.value.trim();
                model = modelField.value.trim();
                part = partField.value.trim();
                engine = engineField.value.trim();
                
                if (!part) {
                    showValidationError("Please enter the part you're looking for.");
                    return;
                }
                
                if (!year && !make) {
                    showValidationError("Please enter at least the vehicle year or make.");
                    return;
                }
            }
            
            // Disable the search button and show loading
            searchButton.disabled = true;
            searchButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2" style="width: 1rem; height: 1rem;" role="status" aria-hidden="true"></span><span style="vertical-align: middle;">Finding Parts...</span>';
            
            // Reset UI
            hideValidationError();
            resultContainer.style.display = 'none';
            questionsContainer.innerHTML = '';
            productsContainer.innerHTML = '';
            
            // Show loading indicator for analysis
            searchLoading.style.display = 'block';
            
            try {
                // Step 1: Send the field-based search request
                // If we're in single-field mode, fieldPrompt is already set
                // Otherwise, build it from the individual fields
                if (!isSingleFieldMode) {
                    fieldPrompt = '';
                    if (year) fieldPrompt += year + ' ';
                    if (make) fieldPrompt += make + ' ';
                    if (model) fieldPrompt += model + ' ';
                    if (part) fieldPrompt += part + ' ';
                    if (engine) fieldPrompt += engine + ' ';
                    fieldPrompt = fieldPrompt.trim();
                }
                
                // Use the existing 'prompt' parameter expected by the API
                const formData = new FormData();
                formData.append('prompt', fieldPrompt);
                
                // Also include the separate fields as structured data (some APIs might use this)
                const structuredData = {
                    year, make, model, part, engine
                };
                
                // Pass the structured data as JSON string in the form data
                formData.append('structured_data', JSON.stringify(structuredData));
                
                const analysisStartTime = performance.now();
                // Use the existing analyze endpoint instead of the field-search endpoint
                const analysisResponse = await fetch('/api/analyze', {
                    method: 'POST',
                    body: formData
                });
                
                const analysisData = await analysisResponse.json();
                const analysisEndTime = performance.now();
                const analysisTime = ((analysisEndTime - analysisStartTime) / 1000).toFixed(2);
                
                // Hide analysis loading
                searchLoading.style.display = 'none';
                
                if (!analysisData.success) {
                    if (analysisData.validation_error) {
                        showValidationError(analysisData.validation_error);
                    } else {
                        showValidationError(analysisData.error || 'An error occurred. Please try again.');
                    }
                    resultContainer.style.display = 'flex';
                    return;
                }
                
                // Display AI analysis
                questionsContainer.innerHTML = analysisData.questions.replace(/\\n/g, '<br>');
                
                // Display the analysis time
                analysisTimeSpan.textContent = `${analysisTime}s`;
                
                // Show results container
                resultContainer.style.display = 'flex';
                
                // Step 2: Search for products
                if (analysisData.search_terms && analysisData.search_terms.length > 0) {
                    // Show loading for products
                    productsLoading.style.display = 'block';
                    
                    // Prepare form data for product search
                    const productFormData = new FormData();
                    productFormData.append('search_term', analysisData.search_terms[0]);
                    
                    // Build original query string for context
                    let originalQuery;
                    if (isSingleFieldMode) {
                        // For single field, use the field prompt directly
                        originalQuery = fieldPrompt;
                    } else {
                        // For multi-field, join the individual fields
                        originalQuery = [year, make, model, part, engine].filter(Boolean).join(' ');
                    }
                    productFormData.append('original_query', originalQuery);
                    
                    // Also pass structured data for better search handling
                    productFormData.append('structured_data', JSON.stringify({
                        year, make, model, part, engine
                    }));
                    
                    const productResponse = await fetch('/api/search-products', {
                        method: 'POST',
                        body: productFormData
                    });
                    
                    const productData = await productResponse.json();
                    
                    // Hide products loading
                    productsLoading.style.display = 'none';
                    
                    if (productData.success) {
                        // Update the product tab badge count
                        if (productCountBadge) {
                            productCountBadge.textContent = productData.listings.length;
                        }
                        
                        if (productTotalCount) {
                            productTotalCount.textContent = productData.listings.length;
                        }
                        
                        // Use the product display system if available
                        if (window.productDisplay) {
                            window.productDisplay.setProducts(productData.listings);
                        } else if (window.displayProducts) {
                            window.displayProducts(productData.listings);
                        } else {
                            // Basic fallback display
                            displayBasicProducts(productData.listings);
                        }
                        
                        // Auto-switch to the products tab if we have products
                        if (productData.listings.length > 0) {
                            setTimeout(() => {
                                const productsTab = document.getElementById('products-tab');
                                if (productsTab) {
                                    productsTab.click();
                                }
                            }, 100);
                        }
                    }
                }
            } catch (error) {
                console.error('Error:', error);
                searchLoading.style.display = 'none';
                productsLoading.style.display = 'none';
                showValidationError('A network error occurred. Please try again.');
                resultContainer.style.display = 'flex';
            }
            
            // Re-enable the search button
            searchButton.disabled = false;
            searchButton.innerHTML = '<i class="fas fa-search me-1"></i> Find Parts';
        });
    }
    
    // Helper function to show validation errors
    function showValidationError(message) {
        if (validationError) {
            validationError.textContent = message;
            validationError.classList.remove('d-none');
        }
    }
    
    // Helper function to hide validation errors
    function hideValidationError() {
        if (validationError) {
            validationError.textContent = '';
            validationError.classList.add('d-none');
        }
    }
    
    // Basic product display fallback if the main display system is not available
    function displayBasicProducts(listings) {
        if (!productsContainer) return;
        
        productsContainer.innerHTML = '';
        
        if (!listings || listings.length === 0) {
            productsContainer.innerHTML = '<div class="col-12 text-center"><p>No products found. Try a different search term.</p></div>';
            return;
        }
        
        listings.forEach(item => {
            const productId = btoa(item.title.substring(0, 30) + item.price).replace(/[^a-zA-Z0-9]/g, '');
            const sourceClass = item.source === 'eBay' ? 'source-ebay' : 'source-google';
            const conditionClass = item.condition.toLowerCase().includes('new') ? 'condition-new' : 'condition-used';
            const shippingClass = item.shipping.toLowerCase().includes('free') ? 'free-shipping' : '';
            
            const productCard = document.createElement('div');
            productCard.className = 'col-md-4 col-lg-3 mb-3';
            productCard.innerHTML = `
                <div class="product-card">
                    <div class="product-source ${sourceClass}">${item.source}</div>
                    <button class="favorite-btn" data-product-id="${productId}">
                        <i class="fas fa-heart"></i>
                    </button>
                    <div class="product-image-container" data-image="${item.image || '/static/placeholder.png'}">
                        <img src="${item.image || '/static/placeholder.png'}" class="product-image" alt="${item.title}">
                    </div>
                    <div class="p-3">
                        <div class="product-title mb-2">${item.title}</div>
                        <div class="d-flex justify-content-between mb-1">
                            <span>Condition:</span>
                            <span class="${conditionClass}">${item.condition}</span>
                        </div>
                        <div class="d-flex justify-content-between mb-1">
                            <span>Price:</span>
                            <span class="product-price">${item.price}</span>
                        </div>
                        <div class="d-flex justify-content-between mb-3">
                            <span>Shipping:</span>
                            <span class="${shippingClass}">${item.shipping}</span>
                        </div>
                        <a href="${item.link}" target="_blank" class="btn btn-danger btn-sm w-100">View Details</a>
                    </div>
                </div>
            `;
            
            productsContainer.appendChild(productCard);
        });
        
        // Dispatch event to notify that products were displayed
        document.dispatchEvent(new CustomEvent('productsDisplayed'));
    }
});