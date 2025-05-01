/**
 * AutoXpress Main Script
 * Handles form submission, API calls, and UI functionality
 */
document.addEventListener('DOMContentLoaded', function () {
    // DOM Elements
    const searchForm = document.getElementById('search-form');
    const searchButton = document.getElementById('search-button');
    const singleSearchButton = document.getElementById('single-search-button');
    const vinForm = document.getElementById('vin-form');
    const vinButton = document.getElementById('vin-button');
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
        promptField.addEventListener('input', function () {
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
            field.addEventListener('change', function () {
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
        
        // Check if this is being called from the favorites tab
        const isFavoritesTab = document.getElementById('favorites-content') && 
                              document.getElementById('favorites-content').classList.contains('active');

        if (favorites[productId]) {
            // Store the notes before removing the favorite
            const notes = favorites[productId].notes || '';
            delete favorites[productId];
            
            // Only add back the item if we're NOT in the favorites tab and we have notes
            if (!isFavoritesTab && notes && productData) {
                // If toggling elsewhere in the app and we have notes to preserve
                favorites[productId] = {
                    ...productData,
                    notes: notes,
                    savedAt: new Date().toISOString()
                };
                return true;
            }
        } else {
            // Adding a new favorite
            favorites[productId] = {
                ...productData,
                notes: '',  // Initialize with empty notes
                savedAt: new Date().toISOString()
            };
        }

        saveFavorites(favorites);
        updateFavoriteButtons();
        return favorites[productId] !== undefined;
    }

    // In the event listener for favorite buttons:
    document.addEventListener('click', function (e) {
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
        const notesElement = productCard.querySelector('.favorite-notes');
        
        // Get the condition and shipping values more carefully
        let condition = 'Not specified';
        let shipping = 'Shipping not specified';
        
        // First, check if we have a product-meta structure (from updated_products.js display)
        const conditionValueEl = productCard.querySelector('.condition-value');
        const shippingValueEl = productCard.querySelector('.shipping-value');
        
        if (conditionValueEl) {
            condition = conditionValueEl.textContent.trim();
        } else {
            // Fallback to searching in flex rows
            const conditionRow = Array.from(productCard.querySelectorAll('.d-flex')).find(row => 
                row.textContent.includes('Condition:')
            );
            if (conditionRow) {
                const valueEl = conditionRow.querySelector('span:last-child');
                if (valueEl && !valueEl.textContent.includes('Condition:')) {
                    condition = valueEl.textContent.trim();
                }
            }
        }
        
        if (shippingValueEl) {
            shipping = shippingValueEl.textContent.trim();
        } else {
            // Fallback to searching in flex rows
            const shippingRow = Array.from(productCard.querySelectorAll('.d-flex')).find(row => 
                row.textContent.includes('Shipping:')
            );
            if (shippingRow) {
                const valueEl = shippingRow.querySelector('span:last-child');
                if (valueEl && !valueEl.textContent.includes('Shipping:')) {
                    shipping = valueEl.textContent.trim();
                }
            }
        }
        
        const linkElement = productCard.querySelector('a');
        const sourceElement = productCard.querySelector('.product-source');

        if (!titleElement || !priceElement || !imageElement) {
            console.error('Required product elements not found');
            return;
        }

        // Log for debugging
        console.log('Found product data:',
            '\n - Condition:', condition,
            '\n - Shipping:', shipping);

        const productData = {
            title: titleElement.textContent,
            price: priceElement.textContent,
            image: imageElement.src,
            condition: condition,
            shipping: shipping,
            link: linkElement ? linkElement.href : '#',
            source: sourceElement ? sourceElement.textContent : 'Unknown',
            notes: notesElement ? notesElement.value.trim() : ''
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
            
            // Process condition class
            let conditionClass = 'condition-unknown';
            if (item.condition && item.condition.toLowerCase().includes('new')) {
                conditionClass = 'condition-new';
            } else if (item.condition && item.condition.toLowerCase().includes('used')) {
                conditionClass = 'condition-used';
            } else if (item.condition && item.condition.toLowerCase().includes('refurbished')) {
                conditionClass = 'condition-refurbished';
            }
            
            // Process shipping class
            let shippingClass = '';
            if (item.shipping && item.shipping.toLowerCase().includes('free')) {
                shippingClass = 'free-shipping';
            }
            
            const notes = item.notes || '';
            
            // Log for debugging
            console.log('Displaying favorite item:',
                '\n - ID:', id,
                '\n - Condition:', item.condition,
                '\n - Shipping:', item.shipping);

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
                            <span class="${conditionClass} condition-value">${item.condition}</span>
                        </div>
                        <div class="d-flex justify-content-between mb-1">
                            <span>Price:</span>
                            <span class="product-price">${item.price}</span>
                        </div>
                        <div class="d-flex justify-content-between mb-3">
                            <span>Shipping:</span>
                            <span class="${shippingClass} shipping-value">${item.shipping}</span>
                        </div>
                        <a href="${item.link}" target="_blank" class="btn btn-danger btn-sm w-100 mb-2">View Details</a>
                        <div class="favorite-notes-container mt-2">
                            <label for="notes-${id}" class="favorite-notes-label">Notes:</label>
                            <textarea id="notes-${id}" class="favorite-notes" placeholder="Add notes about this item..." data-product-id="${id}">${notes}</textarea>
                        </div>
                    </div>
                </div>
            `;

            favoritesList.appendChild(productCard);
        });

        // Add event listeners to the favorite buttons
        attachFavoriteButtonListeners();
        // Add event listeners to the image containers
        attachImagePreviewListeners();
        // Add event listeners to the notes textareas
        attachNotesListeners();
    }
    
    // Save notes for a favorite
    function saveNotes(productId, notesText) {
        const favorites = loadFavorites();
        if (favorites[productId]) {
            favorites[productId].notes = notesText;
            saveFavorites(favorites);
        }
    }
    
    // Attach listeners to notes textareas
    function attachNotesListeners() {
        document.querySelectorAll('.favorite-notes').forEach(textarea => {
            // Save notes when user stops typing
            textarea.addEventListener('blur', function() {
                const productId = this.dataset.productId;
                const notesText = this.value.trim();
                saveNotes(productId, notesText);
            });
            
            // Auto-resize textarea as user types
            textarea.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = (this.scrollHeight) + 'px';
            });
            
            // Initialize height
            textarea.dispatchEvent(new Event('input'));
        });
    }

    // Export favorites as JSON file
    function exportFavorites() {
        const favorites = loadFavorites();
        
        // Ensure all notes are up-to-date before exporting
        document.querySelectorAll('.favorite-notes').forEach(textarea => {
            const productId = textarea.dataset.productId;
            const notesText = textarea.value.trim();
            if (favorites[productId]) {
                favorites[productId].notes = notesText;
            }
        });
        
        // Save updated favorites first
        saveFavorites(favorites);
        
        const dataStr = JSON.stringify(favorites, null, 2);
        const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);

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
            btn.addEventListener('click', function (e) {
                e.preventDefault();
                e.stopPropagation();
                const productId = this.dataset.productId;

                // Find the product card
                const productCard = this.closest('.product-card');
                const title = productCard.querySelector('.product-title').textContent;
                const price = productCard.querySelector('.product-price').textContent;
                const image = productCard.querySelector('.product-image').src;
                
                // Get the condition and shipping values more carefully
                let condition = 'Not specified';
                let shipping = 'Shipping not specified';
                
                // First, check if we have a product-meta structure (from updated_products.js display)
                const conditionValueEl = productCard.querySelector('.condition-value');
                const shippingValueEl = productCard.querySelector('.shipping-value');
                
                if (conditionValueEl) {
                    condition = conditionValueEl.textContent.trim();
                } else {
                    // Fallback to searching in flex rows
                    const conditionRow = Array.from(productCard.querySelectorAll('.d-flex')).find(row => 
                        row.textContent.includes('Condition:')
                    );
                    if (conditionRow) {
                        const valueEl = conditionRow.querySelector('span:last-child');
                        if (valueEl && !valueEl.textContent.includes('Condition:')) {
                            condition = valueEl.textContent.trim();
                        }
                    }
                }
                
                if (shippingValueEl) {
                    shipping = shippingValueEl.textContent.trim();
                } else {
                    // Fallback to searching in flex rows
                    const shippingRow = Array.from(productCard.querySelectorAll('.d-flex')).find(row => 
                        row.textContent.includes('Shipping:')
                    );
                    if (shippingRow) {
                        const valueEl = shippingRow.querySelector('span:last-child');
                        if (valueEl && !valueEl.textContent.includes('Shipping:')) {
                            shipping = valueEl.textContent.trim();
                        }
                    }
                }
                
                const link = productCard.querySelector('a').href;
                const source = productCard.querySelector('.product-source').textContent;
                
                // Get notes if they exist (for favorites tab)
                const notesTextarea = productCard.querySelector('.favorite-notes');
                let notes = '';
                if (notesTextarea) {
                    notes = notesTextarea.value.trim();
                }

                // Log for debugging
                console.log('Found product data (attachFavoriteButtonListeners):',
                    '\n - Condition:', condition,
                    '\n - Shipping:', shipping);

                const productData = {
                    title, price, image, condition, shipping, link, source, 
                    notes: notes // Include notes in the product data
                };

                const isFavorite = toggleFavorite(productId, productData);
                this.classList.toggle('active', isFavorite);

                // If we're on the favorites tab, refresh the display
                // We need a short delay to let the DOM update, especially when removing items
                if (document.getElementById('favorites-content').classList.contains('active')) {
                    // Give a small delay for DOM updates to complete
                    setTimeout(() => {
                        displayFavorites();
                    }, 50);
                }
            });
        });
    }

    // Global image modal functions - made available to window so they can be called from anywhere
    window.openImageModal = function (imgSrc) {
        if (!imageModal || !modalImage) {
            return;
        }
        
        // Try to get a higher-quality version of the image if available
        const highQualityImg = getHighQualityImageUrl(imgSrc);
        
        // Set the image source with a loading indicator
        modalImage.src = '/static/placeholder.png'; // Use a placeholder while loading
        modalImage.style.opacity = '0.5';
        
        // Create a new image object to preload the high-quality image
        const img = new Image();
        img.onload = function() {
            // Once loaded, update the modal image and fade it in
            modalImage.src = this.src;
            modalImage.style.opacity = '1';
        };
        img.onerror = function() {
            // On error, fall back to the original image
            console.log('Failed to load high-quality image, falling back to original');
            modalImage.src = imgSrc;
            modalImage.style.opacity = '1';
        };
        img.src = highQualityImg;
        
        // Show the modal
        imageModal.style.display = 'block';
    };
    
    // Function to attempt to get a higher quality version of an image
    function getHighQualityImageUrl(url) {
        if (!url) return url;
        
        try {
            // For eBay images, try to modify the URL to get a higher quality version
            // Example: https://i.ebayimg.com/thumbs/images/g/XYZ/s-l225.jpg → https://i.ebayimg.com/images/g/XYZ/s-l1600.jpg
            if (url.includes('ebayimg.com')) {
                // Step 1: Extract the unique identifier from the URL
                const imgId = url.match(/\/g\/([^/]+)\//);
                if (imgId && imgId[1]) {
                    // We found the image identifier, reconstruct the URL with high quality
                    return `https://i.ebayimg.com/images/g/${imgId[1]}/s-l1600.jpg`;
                }
                
                // Fall back to simple replacement if pattern matching fails
                return url.replace('/thumbs', '')
                         .replace('s-l225', 's-l1600')
                         .replace('s-l300', 's-l1600')
                         .replace('s-l400', 's-l1600');
            }
            
            // For Amazon images
            if (url.includes('amazon.com') || url.includes('images-amazon.com')) {
                // Replace thumbnail size indicators with larger ones
                return url.replace(/_SL\d+_/, '_SL1500_')
                         .replace(/_SS\d+_/, '_SL1500_');
            }
            
            // For Walmart images
            if (url.includes('walmart.com') || url.includes('walmartimages.com')) {
                // Remove size limitations
                return url.replace(/[?&]odnHeight=\d+/, '')
                         .replace(/[?&]odnWidth=\d+/, '')
                         .replace(/[?&]odnBg=\w+/, '');
            }
            
            // For Google Shopping images, no specific pattern to upgrade, return as is
            return url;
        } catch (e) {
            console.error('Error processing image URL:', e);
            return url;
        }
    };

    window.closeImageModal = function () {
        if (!imageModal) {
            return;
        }
        imageModal.style.display = 'none';
    };

    // Attach event listeners to image containers
    function attachImagePreviewListeners() {
        const containers = document.querySelectorAll('.product-image-container');

        containers.forEach(container => {
            container.style.cursor = 'pointer'; // Visual feedback that it's clickable

            // Remove any existing listeners to prevent duplicates
            const clone = container.cloneNode(true);
            container.parentNode.replaceChild(clone, container);

            // Add new click listener
            clone.addEventListener('click', function (e) {
                e.preventDefault();
                e.stopPropagation();

                const imgSrc = this.dataset.image || this.querySelector('img')?.src || '/static/placeholder.png';
                window.openImageModal(imgSrc);
            });
        });
    }

    // Set up modal close handlers
    if (closeModal) {
        closeModal.addEventListener('click', function () {
            window.closeImageModal();
        });
    }

    // Close modal when clicking outside the image
    window.addEventListener('click', function (event) {
        if (event.target === imageModal) {
            window.closeImageModal();
        }
    });

    // Tab Navigation
    if (favoritesNavLink && favoritesTab) {
        favoritesNavLink.addEventListener('click', function (e) {
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
        tab.addEventListener('click', function () {
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
        toggleSortBtn.addEventListener('click', function () {
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
        searchForm.addEventListener('submit', async function (e) {
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
                            document.getElementById('load-more-btn').addEventListener('click', function () {
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

    // Add event listener to auto-capitalize VIN input
    const vinInput = document.getElementById('vin');
    if (vinInput) {
        vinInput.addEventListener('input', function() {
            // Convert to uppercase as they type
            this.value = this.value.toUpperCase();
        });
    }
    
    // VIN form submission
    if (vinForm) {
        vinForm.addEventListener('submit', async function (e) {
            e.preventDefault();
            const vinValue = document.getElementById('vin').value.trim();
            const vinButton = document.getElementById('vin-button');

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
            
            // Disable the button during request
            vinButton.disabled = true;
            vinButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Decoding...';

            try {
                const formData = new FormData();
                formData.append('vin', vinValue);
                
                const response = await fetch('/api/vin-decode', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();
                
                // Debug output
                console.log("VIN decode response:", data);

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
            } finally {
                // Re-enable the button
                vinButton.disabled = false;
                vinButton.innerHTML = '<i class="fas fa-search me-1" style="font-size: 0.9rem;"></i> Decode VIN';
            }
        });
    }

    // Function to display products
    function displayProducts(listings) {
        // If we have a productDisplay module, use it
        if (window.productDisplay) {
            // Process and enhance listings
            const enhancedListings = enhanceProductListings(listings, lastQuery,
                queryParseData && queryParseData.vehicle_info ?
                    queryParseData.vehicle_info :
                    extractVehicleInfo(lastQuery));

            // Save current listings and set them in the display system
            currentListings = enhancedListings;
            window.productDisplay.setProducts(enhancedListings);
        } else {
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
        
        // Safety check - make sure we have data
        if (!data || typeof data !== 'object') {
            vinError.textContent = "Invalid data received from VIN decoder";
            vinError.classList.remove('d-none');
            return;
        }
        
        // Check for API error response
        if (data.error) {
            vinError.textContent = data.error;
            vinError.classList.remove('d-none');
            return;
        }

        // Create primary info card
        const primaryInfoCard = document.createElement('div');
        primaryInfoCard.className = 'col-md-6 mb-4';
        
        // Handle the API property format - check if data has Results array (API format) or direct properties
        // Add robust fallbacks and console logging for debugging
        let vehicleData;
        
        if (data.Results && Array.isArray(data.Results) && data.Results.length > 0) {
            console.log("Using Results[0] for VIN data");
            vehicleData = data.Results[0];
        } else if (data.Count && data.Count > 0 && data.Results) {
            console.log("Data has Count but Results not usable, data:", data);
            vehicleData = data;
        } else {
            console.log("Using direct properties for VIN data");
            vehicleData = data;
        }
        
        // Log the vehicle data we're using
        console.log("Vehicle data to display:", vehicleData);
        
        primaryInfoCard.innerHTML = `
            <div class="card h-100">
                <div class="card-header bg-primary text-white">Vehicle Information</div>
                <div class="card-body">
                    <h5>${vehicleData.ModelYear || 'Unknown'} ${vehicleData.Make || 'Unknown'} ${vehicleData.Model || 'Unknown'} ${vehicleData.Trim || ''}</h5>
                    <table class="table table-sm">
                        <tr>
                            <th>Engine:</th>
                            <td>${vehicleData.DisplacementL ? vehicleData.DisplacementL + 'L' : ''} ${vehicleData.EngineConfiguration || ''} ${vehicleData.EngineCylinders ? vehicleData.EngineCylinders + '-cyl' : ''}</td>
                        </tr>
                        <tr>
                            <th>Transmission:</th>
                            <td>${vehicleData.TransmissionStyle || 'N/A'}</td>
                        </tr>
                        <tr>
                            <th>Drive Type:</th>
                            <td>${vehicleData.DriveType || 'N/A'}</td>
                        </tr>
                        <tr>
                            <th>Body Style:</th>
                            <td>${vehicleData.BodyClass || 'N/A'}</td>
                        </tr>
                        <tr>
                            <th>Fuel Type:</th>
                            <td>${vehicleData.FuelTypePrimary || 'N/A'}</td>
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
                            <td>${vehicleData.VIN || 'N/A'}</td>
                        </tr>
                        <tr>
                            <th>Plant:</th>
                            <td>${vehicleData.PlantCity ? vehicleData.PlantCity + ', ' + vehicleData.PlantCountry : 'N/A'}</td>
                        </tr>
                        <tr>
                            <th>Series:</th>
                            <td>${vehicleData.Series || 'N/A'}</td>
                        </tr>
                        <tr>
                            <th>Vehicle Type:</th>
                            <td>${vehicleData.VehicleType || 'N/A'}</td>
                        </tr>
                        <tr>
                            <th>GVWR:</th>
                            <td>${vehicleData.GVWR || 'N/A'}</td>
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
        document.getElementById('search-this-vehicle').addEventListener('click', function () {
            // Populate the multi-field form with VIN data
            if (!document.getElementById('single-field-container').classList.contains('d-none')) {
                // If in single field mode, switch to multi-field
                document.getElementById('multi-field-toggle').click();
            }

            // Fill in the fields
            yearField.value = vehicleData.ModelYear || '';
            makeField.value = vehicleData.Make || '';
            modelField.value = vehicleData.Model || '';
            engineField.value = vehicleData.DisplacementL ? vehicleData.DisplacementL + 'L' : '';

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
    document.addEventListener('click', function (e) {
        // Find if we clicked on a product image container or one of its children
        const imageContainer = e.target.closest('.product-image-container');
        if (!imageContainer) return;

        e.preventDefault();
        e.stopPropagation();

        // Get the image source from data attribute or img element
        const imgSrc = imageContainer.dataset.image ||
            imageContainer.querySelector('img')?.src ||
            '/static/placeholder.png';

        window.openImageModal(imgSrc);
    });

    // Also update the modal content styling in the CSS
    if (imageModal && modalImage) {
        // Add CSS classes for consistent styling
        modalImage.classList.add('modal-content');
        
        // Add a loading indicator to the modal
        const loadingSpinner = document.createElement('div');
        loadingSpinner.className = 'image-loading';
        loadingSpinner.id = 'image-loading';
        imageModal.appendChild(loadingSpinner);
        
        // Center the modal
        imageModal.style.display = 'none';
        imageModal.style.alignItems = 'center';
        imageModal.style.justifyContent = 'center';
        
        // Update the openImageModal function to show/hide the spinner
        const originalOpen = window.openImageModal;
        window.openImageModal = function(imgSrc) {
            // Show the loading spinner
            document.getElementById('image-loading').style.display = 'block';
            
            // Call the original function
            originalOpen(imgSrc);
            
            // Hide the spinner when the image is loaded
            modalImage.onload = function() {
                document.getElementById('image-loading').style.display = 'none';
            };
        };
    }

});

/**
 * This code replaces the button color override section at the end of main.js
 * Remove these lines from the original file and use the class-based approach instead
 */

document.addEventListener('DOMContentLoaded', function () {
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
    const observer = new MutationObserver(function (mutations) {
        mutations.forEach(function (mutation) {
            if (mutation.addedNodes && mutation.addedNodes.length > 0) {
                mutation.addedNodes.forEach(function (node) {
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