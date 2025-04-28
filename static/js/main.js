/**
 * AutoXpress Main Script
 * Handles form submission, API calls, and UI functionality
 */
document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const searchForm = document.getElementById('search-form');
    const searchButton = document.getElementById('search-button');
    const singleSearchButton = document.getElementById('single-search-button');
    const vinForm = document.getElementById('vin-form');
    const resultContainer = document.getElementById('result-container');
    const vinResultContainer = document.getElementById('vin-result-container');
    const questionsContainer = document.getElementById('questions');
    const productsContainer = document.getElementById('products-container');
    const validationError = document.getElementById('validation-error');
    const analysisTimeSpan = document.getElementById('analysis-time');
    const searchLoading = document.getElementById('search-loading');
    const productsLoading = document.getElementById('products-loading');
    const vinLoading = document.getElementById('vin-loading');
    const vinError = document.getElementById('vin-error');
    const vinData = document.getElementById('vin-data');
    const toggleSortBtn = document.getElementById('toggle-sort');
    const sortLabel = document.getElementById('sort-label');
    const favoritesNavLink = document.getElementById('favorites-nav-link');
    const favoritesTab = document.getElementById('favorites-tab');
    const favoritesList = document.getElementById('favorites-list');
    const exportFavoritesBtn = document.getElementById('export-favorites');
    const clearFavoritesBtn = document.getElementById('clear-favorites');
    const imageModal = document.getElementById('imageModal');
    const modalImage = document.getElementById('modalImage');
    const closeModal = document.querySelector('.close-modal');
    
    // Input fields
    const yearField = document.getElementById('year-field');
    const makeField = document.getElementById('make-field');
    const modelField = document.getElementById('model-field');
    const partField = document.getElementById('part-field');
    const engineField = document.getElementById('engine-field');
    const promptField = document.getElementById('prompt');
    
    // State variables
    let currentListings = [];
    let sortMode = 'relevance'; // Default sort mode: relevance
    let queryParseData = null;
    let lastQuery = '';
    let parseTimeout = null;
    
    // Create and insert the search feedback elements
    const searchFeedbackContainer = document.createElement('div');
    searchFeedbackContainer.className = 'search-feedback mt-2 d-none';
    searchFeedbackContainer.innerHTML = `
    <div class="card">
        <div class="card-body p-2">
            <div class="small mb-1 text-muted">Detected vehicle information:</div>
            <div class="d-flex flex-wrap gap-2">
                <span class="badge border border-primary text-primary year-badge">Year: <span>--</span></span>
                <span class="badge border border-success text-success make-badge">Make: <span>--</span></span>
                <span class="badge border border-info text-info model-badge">Model: <span>--</span></span>
                <span class="badge border border-warning text-warning part-badge">Part: <span>--</span></span>
                <span class="badge border border-secondary text-secondary position-badge d-none">Position: <span>--</span></span>
                <span class="badge border border-danger text-danger engine-badge d-none">Engine: <span>--</span></span>
            </div>
            <div class="confidence-meter mt-2 mb-1">
                <div class="progress" style="height: 4px;">
                    <div class="progress-bar" role="progressbar" style="width: 0%"></div>
                </div>
                <div class="d-flex justify-content-between mt-1">
                    <small class="text-muted">Search confidence</small>
                    <small class="confidence-value text-muted">0%</small>
                </div>
            </div>
        </div>
    </div>
`;
    
    // Insert the feedback container after the search form
    searchForm.parentNode.insertBefore(searchFeedbackContainer, searchForm.nextSibling);
    
    // DOM references to the feedback elements
    const yearBadge = searchFeedbackContainer.querySelector('.year-badge span');
    const makeBadge = searchFeedbackContainer.querySelector('.make-badge span');
    const partBadge = searchFeedbackContainer.querySelector('.part-badge span');
    const positionBadge = searchFeedbackContainer.querySelector('.position-badge');
    const positionBadgeText = positionBadge.querySelector('span');
    const confidenceBar = searchFeedbackContainer.querySelector('.progress-bar');
    const confidenceValue = searchFeedbackContainer.querySelector('.confidence-value');
    const modelBadge = searchFeedbackContainer.querySelector('.model-badge span');
    const engineBadge = searchFeedbackContainer.querySelector('.engine-badge span');
    
    // Construct a query from multiple fields
    function constructQueryFromFields() {
        const yearVal = yearField.value.trim();
        const makeVal = makeField.value.trim();
        const modelVal = modelField.value.trim();
        const partVal = partField.value.trim();
        const engineVal = engineField.value.trim();
        
        let query = '';
        
        if (yearVal) query += yearVal + ' ';
        if (makeVal) query += makeVal + ' ';
        if (modelVal) query += modelVal + ' ';
        if (partVal) query += partVal + ' ';
        if (engineVal) query += engineVal + ' ';
        
        return query.trim();
    }
    
    // Get structured data from fields
    function getStructuredDataFromFields() {
        return {
            year: yearField.value.trim(),
            make: makeField.value.trim(),
            model: modelField.value.trim(),
            part: partField.value.trim(),
            engine: engineField.value.trim()
        };
    }
    
    // Enhanced product filtering function
    function enhanceProductListings(listings, query, vehicleInfo) {
        if (!listings || !listings.length) return [];
        
        // Check if we're searching for a bumper
        const isBumperSearch = vehicleInfo.part && 
                             vehicleInfo.part.toLowerCase().includes('bumper');
        
        // Define priority keywords that indicate an actual bumper assembly (not accessories)
        const assemblyKeywords = [
            'complete assembly', 
            'assembly',
            'front end',
            'full bumper',
            'bumper cover'
        ];
        
        // Define keywords that usually indicate just accessories (not the main part)
        const accessoryKeywords = [
            'guard',
            'protector',
            'cover only',
            'bracket only',
            'pad',
            'trim piece',
            'molding'
        ];
        
        // Score each listing based on relevance to the search
        const scoredListings = listings.map(listing => {
            let score = 0;
            const title = listing.title.toLowerCase();
            
            // Start with base score based on source (prefer eBay for parts)
            score += listing.source === 'eBay' ? 5 : 0;
            
            // Add points for each vehicle info match
            if (vehicleInfo.year && title.includes(vehicleInfo.year)) {
                score += 10;
            }
            
            if (vehicleInfo.make && title.includes(vehicleInfo.make.toLowerCase())) {
                score += 10;
            }
            
            if (vehicleInfo.model) {
                // Check for model with different formats (F-150, F150, etc.)
                const modelVariants = [
                    vehicleInfo.model.toLowerCase(),
                    vehicleInfo.model.toLowerCase().replace('-', ''),
                    vehicleInfo.model.toLowerCase().replace('-', ' ')
                ];
                
                if (modelVariants.some(variant => title.includes(variant))) {
                    score += 15;
                }
            }
            
            // Add points for condition (prefer new parts)
            if (listing.condition.toLowerCase().includes('new')) {
                score += 5;
            }
            
            // Adjust score for bumper searches
            if (isBumperSearch) {
                // Boost score for actual bumper assemblies
                if (assemblyKeywords.some(keyword => title.includes(keyword))) {
                    score += 25;
                }
                
                // Penalize accessories when searching for full assemblies
                if (vehicleInfo.part.toLowerCase().includes('assembly')) {
                    if (accessoryKeywords.some(keyword => title.includes(keyword)) &&
                        !assemblyKeywords.some(keyword => title.includes(keyword))) {
                        score -= 30;
                    }
                }
            }
            
            return {
                ...listing,
                relevanceScore: score
            };
        });
        
        // Sort by relevance score (highest first)
        scoredListings.sort((a, b) => b.relevanceScore - a.relevanceScore);
        
        // Filter out very low-scoring items (likely irrelevant)
        const filteredListings = scoredListings.filter(item => item.relevanceScore > 0);
        
        return filteredListings;
    }
    
    // Extract vehicle info from a query
    function extractVehicleInfo(query) {
        // This is a simplified version - the server does a more thorough job
        const yearMatch = query.match(/\b(19|20)\d{2}\b/);
        const year = yearMatch ? yearMatch[0] : null;
        
        // Extract make (simplified)
        let make = null;
        const makes = ["ford", "toyota", "honda", "nissan", "chevrolet", "dodge"];
        for (const m of makes) {
            if (query.toLowerCase().includes(m)) {
                make = m;
                break;
            }
        }
        
        // Extract model (simplified for common models)
        let model = null;
        if (make === "ford" && query.toLowerCase().match(/\bf[-\s]?150\b/)) {
            model = "f-150";
        } else if (make === "toyota" && query.toLowerCase().includes("camry")) {
            model = "camry";
        } else if (make === "honda" && query.toLowerCase().includes("civic")) {
            model = "civic";
        } else if (make === "nissan" && query.toLowerCase().includes("frontier")) {
            model = "frontier";
        }
        
        // Extract part (simplified)
        let part = null;
        const parts = ["front bumper assembly", "bumper assembly", "front bumper", "brake pads", "alternator"];
        for (const p of parts) {
            if (query.toLowerCase().includes(p)) {
                part = p;
                break;
            }
        }
        
        return { year, make, model, part };
    }
    
    // Real-time query parsing with debouncing (for single field)
    if (promptField) {
        promptField.addEventListener('input', function() {
            const query = this.value.trim();
            
            // Only process if the query is different and not empty
            if (query === lastQuery || query.length < 3) {
                if (query.length === 0) {
                    searchFeedbackContainer.classList.add('d-none');
                }
                return;
            }
            
            lastQuery = query;
            
            // Clear previous timeout
            if (parseTimeout) {
                clearTimeout(parseTimeout);
            }
            
            // Set a new timeout to avoid too many requests
            parseTimeout = setTimeout(() => {
                parseQuery(query);
            }, 500);
        });
    }
    
    // For multi-field search, parse when fields change
    const multiFields = [yearField, makeField, modelField, partField, engineField];
    multiFields.forEach(field => {
        if (field) {
            field.addEventListener('change', function() {
                const query = constructQueryFromFields();
                if (query.length >= 3) {
                    parseQuery(query, getStructuredDataFromFields());
                } else {
                    searchFeedbackContainer.classList.add('d-none');
                }
            });
        }
    });
    
    // Function to parse the query and update the UI
    function parseQuery(query, structuredData = null) {
        // Prepare form data
        const formData = new FormData();
        formData.append('prompt', query);
        
        // Add structured data if available
        if (structuredData) {
            formData.append('structured_data', JSON.stringify(structuredData));
        }
        
        fetch('/api/parse-query', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                queryParseData = data.parsed_data;
                updateQueryFeedback(queryParseData);
                searchFeedbackContainer.classList.remove('d-none');
            } else {
                // Hide the feedback if there's an error
                searchFeedbackContainer.classList.add('d-none');
            }
        })
        .catch(error => {
            console.error('Error parsing query:', error);
            searchFeedbackContainer.classList.add('d-none');
        });
    }
    
    function updateQueryFeedback(data) {
        const vehicleInfo = data.vehicle_info;
        
        // Update year badge
        if (vehicleInfo.year) {
            yearBadge.textContent = vehicleInfo.year;
            yearBadge.parentElement.classList.remove('bg-secondary');
            yearBadge.parentElement.classList.add('bg-primary');
        } else {
            yearBadge.textContent = 'Unknown';
            yearBadge.parentElement.classList.remove('bg-primary');
            yearBadge.parentElement.classList.add('bg-secondary');
        }
        
        // Update make badge
        if (vehicleInfo.make) {
            makeBadge.textContent = vehicleInfo.make.charAt(0).toUpperCase() + vehicleInfo.make.slice(1);
            makeBadge.parentElement.classList.remove('bg-secondary');
            makeBadge.parentElement.classList.add('bg-success');
        } else {
            makeBadge.textContent = 'Unknown';
            makeBadge.parentElement.classList.remove('bg-success');
            makeBadge.parentElement.classList.add('bg-secondary');
        }
        
        // Update model badge
        const modelBadgeEl = modelBadge.parentElement;
        if (vehicleInfo.model) {
            modelBadge.textContent = vehicleInfo.model.charAt(0).toUpperCase() + vehicleInfo.model.slice(1);
            modelBadgeEl.classList.remove('bg-secondary', 'd-none');
            modelBadgeEl.classList.add('bg-info');
        } else {
            modelBadge.textContent = 'Unknown';
            modelBadgeEl.classList.remove('bg-info');
            modelBadgeEl.classList.add('bg-secondary', 'd-none');
        }
        
        // Update part badge
        if (vehicleInfo.part) {
            partBadge.textContent = vehicleInfo.part;
            partBadge.parentElement.classList.remove('bg-secondary');
            partBadge.parentElement.classList.add('bg-warning');
        } else {
            partBadge.textContent = 'Unknown';
            partBadge.parentElement.classList.remove('bg-warning');
            partBadge.parentElement.classList.add('bg-secondary');
        }
        
        // Update position badge
        if (vehicleInfo.position && vehicleInfo.position.length > 0) {
            positionBadgeText.textContent = vehicleInfo.position.join(', ');
            positionBadge.classList.remove('d-none');
        } else {
            positionBadge.classList.add('d-none');
        }
        
        // Update engine badge
        const engineBadgeEl = engineBadge.parentElement;
        if (vehicleInfo.engine_specs) {
            let engineText = '';
            if (vehicleInfo.engine_specs.displacement) {
                engineText += vehicleInfo.engine_specs.displacement;
            }
            if (vehicleInfo.engine_specs.type) {
                engineText += (engineText ? ' ' : '') + vehicleInfo.engine_specs.type;
            }
            if (engineText) {
                engineBadge.textContent = engineText;
                engineBadgeEl.classList.remove('d-none');
            } else {
                engineBadgeEl.classList.add('d-none');
            }
        } else {
            engineBadgeEl.classList.add('d-none');
        }
        
        // Update confidence meter
        const confidence = data.confidence || 0;
        confidenceBar.style.width = `${confidence}%`;
        confidenceValue.textContent = `${confidence}%`;
        
        // Update confidence bar color
        if (confidence >= 80) {
            confidenceBar.className = 'progress-bar bg-success';
        } else if (confidence >= 50) {
            confidenceBar.className = 'progress-bar bg-warning';
        } else {
            confidenceBar.className = 'progress-bar bg-danger';
        }
    }
    
    // Favorites system
    const FAVORITES_STORAGE_KEY = 'autoxpress_favorites';
    
    // Load favorites from localStorage
    function loadFavorites() {
        const favoritesJson = localStorage.getItem(FAVORITES_STORAGE_KEY);
        return favoritesJson ? JSON.parse(favoritesJson) : {};
    }
    
    // Save favorites to localStorage
    function saveFavorites(favorites) {
        localStorage.setItem(FAVORITES_STORAGE_KEY, JSON.stringify(favorites));
    }
    
    // Toggle favorite status for a product
    function toggleFavorite(productId, productData) {
      const favorites = loadFavorites();
      
      if (favorites[productId]) {
          delete favorites[productId];
      } else {
          favorites[productId] = {
              ...productData,
              savedAt: new Date().toISOString()
          };
      }
      
      saveFavorites(favorites);
      updateFavoriteButtons();
      return favorites[productId] !== undefined;
  }
  
  // In the event listener for favorite buttons:
  document.addEventListener('click', function(e) {
      // Check if the clicked element is a favorite button or a child of it
      const btn = e.target.closest('.favorite-btn');
      if (!btn) return; // Not a favorite button, exit
  
      e.preventDefault();
      e.stopPropagation();
      
      const productId = btn.dataset.productId;
      if (!productId) {
          console.error('No product ID found on favorite button');
          return;
      }
      
      // Find the product card
      const productCard = btn.closest('.product-card');
      if (!productCard) {
          console.error('Product card not found');
          return;
      }
      
      // Get product data with null checks
      const titleElement = productCard.querySelector('.product-title');
      const priceElement = productCard.querySelector('.product-price');
      const imageElement = productCard.querySelector('.product-image');
      const conditionElement = productCard.querySelector('[class*="condition-"]');
      const shippingElement = productCard.querySelector('[class*="shipping"]');
      const linkElement = productCard.querySelector('a');
      const sourceElement = productCard.querySelector('.product-source');
      
      if (!titleElement || !priceElement || !imageElement) {
          console.error('Required product elements not found');
          return;
      }
      
      const productData = {
          title: titleElement.textContent,
          price: priceElement.textContent,
          image: imageElement.src,
          condition: conditionElement ? conditionElement.textContent : 'Not specified',
          shipping: shippingElement ? shippingElement.textContent : 'Shipping not specified',
          link: linkElement ? linkElement.href : '#',
          source: sourceElement ? sourceElement.textContent : 'Unknown'
      };
      
      const isFavorite = toggleFavorite(productId, productData);
      btn.classList.toggle('active', isFavorite);
      
      // If we're on the favorites tab, refresh the display
      const favoritesContent = document.getElementById('favorites-content');
      if (favoritesContent && favoritesContent.classList.contains('active')) {
          if (typeof displayFavorites === 'function') {
              displayFavorites();
          }
      }
  });
  
    // Update all favorite buttons to reflect current state
    function updateFavoriteButtons() {
        const favorites = loadFavorites();
        const favoriteButtons = document.querySelectorAll('.favorite-btn');
        
        favoriteButtons.forEach(btn => {
            const productId = btn.dataset.productId;
            if (favorites[productId]) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
    }
    
    // Display favorites in the favorites tab
    function displayFavorites() {
        const favorites = loadFavorites();
        const favoriteIds = Object.keys(favorites);
        
        if (favoriteIds.length === 0) {
            favoritesList.innerHTML = `
                <div class="col-12 no-favorites-msg">
                    <i class="fas fa-heart fa-3x mb-3 text-muted"></i>
                    <p>You haven't saved any favorites yet</p>
                </div>
            `;
            return;
        }
        
        favoritesList.innerHTML = '';
        favoriteIds.forEach(id => {
            const item = favorites[id];
            const sourceClass = item.source === 'eBay' ? 'source-ebay' : 'source-google';
           const conditionClass = item.condition.toLowerCase().includes('new') ? 'condition-new' : 'condition-used';
            const shippingClass = item.shipping.toLowerCase().includes('free') ? 'free-shipping' : '';
            
            const productCard = document.createElement('div');
            productCard.className = 'col-md-6 col-lg-4 mb-3';
            productCard.innerHTML = `
                <div class="product-card h-100">
                    <div class="product-source ${sourceClass}">${item.source}</div>
                    <button class="favorite-btn active" data-product-id="${id}">
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
                        <a href="${item.link}" target="_blank" class="btn btn-primary btn-sm w-100">View Details</a>
                    </div>
                </div>
            `;
            
            favoritesList.appendChild(productCard);
        });
        
        // Add event listeners to the favorite buttons
        attachFavoriteButtonListeners();
        // Add event listeners to the image containers
        attachImagePreviewListeners();
    }
    
    // Export favorites as JSON file
    function exportFavorites() {
        const favorites = loadFavorites();
        const dataStr = JSON.stringify(favorites, null, 2);
        const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
        
        const exportFileDefaultName = 'autoxpress_favorites.json';
        
        const linkElement = document.createElement('a');
        linkElement.setAttribute('href', dataUri);
        linkElement.setAttribute('download', exportFileDefaultName);
        linkElement.click();
    }
    
    // Clear all favorites
    function clearAllFavorites() {
        if (confirm('Are you sure you want to clear all favorites? This cannot be undone.')) {
            localStorage.removeItem(FAVORITES_STORAGE_KEY);
            displayFavorites();
        }
    }
    
    // Generate a unique ID for a product
    function generateProductId(product) {
      // Create a unique ID based on title and price, handling non-ASCII characters
      try {
        return btoa(product.title.substring(0, 30) + product.price).replace(/[^a-zA-Z0-9]/g, '');
      } catch (e) {
        // Handle non-ASCII characters by using encodeURIComponent
        const safeString = encodeURIComponent(product.title.substring(0, 30) + product.price);
        return btoa(safeString).replace(/[^a-zA-Z0-9]/g, '');
      }
    }
    
    // Attach event listeners to favorite buttons
    function attachFavoriteButtonListeners() {
        document.querySelectorAll('.favorite-btn').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                const productId = this.dataset.productId;
                
                // Find the product card
                const productCard = this.closest('.product-card');
                const title = productCard.querySelector('.product-title').textContent;
                const price = productCard.querySelector('.product-price').textContent;
                const image = productCard.querySelector('.product-image').src;
                const condition = productCard.querySelector('[class*="condition-"]').textContent;
                const shipping = productCard.querySelector('[class*="shipping"]') ? 
                                productCard.querySelector('[class*="shipping"]').textContent : 'Shipping not specified';
                const link = productCard.querySelector('a').href;
                const source = productCard.querySelector('.product-source').textContent;
                
                const productData = {
                    title, price, image, condition, shipping, link, source
                };
                
                const isFavorite = toggleFavorite(productId, productData);
                this.classList.toggle('active', isFavorite);
                
                // If we're on the favorites tab, refresh the display
                if (document.getElementById('favorites-content').classList.contains('active')) {
                    displayFavorites();
                }
            });
        });
    }
  
    // Global image modal functions - made available to window so they can be called from anywhere
    window.openImageModal = function(imgSrc) {
      if (!imageModal || !modalImage) {
        console.error('Image modal elements not found');
        return;
      }
      modalImage.src = imgSrc;
      imageModal.style.display = 'block';
      console.log('Modal opened with image:', imgSrc);
    };
  
    window.closeImageModal = function() {
      if (!imageModal) {
        console.error('Image modal element not found');
        return;
      }
      imageModal.style.display = 'none';
      console.log('Modal closed');
    };
  
    // Attach event listeners to image containers
    function attachImagePreviewListeners() {
      const containers = document.querySelectorAll('.product-image-container');
      console.log(`Found ${containers.length} image containers to attach listeners to`);
      
      containers.forEach(container => {
        container.style.cursor = 'pointer'; // Visual feedback that it's clickable
        
        // Remove any existing listeners to prevent duplicates
        const clone = container.cloneNode(true);
        container.parentNode.replaceChild(clone, container);
        
        // Add new click listener
        clone.addEventListener('click', function(e) {
          e.preventDefault();
          e.stopPropagation();
          
          const imgSrc = this.dataset.image || this.querySelector('img')?.src || '/static/placeholder.png';
          console.log('Image container clicked, opening modal with:', imgSrc);
          window.openImageModal(imgSrc);
        });
      });
    }
    
    // Set up modal close handlers
    if (closeModal) {
      closeModal.addEventListener('click', function() {
        window.closeImageModal();
      });
    }
    
    // Close modal when clicking outside the image
    window.addEventListener('click', function(event) {
      if (event.target === imageModal) {
        window.closeImageModal();
      }
    });
    
    // Tab Navigation
    if (favoritesNavLink && favoritesTab) {
        favoritesNavLink.addEventListener('click', function(e) {
            e.preventDefault();
            favoritesTab.click();
        });
    }
    
    // Favorites system event listeners
    if (exportFavoritesBtn) {
        exportFavoritesBtn.addEventListener('click', exportFavorites);
    }
    
    if (clearFavoritesBtn) {
        clearFavoritesBtn.addEventListener('click', clearAllFavorites);
    }
    
    // Display favorites on tab activation
    const favoritesTabElem = document.getElementById('favorites-tab');
    if (favoritesTabElem) {
        favoritesTabElem.addEventListener('shown.bs.tab', displayFavorites);
    }
    
    // Don't hide results when switching tabs
    document.querySelectorAll('button[data-bs-toggle="tab"]').forEach(tab => {
        tab.addEventListener('click', function() {
            // Don't hide results, they should persist between tab switches
            // However, make sure the appropriate container is shown based on the active tab
            if (this.id === 'vin-tab') {
                if (!vinResultContainer.classList.contains('d-none') && 
                    vinData.querySelector('.card')) {
                    // Show VIN results if they exist
                    vinResultContainer.classList.remove('d-none');
                }
            } else if (this.id === 'search-tab') {
                if (resultContainer.style.display === 'flex') {
                    // Show search results if they exist
                    resultContainer.style.display = 'flex';
                }
            }
        });
    });
  
    // Toggle between sort modes (price vs. relevance)
    if (toggleSortBtn) {
        toggleSortBtn.addEventListener('click', function() {
            if (sortMode === 'price') {
                sortMode = 'relevance';
                sortLabel.textContent = 'Relevance';
                toggleSortBtn.innerHTML = '<i class="fas fa-sort-amount-down-alt"></i> Relevance';
            } else {
                sortMode = 'price';
                sortLabel.textContent = 'Price';
                toggleSortBtn.innerHTML = '<i class="fas fa-sort-amount-down-alt"></i> Price';
            }
            
            // Re-sort and display the current listings
            sortAndDisplayProducts();
        });
    }
  
    // Function to sort and display products
    function sortAndDisplayProducts() {
        if (!currentListings || currentListings.length === 0) return;
        
        let sortedListings = [...currentListings];
        
        if (sortMode === 'price') {
            // Sort by price
            sortedListings = sortedListings.sort((a, b) => {
                const priceA = parseFloat(a.price.replace(/[^0-9.]/g, '')) || 0;
                const priceB = parseFloat(b.price.replace(/[^0-9.]/g, '')) || 0;
                return priceA - priceB;
            });
        } else if (sortMode === 'relevance' && sortedListings[0].relevanceScore !== undefined) {
            // Sort by relevance score if available
            sortedListings = sortedListings.sort((a, b) => 
                (b.relevanceScore || 0) - (a.relevanceScore || 0)
            );
        }
        
        displayProducts(currentListings);
    }
  
    // Search form submission
    if (searchForm) {
        searchForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Determine which search approach to use (single field or multi-field)
            const isSingleField = !document.getElementById('single-field-container').classList.contains('d-none');
            
            let query, structuredData;
            
            if (isSingleField) {
                query = promptField.value.trim();
                structuredData = null;
            } else {
                query = constructQueryFromFields();
                structuredData = getStructuredDataFromFields();
            }
            
            if (!query) {
                alert('Please enter search criteria.');
                return;
            }
            
            // Disable the search button and show loading
            const activeSearchButton = isSingleField ? singleSearchButton : searchButton;
            activeSearchButton.disabled = true;
            activeSearchButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2" style="width: 1rem; height: 1rem;" role="status" aria-hidden="true"></span><span style="vertical-align: middle;">Finding Parts...</span>';
            
            // Reset UI for search results only
            validationError.classList.add('d-none');
            resultContainer.style.display = 'none';
            questionsContainer.innerHTML = '';
            productsContainer.innerHTML = '';
            currentListings = [];
            
            // Show loading indicator for analysis
            searchLoading.style.display = 'block';
            
            try {
                // Step 1: Get AI analysis
                const analysisStartTime = performance.now();
                
                // Prepare form data for analysis request
                const formData = new FormData();
                formData.append('prompt', query);
                
                // Add structured data if available
                if (structuredData) {
                    formData.append('structured_data', JSON.stringify(structuredData));
                } else if (queryParseData) {
                    formData.append('parsed_data', JSON.stringify(queryParseData));
                }
                
                // Add local pickup parameter 
                formData.append('local_pickup', 'true');
                
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
                        validationError.textContent = analysisData.validation_error;
                        validationError.classList.remove('d-none');
                    } else {
                        validationError.textContent = analysisData.error || 'An error occurred. Please try again.';
                        validationError.classList.remove('d-none');
                    }
                    resultContainer.style.display = 'flex';
                    return;
                }
                
                // Display AI analysis
                questionsContainer.innerHTML = analysisData.questions.replace(/\n/g, '<br>');
                
                // Display the analysis time if available
                if (analysisData.processed_locally) {
                    analysisTimeSpan.textContent = 'local';
                    analysisTimeSpan.classList.remove('bg-secondary');
                    analysisTimeSpan.classList.add('bg-success');
                } else {
                    analysisTimeSpan.textContent = `${analysisTime}s`;
                    analysisTimeSpan.classList.remove('bg-success');
                    analysisTimeSpan.classList.add('bg-secondary');
                }
                
                resultContainer.style.display = 'flex';
                
                // Step 2: Search for products
                if (analysisData.search_terms && analysisData.search_terms.length > 0) {
                    // Show loading for products
                    productsLoading.style.display = 'block';
                    
                    // Prepare form data for product search
                    const productFormData = new FormData();
                    productFormData.append('search_term', analysisData.search_terms[0]);
                    productFormData.append('original_query', query);
                    
                    // Add structured data if available
                    if (structuredData) {
                        productFormData.append('structured_data', JSON.stringify(structuredData));
                    }
                    
                    // Add local pickup parameter
                    productFormData.append('local_pickup', 'true');
                    
                    const productResponse = await fetch('/api/search-products', {
                        method: 'POST',
                        body: productFormData
                    });
                    
                    const productData = await productResponse.json();
                    
                    // Hide products loading
                    productsLoading.style.display = 'none';
                    
                    if (productData.success) {
                        // Store the original listings
                        const listings = productData.listings;
                        
                        // Extract vehicle info for enhanced filtering
                        const vehicleInfo = structuredData || 
                              (queryParseData && queryParseData.vehicle_info ? 
                                queryParseData.vehicle_info : 
                                extractVehicleInfo(query));
                        
                        // Apply enhanced filtering
                        const enhancedListings = enhanceProductListings(listings, query, vehicleInfo);
                        
                        // Save the enhanced listings to current listings
                        currentListings = enhancedListings;
  
                        // Use the new product display system if available, otherwise use the old one
                        if (window.productDisplay) {
                          // Update the product tab badge count
                          const productCountBadge = document.getElementById('products-count');
                          if (productCountBadge) {
                              productCountBadge.textContent = currentListings.length;
                          }
                          
                          // Set products in the display system
                          window.productDisplay.setProducts(currentListings);
                          
                          // Auto-switch to the products tab if we have products
                          if (currentListings.length > 0) {
                              const productsTab = document.getElementById('products-tab');
                              if (productsTab) {
                                  productsTab.click();
                              }
                          }
                      } else {
                          // Fallback to original display function
                          displayProducts(currentListings);
                      }
                        
                          
                      if (document.getElementById('load-more-btn')) {
                          document.getElementById('load-more-btn').addEventListener('click', function() {
                              const btn = this;
                              btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Loading...';
                              
                              // Enable button and restore text after a short delay
                              setTimeout(() => {
                                  btn.innerHTML = '<i class="fas fa-sync me-2"></i>Load More Products';
                              }, 500);
                          });
                      }
  
                        // Set default sort mode based on what we have
                        sortMode = 'relevance';
                        if (sortLabel) sortLabel.textContent = 'Relevance';
                        if (toggleSortBtn) toggleSortBtn.innerHTML = '<i class="fas fa-sort-amount-down-alt"></i> Relevance';
                        
                
                    }
                }
                
            } catch (error) {
                console.error('Error:', error);
                searchLoading.style.display = 'none';
                productsLoading.style.display = 'none';
                validationError.textContent = 'A network error occurred. Please try again.';
                validationError.classList.remove('d-none');
                resultContainer.style.display = 'flex';
            }
            
            // Re-enable the search button
            activeSearchButton.disabled = false;
            activeSearchButton.innerHTML = '<i class="fas fa-search me-1"></i> Find Parts';
        });
    }
    
    // VIN form submission
    if (vinForm) {
        vinForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const vinValue = document.getElementById('vin').value.trim();
            
            if (!vinValue) {
                alert('Please enter a VIN.');
                return;
            }
            
            // Reset UI for VIN results
            vinError.classList.add('d-none');
            vinData.innerHTML = '';
            vinResultContainer.classList.remove('d-none');
            
            // Show loading
            vinLoading.classList.remove('d-none');
            
            try {
                const response = await fetch('/api/vin-decode', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: new URLSearchParams({
                        'vin': vinValue
                    })
                });
                
                const data = await response.json();
                
                // Hide loading
                vinLoading.classList.add('d-none');
                
                if (data.error) {
                    vinError.textContent = data.error;
                    vinError.classList.remove('d-none');
                    return;
                }
                
                // Display VIN data
                displayVinData(data);
                
            } catch (error) {
                console.error('Error:', error);
                vinLoading.classList.add('d-none');
                vinError.textContent = 'A network error occurred. Please try again later.';
                vinError.classList.remove('d-none');
            }
        });
    }
    
    // Function to display products
    function displayProducts(listings) {
      // If we have a productDisplay module, use it
      if (window.productDisplay && window.productDisplay.setProducts) {
          console.log("Using product display module to show", listings.length, "products");
          // Process and enhance listings
          const enhancedListings = enhanceProductListings(listings, lastQuery, 
              queryParseData && queryParseData.vehicle_info ? 
              queryParseData.vehicle_info : 
              extractVehicleInfo(lastQuery));
          
          // Save current listings and set them in the display system
          currentListings = enhancedListings;
          window.productDisplay.setProducts(enhancedListings);
      } else {
          console.log("Using original product display logic for", listings.length, "products");
          // Original displayProducts code (for backward compatibility)
          productsContainer.innerHTML = '';
          
          if (!listings || listings.length === 0) {
              productsContainer.innerHTML = '<div class="col-12 text-center"><p>No products found. Try a different search term.</p></div>';
              return;
          }
          
          listings.forEach(item => {
              const productId = generateProductId(item);
              const sourceClass = item.source === 'eBay' ? 'source-ebay' : 'source-google';
              const conditionClass = item.condition.toLowerCase().includes('new') ? 'condition-new' : 'condition-used';
              const shippingClass = item.shipping.toLowerCase().includes('free') ? 'free-shipping' : '';
              
              // Check if this product is a favorite
              const favorites = loadFavorites();
              const isFavorite = favorites[productId] !== undefined;
              
              const productCard = document.createElement('div');
              productCard.className = 'col-md-4 col-lg-3 mb-3';
              productCard.innerHTML = `
                  <div class="product-card">
                      <div class="product-source ${sourceClass}">${item.source}</div>
                      <button class="favorite-btn ${isFavorite ? 'active' : ''}" data-product-id="${productId}">
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
                          <a href="${item.link}" target="_blank" class="btn btn-primary btn-sm w-100">View Details</a>
                      </div>
                  </div>
              `;
              
              productsContainer.appendChild(productCard);
          });
          
          // Add event listeners to the favorite buttons
          attachFavoriteButtonListeners();
          // Add event listeners to the image containers
          attachImagePreviewListeners();
      }
      
      // Update product count badges
      const productCountBadge = document.getElementById('products-count');
      if (productCountBadge) {
          productCountBadge.textContent = listings.length;
      }
      
      // Update "Products" tab badge to show count
      const productsTab = document.getElementById('products-tab');
      if (productsTab) {
          // Auto-switch to products tab if we have products
          if (listings.length > 0) {
              productsTab.click();
          }
      }
  }
    
    // Function to display VIN data
    function displayVinData(data) {
        vinData.innerHTML = '';
        
        // Create primary info card
        const primaryInfoCard = document.createElement('div');
        primaryInfoCard.className = 'col-md-6 mb-4';
        primaryInfoCard.innerHTML = `
            <div class="card h-100">
                <div class="card-header bg-primary text-white">Vehicle Information</div>
                <div class="card-body">
                    <h5>${data.ModelYear} ${data.Make} ${data.Model} ${data.Trim || ''}</h5>
                    <table class="table table-sm">
                        <tr>
                            <th>Engine:</th>
                            <td>${data.DisplacementL ? data.DisplacementL + 'L' : ''} ${data.EngineConfiguration || ''} ${data.EngineCylinders ? data.EngineCylinders + '-cyl' : ''}</td>
                        </tr>
                        <tr>
                            <th>Transmission:</th>
                            <td>${data.TransmissionStyle || 'N/A'}</td>
                        </tr>
                        <tr>
                            <th>Drive Type:</th>
                            <td>${data.DriveType || 'N/A'}</td>
                        </tr>
                        <tr>
                            <th>Body Style:</th>
                            <td>${data.BodyClass || 'N/A'}</td>
                        </tr>
                        <tr>
                            <th>Fuel Type:</th>
                            <td>${data.FuelTypePrimary || 'N/A'}</td>
                        </tr>
                    </table>
                </div>
            </div>
        `;
        vinData.appendChild(primaryInfoCard);
        
        // Create additional info card
        const additionalInfoCard = document.createElement('div');
        additionalInfoCard.className = 'col-md-6 mb-4';
        additionalInfoCard.innerHTML = `
            <div class="card h-100">
                <div class="card-header bg-secondary text-white">Additional Details</div>
                <div class="card-body">
                    <table class="table table-sm">
                        <tr>
                            <th>VIN:</th>
                            <td>${data.VIN || 'N/A'}</td>
                        </tr>
                        <tr>
                            <th>Plant:</th>
                            <td>${data.PlantCity ? data.PlantCity + ', ' + data.PlantCountry : 'N/A'}</td>
                        </tr>
                        <tr>
                            <th>Series:</th>
                            <td>${data.Series || 'N/A'}</td>
                        </tr>
                        <tr>
                            <th>Vehicle Type:</th>
                            <td>${data.VehicleType || 'N/A'}</td>
                        </tr>
                        <tr>
                            <th>GVWR:</th>
                            <td>${data.GVWR || 'N/A'}</td>
                        </tr>
                    </table>
                    <button class="btn btn-primary mt-2" id="search-this-vehicle">
                        <i class="fas fa-search me-1"></i> Search Parts for This Vehicle
                    </button>
                </div>
            </div>
        `;
        vinData.appendChild(additionalInfoCard);
        
        // Add event listener to the "Search Parts for This Vehicle" button
        document.getElementById('search-this-vehicle').addEventListener('click', function() {
            // Populate the multi-field form with VIN data
            if (!document.getElementById('single-field-container').classList.contains('d-none')) {
                // If in single field mode, switch to multi-field
                document.getElementById('multi-field-toggle').click();
            }
            
            // Fill in the fields
            yearField.value = data.ModelYear || '';
            makeField.value = data.Make || '';
            modelField.value = data.Model || '';
            engineField.value = data.DisplacementL ? data.DisplacementL + 'L' : '';
            
            // Focus on the part field
            partField.value = '';
            partField.focus();
            
            // Switch to search tab
            document.getElementById('search-tab').click();
        });
    }
    
    // Initialize favorites display
    displayFavorites();
  
  // Directly attach a click handler for product images at the document level
  document.addEventListener('click', function(e) {
    // Find if we clicked on a product image container or one of its children
    const imageContainer = e.target.closest('.product-image-container');
    if (!imageContainer) return;
    
    e.preventDefault();
    e.stopPropagation();
    
    // Get the image source from data attribute or img element
    const imgSrc = imageContainer.dataset.image || 
                   imageContainer.querySelector('img')?.src || 
                   '/static/placeholder.png';
    
    console.log('Image container clicked via document handler, src:', imgSrc);
    window.openImageModal(imgSrc);
  });
  
  // Also update the modal content styling in the CSS
  if (imageModal && modalImage) {
    // Add CSS styles for better modal positioning and sizing
    modalImage.classList.add('modal-content');
    modalImage.style.maxWidth = '650px';
    modalImage.style.maxHeight = '450px';
    modalImage.style.objectFit = 'contain';
    
    // Center the modal better
    imageModal.style.display = 'none';
    imageModal.style.alignItems = 'center';
    imageModal.style.justifyContent = 'center';
  }
  
});

