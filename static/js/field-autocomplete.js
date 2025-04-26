/**
 * AutoXpress Field-Based Autocomplete
 * Enhanced version with separate autocomplete instances for each field
 */

// Vehicle data for autocomplete
const vehicleData = {
  "Acura": ["ILX", "MDX", "RDX", "TLX", "NSX", "RLX", "TSX", "Integra", "Legend", "Vigor", "ZDX"],
  "AMC": ["Ambassador", "AMX", "Concord", "Eagle", "Gremlin", "Hornet", "Javelin", "Marlin", "Matador", "Pacer", "Rambler", "Rebel", "Spirit"],
  "Buick": ["Cascada", "Century", "Electra", "Enclave", "Encore", "Envision", "Estate Wagon", "Invicta", "LaCrosse", "LeSabre", "Lucerne", "Park Avenue", "Rainier", "Reatta", "Regal", "Rendezvous", "Riviera", "Roadmaster", "Skylark", "Terraza", "Verano", "Wildcat"],
  "Cadillac": ["Allante", "ATS", "Brougham", "Catera", "CT4", "CT5", "CT6", "CTS", "DeVille", "DTS", "Eldorado", "Escalade", "Fleetwood", "Seville", "SRX", "STS", "XLR", "XT4", "XT5", "XT6"],
  "Chevrolet": ["Astro", "Avalanche", "Aveo", "Bel Air", "Beretta", "Blazer", "Bolt", "C10", "C20", "C30", "Camaro", "Caprice", "Cavalier", "Chevelle", "Cobalt", "Colorado", "Corsica", "Corvair", "Corvette", "Cruze", "El Camino", "Equinox", "Express", "HHR", "Impala", "K5 Blazer", "Lumina", "Malibu", "Monte Carlo", "Nova", "S-10", "Silverado", "Sonic", "Spark", "Suburban", "Tahoe", "Tracker", "Trailblazer", "Traverse", "Trax", "Uplander", "Venture", "Volt"],
  "Chevy": ["Astro", "Avalanche", "Aveo", "Bel Air", "Beretta", "Blazer", "Bolt", "C10", "C20", "C30", "Camaro", "Caprice", "Cavalier", "Chevelle", "Cobalt", "Colorado", "Corsica", "Corvair", "Corvette", "Cruze", "El Camino", "Equinox", "Express", "HHR", "Impala", "K5 Blazer", "Lumina", "Malibu", "Monte Carlo", "Nova", "S-10", "Silverado", "Sonic", "Spark", "Suburban", "Tahoe", "Tracker", "Trailblazer", "Traverse", "Trax", "Uplander", "Venture", "Volt"],
  "Chrysler": ["200", "300", "Aspen", "Cirrus", "Concorde", "Conquest", "Cordoba", "Crossfire", "E-Class", "Fifth Avenue", "Imperial", "LHS", "New Yorker", "Pacifica", "Prowler", "PT Cruiser", "Sebring", "Town & Country", "Voyager"],
  "Dodge": ["Avenger", "Caliber", "Caravan", "Challenger", "Charger", "Colt", "Coronet", "Dakota", "Dart", "Daytona", "Diplomat", "Durango", "Dynasty", "Grand Caravan", "Intrepid", "Journey", "Magnum", "Monaco", "Neon", "Nitro", "Omni", "Polara", "Ram", "Ram Van", "Ramcharger", "Shadow", "Spirit", "Sprinter", "Stealth", "Stratus", "Viper"],
  "Eagle": ["Premier", "Summit", "Talon", "Vision"],
  "Ford": ["Aerostar", "Aspire", "Bronco", "Bronco II", "Bronco Sport", "C-Max", "Contour", "Crown Victoria", "E-Series", "E-150", "E-250", "E-350", "EcoSport", "Edge", "Escape", "Escort", "Excursion", "Expedition", "Explorer", "Explorer Sport Trac", "F-150", "F-250", "F-350", "F-450", "F-550", "Fairlane", "Fairmont", "Falcon", "Festiva", "Fiesta", "Five Hundred", "Flex", "Focus", "Freestar", "Freestyle", "Fusion", "Galaxie", "Gran Torino", "GT", "LTD", "Maverick", "Model A", "Model T", "Mustang", "Mustang Mach-E", "Pinto", "Probe", "Ranger", "Taurus", "Tempo", "Thunderbird", "Torino", "Transit", "Transit Connect", "Windstar"],
  "Geo": ["Metro", "Prizm", "Storm", "Tracker"],
  "GMC": ["Acadia", "Canyon", "Envoy", "Jimmy", "Safari", "Savana", "Sierra", "Sonoma", "Suburban", "Terrain", "Vandura", "Yukon"],
  "Honda": ["Accord", "Civic", "Clarity", "CR-V", "CR-Z", "Crosstour", "Del Sol", "Element", "Fit", "HR-V", "Insight", "Odyssey", "Passport", "Pilot", "Prelude", "Ridgeline", "S2000"],
  "Hummer": ["H1", "H2", "H3"],
  "Hyundai": ["Accent", "Azera", "Elantra", "Entourage", "Equus", "Genesis", "Ioniq", "Kona", "Nexo", "Palisade", "Santa Fe", "Sonata", "Tiburon", "Tucson", "Veloster", "Venue", "Veracruz", "XG300", "XG350"],
  "Infiniti": ["EX35", "FX35", "FX45", "G20", "G35", "G37", "I30", "I35", "J30", "M30", "M35", "M45", "Q45", "Q50", "Q60", "Q70", "QX4", "QX30", "QX50", "QX55", "QX60", "QX70", "QX80"],
  "Isuzu": ["Amigo", "Ascender", "Axiom", "Hombre", "I-Mark", "Impulse", "Oasis", "Pickup", "Rodeo", "Stylus", "Trooper", "VehiCROSS"],
  "Jeep": ["Cherokee", "CJ", "Commander", "Compass", "Gladiator", "Grand Cherokee", "Liberty", "Patriot", "Renegade", "Wagoner", "Wagoneer", "Wrangler"],
  "Kia": ["Amanti", "Borrego", "Cadenza", "Carnival", "EV6", "Forte", "K5", "K900", "Niro", "Optima", "Rio", "Rondo", "Sedona", "Seltos", "Sephia", "Sorento", "Soul", "Spectra", "Sportage", "Stinger", "Telluride"],
  "Lexus": ["CT", "ES", "GS", "GX", "IS", "LC", "LFA", "LS", "LX", "NX", "RC", "RX", "SC", "UX"],
  "Lincoln": ["Aviator", "Blackwood", "Continental", "Corsair", "LS", "Mark LT", "Mark Series", "MKC", "MKS", "MKT", "MKX", "MKZ", "Navigator", "Nautilus", "Town Car", "Zephyr"],
  "Mazda": ["2", "3", "323", "5", "6", "626", "929", "B-Series", "CX-3", "CX-30", "CX-5", "CX-7", "CX-9", "Mazda2", "Mazda3", "Mazda5", "Mazda6", "Miata", "Millenia", "MPV", "MX-3", "MX-5", "MX-5 Miata", "MX-6", "Navajo", "Protege", "RX-7", "RX-8", "Tribute"],
  "Mercury": ["Bobcat", "Capri", "Colony Park", "Comet", "Cougar", "Grand Marquis", "Lynx", "Marauder", "Mariner", "Marquis", "Milan", "Montego", "Monterey", "Mountaineer", "Mystique", "Sable", "Topaz", "Tracer", "Villager", "Zephyr"],
  "Mitsubishi": ["3000GT", "Diamante", "Eclipse", "Eclipse Cross", "Endeavor", "Expo", "Galant", "i-MiEV", "Lancer", "Mirage", "Montero", "Montero Sport", "Outlander", "Outlander Sport", "Raider", "Sigma", "Starion"],
  "Nissan": ["200SX", "240SX", "300ZX", "350Z", "370Z", "Altima", "Armada", "Cube", "Frontier", "GT-R", "Juke", "Leaf", "Maxima", "Murano", "NV", "Pathfinder", "Patrol", "Pulsar", "Quest", "Rogue", "Sentra", "Skyline", "Stanza", "Titan", "Versa", "Xterra", "Z"],
  "Oldsmobile": ["98", "Achieva", "Alero", "Aurora", "Bravada", "Calais", "Cutlass", "Cutlass Ciera", "Cutlass Supreme", "Delta 88", "Eighty-Eight", "Firenza", "Intrigue", "Ninety-Eight", "Omega", "Regency", "Silhouette", "Starfire", "Toronado"],
  "Plymouth": ["Acclaim", "Barracuda", "Breeze", "Colt", "Conquest", "Fury", "Grand Voyager", "Horizon", "Laser", "Neon", "Prowler", "Reliant", "Roadrunner", "Satellite", "Sundance", "Valiant", "Volare", "Voyager"],
  "Pontiac": ["Aztek", "Bonneville", "Catalina", "Fiero", "Firebird", "G3", "G5", "G6", "G8", "Grand Am", "Grand Prix", "GTO", "LeMans", "Montana", "Parisienne", "Phoenix", "Solstice", "Sunbird", "Sunfire", "Torrent", "Trans Am", "Trans Sport", "Vibe"],
  "Ram": ["1500", "2500", "3500", "4500", "5500", "Cargo Van", "Dakota", "ProMaster", "ProMaster City"],
  "Saturn": ["Astra", "Aura", "Ion", "L-Series", "Outlook", "Relay", "S-Series", "Sky", "Vue"],
  "Scion": ["FR-S", "iA", "iM", "iQ", "tC", "xB", "xD"],
  "Studebaker": ["Avanti", "Champion", "Commander", "Daytona", "Gran Turismo Hawk", "Hawk", "Lark", "President", "Wagonaire"],
  "Subaru": ["Ascent", "Baja", "BRZ", "Crosstrek", "Forester", "Impreza", "Legacy", "Outback", "SVX", "Tribeca", "WRX", "XT", "XV"],
  "Tesla": ["Model 3", "Model S", "Model X", "Model Y", "Roadster", "Cybertruck"],
  "Toyota": ["4Runner", "86", "Avalon", "C-HR", "Camry", "Celica", "Corolla", "Corona", "Cressida", "Echo", "FJ Cruiser", "GR86", "Highlander", "Land Cruiser", "Matrix", "Mirai", "MR2", "Paseo", "Previa", "Prius", "RAV4", "Sequoia", "Sienna", "Supra", "T100", "Tacoma", "Tercel", "Tundra", "Venza", "Yaris"],
  "Volkswagen": ["Arteon", "Atlas", "Beetle", "Cabrio", "Cabriolet", "CC", "Corrado", "Eos", "Eurovan", "Fox", "Golf", "GTI", "ID.4", "Jetta", "Karmann Ghia", "New Beetle", "Passat", "Phaeton", "Rabbit", "Routan", "Scirocco", "Taos", "Tiguan", "Touareg", "Type 2"]
};

