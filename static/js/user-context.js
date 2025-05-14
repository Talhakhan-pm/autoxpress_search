/**
 * User Context Module
 * Maintains information about the user's vehicle and search history
 * for more personalized chat responses
 */

// Store user context info
let userVehicleContext = {};

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Load saved vehicle context from session storage
    loadVehicleContext();
    
    // Add event listeners to capture vehicle information from search form
    const searchForm = document.getElementById('search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            captureVehicleContext();
        });
    }
    
    // Add event listeners to capture VIN information
    const vinForm = document.getElementById('vin-form');
    if (vinForm) {
        vinForm.addEventListener('submit', function(e) {
            const vinInput = document.getElementById('vin');
            if (vinInput && vinInput.value) {
                updateVehicleContext({
                    vin: vinInput.value.trim()
                });
            }
        });
    }
});

/**
 * Captures vehicle information from search form fields
 */
function captureVehicleContext() {
    const yearField = document.getElementById('year-field');
    const makeField = document.getElementById('make-field');
    const modelField = document.getElementById('model-field');
    const engineField = document.getElementById('engine-field');
    
    // Build vehicle context object with available information
    const vehicleInfo = {};
    
    if (yearField && yearField.value) vehicleInfo.year = yearField.value.trim();
    if (makeField && makeField.value) vehicleInfo.make = makeField.value.trim();
    if (modelField && modelField.value) vehicleInfo.model = modelField.value.trim();
    if (engineField && engineField.value) vehicleInfo.engine = engineField.value.trim();
    
    // Try to extract from single field if multi-field is empty
    if (!vehicleInfo.year && !vehicleInfo.make && !vehicleInfo.model) {
        const promptField = document.getElementById('prompt');
        if (promptField && promptField.value) {
            const singleFieldQuery = promptField.value.trim();
            
            // Try to extract year (4 digits starting with 19 or 20)
            const yearMatch = singleFieldQuery.match(/\b(19|20)\d{2}\b/);
            if (yearMatch) vehicleInfo.year = yearMatch[0];
            
            // For make and model, we'd need more sophisticated parsing
            // This is a simplified approach for common makes
            const commonMakes = ['Honda', 'Toyota', 'Ford', 'Chevrolet', 'Nissan', 'BMW', 'Mercedes', 'Audi', 'Hyundai', 'Kia'];
            for (const make of commonMakes) {
                if (singleFieldQuery.toLowerCase().includes(make.toLowerCase())) {
                    vehicleInfo.make = make;
                    break;
                }
            }
        }
    }
    
    // Only update if we have at least some vehicle information
    if (Object.keys(vehicleInfo).length > 0) {
        updateVehicleContext(vehicleInfo);
    }
}

/**
 * Updates the vehicle context with new information
 */
function updateVehicleContext(newInfo) {
    // Update the context with new info
    userVehicleContext = {...userVehicleContext, ...newInfo};
    
    // Clean up any empty values
    Object.keys(userVehicleContext).forEach(key => {
        if (!userVehicleContext[key]) {
            delete userVehicleContext[key];
        }
    });
    
    // Save to session storage
    saveVehicleContext();
}

/**
 * Gets the current vehicle context for API requests
 */
function getVehicleContext() {
    return {...userVehicleContext};
}

/**
 * Saves vehicle context to session storage
 */
function saveVehicleContext() {
    sessionStorage.setItem('userVehicleContext', JSON.stringify(userVehicleContext));
}

/**
 * Loads vehicle context from session storage
 */
function loadVehicleContext() {
    const savedContext = sessionStorage.getItem('userVehicleContext');
    if (savedContext) {
        try {
            userVehicleContext = JSON.parse(savedContext);
        } catch (e) {
            console.error('Error loading vehicle context:', e);
            userVehicleContext = {};
        }
    }
}

// Track parts the user has searched for
let partsSearchHistory = [];

/**
 * Adds a part to the search history
 */
function addPartToHistory(partName) {
    if (partName && typeof partName === 'string') {
        // Add to beginning of array (most recent first)
        partsSearchHistory.unshift(partName.trim());
        
        // Keep only the 10 most recent searches
        if (partsSearchHistory.length > 10) {
            partsSearchHistory = partsSearchHistory.slice(0, 10);
        }
        
        // Save to session storage
        sessionStorage.setItem('partsSearchHistory', JSON.stringify(partsSearchHistory));
    }
}

/**
 * Gets the parts search history
 */
function getPartsHistory() {
    return [...partsSearchHistory];
}

// Initialize parts history from session storage
document.addEventListener('DOMContentLoaded', function() {
    const savedHistory = sessionStorage.getItem('partsSearchHistory');
    if (savedHistory) {
        try {
            partsSearchHistory = JSON.parse(savedHistory);
        } catch (e) {
            console.error('Error loading parts history:', e);
            partsSearchHistory = [];
        }
    }
    
    // Add event listener to capture part searches
    const partField = document.getElementById('part-field');
    const searchForm = document.getElementById('search-form');
    
    if (partField && searchForm) {
        searchForm.addEventListener('submit', function() {
            if (partField.value) {
                addPartToHistory(partField.value);
            }
        });
    }
});

// Make functions globally available
window.getVehicleContext = getVehicleContext;
window.getPartsHistory = getPartsHistory;