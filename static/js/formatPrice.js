/**
 * Format price to ensure it has a dollar sign
 * @param {string|number} price The price to format
 * @return {string} Formatted price with dollar sign
 */
function formatPrice(price) {
  if (!price) return '$0.00';
  
  // Convert to string in case it's a number
  const priceStr = price.toString();
  
  // Check if it already has a dollar sign
  if (priceStr.charAt(0) === '$') {
    return priceStr;
  }
  
  // Add dollar sign if missing
  return '$' + priceStr;
}

// Add a console log on load to help with debugging
console.log('Price formatting module loaded');

// Export to window
window.formatPrice = formatPrice;