// Generate years for autocomplete (1950 to current year)
const generateYears = () => {
  const years = [];
  const currentYear = new Date().getFullYear();
  for (let year = 1950; year <= currentYear + 1; year++) {
    years.push(year.toString());
  }
  return years;
};

// Get all makes as an array
const makes = Object.keys(vehicleData);

// Make synonyms for normalization
const makeSynonyms = {
  "chevy": "Chevrolet",
  "vw": "Volkswagen",
  "mercedes": "Mercedes-Benz"
};

// Class definition for field-based autocomplete
class FieldAutocomplete {
  constructor(options) {
    this.options = Object.assign({
      fieldId: null,
      suggestionsContainerId: null,
      dataSource: [],
      minChars: 1,
      maxSuggestions: 10,
      filterFunction: null,
      dependsOn: null,
      dependencyFunction: null,
      onSelect: null,
      hideOnComplete: false
    }, options);
    
    this.field = document.getElementById(this.options.fieldId);
    this.suggestionsContainer = document.getElementById(this.options.suggestionsContainerId);
    
    if (!this.field || !this.suggestionsContainer) {
      console.error(`FieldAutocomplete: Could not find field or suggestions container for ${this.options.fieldId}`);
      return;
    }
    
    this.selectedIndex = -1;
    this.suggestions = [];
    this.visible = false;
    
    // Initialize
    this.init();
  }
  
