/**
 * Enhanced Part Number Display and Listing UI Module
 * 
 * This module handles the improved display of product listings from part numbers
 * It provides a better UI for displaying part number search results in a modal dialog
 */

// Function to display product listings in a modal dialog
function displayEnhancedProductListings(listings, primaryPartNumber, alternativeNumbers) {
    // Create a modal container for the listings
    let listingsModal = document.getElementById('part-listings-modal');
    
    // If the modal doesn't exist, create it
    if (!listingsModal) {
        listingsModal = document.createElement('div');
        listingsModal.id = 'part-listings-modal';
        listingsModal.className = 'modal fade';
        listingsModal.tabIndex = '-1';
        listingsModal.setAttribute('aria-labelledby', 'part-listings-modal-label');
        listingsModal.setAttribute('aria-hidden', 'true');
        
        // Create the modal HTML structure
        listingsModal.innerHTML = `
            <div class="modal-dialog modal-dialog-centered modal-xl">
                <div class="modal-content">
                    <div class="modal-header bg-danger text-white">
                        <h5 class="modal-title" id="part-listings-modal-label">
                            <i class="fas fa-shopping-cart me-2"></i> Product Listings
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <div id="product-listings-grid" class="row"></div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        `;
        
        // Add the modal to the body
        document.body.appendChild(listingsModal);
    }
    
    // Get the grid element within the modal
    const listingsGrid = document.getElementById('product-listings-grid');
    
    // Clear any existing listings
    listingsGrid.innerHTML = '';
    
    // Add a header for the listings count
    const headerElement = document.createElement('div');
    headerElement.className = 'col-12 mb-3';
    headerElement.innerHTML = `
        <div class="alert alert-info">
            <i class="fas fa-info-circle me-2"></i>
            Found <strong>${listings.length}</strong> product listings for <strong>${primaryPartNumber}</strong>
            ${alternativeNumbers && alternativeNumbers.length > 0 ? 
                ` and <strong>${alternativeNumbers.length}</strong> alternative part number${alternativeNumbers.length > 1 ? 's' : ''}` : ''}
        </div>
    `;
    listingsGrid.appendChild(headerElement);
    
    // Add each listing to the modal
    listings.forEach(listing => {
        // Determine the source class and label (eBay, Google, etc.)
        const sourceClass = listing.source === 'eBay' ? 'source-ebay' : 'source-google';
        const sourceLabel = listing.source === 'eBay' ? 'eBay' : 'Google Shopping';
        const sourceBadgeClass = listing.source === 'eBay' ? 'bg-warning text-dark' : 'bg-primary text-white';
        const sourceIcon = listing.source === 'eBay' ? 'fab fa-ebay' : 'fab fa-google';
        
        // Determine condition class
        const conditionClass = listing.condition && listing.condition.toLowerCase().includes('new') 
            ? 'condition-new text-success' 
            : 'condition-used text-secondary';
        
        // Determine if it's from the primary part or an alternative
        const sourcePart = listing.source_part || primaryPartNumber;
        const isPrimary = sourcePart === primaryPartNumber;
        const sourcePartIndex = !isPrimary && alternativeNumbers 
            ? alternativeNumbers.indexOf(sourcePart) + 1
            : 0;
        
        // Create card for the listing
        const listingCard = document.createElement('div');
        listingCard.className = 'col-md-6 col-lg-4 mb-3';
        listingCard.innerHTML = `
            <div class="card h-100 shadow-sm ${isPrimary ? 'border-success' : ''}">
                <div class="position-relative">
                    ${isPrimary 
                        ? '<span class="position-absolute top-0 start-0 badge rounded-pill bg-success ms-2 mt-2 shadow-sm" style="z-index:2"><i class="fas fa-check-circle me-1"></i> Primary Part</span>' 
                        : `<span class="position-absolute top-0 start-0 badge rounded-pill bg-info ms-2 mt-2 shadow-sm" style="z-index:2"><i class="fas fa-exchange-alt me-1"></i> Alt Part #${sourcePartIndex}</span>`}
                    <span class="position-absolute top-0 end-0 badge rounded-pill ${sourceBadgeClass} me-2 mt-2 shadow-sm" style="z-index:2">
                        <i class="${sourceIcon} me-1"></i> ${sourceLabel}
                    </span>
                    <div class="product-image-container" style="height: 160px; overflow: hidden; display: flex; align-items: center; justify-content: center; background-color: #f8f9fa; padding: 10px;">
                        <img src="${listing.image || '/static/placeholder.png'}" class="product-image" 
                            alt="${listing.title}" style="max-height: 100%; max-width: 100%; object-fit: contain;">
                    </div>
                </div>
                <div class="card-body">
                    <h6 class="product-title mb-3" style="height: 3em; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; text-overflow: ellipsis;">${listing.title}</h6>
                    <div class="d-flex justify-content-between mb-1">
                        <span class="text-muted">Condition:</span>
                        <span class="${conditionClass} fw-bold">${listing.condition || 'Not specified'}</span>
                    </div>
                    <div class="d-flex justify-content-between mb-1">
                        <span class="text-muted">Price:</span>
                        <span class="product-price fw-bold fs-5">${listing.price || 'Not available'}</span>
                    </div>
                    <div class="d-flex justify-content-between mb-3">
                        <span class="text-muted">Shipping:</span>
                        <span class="${listing.shipping && listing.shipping.toLowerCase().includes('free') ? 'text-success' : ''}">${listing.shipping || 'Not specified'}</span>
                    </div>
                    <a href="${listing.link}" target="_blank" class="btn btn-danger w-100">
                        <i class="fas fa-external-link-alt me-1"></i> View Details
                    </a>
                </div>
            </div>
        `;
        
        listingsGrid.appendChild(listingCard);
    });
    
    // Show the modal using Bootstrap's modal API
    const modal = new bootstrap.Modal(listingsModal);
    modal.show();

    // Also add a count badge to the button
    const findListingsBtn = document.getElementById('find-listings-btn');
    if (findListingsBtn) {
        findListingsBtn.innerHTML = `
            <i class="fas fa-search-dollar me-1"></i>
            Product Listings <span class="badge bg-light text-dark ms-1">${listings.length}</span>
        `;

        // Update the button class to match theme
        findListingsBtn.className = 'btn btn-danger mt-2 w-100 py-2';
        
        // Add a click handler to reopen the modal if it's closed
        findListingsBtn.onclick = function() {
            modal.show();
            return false; // Prevent default button behavior
        };
    }
}

// Export the enhanced display function
window.displayEnhancedProductListings = displayEnhancedProductListings;