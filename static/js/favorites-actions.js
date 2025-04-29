/**
 * Favorites Actions - Additional functionality for favorites listings
 * Adds actions menu for callback and order creation
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize favorites action functionality
    initFavoritesActions();
});

/**
 * Initialize all favorites actions functionality
 */
function initFavoritesActions() {
    // Listen for favorites tab activation to add action menus
    const favoritesTab = document.getElementById('favorites-tab');
    if (favoritesTab) {
        favoritesTab.addEventListener('shown.bs.tab', function() {
            // Add a small delay to ensure favorites are loaded
            setTimeout(addActionsMenuToFavorites, 200);
        });
    }

    // Listen for document clicks to handle actions menu
    document.addEventListener('click', handleActionsMenuClick);
}

/**
 * Add actions menu to all favorites cards
 */
function addActionsMenuToFavorites() {
    const favoriteCards = document.querySelectorAll('#favorites-list .product-card');
    
    favoriteCards.forEach(card => {
        // Check if card already has an actions menu
        if (card.querySelector('.favorite-actions-menu')) return;
        
        // Create actions menu button
        const actionsBtn = document.createElement('button');
        actionsBtn.className = 'favorite-actions-btn';
        actionsBtn.innerHTML = '<i class="fas fa-ellipsis-v"></i>';
        
        // Create actions menu
        const actionsMenu = document.createElement('div');
        actionsMenu.className = 'favorite-actions-menu';
        actionsMenu.innerHTML = `
            <div class="favorite-action-item schedule-callback" data-action="callback">
                <i class="fas fa-phone me-2"></i>Schedule Callback
            </div>
            <div class="favorite-action-item create-order" data-action="order">
                <i class="fas fa-shopping-cart me-2"></i>Create New Order
            </div>
        `;
        
        // Add elements to card
        card.appendChild(actionsBtn);
        card.appendChild(actionsMenu);
    });
}

/**
 * Handle clicks on the actions menu
 */
function handleActionsMenuClick(event) {
    // Handle opening/closing the menu
    if (event.target.closest('.favorite-actions-btn')) {
        const button = event.target.closest('.favorite-actions-btn');
        const card = button.closest('.product-card');
        const menu = card.querySelector('.favorite-actions-menu');
        
        // Close all other open menus
        document.querySelectorAll('.favorite-actions-menu.active').forEach(m => {
            if (m !== menu) m.classList.remove('active');
        });
        
        // Toggle this menu
        menu.classList.toggle('active');
        event.stopPropagation();
        return;
    }
    
    // Close menu when clicking elsewhere
    if (!event.target.closest('.favorite-actions-menu')) {
        document.querySelectorAll('.favorite-actions-menu.active').forEach(menu => {
            menu.classList.remove('active');
        });
    }
    
    // Handle action items
    if (event.target.closest('.favorite-action-item')) {
        const actionItem = event.target.closest('.favorite-action-item');
        const action = actionItem.dataset.action;
        const card = actionItem.closest('.product-card');
        const productId = card.querySelector('.favorite-btn').dataset.productId;
        
        // Execute the appropriate action
        if (action === 'callback') {
            openCallbackForm(productId);
        } else if (action === 'order') {
            openOrderForm(productId);
        }
        
        // Close the menu
        card.querySelector('.favorite-actions-menu').classList.remove('active');
        event.stopPropagation();
    }
}

/**
 * Extract vehicle info from a product title
 */