  init() {
    // Set up input event listener
    this.field.addEventListener('input', () => this.onInput());
    
    // Set up keyboard navigation
    this.field.addEventListener('keydown', (e) => this.onKeyDown(e));
    
    // Show suggestions on focus if field has a dependency
    this.field.addEventListener('focus', () => {
      if (this.options.dependsOn && this.field.value.trim().length === 0) {
        const dependencyField = document.getElementById(this.options.dependsOn);
        if (dependencyField && dependencyField.value.trim().length > 0) {
          // Generate suggestions based on the dependency
          this.generateSuggestions('');
        }
      }
    });
    
    // Close suggestions when clicking outside
    document.addEventListener('click', (e) => {
      if (!this.suggestionsContainer.contains(e.target) && e.target !== this.field) {
        this.hideSuggestions();
      }
    });
    
    // Set initial styling for suggestions container
    this.styleContainer();
  }
  
  styleContainer() {
    this.suggestionsContainer.style.position = 'absolute';
    this.suggestionsContainer.style.width = `${this.field.offsetWidth}px`;
    this.suggestionsContainer.style.zIndex = '1000';
    this.suggestionsContainer.style.backgroundColor = 'white';
    this.suggestionsContainer.style.border = '1px solid #ddd';
    this.suggestionsContainer.style.borderRadius = '0 0 4px 4px';
    this.suggestionsContainer.style.boxShadow = '0 4px 8px rgba(0,0,0,0.1)';
    this.suggestionsContainer.style.maxHeight = '300px';
    this.suggestionsContainer.style.overflowY = 'auto';
    this.suggestionsContainer.style.display = 'none';
    
    // Position under the input field
    this.updateContainerPosition();
    
    // Add resize listener to update position when window is resized
    window.addEventListener('resize', () => this.updateContainerPosition());
  }
  
