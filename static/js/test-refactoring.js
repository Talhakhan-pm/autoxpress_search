/**
 * Test script for verifying the refactored product rendering and filtering functionality
 * 
 * To use this script:
 * 1. Load the application in your browser
 * 2. Open the browser console
 * 3. Copy and paste this entire script into the console
 * 4. Run the tests by calling the test functions (e.g., testProductRendering())
 */

// Global test state
const testState = {
  testResults: {},
  passCount: 0,
  failCount: 0,
  currentTest: null,
};

// Helper function to log test results
function logTestResult(testName, passed, message) {
  console.log(
    `${passed ? '✅' : '❌'} ${testName}: ${message}`
  );
  
  testState.testResults[testName] = {
    passed,
    message
  };
  
  if (passed) {
    testState.passCount++;
  } else {
    testState.failCount++;
  }
}

// Helper function to simulate a search
async function simulateSearch(query = "2018 Toyota Camry brake pads") {
  console.log(`Simulating search for: "${query}"`);
  
  // Set the prompt field value
  const promptField = document.getElementById('prompt');
  if (promptField) {
    promptField.value = query;
  } else {
    throw new Error("Cannot find prompt field");
  }
  
  // Get the form element
  const form = document.getElementById('search-form');
  if (!form) {
    throw new Error("Cannot find search form");
  }
  
  // Trigger form submission
  form.dispatchEvent(new Event('submit', { cancelable: true }));
  
  // Wait for results to load
  console.log("Waiting for results to load...");
  return new Promise(resolve => {
    // Check every 500ms if results are loaded
    const checkInterval = setInterval(() => {
      const productsContainer = document.getElementById('products-container');
      if (productsContainer && productsContainer.children.length > 0) {
        clearInterval(checkInterval);
        // Give a little extra time for everything to render
        setTimeout(() => {
          console.log("Search results loaded");
          resolve(true);
        }, 1000);
      }
    }, 500);
    
    // Timeout after 15 seconds
    setTimeout(() => {
      clearInterval(checkInterval);
      console.warn("Timeout waiting for search results");
      resolve(false);
    }, 15000);
  });
}

// Main test for product rendering functionality
async function testProductRendering() {
  console.group("🧪 TESTING PRODUCT RENDERING");
  testState.currentTest = "productRendering";
  
  try {
    // First, check if we're on the right page
    if (!document.getElementById('search-form')) {
      throw new Error("Not on the search page");
    }
    
    // 1. Check if the unified API exists
    if (!window.productDisplay) {
      logTestResult("API Check", false, "window.productDisplay not found");
      throw new Error("Unified API not found");
    } else {
      logTestResult("API Check", true, "window.productDisplay exists");
    }
    
    // 2. Check if required API methods exist
    const requiredMethods = ['setProducts', 'applyFilters', 'updateViewMode', 'resetFilters'];
    const missingMethods = requiredMethods.filter(
      method => typeof window.productDisplay[method] !== 'function'
    );
    
    if (missingMethods.length > 0) {
      logTestResult(
        "API Methods", 
        false, 
        `Missing required methods: ${missingMethods.join(', ')}`
      );
    } else {
      logTestResult("API Methods", true, "All required API methods exist");
    }
    
    // 3. Check if we can load search results
    const searchSuccess = await simulateSearch();
    logTestResult(
      "Search Results", 
      searchSuccess, 
      searchSuccess ? "Search results loaded successfully" : "Failed to load search results"
    );
    
    if (!searchSuccess) {
      throw new Error("Search failed");
    }
    
    // 4. Test different view modes
    const viewModes = ['grid', 'list', 'compact'];
    for (const mode of viewModes) {
      console.log(`Testing view mode: ${mode}`);
      
      if (typeof window.productDisplay.updateViewMode === 'function') {
        window.productDisplay.updateViewMode(mode);
        
        // Check if the container has the correct class
        const container = document.getElementById('products-container');
        const hasCorrectClass = container.classList.contains(`${mode}-view`);
        
        logTestResult(
          `${mode} View Mode`, 
          hasCorrectClass, 
          hasCorrectClass ? 
            `${mode} view applied successfully` : 
            `Failed to apply ${mode} view`
        );
      } else {
        logTestResult(
          `${mode} View Mode`, 
          false, 
          "updateViewMode function not available"
        );
      }
    }
    
    // Summary
    console.log(`\nProduct Rendering Test Summary: ${testState.passCount} passed, ${testState.failCount} failed`);
    
  } catch (error) {
    console.error("Test failed with error:", error);
    logTestResult("Overall Test", false, error.message);
  }
  
  console.groupEnd();
  return testState.testResults;
}

