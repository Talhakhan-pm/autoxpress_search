/**
 * Unit tests for ProductRenderer module
 */

// Mock data for testing
const testProducts = [
  {
    id: 'product1',
    title: '2018 Toyota Camry Brake Pads - New OEM',
    brand: 'Toyota',
    partType: 'Brake Pads',
    condition: 'New',
    price: 79.99,
    shipping: 'Free Shipping',
    image: '/path/to/image.jpg',
    relevanceScore: 85,
    primaryBadge: { type: 'relevance', label: 'Best Match', priority: 1 },
    secondaryBadges: [
      { type: 'year', label: 'Exact Year', priority: 2 },
      { type: 'condition', label: 'New', priority: 4 }
    ]
  },
  {
    id: 'product2',
    title: '2015-2020 Toyota Camry Brake Pads - Aftermarket',
    brand: 'Bosch',
    partType: 'Brake Pads',
    condition: 'New',
    price: 49.99,
    shipping: '$5.99 Shipping',
    image: '/path/to/image.jpg',
    relevanceScore: 65,
    primaryBadge: { type: 'partType', label: 'Exact Part', priority: 1 },
    secondaryBadges: [
      { type: 'yearRange', label: 'Year Compatible', priority: 3 },
      { type: 'shipping', label: 'Free Shipping', priority: 5 }
    ]
  }
];

/**
 * Test suite for ProductRenderer
 */
function testProductRenderer() {
  console.log('TESTING ProductRenderer MODULE...');
  
  // Test 1: renderProductCard function
  console.log('\nTest 1: renderProductCard function');
  const productCardHTML = ProductRenderer.renderProductCard(testProducts[0]);
  console.log('- Returns non-empty string:', typeof productCardHTML === 'string' && productCardHTML.length > 0);
  console.log('- Contains product title:', productCardHTML.includes(testProducts[0].title));
  console.log('- Contains product price:', productCardHTML.includes(testProducts[0].price.toString()));
  console.log('- Applied relevance class:', productCardHTML.includes('product-relevance-high'));
  
  // Test 2: renderProductList function (mock container)
  console.log('\nTest 2: renderProductList function');
  
  // Create a mock container element
  const mockContainer = document.createElement('div');
  mockContainer.id = 'mock-container';
  document.body.appendChild(mockContainer);
  
  // Add event listener to test custom event
  let eventFired = false;
  mockContainer.addEventListener('products-rendered', function(e) {
    eventFired = true;
  });
  
  // Call the function
  ProductRenderer.renderProductList(testProducts, mockContainer);
  
  console.log('- Populates container with content:', mockContainer.innerHTML.length > 0);
  console.log('- Creates correct number of product cards:', 
    mockContainer.querySelectorAll('.product-card').length === testProducts.length);
  console.log('- Fires custom event:', eventFired);
  
  // Clean up
  document.body.removeChild(mockContainer);
  
  // Test 3: updateProductCards function
  console.log('\nTest 3: updateProductCards function');
  console.log('- Function exists:', typeof ProductRenderer.updateProductCards === 'function');
  
  // Create test elements to update
  const testContainer = document.createElement('div');
  testContainer.innerHTML = `
    <div class="product-card" data-product-id="product1">
      <div class="product-badges-container"></div>
    </div>
  `;
  document.body.appendChild(testContainer);
  
  // This would update the elements if they exist in the document
  ProductRenderer.updateProductCards(testProducts);
  console.log('- Function executes without errors');
  
  // Clean up
  document.body.removeChild(testContainer);
  
  console.log('\nProductRenderer TESTS COMPLETE');
}

// Run tests when the page loads
window.addEventListener('load', function() {
  // Check if ProductRenderer is available
  if (window.ProductRenderer) {
    testProductRenderer();
  } else {
    console.error('ProductRenderer module not found!');
  }
});