  updateContainerPosition() {
    if (!this.field) return;
    
    try {
        const fieldRect = this.field.getBoundingClientRect();
        const formGroup = this.field.closest('.form-group');
        
        if (formGroup) {
            // Position relative to the form group containing the field
            const formRect = formGroup.getBoundingClientRect();
            
            // Set width to match the input field
            this.suggestionsContainer.style.width = `${this.field.offsetWidth}px`;
            
            // Set the top position to be directly below the input field
            this.suggestionsContainer.style.top = `${fieldRect.height}px`;
            this.suggestionsContainer.style.left = '0';
            
            // Make sure the suggestions container is positioned relative to its parent
            this.suggestionsContainer.style.position = 'absolute';
            
            console.log(`Positioned dropdown for ${this.options.fieldId} relative to form group`);
        } else {
            // Fallback to absolute positioning relative to document
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;
            
            this.suggestionsContainer.style.top = `${fieldRect.bottom + scrollTop}px`;
            this.suggestionsContainer.style.left = `${fieldRect.left + scrollLeft}px`;
            this.suggestionsContainer.style.position = 'absolute';
            
            console.log(`Positioned dropdown for ${this.options.fieldId} using absolute positioning`);
        }
    } catch (error) {
        console.error("Error positioning dropdown:", error);
    }
  }
  