/**
 * This code replaces the button color override section at the end of main.js
 * Remove these lines from the original file and use the class-based approach instead
 */

document.addEventListener('DOMContentLoaded', function() {
    // Remove any direct style overrides for buttons
    // Instead of manually styling buttons in JavaScript, we'll let CSS handle it through proper classes
    
    // Ensure all "Find Parts" buttons have the btn-danger class instead of btn-primary
    const findPartsButtons = document.querySelectorAll('#find-parts-btn, [id$="find-parts"], button[type="submit"]');
    findPartsButtons.forEach(button => {
        if (button.classList.contains('btn-primary')) {
            button.classList.remove('btn-primary');
            button.classList.add('btn-danger');
        }
    });
    
    // Make sure that View Details buttons have the correct classes
    const viewDetailsButtons = document.querySelectorAll('.view-details, .product-card .btn, .product-actions .btn');
    viewDetailsButtons.forEach(button => {
        if (button.classList.contains('btn-primary')) {
            button.classList.remove('btn-primary');
            button.classList.add('btn-danger');
        }
    });
    
    // Use MutationObserver to handle dynamically added buttons
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes && mutation.addedNodes.length > 0) {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1) { // ELEMENT_NODE
                        // Find new buttons inside the added node
                        const newButtons = node.querySelectorAll('.btn-primary, .view-details, .product-card .btn');
                        newButtons.forEach(button => {
                            if (button.classList.contains('btn-primary')) {
                                button.classList.remove('btn-primary');
                                button.classList.add('btn-danger');
                            }
                        });
                    }
                });
            }
        });
    });
    
    // Observe the entire document body for changes
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
});
// Add this to your main.js file to integrate the exact year matching improvements