function extractVehicleInfoFromTitle(title) {
    const info = {
        year: '',
        make: '',
        model: ''
    };
    
    if (!title) return info;
    
    // Check for "For: [Year] [Make] [Model]" pattern
    const forPattern = /For:\s+(19|20)\d{2}\s+([A-Za-z]+(?:\s+[A-Za-z]+)?)\s+([A-Za-z0-9]+(?:[-\s][A-Za-z0-9]+)*)/i;
    const forMatch = title.match(forPattern);
    
    if (forMatch) {
        // We found a "For:" pattern in the title
        info.year = forMatch[1]; // Year
        info.make = forMatch[2]; // Make
        info.model = forMatch[3]; // Model
        return info;
    }
    
    // If no "For:" pattern, try regular extraction
    
    // Extract year (4 digits starting with 19 or 20)
    const yearMatch = title.match(/\b(19|20)\d{2}\b/);
    if (yearMatch) {
        info.year = yearMatch[0];
    }
    
    // If we have a year, look for make and model after the year
    if (info.year) {
        const afterYear = title.substring(title.indexOf(info.year) + 4).trim();
        const words = afterYear.split(/\s+/);
        
        if (words.length >= 2) {
            // Simple assumption: First word after year is make, second word (and optionally third) is model
            info.make = words[0];
            
            // For model, get next 1-2 words but stop if we hit common stopwords
            const stopwords = ['for', 'oem', 'new', 'used', 'complete', 'assembly', 'part'];
            let modelWords = [];
            
            for (let i = 1; i < Math.min(words.length, 4); i++) {
                const word = words[i].toLowerCase();
                if (stopwords.includes(word) || word.length <= 1) break;
                modelWords.push(words[i]);
            }
            
            info.model = modelWords.join(' ');
        }
    }
    
    // Capitalize make and model
    if (info.make) {
        info.make = info.make.charAt(0).toUpperCase() + info.make.slice(1).toLowerCase();
    }
    if (info.model) {
        // For multi-word models, capitalize each word
        info.model = info.model.split(' ')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
            .join(' ');
    }
    
    return info;
}

/**
 * Open callback form with prefilled data from favorite
 */
function openCallbackForm(productId) {
    const favorites = loadFavorites();
    if (!favorites[productId]) return;
    
    const item = favorites[productId];
    
    // Extract vehicle info from title
    const vehicleInfo = extractVehicleInfoFromTitle(item.title);
    
    // Parse notes for any customer info the agent might have added
    const parsedNotes = parseNotes(item.notes);
    
    // Open callback form in a modal
    openFormModal('callback', {
        product: item.title,
        year: vehicleInfo.year || '',
        vehicleInfo: `${vehicleInfo.make} ${vehicleInfo.model}`.trim(),
        customerName: parsedNotes.name || '',
        callbackNumber: parsedNotes.phone || '',
        zip: parsedNotes.zip || '',
        comments: `Listing: ${item.link}\n${item.notes || ''}`
    });
}

/**
 * Open order form with prefilled data from favorite
 */
function openOrderForm(productId) {
    const favorites = loadFavorites();
    if (!favorites[productId]) return;
    
    const item = favorites[productId];
    
    // Extract vehicle info from title
    const vehicleInfo = extractVehicleInfoFromTitle(item.title);
    
    // Parse notes for any customer info the agent might have added
    const parsedNotes = parseNotes(item.notes);
    
    // Extract price (remove currency symbol and commas)
    const price = item.price.replace(/[^0-9.]/g, '');
    
    // Open order form in a modal
    openFormModal('order', {
        product: item.title,
        year: vehicleInfo.year || '',
        car: `${vehicleInfo.make} ${vehicleInfo.model}`.trim(),
        customerName: parsedNotes.name || '',
        number: parsedNotes.phone || '',
        condition: item.condition.toLowerCase().includes('new') ? 'New' : 'Used',
        charge: price,
        comments: `Listing: ${item.link}\n${item.notes || ''}`
    });
}

/**
 * Parse notes field for common customer info patterns
 */
