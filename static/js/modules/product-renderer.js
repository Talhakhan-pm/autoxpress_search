/**
 * Product Renderer Module
 * Handles the rendering of product cards with badge support
 */

const ProductRenderer = (function() {
  
  /**
   * Renders a single product card
   * @param {Object} product - Product data with ranking data
   * @returns {string} HTML for the product card
   */
  function renderProductCard(product) {
    // Get relevance class based on score
    const relevanceClass = product.relevanceScore >= 80 ? 'product-relevance-high' : 
                          product.relevanceScore >= 50 ? 'product-relevance-medium' : '';
    
    // Generate unique product ID
    const productId = typeof generateProductId === 'function' ? 
                     generateProductId(product) : 
                     product.id || btoa(product.title + product.price);
    
    // Determine if product is favorite
    const favorites = typeof loadFavorites === 'function' ? loadFavorites() : {};
    const isFavorite = favorites[productId] !== undefined;
    
    // Render badges using ProductBadges if available
    const badgesHTML = window.ProductBadges ? renderBadgesHTML(product) : '';
    
    return `
      <div class="col-md-4 mb-4">
        <div class="card product-card h-100 ${relevanceClass}" data-product-id="${productId}">
          <div class="card-header">
            <div class="product-title">${product.title}</div>
            ${badgesHTML}
          </div>
          <div class="card-img-container">
            <img src="${product.image}" class="card-img-top product-image" 
                 alt="${product.title}" data-full-img="${product.fullImage || product.image}">
          </div>
          <div class="card-body">
            <p class="card-text">
              <strong>Brand:</strong> ${product.brand || 'N/A'}<br>
              <strong>Part Type:</strong> ${product.partType || 'N/A'}<br>
              <strong>Condition:</strong> ${product.condition || 'N/A'}<br>
              <strong>Price:</strong> ${typeof product.price === 'number' ? 
                                       '$' + product.price.toFixed(2) : 
                                       product.price}
            </p>
          </div>
          <div class="card-footer">
            <div class="btn-group w-100">
              <button class="btn btn-primary view-details-btn" data-product-id="${productId}">
                <i class="fas fa-info-circle"></i> Details
              </button>
              <button class="btn btn-outline-primary add-favorite-btn" data-product-id="${productId}">
                <i class="${isFavorite ? 'fas' : 'far'} fa-heart"></i>
              </button>
              <button class="btn btn-success add-to-cart-btn" data-product-id="${productId}">
                <i class="fas fa-shopping-cart"></i> Add
              </button>
            </div>
          </div>
        </div>
      </div>
    `;
  }
  
  /**
   * Renders badges HTML using ProductBadges module
   * @param {Object} product - Ranked product with badge data
   * @returns {string} HTML for badges
   */
  function renderBadgesHTML(product) {
    if (!window.ProductBadges) return '';
    
    const badges = window.ProductBadges.renderBadges(product);
    return `
      <div class="product-badges-container">
        ${badges.primary}
        <div class="product-secondary-badges">
          ${badges.secondary}
        </div>
      </div>
    `;
  }
  
  /**
   * Renders a list of products
   * @param {Array} products - Array of already ranked product data objects
   * @param {HTMLElement} container - DOM element to render products into
   */
  function renderProductList(products, container) {
    // Clear the container and add products
    container.innerHTML = '';
    
    if (!products || products.length === 0) {
      container.innerHTML = '<div class="col-12"><div class="alert alert-info">No products found matching your criteria.</div></div>';
      return;
    }
    
    const row = document.createElement('div');
    row.className = 'row product-grid';
    
    products.forEach(product => {
      row.innerHTML += renderProductCard(product);
    });
    
    container.appendChild(row);
    
    // Dispatch an event indicating products have been rendered
    container.dispatchEvent(new CustomEvent('products-rendered', {
      detail: { products: products }
    }));
  }
  
  /**
   * Updates existing product cards with new ranking data
   * @param {Array} products - Array of ranked product data objects
   */
  function updateProductCards(products) {
    if (!products || !Array.isArray(products)) return;
    
    products.forEach(product => {
      const productId = typeof generateProductId === 'function' ? 
                       generateProductId(product) : product.id;
      
      const card = document.querySelector(`.product-card[data-product-id="${productId}"]`);
      if (!card) return;
      
      // Update relevance class
      card.classList.remove('product-relevance-high', 'product-relevance-medium');
      if (product.relevanceScore >= 80) {
        card.classList.add('product-relevance-high');
      } else if (product.relevanceScore >= 50) {
        card.classList.add('product-relevance-medium');
      }
      
      // Update badges
      if (window.ProductBadges) {
        const badgeContainer = card.querySelector('.product-badges-container');
        if (badgeContainer) {
          badgeContainer.outerHTML = renderBadgesHTML(product);
        }
      }
    });
    
    // Dispatch update event
    document.dispatchEvent(new CustomEvent('products-updated', {
      detail: { products: products }
    }));
  }
  
  // Public API
  return {
    renderProductCard,
    renderProductList,
    updateProductCards
  };
})();

// Export globally
window.ProductRenderer = ProductRenderer;