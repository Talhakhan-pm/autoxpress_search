/**
 * VIN Decoder Module
 * Handles VIN lookup and display functionality
 */

const VinDecoder = (function() {
  // Private variables
  let vinResultContainer, vinError, vinData, vinLoading;
  let vinResultsTab, vinResultsTabItem;
  let yearField, makeField, modelField, engineField, partField;
  
  // Initialize the module
  function init() {
    // Get DOM elements for VIN decoder
    vinResultContainer = document.getElementById('result-container'); // Now using the main result container
    vinError = document.getElementById('vin-error');
    vinData = document.getElementById('vin-data');
    vinLoading = document.getElementById('vin-loading');
    
    // Get tab elements
    vinResultsTab = document.getElementById('vin-results-tab');
    vinResultsTabItem = document.getElementById('vin-results-tab-item');
    
    // Get form field references
    yearField = document.getElementById('year-field');
    makeField = document.getElementById('make-field');
    modelField = document.getElementById('model-field');
    engineField = document.getElementById('engine-field');
    partField = document.getElementById('part-field');
    
    // Add event listener for auto-capitalization
    const vinInput = document.getElementById('vin');
    if (vinInput) {
      vinInput.addEventListener('input', function() {
        // Convert to uppercase as they type
        this.value = this.value.toUpperCase();
      });
    }
    
    // Set up form submission
    const vinForm = document.getElementById('vin-form');
    if (vinForm) {
      vinForm.addEventListener('submit', handleVinSubmit);
    }
  }
  
  // Handle VIN form submission
  async function handleVinSubmit(e) {
    e.preventDefault();
    const vinValue = document.getElementById('vin').value.trim();
    const vinButton = document.getElementById('vin-button');

    if (!vinValue) {
      alert('Please enter a VIN.');
      return;
    }

    // Reset UI for VIN results
    vinError.classList.add('d-none');
    vinData.innerHTML = '';
    
    // Show the main results container and ensure VIN tab is visible
    vinResultContainer.style.display = 'flex';
    vinResultsTabItem.classList.remove('d-none');

    // Show loading
    vinLoading.classList.remove('d-none');
    
    // Disable the button during request
    vinButton.disabled = true;
    vinButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Decoding...';

    try {
      const vinInfo = await decodeVin(vinValue);
      
      // Hide loading
      vinLoading.classList.add('d-none');

      if (vinInfo.error) {
        vinError.textContent = vinInfo.error;
        vinError.classList.remove('d-none');
        return;
      }

      // Display VIN data
      displayVinData(vinInfo);
      
      // Switch to the VIN results tab
      vinResultsTab.click();

    } catch (error) {
      console.error('Error:', error);
      vinLoading.classList.add('d-none');
      vinError.textContent = 'A network error occurred. Please try again later.';
      vinError.classList.remove('d-none');
    } finally {
      // Re-enable the button
      vinButton.disabled = false;
      vinButton.innerHTML = '<i class="fas fa-search me-1" style="font-size: 0.9rem;"></i> Decode VIN';
    }
  }
  
  // Function to decode VIN via API
  async function decodeVin(vin) {
    const formData = new FormData();
    formData.append('vin', vin);
    
    const response = await fetch('/api/vin-decode', {
      method: 'POST',
      body: formData
    });

    const data = await response.json();
    
    // Debug output
    console.log("VIN decode response:", data);
    
    return data;
  }
  
  // Function to display VIN data
  function displayVinData(data) {
    vinData.innerHTML = '';
    
    // Safety check - make sure we have data
    if (!data || typeof data !== 'object') {
      vinError.textContent = "Invalid data received from VIN decoder";
      vinError.classList.remove('d-none');
      return;
    }
    
    // Check for API error response
    if (data.error) {
      vinError.textContent = data.error;
      vinError.classList.remove('d-none');
      return;
    }

    // Handle the API property format
    let vehicleData;
    
    if (data.Results && Array.isArray(data.Results) && data.Results.length > 0) {
      console.log("Using Results[0] for VIN data");
      vehicleData = data.Results[0];
    } else if (data.Count && data.Count > 0 && data.Results) {
      console.log("Data has Count but Results not usable, data:", data);
      vehicleData = data;
    } else {
      console.log("Using direct properties for VIN data");
      vehicleData = data;
    }
    
    // Create primary info card
    const primaryInfoCard = document.createElement('div');
    primaryInfoCard.className = 'col-md-6 mb-4';
    
    primaryInfoCard.innerHTML = `
      <div class="card h-100">
        <div class="card-header bg-primary text-white">Vehicle Information</div>
        <div class="card-body">
          <h5>${vehicleData.ModelYear || 'Unknown'} ${vehicleData.Make || 'Unknown'} ${vehicleData.Model || 'Unknown'} ${vehicleData.Trim || ''}</h5>
          <table class="table table-sm">
            <tr>
              <th>Engine:</th>
              <td>${vehicleData.DisplacementL ? vehicleData.DisplacementL + 'L' : ''} ${vehicleData.EngineConfiguration || ''} ${vehicleData.EngineCylinders ? vehicleData.EngineCylinders + '-cyl' : ''}</td>
            </tr>
            <tr>
              <th>Transmission:</th>
              <td>${vehicleData.TransmissionStyle || 'N/A'}</td>
            </tr>
            <tr>
              <th>Drive Type:</th>
              <td>${vehicleData.DriveType || 'N/A'}</td>
            </tr>
            <tr>
              <th>Body Style:</th>
              <td>${vehicleData.BodyClass || 'N/A'}</td>
            </tr>
            <tr>
              <th>Fuel Type:</th>
              <td>${vehicleData.FuelTypePrimary || 'N/A'}</td>
            </tr>
          </table>
        </div>
      </div>
    `;
    vinData.appendChild(primaryInfoCard);

    // Create additional info card
    const additionalInfoCard = document.createElement('div');
    additionalInfoCard.className = 'col-md-6 mb-4';
    additionalInfoCard.innerHTML = `
      <div class="card h-100">
        <div class="card-header bg-secondary text-white">Additional Details</div>
        <div class="card-body">
          <table class="table table-sm">
            <tr>
              <th>VIN:</th>
              <td>${vehicleData.VIN || 'N/A'}</td>
            </tr>
            <tr>
              <th>Plant:</th>
              <td>${vehicleData.PlantCity ? vehicleData.PlantCity + ', ' + vehicleData.PlantCountry : 'N/A'}</td>
            </tr>
            <tr>
              <th>Series:</th>
              <td>${vehicleData.Series || 'N/A'}</td>
            </tr>
            <tr>
              <th>Vehicle Type:</th>
              <td>${vehicleData.VehicleType || 'N/A'}</td>
            </tr>
            <tr>
              <th>GVWR:</th>
              <td>${vehicleData.GVWR || 'N/A'}</td>
            </tr>
          </table>
          <button class="btn btn-primary mt-2" id="search-this-vehicle">
            <i class="fas fa-search me-1"></i> Search Parts for This Vehicle
          </button>
        </div>
      </div>
    `;
    vinData.appendChild(additionalInfoCard);

    // Add event listener to the "Search Parts for This Vehicle" button
    document.getElementById('search-this-vehicle').addEventListener('click', function () {
      // Populate the multi-field form with VIN data
      if (!document.getElementById('single-field-container').classList.contains('d-none')) {
        // If in single field mode, switch to multi-field
        document.getElementById('multi-field-toggle').click();
      }

      // Fill in the fields
      yearField.value = vehicleData.ModelYear || '';
      makeField.value = vehicleData.Make || '';
      modelField.value = vehicleData.Model || '';
      engineField.value = vehicleData.DisplacementL ? vehicleData.DisplacementL + 'L' : '';

      // Focus on the part field
      partField.value = '';
      partField.focus();

      // First, switch to the search tab in the main UI
      document.getElementById('search-tab').click();
      
      // We're keeping the result container visible (with the VIN tab)
      // so the user can quickly switch back to the VIN info without resubmitting
    });
  }

  // Public API
  return {
    init: init,
    decodeVin: decodeVin,
    displayVinData: displayVinData
  };
})();

// Make globally available
window.VinDecoder = VinDecoder;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
  VinDecoder.init();
});