function parseNotes(notes) {
    const result = {
        name: '',
        phone: '',
        zip: ''
    };
    
    if (!notes) return result;
    
    // Look for phone number patterns
    const phoneMatch = notes.match(/(?:phone|number|tel|cell|mobile|contact)?\s*[:\-]?\s*(\+?1?\s*(?:\(\d{3}\)|\d{3})[\s.-]?\d{3}[\s.-]?\d{4})/i);
    if (phoneMatch) {
        result.phone = phoneMatch[1];
    }
    
    // Look for 5-digit zip code patterns (with or without "zip:" label)
    const zipLabeledMatch = notes.match(/(?:zip|postal|zipcode)\s*[:\-]?\s*(\d{5}(?:-\d{4})?)/i);
    if (zipLabeledMatch) {
        result.zip = zipLabeledMatch[1];
    } else {
        // Look for standalone 5-digit numbers that could be zip codes
        const zipStandaloneMatch = notes.match(/\b(\d{5})\b(?![-\d])/);
        if (zipStandaloneMatch) {
            result.zip = zipStandaloneMatch[1];
        }
    }
    
    // Look for name patterns
    const nameMatch = notes.match(/(?:customer|name|client|buyer)\s*[:\-]?\s*([A-Z][a-z]+ [A-Z][a-z]+)/i);
    if (nameMatch) {
        result.name = nameMatch[1];
    } else {
        // Look for what looks like a name (capitalized words)
        const nameGuessMatch = notes.match(/\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b/);
        if (nameGuessMatch) {
            result.name = nameGuessMatch[1];
        }
    }
    
    return result;
}

/**
 * Opens a modal with an iframe containing the form
 */
function openFormModal(formType, data) {
    // Check if modal already exists
    let modal = document.getElementById('action-form-modal');
    
    // Create modal if it doesn't exist
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'action-form-modal';
        modal.className = 'modal fade';
        modal.setAttribute('tabindex', '-1');
        modal.setAttribute('aria-hidden', 'true');
        
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title"></h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body p-0">
                        <iframe id="form-iframe" style="width:100%; height:600px; border:0;"></iframe>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }
    
    // Set the title based on form type
    const title = formType === 'callback' ? 'Schedule Callback' : 'Create New Order';
    modal.querySelector('.modal-title').textContent = title;
    
    // Create Bootstrap modal instance if it doesn't exist
    let modalInstance = bootstrap.Modal.getInstance(modal);
    if (!modalInstance) {
        modalInstance = new bootstrap.Modal(modal);
    }
    
    // Show the modal
    modalInstance.show();
    
    // Load the iframe with the form once the modal is shown
    modal.addEventListener('shown.bs.modal', function() {
        const iframe = document.getElementById('form-iframe');
        
        // Determine which form to load
        const formUrl = formType === 'callback' ? 'callbacks.html' : 'orders.html';
        
        // Load the iframe
        iframe.src = formUrl;
        
        // Wait for iframe to load before setting form values
        iframe.onload = function() {
            // Set timeout to ensure form is fully loaded
            setTimeout(function() {
                prefillForm(iframe, formType, data);
            }, 500);
        };
    });
}

/**
 * Prefill the form inside the iframe
 */
function prefillForm(iframe, formType, data) {
    try {
        const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
        
        // Different field IDs for each form type
        if (formType === 'callback') {
            // Prefill callback form
            setValue(iframeDoc, 'product', data.product);
            setValue(iframeDoc, 'customerName', data.customerName);
            setValue(iframeDoc, 'callbackNumber', data.callbackNumber);
            setValue(iframeDoc, 'zip', data.zip);
            setValue(iframeDoc, 'comments', data.comments);
        } else {
            // Prefill order form
            setValue(iframeDoc, 'product', data.product);
            setValue(iframeDoc, 'customerName', data.customerName);
            setValue(iframeDoc, 'number', data.number);
            setValue(iframeDoc, 'condition', data.condition);
            setValue(iframeDoc, 'charge', data.charge);
            setValue(iframeDoc, 'comments', data.comments);
        }
    } catch (e) {
        console.error('Error prefilling form:', e);
    }
}

/**
 * Helper function to set a form value
 */
function setValue(doc, id, value) {
    const element = doc.getElementById(id);
    if (!element) return;
    
    if (element.tagName === 'SELECT') {
        // For select elements, find the matching option
        for (let i = 0; i < element.options.length; i++) {
            if (element.options[i].text === value || element.options[i].value === value) {
                element.selectedIndex = i;
                break;
            }
        }
    } else if (element.tagName === 'TEXTAREA' || element.tagName === 'INPUT') {
        // For text inputs and textareas
        element.value = value || '';
    }
}

// Helper to load favorites
function loadFavorites() {
    const favoritesJson = localStorage.getItem('autoxpress_favorites');
    return favoritesJson ? JSON.parse(favoritesJson) : {};
}