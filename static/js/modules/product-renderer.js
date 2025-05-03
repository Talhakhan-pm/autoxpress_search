/**
 * Product Renderer Module
 * Handles rendering product cards and displaying products in different views
 */

// Helper function to get the search year
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
  const productsContainer = document.getElementById('products-container');
  if (!productsContainer) return;

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

  // Generate appropriate badges based on product attributes
  let badgeHtml = '';
  
  // Exact match or compatibility badge (positioned top right)
  if (isExactMatch) {
    badgeHtml += `<div class="product-badge badge-exact-match badge-top-right">Exact Match</div>`;
  } else if (isCompatible) {
    badgeHtml += `<div class="product-badge badge-compatible badge-top-right">Compatible</div>`;
  }
  
  // Determine product type (OEM/Premium) from text
  const productText = (product.title + ' ' + (product.description || '')).toLowerCase();
  const isOEM = productText.includes('oem') || productText.includes('original');
  const isPremium = productText.includes('premium') || productText.includes('performance') || productText.includes('pro');
  
  // Condition badge (only for used items, since "new" is expected)
  if (product.condition.toLowerCase().includes('used')) {
    badgeHtml += `<div class="product-badge badge-used badge-bottom-right">Used</div>`;
  }

  // Highlight matching terms in the product title
  const highlightedTitle = highlightKeywords(product.title, getSearchTerms());

  // Build the card HTML
  productCard.innerHTML = `
    <div class="${cardClasses}">
      <div class="product-source ${sourceClass}">${product.source}</div>
      ${badgeHtml}
      <button class="favorite-btn ${isFavorite ? 'active' : ''}" data-product-id="${productId}" aria-label="${isFavorite ? 'Remove from favorites' : 'Add to favorites'}">
        <i class="fas fa-heart"></i>
      </button>
      <div class="product-image-container" data-image="${product.image || '/static/placeholder.png'}">
        <img src="${product.image || '/static/placeholder.png'}" 
             class="product-image" 
             alt="${product.title || 'Product'}" 
             onerror="this.src='/static/placeholder.png'; this.onerror=null;">
      </div>
      <div class="p-3">
        <div class="product-title mb-2">${highlightedTitle}</div>
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
        <a href="${product.link || '#'}" target="_blank" class="btn btn-danger btn-sm w-100">View Details</a>
      </div>
    </div>
  `;

  productsContainer.appendChild(productCard);
}

/**
 * Displays products with enhanced highlighting and badges
 */
function displayProducts(listings) {
  const productsContainer = document.getElementById('products-container');
  if (!productsContainer) return;
  
  // Clear the container
  productsContainer.innerHTML = '';

  if (!listings || listings.length === 0) {
    productsContainer.innerHTML = '<div class="col-12 text-center"><p>No products found. Try a different search term.</p></div>';
    return;
  }

  // Extract the year we searched for (from query or structured form)
  const searchYear = getSearchYear();
  
  // Get all search fields for term matching
  const searchTerms = getSearchTerms();

  // Enhanced display with badges and match highlighting 
  listings.forEach(item => {
    // Check if this is an exact match based on year
    const isExactMatch = searchYear && item.title && 
      (item.title.includes(searchYear) || 
       (item.description && item.description.includes(searchYear)));
    
    // Check if compatible but not exact match
    const isCompatible = !isExactMatch && determineCompatibility(item, searchTerms);
    
    renderProductCard(item, isExactMatch, isCompatible);
  });

  // Add event listeners to the favorite buttons
  if (typeof attachFavoriteButtonListeners === 'function') {
    attachFavoriteButtonListeners();
  }
  
  // Add event listeners to the image containers
  if (typeof attachImagePreviewListeners === 'function') {
    attachImagePreviewListeners();
  }

  // Update product count badges
  const productCountBadge = document.getElementById('products-count');
  if (productCountBadge) {
    productCountBadge.textContent = listings.length;
  }
  
  // Trigger a custom event to notify that products were displayed
  // This helps other modules (like the image modal) know when to attach handlers
  document.dispatchEvent(new CustomEvent('productsDisplayed'));
}

/**
 * Helper function to collect all search terms from the form
 * Used for term matching in product listings
 */
function getSearchTerms() {
  const terms = [];
  
  // Try multi-field search form first
  const yearField = document.getElementById('year-field');
  const makeField = document.getElementById('make-field');
  const modelField = document.getElementById('model-field');
  const partField = document.getElementById('part-field');
  const engineField = document.getElementById('engine-field');
  
  if (yearField && yearField.value) terms.push(yearField.value.trim());
  if (makeField && makeField.value) terms.push(makeField.value.trim());
  if (modelField && modelField.value) terms.push(modelField.value.trim());
  if (partField && partField.value) terms.push(partField.value.trim());
  if (engineField && engineField.value) terms.push(engineField.value.trim());
  
  // If no multi-field terms, try single field prompt
  if (terms.length === 0) {
    const promptField = document.getElementById('prompt');
    if (promptField && promptField.value) {
      // Split the prompt into individual terms
      const promptTerms = promptField.value.split(/\s+/);
      terms.push(...promptTerms.filter(term => term.length > 2)); // Only use terms with 3+ chars
    }
  }
  
  return terms;
}

/**
 * Determines if a product is compatible based on search terms
 * Doesn't change existing sorting or filtering logic
 */
function determineCompatibility(product, searchTerms) {
  if (!searchTerms || searchTerms.length === 0) return false;
  
  // Check product title and description for search terms
  const productText = (product.title + ' ' + (product.description || '')).toLowerCase();
  
  // Count how many terms match
  let matchCount = 0;
  for (const term of searchTerms) {
    if (term.length >= 3 && productText.includes(term.toLowerCase())) {
      matchCount++;
    }
  }
  
  // If more than half of the search terms match, consider it compatible
  return matchCount >= Math.ceil(searchTerms.length / 2);
}

/**
 * Highlights keywords in a text string based on search terms
 * @param {string} text - The text to highlight
 * @param {string[]} keywords - The keywords to highlight
 * @returns {string} - HTML with highlighted keywords
 */
function highlightKeywords(text, keywords) {
  if (!text || !keywords || keywords.length === 0) {
    return text;
  }
  
  // Filter keywords to avoid highlighting common words
  const validKeywords = keywords.filter(keyword => {
    // Only use keywords with 3+ characters
    if (keyword.length < 3) return false;
    
    // Skip common words that shouldn't be highlighted
    const commonWords = ['the', 'and', 'for', 'with', 'this', 'that', 'from'];
    return !commonWords.includes(keyword.toLowerCase());
  });
  
  if (validKeywords.length === 0) {
    return text;
  }
  
  // Create a regex that matches any of the keywords
  // Use word boundaries to match whole words when possible
  const regex = new RegExp(
    validKeywords.map(term => 
      // If the term is alphanumeric, use word boundaries
      /^[a-zA-Z0-9]+$/.test(term) 
        ? `\\b${term}\\b` 
        : term
    ).join('|'), 
    'gi'
  );
  
  try {
    // Replace all matches with highlighted spans
    return text.replace(regex, match => {
      return `<span class="keyword-highlight">${match}</span>`;
    });
  } catch (e) {
    // In case of regex error, return the original text
    console.error('Error highlighting keywords:', e);
    return text;
  }
}

// Make globally available
window.renderProductCard = renderProductCard;
window.getSearchYear = getSearchYear;
window.displayProducts = displayProducts;
window.highlightKeywords = highlightKeywords;