/**
 * Enhanced function to display products with exact year highlighting
 */
function displayProducts(listings) {
    // Clear the container
    productsContainer.innerHTML = '';
    
    if (!listings || listings.length === 0) {
        productsContainer.innerHTML = '<div class="col-12 text-center"><p>No products found. Try a different search term.</p></div>';
        return;
    }
    
    // Extract the year we searched for (from query or structured form)
    const searchYear = getSearchYear();
    
    // Group by match type if we have exact year matches
    const exactMatches = listings.filter(item => item.exactYearMatch);
    const compatibleMatches = listings.filter(item => item.compatibleRange && !item.exactYearMatch);
    const otherMatches = listings.filter(item => !item.exactYearMatch && !item.compatibleRange);
    
    // Show headers for each section if we have exact matches
    if (exactMatches.length > 0) {
        // Create exact match section header
        const exactMatchHeader = document.createElement('div');
        exactMatchHeader.className = 'col-12';
        exactMatchHeader.innerHTML = `
            <div class="results-section-title">
                <i class="fas fa-check-circle text-success me-2"></i>
                Exact Year Matches (${exactMatches.length})
            </div>
        `;
        productsContainer.appendChild(exactMatchHeader);
        
        // Display exact matches
        exactMatches.forEach(item => {
            renderProductCard(item, true);
        });
        
        // Show compatible matches if any
        if (compatibleMatches.length > 0) {
            const compatibleHeader = document.createElement('div');
            compatibleHeader.className = 'col-12 mt-4';
            compatibleHeader.innerHTML = `
                <div class="results-section-title">
                    <i class="fas fa-calendar-alt text-primary me-2"></i>
                    Compatible Year Range Matches (${compatibleMatches.length})
                </div>
            `;
            productsContainer.appendChild(compatibleHeader);
            
            // Display compatible matches
            compatibleMatches.forEach(item => {
                renderProductCard(item, false, true);
            });
        }
        
        // Show other matches if any
        if (otherMatches.length > 0) {
            const otherHeader = document.createElement('div');
            otherHeader.className = 'col-12 mt-4';
            otherHeader.innerHTML = `
                <div class="results-section-title">
                    <i class="fas fa-search me-2"></i>
                    Other Matches (${otherMatches.length})
                </div>
            `;
            productsContainer.appendChild(otherHeader);
            
            // Display other matches
            otherMatches.forEach(item => {
                renderProductCard(item, false, false);
            });
        }
    } else {
        // No exact matches - just show all listings without sections
        listings.forEach(item => {
            renderProductCard(item, false, !!item.compatibleRange);
        });
    }
    
    // Add event listeners to the favorite buttons
    attachFavoriteButtonListeners();
    // Add event listeners to the image containers
    attachImagePreviewListeners();
    
    // Update product count badges
    const productCountBadge = document.getElementById('products-count');
    if (productCountBadge) {
        productCountBadge.textContent = listings.length;
    }
}