  onInput() {
    const query = this.field.value.trim();
    
    // For model field with dependency on make, always show suggestions
    // as long as the make field has a value
    if (this.options.fieldId === 'model-field' && this.options.dependsOn === 'make-field') {
      const makeField = document.getElementById('make-field');
      if (makeField && makeField.value.trim().length > 0) {
        this.generateSuggestions(query);
        return;
      }
    }
    
    // Hide suggestions if query is too short
    if (query.length < this.options.minChars) {
      this.hideSuggestions();
      return;
    }
    
    // Check if we should hide suggestions for complete inputs
    if (this.options.hideOnComplete && this.isCompleteInput(query)) {
      this.hideSuggestions();
      return;
    }
    
    // Generate suggestions
    this.generateSuggestions(query);
  }
  
  isCompleteInput(query) {
    // For year field: consider complete if it's a 4-digit year
    if (this.options.fieldId === 'year-field') {
      return /^(19|20)\d{2}$/.test(query);
    }
    return false;
  }
  
  onKeyDown(e) {
    if (!this.visible) return;
    
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        this.selectedIndex = Math.min(this.selectedIndex + 1, this.suggestions.length - 1);
        this.updateSelectedSuggestion();
        break;
        
      case 'ArrowUp':
        e.preventDefault();
        this.selectedIndex = Math.max(this.selectedIndex - 1, -1);
        this.updateSelectedSuggestion();
        break;
        
      case 'Enter':
        if (this.selectedIndex >= 0) {
          e.preventDefault();
          this.selectSuggestion(this.suggestions[this.selectedIndex]);
        }
        break;
        
      case 'Escape':
        this.hideSuggestions();
        break;
        
      case 'Tab':
        // Allow normal tab behavior but close suggestions
        this.hideSuggestions();
        break;
    }
  }
  
  generateSuggestions(query) {
    // Get dependency value if this field depends on another field
    let dependencyValue = null;
    if (this.options.dependsOn) {
      const dependencyField = document.getElementById(this.options.dependsOn);
      if (dependencyField) {
        dependencyValue = dependencyField.value.trim();
        
        // If dependency field is empty and it's required, show no suggestions
        if (!dependencyValue && this.options.requireDependency) {
          this.suggestions = [];
          this.displaySuggestions();
          return;
        }
      }
    }
    
    // Filter data source based on query
    let filteredSuggestions;
    
    if (typeof this.options.dataSource === 'function') {
      // If dataSource is a function, call it with the query and dependency value
      filteredSuggestions = this.options.dataSource(query, dependencyValue);
    } else if (Array.isArray(this.options.dataSource)) {
      // If dataSource is an array, filter it based on the query
      filteredSuggestions = this.options.dataSource.filter(item => {
        if (typeof this.options.filterFunction === 'function') {
          return this.options.filterFunction(item, query, dependencyValue);
        }
        
        // Default filtering: case-insensitive substring match
        return item.toString().toLowerCase().includes(query.toLowerCase());
      });
    } else if (typeof this.options.dataSource === 'object') {
      // If dataSource is an object and we have a dependency value, use it as a key
      if (dependencyValue && this.options.dataSource[dependencyValue]) {
        filteredSuggestions = this.options.dataSource[dependencyValue].filter(item => {
          if (typeof this.options.filterFunction === 'function') {
            return this.options.filterFunction(item, query, dependencyValue);
          }
          return item.toString().toLowerCase().includes(query.toLowerCase());
        });
      } else {
        // If no dependency or invalid dependency, show no suggestions
        filteredSuggestions = [];
      }
    } else {
      // Invalid data source
      filteredSuggestions = [];
    }
    
    // Apply additional filtering through dependencyFunction if provided
    if (this.options.dependencyFunction && dependencyValue) {
      filteredSuggestions = this.options.dependencyFunction(filteredSuggestions, dependencyValue);
    }
    
    // Limit number of suggestions
    this.suggestions = filteredSuggestions.slice(0, this.options.maxSuggestions);
    
    // Display suggestions
    this.displaySuggestions();
  }
  
  displaySuggestions() {
    console.log(`Displaying suggestions for ${this.options.fieldId}:`, this.suggestions);
    this.suggestionsContainer.innerHTML = '';
    
    if (this.suggestions.length === 0) {
      this.hideSuggestions();
      return;
    }
    
    // Make sure the container is positioned correctly
    this.updateContainerPosition();
    
    // Create suggestion elements
    this.suggestions.forEach((suggestion, index) => {
      const item = document.createElement('div');
      item.className = 'autocomplete-item';
      item.style.padding = '10px 15px';
      item.style.cursor = 'pointer';
      item.style.transition = 'background-color 0.2s';
      
      // Highlight matching text
      const query = this.field.value.trim().toLowerCase();
      const suggestionText = suggestion.toString();
      const suggestionLower = suggestionText.toLowerCase();
      
      if (query && suggestionLower.includes(query)) {
        const startIndex = suggestionLower.indexOf(query);
        const beforeMatch = suggestionText.substring(0, startIndex);
        const match = suggestionText.substring(startIndex, startIndex + query.length);
        const afterMatch = suggestionText.substring(startIndex + query.length);
        
        item.innerHTML = `${beforeMatch}<strong>${match}</strong>${afterMatch}`;
      } else {
        item.textContent = suggestionText;
      }
      
      // Add event listeners
      item.addEventListener('click', () => this.selectSuggestion(suggestion));
      item.addEventListener('mouseover', () => {
        this.selectedIndex = index;
        this.updateSelectedSuggestion();
      });
      
      this.suggestionsContainer.appendChild(item);
    });
    
    // Show suggestions container
    this.suggestionsContainer.style.display = 'block';
    this.visible = true;
  }
  
  updateSelectedSuggestion() {
    const items = this.suggestionsContainer.querySelectorAll('.autocomplete-item');
    
    items.forEach((item, index) => {
      if (index === this.selectedIndex) {
        item.style.backgroundColor = '#f0f0f0';
      } else {
        item.style.backgroundColor = '';
      }
    });
  }
  
  selectSuggestion(suggestion) {
    this.field.value = suggestion.toString();
    this.hideSuggestions();
    
    // Call onSelect callback if provided
    if (typeof this.options.onSelect === 'function') {
      this.options.onSelect(suggestion);
    }
    
    // Focus the next field if specified
    if (this.options.nextField) {
      const nextField = document.getElementById(this.options.nextField);
      if (nextField) {
        nextField.focus();
      }
    }
  }
  
  hideSuggestions() {
    this.suggestionsContainer.style.display = 'none';
    this.suggestionsContainer.innerHTML = '';
    this.selectedIndex = -1;
    this.visible = false;
  }
  
  updateDataSource(newDataSource) {
    this.options.dataSource = newDataSource;
  }
}