// Test filtering functionality
async function testFiltering() {
  console.group("🧪 TESTING FILTERING FUNCTIONALITY");
  
  // Reset our test counters
  testState.passCount = 0;
  testState.failCount = 0;
  testState.currentTest = "filtering";
  
  try {
    // 1. Check if the filtering API exists
    if (!window.productDisplay || typeof window.productDisplay.applyFilters !== 'function') {
      logTestResult("Filtering API", false, "Filtering API not available");
      throw new Error("Filtering API not found");
    } else {
      logTestResult("Filtering API", true, "Filtering API exists");
    }
    
    // Make sure we have search results to filter
    const productsContainer = document.getElementById('products-container');
    if (!productsContainer || productsContainer.children.length === 0) {
      const searchSuccess = await simulateSearch();
      if (!searchSuccess) {
        throw new Error("Cannot test filtering without search results");
      }
    }
    
    // Count the initial number of products
    const initialProductCount = document.querySelectorAll('.product-card').length;
    logTestResult("Initial Products", initialProductCount > 0, `Found ${initialProductCount} products to test filtering`);
    
    // Get filter checkboxes
    const filterCheckboxes = document.querySelectorAll('.filter-check');
    logTestResult("Filter UI", filterCheckboxes.length > 0, `Found ${filterCheckboxes.length} filter checkboxes`);
    
    // 2. Test condition filtering
    console.log("Testing condition filtering...");
    
    // Find condition checkboxes
    const newOnlyCheckbox = document.getElementById('newOnly');
    const usedOnlyCheckbox = document.getElementById('usedOnly');
    
    if (newOnlyCheckbox && usedOnlyCheckbox) {
      // Test 'New Only' filter
      newOnlyCheckbox.checked = true;
      newOnlyCheckbox.dispatchEvent(new Event('change', { bubbles: true }));
      
      // Wait for filtering to apply
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Check if filtering happened
      const newFilteredCount = document.querySelectorAll('.product-card:not([style*="display: none"])').length;
      logTestResult(
        "New Only Filter", 
        newFilteredCount <= initialProductCount, 
        `New Only filter applied: ${newFilteredCount} products showing (was ${initialProductCount})`
      );
      
      // Reset filter
      newOnlyCheckbox.checked = false;
      newOnlyCheckbox.dispatchEvent(new Event('change', { bubbles: true }));
      await new Promise(resolve => setTimeout(resolve, 500));
    } else {
      logTestResult("Condition Filters", false, "Could not find condition filter checkboxes");
    }
    
    // 3. Test shipping filtering
    console.log("Testing shipping filtering...");
    const freeShippingCheckbox = document.getElementById('freeShipping');
    
    if (freeShippingCheckbox) {
      // Test 'Free Shipping' filter
      freeShippingCheckbox.checked = true;
      freeShippingCheckbox.dispatchEvent(new Event('change', { bubbles: true }));
      
      // Wait for filtering to apply
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Check if filtering happened
      const shippingFilteredCount = document.querySelectorAll('.product-card:not([style*="display: none"])').length;
      logTestResult(
        "Free Shipping Filter", 
        shippingFilteredCount <= initialProductCount, 
        `Free Shipping filter applied: ${shippingFilteredCount} products showing (was ${initialProductCount})`
      );
      
      // Reset filter
      freeShippingCheckbox.checked = false;
      freeShippingCheckbox.dispatchEvent(new Event('change', { bubbles: true }));
      await new Promise(resolve => setTimeout(resolve, 500));
    } else {
      logTestResult("Shipping Filters", false, "Could not find free shipping filter checkbox");
    }
    
    // 4. Test filter reset
    console.log("Testing filter reset...");
    const resetButton = document.getElementById('resetFilters');
    
    if (resetButton) {
      // Apply multiple filters
      if (newOnlyCheckbox) {
        newOnlyCheckbox.checked = true;
        newOnlyCheckbox.dispatchEvent(new Event('change', { bubbles: true }));
      }
      
      if (freeShippingCheckbox) {
        freeShippingCheckbox.checked = true;
        freeShippingCheckbox.dispatchEvent(new Event('change', { bubbles: true }));
      }
      
      // Wait for filtering to apply
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Get filtered count
      const multiFilterCount = document.querySelectorAll('.product-card:not([style*="display: none"])').length;
      
      // Reset filters
      resetButton.click();
      
      // Wait for reset to apply
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Check if reset worked
      const resetCount = document.querySelectorAll('.product-card:not([style*="display: none"])').length;
      
      logTestResult(
        "Filter Reset", 
        resetCount >= multiFilterCount, 
        `Filter reset worked: ${multiFilterCount} → ${resetCount} products showing`
      );
    } else {
      logTestResult("Filter Reset", false, "Could not find reset button");
    }
    
    // Summary
    console.log(`\nFiltering Test Summary: ${testState.passCount} passed, ${testState.failCount} failed`);
    
  } catch (error) {
    console.error("Test failed with error:", error);
    logTestResult("Overall Filtering Test", false, error.message);
  }
  
  console.groupEnd();
  return testState.testResults;
}

// Run all tests
async function runAllTests() {
  console.group("🧪 RUNNING ALL TESTS");
  
  const renderingResults = await testProductRendering();
  const filteringResults = await testFiltering();
  
  const totalTests = Object.keys(renderingResults).length + Object.keys(filteringResults).length;
  const passedTests = Object.values(renderingResults).filter(r => r.passed).length + 
                     Object.values(filteringResults).filter(r => r.passed).length;
  
  console.log(`\n📊 FINAL TEST SUMMARY:`);
  console.log(`Total Tests: ${totalTests}`);
  console.log(`Passed: ${passedTests}`);
  console.log(`Failed: ${totalTests - passedTests}`);
  console.log(`Success Rate: ${Math.round((passedTests / totalTests) * 100)}%`);
  
  console.groupEnd();
}

console.log("🧪 Test script loaded successfully!");
console.log("Run tests with runAllTests() or test specific areas with testProductRendering() or testFiltering()");