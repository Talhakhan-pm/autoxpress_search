/**
 * Product Badges Module
 * Provides unified badge rendering for product listings
 */

const ProductBadges = (function() {
  // Badge type definitions with styles
  const BADGE_TYPES = {
    // Primary badges
    relevance: {
      bgColor: '#fff3cd',  // Yellow
      textColor: '#856404',
      icon: 'fas fa-star',
      className: 'badge-best-match'
    },
    year: {
      bgColor: '#d4edda',  // Green
      textColor: '#155724',
      icon: 'fas fa-check-circle',
      className: 'badge-exact-year'
    },
    yearRange: {
      bgColor: '#cce5ff',  // Blue
      textColor: '#004085',
      icon: 'fas fa-calendar-alt',
      className: 'badge-compatible'
    },
    partType: {
      bgColor: '#e2e3e5',  // Gray
      textColor: '#383d41',
      icon: 'fas fa-wrench',
      className: 'badge-part-match'
    },
    oem: {
      bgColor: '#d1ecf1',  // Teal
      textColor: '#0c5460',
      icon: 'fas fa-certificate',
      className: 'badge-oem'
    },
    
    // Secondary badges
    condition: {
      bgColor: '#d4edda',  // Green
      textColor: '#155724',
      icon: 'fas fa-tag',
      className: 'badge-condition'
    },
    shipping: {
      bgColor: '#cff4fc',  // Light blue
      textColor: '#055160',
      icon: 'fas fa-truck',
      className: 'badge-shipping'
    },
    brand: {
      bgColor: '#f8d7da',  // Pink
      textColor: '#721c24',
      icon: 'fas fa-crown',
      className: 'badge-brand'
    }
  };
  
  // Map condition to badge type
  function mapConditionToBadge(condition) {
    condition = condition.toLowerCase();
    if (condition.includes('new')) {
      return { type: 'condition', label: 'New', priority: 4 };
    } else if (condition.includes('refurbished')) {
      return { type: 'condition', label: 'Refurbished', priority: 4 };
    } else if (condition.includes('used') || condition.includes('pre-owned')) {
      return { type: 'condition', label: 'Used', priority: 4 };
    }
    return null;
  }
  
  // Map shipping to badge type
  function mapShippingToBadge(shipping) {
    if (shipping.toLowerCase().includes('free')) {
      return { type: 'shipping', label: 'Free Shipping', priority: 5 };
    }
    return null;
  }
  
  /**
   * Generate HTML for a primary badge
   * @param {Object} badge - Badge data including type and label
   * @return {string} HTML for the badge
   */
  function renderPrimaryBadge(badge) {
    if (!badge) return '';
    
    const badgeStyle = BADGE_TYPES[badge.type] || BADGE_TYPES.relevance;
    
    return `
      <div class="product-primary-badge ${badgeStyle.className}" 
           style="background-color: ${badgeStyle.bgColor}; color: ${badgeStyle.textColor};">
        <i class="${badgeStyle.icon} me-1"></i>
        ${badge.label}
      </div>
    `;
  }
  
  /**
   * Generate HTML for secondary badges
   * @param {Array} badges - Array of secondary badge objects
   * @param {number} limit - Maximum number of secondary badges to show
   * @return {string} HTML for the badges
   */
  function renderSecondaryBadges(badges, limit = 3) {
    if (!badges || !badges.length) return '';
    
    // Limit the number of secondary badges
    const limitedBadges = badges.slice(0, limit);
    
    return limitedBadges.map(badge => {
      const badgeStyle = BADGE_TYPES[badge.type] || BADGE_TYPES.relevance;
      
      return `
        <span class="product-tag ${badgeStyle.className}" 
              style="background-color: ${badgeStyle.bgColor}; color: ${badgeStyle.textColor};">
          <i class="${badgeStyle.icon} me-1"></i>
          ${badge.label}
        </span>
      `;
    }).join('');
  }
  
  /**
   * Render all badges for a product
   * @param {Object} product - Product with badge data
   * @return {Object} HTML strings for secondary badges only (primary badges excluded)
   */
  function renderBadges(product) {
    if (!product) return { primary: '', secondary: '' };
    
    // Create a combined list of all badges - convert primary to secondary
    const allBadges = [];
    
    // Add primary badge as a secondary badge if present
    if (product.primaryBadge) {
      allBadges.push(product.primaryBadge);
    }
    
    // Add all secondary badges
    if (product.secondaryBadges && Array.isArray(product.secondaryBadges)) {
      allBadges.push(...product.secondaryBadges);
    }
    
    // Render all badges as secondary badges
    const secondaryBadges = allBadges.length > 0 ? 
      renderSecondaryBadges(allBadges) : '';
    
    return {
      primary: '',  // Never return primary badges
      secondary: secondaryBadges
    };
  }
  
  /**
   * Get the relevance category CSS class
   * @param {string} category - Relevance category (high, medium, low)
   * @return {string} CSS class
   */
  function getRelevanceClass(category) {
    switch (category) {
      case 'high':
        return 'product-relevance-high';
      case 'medium':
        return 'product-relevance-medium';
      default:
        return '';
    }
  }
  
  // Public API
  return {
    renderBadges,
    getRelevanceClass,
    BADGE_TYPES,
    mapConditionToBadge,
    mapShippingToBadge
  };
})();

// Export globally
window.ProductBadges = ProductBadges;