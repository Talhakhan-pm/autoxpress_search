/**
 * Unit tests for ProductRanking module
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
    image: '/path/to/image.jpg'
  },
  {
    id: 'product2',
    title: '2015-2020 Toyota Camry Brake Pads - Aftermarket',
    brand: 'Bosch',
    partType: 'Brake Pads',
    condition: 'New',
    price: 49.99,
    shipping: '$5.99 Shipping',
    image: '/path/to/image.jpg'
  },
  {
    id: 'product3',
    title: 'Used Toyota Camry Brake Pads 2016',
    brand: 'Toyota',
    partType: 'Brake Pads',
    condition: 'Used',
    price: 29.99,
    shipping: 'Free Shipping',
    image: '/path/to/image.jpg'
  }
];

const testVehicleInfo = {
  make: 'Toyota',
  model: 'Camry',
  year: '2018',
  part: 'Brake Pads'
};

/**
 * Test suite for ProductRanking
 */
function testProductRanking() {
  console.log('TESTING ProductRanking MODULE...');
  
  // Test 1: rankProduct function
  console.log('\nTest 1: rankProduct function');
  const rankedProduct = ProductRanking.rankProduct(testProducts[0], testVehicleInfo);
  console.log('- Ranked product has relevanceScore:', rankedProduct.relevanceScore !== undefined);
  console.log('- Ranked product has primaryBadge:', rankedProduct.primaryBadge !== undefined);
  console.log('- Ranked product has secondaryBadges array:', Array.isArray(rankedProduct.secondaryBadges));
  
  // Test 2: rankProducts function (multiple products)
  console.log('\nTest 2: rankProducts function');
  const rankedProducts = ProductRanking.rankProducts(testProducts, testVehicleInfo);
  console.log('- Returns correct number of products:', rankedProducts.length === testProducts.length);
  console.log('- Products are sorted by relevance score:', 
    rankedProducts[0].relevanceScore >= rankedProducts[1].relevanceScore);
  
  // Test 3: Exact year match scoring
  console.log('\nTest 3: Exact year match scoring');
  const exactYearProduct = ProductRanking.rankProduct(testProducts[0], testVehicleInfo);
  const rangeYearProduct = ProductRanking.rankProduct(testProducts[1], testVehicleInfo);
  console.log('- Exact year match scores higher than range match:', 
    exactYearProduct.relevanceScore > rangeYearProduct.relevanceScore);
  
  // Test 4: Condition affects score
  console.log('\nTest 4: Condition affects score');
  const newProduct = ProductRanking.rankProduct(testProducts[0], testVehicleInfo);
  const usedProduct = ProductRanking.rankProduct(testProducts[2], testVehicleInfo);
  console.log('- New product scores higher than used product (all else equal):', 
    newProduct.relevanceScore > usedProduct.relevanceScore);
  
  // Test 5: Free shipping affects score
  console.log('\nTest 5: Free shipping affects score');
  const freeShippingProduct = ProductRanking.rankProduct(testProducts[0], testVehicleInfo);
  const paidShippingProduct = ProductRanking.rankProduct({
    ...testProducts[0],
    shipping: '$5.99 Shipping'
  }, testVehicleInfo);
  console.log('- Free shipping scores higher than paid shipping:', 
    freeShippingProduct.relevanceScore > paidShippingProduct.relevanceScore);
  
  console.log('\nProductRanking TESTS COMPLETE');
}

// Run tests when the page loads
window.addEventListener('load', function() {
  // Check if ProductRanking is available
  if (window.ProductRanking) {
    testProductRanking();
  } else {
    console.error('ProductRanking module not found!');
  }
});
