/**
 * Product Renderer Module - Compatibility Layer
 * 
 * This module now serves as a compatibility layer that delegates to the 
 * unified product display system in updated_products.js.
 * 
 * This ensures that any code relying on the original product-renderer.js 
 * functions continues to work, without duplicating logic.
 */

// Helper function to get the search year (retained for backward compatibility)
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
 * Get search terms from the form - delegates to the central implementation
 * if available, otherwise falls back to local implementation
 */
function getSearchTerms() {
  // Use centralized implementation if available
  if (window.productDisplay && typeof window.productDisplay.getSearchTerms === 'function') {
    return window.productDisplay.getSearchTerms();
  }
  
  // Fallback implementation (copied from original for backward compatibility)
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
 * (Kept for backward compatibility)
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
 * Highlights keywords in text - delegates to central implementation if available
 */
function highlightKeywords(text, keywords) {
  // Use centralized implementation if available
  if (window.productDisplay && typeof window.productDisplay.highlightKeywords === 'function') {
    return window.productDisplay.highlightKeywords(text, keywords);
  }
  
  // Fallback implementation (if the central system isn't available)
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
  
  // Create a regex pattern for matching
  try {
    const regex = new RegExp(
      validKeywords.map(term => 
        /^[a-zA-Z0-9]+$/.test(term) ? `\\b${term}\\b` : term
      ).join('|'), 
      'gi'
    );
    
    // Replace all matches with highlighted spans
    return text.replace(regex, match => {
      return `<span class="keyword-highlight">${match}</span>`;
    });
  } catch (e) {
    console.error('Error highlighting keywords:', e);
    return text;
  }
}

/**
 * Helper function to render a product card - now delegates to updated_products.js
 * Kept for backward compatibility
 */
function renderProductCard(product, isExactMatch, isCompatible) {
  console.log('renderProductCard called - delegating to unified product display system');
  
  // If the product already exists in the container, just return
  const productsContainer = document.getElementById('products-container');
  if (!productsContainer) return;
  
  // Add compatibility markers to the product
  const enhancedProduct = {
    ...product,
    isExactMatch: isExactMatch === true,
    isCompatible: isCompatible === true
  };
  
  // Use the unified system if available, otherwise fall back
  if (window.productDisplay && window.productDisplay.setProducts) {
    window.productDisplay.setProducts([enhancedProduct]);
  } else {
    // Fallback - simplified version of original renderProductCard
    console.warn('Unified product display system not found - using fallback rendering');
    
    const productId = generateProductId(product);
    const favorites = loadFavorites ? loadFavorites() : {};
    const isFavorite = favorites[productId] !== undefined;
    
    const productCard = document.createElement('div');
    productCard.className = 'col-md-4 col-lg-3 mb-3';
    
    // Simple product card
    productCard.innerHTML = `
      <div class="product-card">
        <button class="favorite-btn ${isFavorite ? 'active' : ''}" data-product-id="${productId}">
          <i class="fas fa-heart"></i>
        </button>
        <div class="product-image-container">
          <img src="${product.image || '/static/placeholder.png'}" class="product-image" alt="${product.title}">
        </div>
        <div class="p-3">
          <div class="product-title mb-2">${product.title}</div>
          <div class="product-price">${product.price}</div>
          <a href="${product.link}" target="_blank" class="btn btn-danger btn-sm w-100 mt-2">View Details</a>
        </div>
      </div>
    `;
    
    productsContainer.appendChild(productCard);
  }
}

/**
 * Displays products - now delegates to updated_products.js if available
 * Kept for backward compatibility
 */
function displayProducts(listings) {
  console.log('displayProducts called from product-renderer.js - delegating to unified product display system');
  
  // Use the unified system if available
  if (window.productDisplay && window.productDisplay.setProducts) {
    // Extract the year we searched for (from query or structured form)
    const searchYear = getSearchYear();
    const searchTerms = getSearchTerms();
    
    // Enhance listings with compatibility flags
    const enhancedListings = listings.map(item => {
      // Check if this is an exact match based on year
      const isExactMatch = searchYear && item.title && 
        (item.title.includes(searchYear) || 
         (item.description && item.description.includes(searchYear)));
      
      // Check if compatible but not exact match
      const isCompatible = !isExactMatch && determineCompatibility(item, searchTerms);
      
      return {
        ...item,
        isExactMatch: isExactMatch,
        isCompatible: isCompatible
      };
    });
    
    // Use the centralized system
    window.productDisplay.setProducts(enhancedListings);
    
    // Update product count badges
    const productCountBadge = document.getElementById('products-count');
    if (productCountBadge) {
      productCountBadge.textContent = listings.length;
    }
    
    return; // Exit early - rendering handled by the unified system
  }
  
  // Fallback if the unified system isn't available - simplified version
  console.warn('Unified product display system not found - using fallback rendering');
  
  const productsContainer = document.getElementById('products-container');
  if (!productsContainer) return;
  
  // Clear the container
  productsContainer.innerHTML = '';

  if (!listings || listings.length === 0) {
    productsContainer.innerHTML = '<div class="col-12 text-center"><p>No products found. Try a different search term.</p></div>';
    return;
  }
  
  // Get search context
  const searchYear = getSearchYear();
  const searchTerms = getSearchTerms();

  // Render each product
  listings.forEach(item => {
    const isExactMatch = searchYear && item.title && 
      (item.title.includes(searchYear) || 
       (item.description && item.description.includes(searchYear)));
    
    const isCompatible = !isExactMatch && determineCompatibility(item, searchTerms);
    
    renderProductCard(item, isExactMatch, isCompatible);
  });

  // Update count badges
  const productCountBadge = document.getElementById('products-count');
  if (productCountBadge) {
    productCountBadge.textContent = listings.length;
  }
  
  // Notify that products were displayed
  document.dispatchEvent(new CustomEvent('productsDisplayed'));
}

// Make globally available for backward compatibility
window.renderProductCard = renderProductCard;
window.getSearchYear = getSearchYear;
window.displayProducts = displayProducts;
window.highlightKeywords = highlightKeywords;
window.getSearchTerms = getSearchTerms;