// Initialize all field autocompletions on document ready
document.addEventListener('DOMContentLoaded', function() {
  // Get the years array
  const years = generateYears();
  
  // Set up year field autocomplete
  const yearAutocomplete = new FieldAutocomplete({
    fieldId: 'year-field',
    suggestionsContainerId: 'year-suggestions',
    dataSource: (query) => {
      // Only show suggestions for partial years
      if (query.length === 4 && /^(19|20)\d{2}$/.test(query)) {
        return [];
      }
      
      return years.filter(year => 
        year.startsWith(query)
      ).slice(0, 10); // Limit to 10 suggestions
    },
    minChars: 1,
    maxSuggestions: 10,
    hideOnComplete: true,
    nextField: 'make-field',
    onSelect: (year) => {
      // After selecting a year, focus on make field
      document.getElementById('make-field').focus();
    }
  });
  
  // Set up make field autocomplete
  const makeAutocomplete = new FieldAutocomplete({
    fieldId: 'make-field',
    suggestionsContainerId: 'make-suggestions',
    dataSource: makes,
    filterFunction: (make, query) => {
      // Case-insensitive starts with or includes
      const makeLower = make.toLowerCase();
      const queryLower = query.toLowerCase();
      
      // Prioritize exact matches and starts with
      return makeLower.startsWith(queryLower) || makeLower.includes(queryLower);
    },
    minChars: 1,
    maxSuggestions: 10,
    nextField: 'model-field',
    onSelect: (make) => {
      // After selecting a make, focus on model field and update model autocomplete
      const modelField = document.getElementById('model-field');
      modelField.value = ''; // Clear the model field
      modelField.focus();
      
      // Normalize the make
      const normalizedMake = makeSynonyms[make.toLowerCase()] || make;
      
      // Get and log the available models for this make
      const models = vehicleData[normalizedMake] || [];
      console.log("Make selected:", normalizedMake);
      console.log("Models available:", models);
      
      // Force trigger focus and input events to show the models dropdown immediately
      modelField.focus();
      const focusEvent = new Event('focus', { bubbles: true });
      modelField.dispatchEvent(focusEvent);
      
      const inputEvent = new Event('input', { bubbles: true });
      modelField.dispatchEvent(inputEvent);
  }
  });
  
  // Set up model field autocomplete (dependent on make)
  const modelAutocomplete = new FieldAutocomplete({
    fieldId: 'model-field',
    suggestionsContainerId: 'model-suggestions',
    dataSource: vehicleData, // The entire vehicle data object
    dependsOn: 'make-field',
    requireDependency: true, // Require a make to be selected
    filterFunction: (model, query, make) => {
      // If make is empty, don't show any suggestions
      if (!make) return false;
      
      // First normalize the make (handle synonyms)
      const normalizedMake = makeSynonyms[make.toLowerCase()] || make;
      
      // Check if this model belongs to the current make and matches the query
      return model.toLowerCase().includes(query.toLowerCase());
    },
    dependencyFunction: (suggestions, make) => {
      // If make is empty, return empty array
      if (!make) return [];
      
      // Convert make to proper case for lookup
      const normalizedMake = makeSynonyms[make.toLowerCase()] || make;
      
      // Get models for this make
      const models = vehicleData[normalizedMake] || [];
      console.log("Models for", normalizedMake, ":", models);
      return models;
  },
    minChars: 1,
    maxSuggestions: 10,
    nextField: 'part-field',
    onSelect: (model) => {
      // After selecting a model, focus on part field
      document.getElementById('part-field').focus();
    }
  });
  
  // Handle tab navigation between fields
  const fields = ['year-field', 'make-field', 'model-field', 'part-field', 'engine-field'];
  
  fields.forEach((fieldId, index) => {
    const field = document.getElementById(fieldId);
    if (!field) return;
    
    field.addEventListener('keydown', (e) => {
      if (e.key === 'Tab' && !e.shiftKey) {
        // Tab to next field
        if (index < fields.length - 1) {
          setTimeout(() => {
            const nextField = document.getElementById(fields[index + 1]);
            if (nextField) nextField.focus();
          }, 10);
        }
      } else if (e.key === 'Tab' && e.shiftKey) {
        // Shift+Tab to previous field
        if (index > 0) {
          setTimeout(() => {
            const prevField = document.getElementById(fields[index - 1]);
            if (prevField) prevField.focus();
          }, 10);
        }
      }
    });
  });
  
  // Enable toggling between single-field and multi-field search
  const singleFieldToggle = document.getElementById('single-field-toggle');
  const multiFieldToggle = document.getElementById('multi-field-toggle');
  const singleFieldContainer = document.getElementById('single-field-container');
  const multiFieldContainer = document.querySelector('.multi-field-search').closest('.mb-3');
  
  if (singleFieldToggle && multiFieldToggle && singleFieldContainer && multiFieldContainer) {
    singleFieldToggle.addEventListener('click', () => {
      multiFieldContainer.classList.add('d-none');
      singleFieldContainer.classList.remove('d-none');
      document.getElementById('prompt').focus();
    });
    
    multiFieldToggle.addEventListener('click', () => {
      singleFieldContainer.classList.add('d-none');
      multiFieldContainer.classList.remove('d-none');
      document.getElementById('year-field').focus();
    });
  }
});