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

  // Build card classes - removed badge classes
  let cardClasses = "product-card";

  // Create the product card element
  const productCard = document.createElement('div');
  productCard.className = 'col-md-4 col-lg-3 mb-3';

  // Badge HTML removed as part of badge strategy redesign
  let badgeHtml = '';

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

/**
 * Displays products with exact year highlighting
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

  // Simplified display without categorization - removed badges
  listings.forEach(item => {
    renderProductCard(item, false, false);
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
}

// Make globally available
window.renderProductCard = renderProductCard;
window.getSearchYear = getSearchYear;
window.displayProducts = displayProducts;