/**
 * Helper function to get the search year
 */
function getSearchYear() {
    // Try multi-field first
    const yearField = document.getElementById('year-field');
    if (yearField && yearField.value) {
        return yearField.value.trim();
    }
    
    // Try single field prompt - extract year with regex
    const promptField = document.getElementById('prompt');
    if (promptField && promptField.value) {
        const yearMatch = promptField.value.match(/\b(19|20)\d{2}\b/);
        if (yearMatch) {
            return yearMatch[0];
        }
    }
    
    return null;
}

/**
 * Helper function to render a product card with appropriate styling
 */
function renderProductCard(product, isExactMatch, isCompatible) {
    const productId = generateProductId(product);
    const sourceClass = product.source === 'eBay' ? 'source-ebay' : 'source-google';
    const conditionClass = product.condition.toLowerCase().includes('new') ? 'condition-new' : 'condition-used';
    const shippingClass = product.shipping.toLowerCase().includes('free') ? 'free-shipping' : '';
    
    // Check if this product is a favorite
    const favorites = loadFavorites();
    const isFavorite = favorites[productId] !== undefined;
    
    // Build card classes
    let cardClasses = "product-card";
    if (isExactMatch) {
        cardClasses += " exact-year-match";
    }
    
    // Create the product card element
    const productCard = document.createElement('div');
    productCard.className = 'col-md-4 col-lg-3 mb-3';
    
    // Build badge HTML
    let badgeHtml = '';
    if (isExactMatch) {
        badgeHtml = '<div class="exact-match-badge">Exact Year Match</div>';
    } else if (isCompatible && product.compatibleRange) {
        badgeHtml = `<div class="compatible-badge">Compatible ${product.compatibleRange}</div>`;
    }
    
    // Build the card HTML
    productCard.innerHTML = `
        <div class="${cardClasses}">
            <div class="product-source ${sourceClass}">${product.source}</div>
            ${badgeHtml}
            <button class="favorite-btn ${isFavorite ? 'active' : ''}" data-product-id="${productId}">
                <i class="fas fa-heart"></i>
            </button>
            <div class="product-image-container" data-image="${product.image || '/static/placeholder.png'}">
                <img src="${product.image || '/static/placeholder.png'}" class="product-image" alt="${product.title}">
            </div>
            <div class="p-3">
                <div class="product-title mb-2">${product.title}</div>
                <div class="d-flex justify-content-between mb-1">
                    <span>Condition:</span>
                    <span class="${conditionClass}">${product.condition}</span>
                </div>
                <div class="d-flex justify-content-between mb-1">
                    <span>Price:</span>
                    <span class="product-price">${product.price}</span>
                </div>
                <div class="d-flex justify-content-between mb-3">
                    <span>Shipping:</span>
                    <span class="${shippingClass}">${product.shipping}</span>
                </div>
                <a href="${product.link}" target="_blank" class="btn btn-danger btn-sm w-100">View Details</a>
            </div>
        </div>
    `;
    
    productsContainer.appendChild(productCard);
}