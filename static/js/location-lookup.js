/**
 * Location Lookup Module
 * Handles ZIP code lookup and management of saved locations
 */

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const zipForm = document.getElementById('zip-form');
    const zipInput = document.getElementById('zip-code');
    const zipButton = document.getElementById('zip-button');
    const zipLoading = document.getElementById('zip-loading');
    const zipError = document.getElementById('zip-error');
    const zipResult = document.getElementById('zip-result');
    const noZipResults = document.getElementById('no-zip-results');
    const saveLocationBtn = document.getElementById('save-location');
    const clearLocationBtn = document.getElementById('clear-location');
    const savedLocationsList = document.getElementById('saved-locations-list');
    const noSavedLocations = document.getElementById('no-saved-locations');
    
    // Location result fields
    const locationCityState = document.getElementById('location-city-state');
    const locationZip = document.getElementById('location-zip');
    const locationState = document.getElementById('location-state');
    const locationCounty = document.getElementById('location-county');
    const locationTimezone = document.getElementById('location-timezone');
    const locationAreaCode = document.getElementById('location-area-code');
    
    // State variables
    let currentLocation = null;
    const SAVED_LOCATIONS_KEY = 'autoxpress_locations';
    
    // Initialize
    initializeModule();
    
    function initializeModule() {
        // Add input validation to ZIP code field
        zipInput.addEventListener('input', function() {
            // Allow only digits and limit to 5 characters
            this.value = this.value.replace(/[^0-9]/g, '').substring(0, 5);
        });
        
        // Form submission
        if (zipForm) {
            zipForm.addEventListener('submit', handleZipSubmit);
        }
        
        // Button event listeners
        if (saveLocationBtn) {
            saveLocationBtn.addEventListener('click', saveCurrentLocation);
        }
        
        if (clearLocationBtn) {
            clearLocationBtn.addEventListener('click', clearLocationDisplay);
        }
        
        // Load and display saved locations
        displaySavedLocations();
        
        // Location tab shown event
        const locationTab = document.getElementById('location-tab');
        if (locationTab) {
            locationTab.addEventListener('shown.bs.tab', function() {
                // Refresh the saved locations display when tab is shown
                displaySavedLocations();
            });
        }
    }
    
    /**
     * Handle ZIP code form submission
     */
    function handleZipSubmit(e) {
        e.preventDefault();
        
        const zipCode = zipInput.value.trim();
        
        // Validate ZIP code
        if (!/^\d{5}$/.test(zipCode)) {
            showError('Please enter a valid 5-digit ZIP code');
            return;
        }
        
        // Show loading, hide error and results
        zipLoading.classList.remove('d-none');
        zipError.classList.add('d-none');
        zipResult.classList.add('d-none');
        
        // Disable the submit button
        zipButton.disabled = true;
        zipButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2" style="width: 1rem; height: 1rem;" role="status" aria-hidden="true"></span><span style="vertical-align: middle;">Searching...</span>';

        // Make the API request
        lookupZipCode(zipCode)
            .then(data => {
                // Hide loading
                zipLoading.classList.add('d-none');
                
                // Update and show results
                updateLocationDisplay(data);
                
                // Store current location data
                currentLocation = data;
                
                // Enable save button
                if (saveLocationBtn) {
                    saveLocationBtn.disabled = false;
                }
            })
            .catch(error => {
                showError(error.message || 'Failed to retrieve location information');
                zipResult.classList.add('d-none');
                noZipResults.classList.remove('d-none');
            })
            .finally(() => {
                // Re-enable the submit button
                zipButton.disabled = false;
                zipButton.innerHTML = '<i class="fas fa-search me-1"></i> Lookup';
            });
    }
    
    /**
     * Look up ZIP code information using the Zippopotam.us API
     * This is a free, public API that doesn't require an API key
     */
    function lookupZipCode(zipCode) {
        return new Promise((resolve, reject) => {
            // Show loading state
            zipLoading.classList.remove('d-none');
            
            // API URL for US zip codes
            const apiUrl = `https://api.zippopotam.us/us/${zipCode}`;
            
            fetch(apiUrl)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('ZIP code not found or invalid');
                    }
                    return response.json();
                })
                .then(data => {
                    // Transform the API response to our format
                    const locationData = {
                        city: data.places[0]['place name'],
                        state: data.places[0]['state abbreviation'],
                        county: data.places[0]['state'], // API doesn't provide county, using state name instead
                        timezone: getTimezoneFromState(data.places[0]['state abbreviation']), // Estimate timezone from state
                        areaCode: getAreaCodeEstimate(data.places[0]['state abbreviation']), // Estimate area code
                        zip: data['post code']
                    };
                    
                    resolve(locationData);
                })
                .catch(error => {
                    console.error('Error fetching ZIP data:', error);
                    reject(new Error('Could not find information for this ZIP code'));
                });
        });
    }
    
    /**
     * Helper function to estimate timezone from state
     * Note: This is an approximation as some states span multiple timezones
     */
    function getTimezoneFromState(stateCode) {
        const timezones = {
            // Eastern
            'CT': 'Eastern', 'DE': 'Eastern', 'FL': 'Eastern', 'GA': 'Eastern',
            'IN': 'Eastern', 'KY': 'Eastern', 'ME': 'Eastern', 'MD': 'Eastern',
            'MA': 'Eastern', 'MI': 'Eastern', 'NH': 'Eastern', 'NJ': 'Eastern',
            'NY': 'Eastern', 'NC': 'Eastern', 'OH': 'Eastern', 'PA': 'Eastern',
            'RI': 'Eastern', 'SC': 'Eastern', 'VT': 'Eastern', 'VA': 'Eastern',
            'WV': 'Eastern', 'DC': 'Eastern',
            
            // Central
            'AL': 'Central', 'AR': 'Central', 'IL': 'Central', 'IA': 'Central',
            'LA': 'Central', 'MN': 'Central', 'MS': 'Central', 'MO': 'Central',
            'OK': 'Central', 'SD': 'Central', 'TN': 'Central', 'TX': 'Central',
            'WI': 'Central',
            
            // Mountain
            'AZ': 'Mountain', 'CO': 'Mountain', 'ID': 'Mountain', 'MT': 'Mountain',
            'NE': 'Mountain', 'NM': 'Mountain', 'ND': 'Mountain', 'UT': 'Mountain',
            'WY': 'Mountain',
            
            // Pacific
            'CA': 'Pacific', 'NV': 'Pacific', 'OR': 'Pacific', 'WA': 'Pacific',
            
            // Alaska
            'AK': 'Alaska',
            
            // Hawaii
            'HI': 'Hawaii'
        };
        
        return timezones[stateCode] || 'Unknown';
    }
    
    /**
     * Helper function to estimate area code from state
     * Note: This returns a common area code for the state, not the exact one for the ZIP
     */
    function getAreaCodeEstimate(stateCode) {
        const areaCodes = {
            'AL': '205', 'AK': '907', 'AZ': '480', 'AR': '501',
            'CA': '213', 'CO': '303', 'CT': '203', 'DE': '302',
            'FL': '305', 'GA': '404', 'HI': '808', 'ID': '208',
            'IL': '312', 'IN': '317', 'IA': '319', 'KS': '316',
            'KY': '502', 'LA': '504', 'ME': '207', 'MD': '301',
            'MA': '617', 'MI': '313', 'MN': '218', 'MS': '601',
            'MO': '314', 'MT': '406', 'NE': '402', 'NV': '702',
            'NH': '603', 'NJ': '201', 'NM': '505', 'NY': '212',
            'NC': '704', 'ND': '701', 'OH': '216', 'OK': '405',
            'OR': '503', 'PA': '215', 'RI': '401', 'SC': '803',
            'SD': '605', 'TN': '615', 'TX': '214', 'UT': '801',
            'VT': '802', 'VA': '703', 'WA': '206', 'WV': '304',
            'WI': '414', 'WY': '307', 'DC': '202'
        };
        
        return areaCodes[stateCode] || 'Unknown';
    }
    
    /**
     * Update the location display with the retrieved data
     */
    function updateLocationDisplay(data) {
        if (!data) return;
        
        // Update the display fields
        locationCityState.textContent = `${data.city}, ${data.state}`;
        locationZip.textContent = data.zip;
        locationState.textContent = data.state;
        locationCounty.textContent = data.county;
        locationTimezone.textContent = data.timezone;
        locationAreaCode.textContent = data.areaCode;
        
        // Show the result, hide the placeholder
        zipResult.classList.remove('d-none');
        noZipResults.classList.add('d-none');
    }
    
    /**
     * Show an error message
     */
    function showError(message) {
        zipError.textContent = message;
        zipError.classList.remove('d-none');
        zipLoading.classList.add('d-none');
    }
    
    /**
     * Clear the location display
     */
    function clearLocationDisplay() {
        // Clear input
        zipInput.value = '';
        
        // Hide results, show placeholder
        zipResult.classList.add('d-none');
        noZipResults.classList.remove('d-none');
        zipError.classList.add('d-none');
        
        // Clear current location data
        currentLocation = null;
        
        // Disable save button
        if (saveLocationBtn) {
            saveLocationBtn.disabled = true;
        }
    }
    
    /**
     * Save the current location
     */
    function saveCurrentLocation() {
        if (!currentLocation) return;
        
        // Get saved locations from localStorage
        const savedLocations = getSavedLocations();
        
        // Check if this ZIP is already saved
        const existingIndex = savedLocations.findIndex(loc => loc.zip === currentLocation.zip);
        
        if (existingIndex >= 0) {
            // If already saved, update it
            savedLocations[existingIndex] = {
                ...currentLocation,
                savedAt: new Date().toISOString()
            };
        } else {
            // Otherwise add it
            savedLocations.push({
                ...currentLocation,
                savedAt: new Date().toISOString()
            });
        }
        
        // Save back to localStorage
        localStorage.setItem(SAVED_LOCATIONS_KEY, JSON.stringify(savedLocations));
        
        // Show success message (could be a toast notification in a real app)
        const messageDiv = document.createElement('div');
        messageDiv.className = 'alert alert-success mt-3 fade show';
        messageDiv.innerHTML = `
            <i class="fas fa-check-circle me-2"></i>
            Location saved successfully!
        `;
        zipForm.appendChild(messageDiv);
        
        // Remove the message after 3 seconds
        setTimeout(() => {
            messageDiv.classList.add('fade');
            setTimeout(() => messageDiv.remove(), 300);
        }, 3000);
        
        // Refresh the saved locations display
        displaySavedLocations();
    }
    
    /**
     * Get saved locations from localStorage
     */
    function getSavedLocations() {
        const savedLocationsJSON = localStorage.getItem(SAVED_LOCATIONS_KEY);
        return savedLocationsJSON ? JSON.parse(savedLocationsJSON) : [];
    }
    
    /**
     * Display saved locations
     */
    function displaySavedLocations() {
        const savedLocations = getSavedLocations();
        
        if (savedLocations.length === 0) {
            // Show the "no saved locations" message
            if (noSavedLocations) {
                noSavedLocations.classList.remove('d-none');
            }
            
            // Clear the list
            if (savedLocationsList) {
                savedLocationsList.innerHTML = '';
                savedLocationsList.appendChild(noSavedLocations);
            }
            
            return;
        }
        
        // Hide the "no saved locations" message
        if (noSavedLocations) {
            noSavedLocations.classList.add('d-none');
        }
        
        // Clear the list
        if (savedLocationsList) {
            savedLocationsList.innerHTML = '';
            
            // Sort locations by most recently saved
            const sortedLocations = [...savedLocations].sort((a, b) => {
                return new Date(b.savedAt) - new Date(a.savedAt);
            });
            
            // Create the location cards
            const locationCards = document.createElement('div');
            locationCards.className = 'row row-cols-1 row-cols-md-2 row-cols-lg-3 g-3 mt-2';
            
            sortedLocations.forEach(location => {
                const card = createLocationCard(location);
                locationCards.appendChild(card);
            });
            
            savedLocationsList.appendChild(locationCards);
        }
    }
    
    /**
     * Create a location card for a saved location
     */
    function createLocationCard(location) {
        const cardCol = document.createElement('div');
        cardCol.className = 'col';
        
        // Format saved date
        const savedDate = new Date(location.savedAt);
        const formattedDate = savedDate.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
        
        cardCol.innerHTML = `
            <div class="card h-100 saved-location-card">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <h6 class="card-title mb-0">${location.city}, ${location.state}</h6>
                        <span class="badge bg-light text-dark">${location.zip}</span>
                    </div>
                    <p class="card-text small text-muted mb-0">County: ${location.county}</p>
                    <p class="card-text small text-muted">Area Code: ${location.areaCode}</p>
                    <div class="d-flex justify-content-between mt-3">
                        <small class="text-muted">Saved on ${formattedDate}</small>
                        <button class="btn btn-sm btn-outline-danger remove-location" data-zip="${location.zip}">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Add click handler for the remove button
        const removeButton = cardCol.querySelector('.remove-location');
        if (removeButton) {
            removeButton.addEventListener('click', function() {
                removeLocation(location.zip);
            });
        }
        
        return cardCol;
    }
    
    /**
     * Remove a saved location
     */
    function removeLocation(zipCode) {
        // Get saved locations
        const savedLocations = getSavedLocations();
        
        // Filter out the location to remove
        const updatedLocations = savedLocations.filter(loc => loc.zip !== zipCode);
        
        // Save back to localStorage
        localStorage.setItem(SAVED_LOCATIONS_KEY, JSON.stringify(updatedLocations));
        
        // Refresh the display
        displaySavedLocations();
    }
});