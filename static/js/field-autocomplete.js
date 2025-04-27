/**
 * AutoXpress Enhanced Field-Based Autocomplete
 * Inspired by the single-field autoxpress.js implementation
 */

// Vehicle data for autocomplete - using the updated inventory
const vehicleData = {
  "Acura": ["ILX", "MDX", "RDX", "TLX", "NSX", "RLX", "TSX", "Integra", "ZDX", "TL", "RL", "CSX", "RSX", "Legend", "Vigor"],
  
  "Alfa Romeo": ["Giulia", "Stelvio", "4C", "Spider", "Giulietta", "164", "GTV", "MiTo"],
  
  "Aston Martin": ["DB11", "Vantage", "DBS", "DBX", "DB9", "Rapide", "Vanquish", "DB7", "Virage", "Lagonda", "DB5", "DB4"],
  
  "Audi": ["A3", "A4", "A5", "A6", "A7", "A8", "Q3", "Q5", "Q7", "Q8", "e-tron", "TT", "R8", "S3", "S4", "S5", "S6", "S7", "S8", "RS3", "RS5", "RS7", "SQ5", "SQ7", "SQ8", "A4 Allroad", "A6 Allroad", "Allroad", "A3 Sportback", "80", "90", "100", "200", "V8", "Cabriolet", "Coupe Quattro"],
  
  "Bentley": ["Continental", "Bentayga", "Flying Spur", "Azure", "Arnage", "Brooklands", "Mulsanne"],
  
  "BMW": ["3-Series", "5-Series", "7-Series", "X1", "X3", "X5", "X7", "M3", "M5", "Z4", "i4", "i7", "iX", "M8", "X3M", "X5M", "330i", "530i", "740i", "X3 xDrive30i", "X5 xDrive40i", "335i", "328i", "325i", "540i", "535i", "M340i", "M550i", "Z3", "8-Series", "6-Series", "4-Series", "2-Series", "1-Series", "X2", "X4", "X6", "i3", "i8", "M2", "M4", "M6", "M235i", "M240i", "X4M", "X6M", "320i", "340i", "550i", "750i", "840i", "M440i", "iX3", "i5", "i8 Roadster", "Z8", "M Roadster", "M Coupe", "X5 M Competition", "M3 Competition", "M5 Competition", "M4 Competition", "iX M60", "i7 M70"],
  
  "Buick": ["Enclave", "Encore", "Envision", "LaCrosse", "Regal", "Verano", "Cascada", "LeSabre", "Century", "Skylark", "Park Avenue", "Riviera", "Roadmaster", "Electra", "Rainier", "Rendezvous", "Terraza", "Lucerne"],
  
  "Cadillac": ["CT4", "CT5", "CT6", "XT4", "XT5", "XT6", "Escalade", "ATS", "CTS", "XTS", "SRX", "STS", "DTS", "Eldorado", "Seville", "DeVille", "Fleetwood", "Allante", "Brougham", "Catera"],
  
  "Chevrolet": ["Silverado", "Camaro", "Corvette", "Malibu", "Equinox", "Tahoe", "Suburban", "Colorado", "Traverse", "Blazer", "Impala", "Spark", "Trax", "Bolt", "Trailblazer", "Cavalier", "Cobalt", "Cruze", "Sonic", "Aveo", "S10", "Monte Carlo", "Nova", "El Camino", "Chevelle", "Caprice", "Bel Air", "Avalanche", "Astro", "Express", "SSR", "HHR", "Silverado HD", "Volt", "Bolt EUV", "Corvette Z06", "Corvette ZR1", "Silverado 1500", "Silverado 2500", "Silverado 3500", "Lumina", "Beretta", "Prizm", "Tracker", "Uplander", "Venture", "Camaro SS", "Camaro ZL1", "Corvette Stingray", "Corvette Grand Sport"],
  
  "Chrysler": ["300", "Pacifica", "Voyager", "Town & Country", "PT Cruiser", "Sebring", "200", "Concorde", "Crossfire", "Aspen", "Cirrus", "Imperial", "LHS", "New Yorker", "Fifth Avenue", "Cordoba", "Newport", "LeBaron"],
  
  "Dodge": ["Charger", "Challenger", "Durango", "Journey", "Grand Caravan", "Ram", "Viper", "Neon", "Avenger", "Dart", "Nitro", "Caliber", "Intrepid", "Stealth", "Magnum", "Stratus", "Shadow", "Dynasty", "Spirit", "Colt", "Daytona", "Caravan", "Omni"],
  
  "Ferrari": ["F8", "Roma", "Portofino", "SF90", "812", "488", "458", "F12", "California", "LaFerrari", "Enzo", "F430", "360", "550", "355", "348", "Testarossa", "F40", "F50"],
  
  "Fiat": ["500", "500X", "500L", "124 Spider", "500e", "500 Abarth", "500c"],
  
  "Ford": ["F-150", "Mustang", "Explorer", "Escape", "Edge", "Ranger", "Bronco", "Expedition", "Focus", "Fusion", "Taurus", "EcoSport", "Maverick", "F-250", "F-350", "Fiesta", "Crown Victoria", "Flex", "Transit", "Five Hundred", "Freestyle", "Excursion", "E-Series", "E-150", "E-250", "E-350", "Thunderbird", "Probe", "Contour", "Tempo", "Escort", "GT", "Model A", "Model T", "Fairlane", "Falcon", "Galaxie", "Bronco Sport", "F-450", "F-550", "Explorer Sport Trac", "Transit Connect", "Windstar", "Aerostar", "Aspire", "Festiva", "Mustang Mach-E", "Lightning", "Super Duty", "Shelby GT500", "Shelby GT350"],
  
  "Genesis": ["G70", "G80", "G90", "GV70", "GV80", "GV60"],
  
  "GMC": ["Sierra", "Yukon", "Acadia", "Terrain", "Canyon", "Savana", "Hummer EV", "Jimmy", "Envoy", "Sonoma", "Safari", "Syclone", "Typhoon", "Suburban", "Sprint", "Rally", "Vandura", "S15"],
  
  "Honda": ["Accord", "Civic", "CR-V", "Pilot", "Odyssey", "Ridgeline", "HR-V", "Passport", "Fit", "Clarity", "Insight", "Element", "S2000", "Crosstour", "Prelude", "CR-Z", "Del Sol", "Accord Hybrid", "Accord Crosstour", "Civic Type R", "Civic Si", "CR-V Hybrid", "Prologue", "Pilot TrailSport", "Civic Hatchback", "Civic Coupe", "Accord Coupe", "e", "EV Plus", "FCX Clarity"],
  
  "Hyundai": ["Elantra", "Sonata", "Tucson", "Santa Fe", "Kona", "Palisade", "Veloster", "Venue", "Ioniq", "Santa Cruz", "Accent", "Veracruz", "Azera", "Equus", "Genesis", "Entourage", "Tiburon", "Excel"],
  
  "Infiniti": ["Q50", "Q60", "QX50", "QX55", "QX60", "QX80", "G35", "G37", "FX35", "FX45", "M35", "M45", "EX35", "JX35", "QX4", "QX56", "Q40", "Q45", "Q70"],
  
  "Jaguar": ["F-Pace", "E-Pace", "I-Pace", "XF", "XE", "F-Type", "XJ", "XK", "S-Type", "X-Type", "XJS", "X300", "X308", "Mark 2", "XKR", "XFR", "XJR"],
  
  "Jeep": ["Wrangler", "Grand Cherokee", "Cherokee", "Compass", "Renegade", "Gladiator", "Wagoneer", "Grand Wagoneer", "Liberty", "Patriot", "Commander", "CJ", "Scrambler", "Comanche"],
  
  "Kia": ["Forte", "Optima", "K5", "Sorento", "Sportage", "Telluride", "Soul", "Stinger", "Carnival", "Rio", "Seltos", "Niro", "Cadenza", "EV6", "Amanti", "Borrego", "Rondo", "Sedona", "Spectra"],
  
  "Lamborghini": ["Huracan", "Aventador", "Urus", "Gallardo", "Murcielago", "Countach", "Diablo", "Reventon", "Veneno", "Centenario", "Sesto Elemento"],
  
  "Land Rover": ["Range Rover", "Discovery", "Defender", "Range Rover Sport", "Range Rover Evoque", "Range Rover Velar", "Discovery Sport", "LR3", "LR4", "LR2", "Freelander"],
  
  "Lexus": ["ES", "IS", "GS", "LS", "RC", "LC", "NX", "RX", "GX", "LX", "UX", "ES350", "ES300h", "IS300", "IS350", "GS350", "LS500", "NX300", "RX350", "GX460", "LX570", "UX250h", "RCF", "LC500", "RX450h", "IS500"],
  
  "Lincoln": ["Navigator", "Aviator", "Corsair", "Nautilus", "MKZ", "Continental", "MKC", "MKX", "MKT", "MKS", "Town Car", "LS", "Blackwood", "Mark LT", "Mark VIII", "Mark VII", "Mark VI", "Mark V", "Mark IV", "Zephyr"],
  
  "Lotus": ["Evora", "Elise", "Exige", "Emira", "Esprit", "Elan", "Europa", "Eletre"],
  
  "Maserati": ["Ghibli", "Levante", "Quattroporte", "MC20", "GranTurismo", "GranCabrio", "Spyder", "Coupe", "Bora", "Merak", "Biturbo"],
  
  "Mazda": ["Mazda3", "Mazda6", "CX-5", "CX-9", "CX-30", "MX-5 Miata", "CX-3", "CX-50", "RX-7", "RX-8", "MPV", "Tribute", "CX-7", "Protege", "Millenia", "Navajo", "B-Series", "B2300", "B4000"],
  
  "McLaren": ["720S", "765LT", "570S", "GT", "Artura", "Senna", "P1", "MP4-12C", "Elva"],
  
  "Mercedes-Benz": ["C-Class", "E-Class", "S-Class", "A-Class", "GLC", "GLE", "GLS", "G-Class", "CLA", "CLS", "SL", "SLK", "AMG GT", "EQS", "EQE", "C300", "E350", "S500", "GLC300", "GLE350", "GLE450", "G550", "C43 AMG", "E63 AMG", "S63 AMG", "C63 AMG", "GLC43 AMG", "ML350", "ML550", "GL450", "GL550", "GLA", "GLB", "SLC", "CLK", "Sprinter", "Metris"],
  
  "MINI": ["Cooper", "Countryman", "Clubman", "Paceman", "Coupe", "Roadster", "Cooper S", "John Cooper Works", "Cooper SE", "Hardtop", "Convertible"],
  
  "Mitsubishi": ["Outlander", "Eclipse Cross", "Mirage", "Outlander Sport", "Lancer", "Galant", "Eclipse", "Endeavor", "Diamante", "3000GT", "Montero", "Raider", "Expo", "Precis", "Mighty Max"],
  
  "Nissan": ["Altima", "Sentra", "Maxima", "Rogue", "Pathfinder", "Murano", "Armada", "Frontier", "Titan", "Kicks", "Versa", "Juke", "Leaf", "Z", "370Z", "350Z", "240SX", "GT-R", "Cube", "Xterra", "Quest"],
  
  "Porsche": ["911", "Cayenne", "Macan", "Panamera", "Taycan", "Boxster", "Cayman", "928", "944", "968", "914", "356", "912", "718"],
  
  "Ram": ["1500", "2500", "3500", "ProMaster", "ProMaster City", "Dakota"],
  
  "Rolls-Royce": ["Phantom", "Ghost", "Wraith", "Dawn", "Cullinan", "Silver Shadow", "Silver Spur", "Corniche", "Camargue", "Silver Seraph"],
  
  "Subaru": ["Outback", "Forester", "Crosstrek", "Impreza", "Legacy", "Ascent", "WRX", "BRZ", "STI", "WRX STI", "Baja", "Tribeca", "SVX", "Justy", "Loyale", "Sambar"],
  
  "Tesla": ["Model 3", "Model S", "Model X", "Model Y", "Cybertruck", "Roadster"],
  
  "Toyota": ["Camry", "Corolla", "RAV4", "Tacoma", "Highlander", "4Runner", "Prius", "Tundra", "Sienna", "Avalon", "Sequoia", "Venza", "C-HR", "Land Cruiser", "FJ Cruiser", "86", "GR86", "Supra", "Mirai", "Matrix", "Yaris", "Echo", "Celica", "Crown", "Corolla Cross", "bZ4X", "GR Corolla", "Camry Solara", "Cressida", "Tercel", "Paseo", "T100", "Previa"],
  
  "Volkswagen": ["Jetta", "Passat", "Tiguan", "Atlas", "Golf", "ID.4", "Taos", "Arteon", "GTI", "Beetle", "Touareg", "Rabbit", "CC", "Eos", "GLI", "R32", "Golf R", "Corrado", "Scirocco", "Thing", "Karmann Ghia", "Type 1", "Type 2", "Type 3", "Vanagon", "New Beetle", "Cabrio", "Phaeton", "Routan"],
  
  "Volvo": ["XC90", "XC60", "XC40", "S60", "S90", "V60", "V90", "C40", "C30", "S40", "S80", "V40", "V50", "V70", "850", "740", "940", "960", "240", "Amazon", "P1800", "PV444", "PV544", "C70"] 
};

// Generate years for autocomplete (1980 to current year + 1)
const generateYears = () => {
  const years = [];
  const currentYear = new Date().getFullYear();
  for (let year = 1980; year <= currentYear + 1; year++) {
    years.push(year.toString());
  }
  return years;
};

// Make synonyms for normalization
const makeSynonyms = {
  "chevy": "Chevrolet",
  "vw": "Volkswagen",
  "mercedes": "Mercedes-Benz",
  "benz": "Mercedes-Benz"
};

// Class definition for enhanced field-based autocomplete
class EnhancedFieldAutocomplete {
  constructor(options) {
    this.options = Object.assign({
      fieldId: null,
      suggestionsContainerId: null,
      dataSource: [],
      dataType: 'generic', // 'year', 'make', 'model', or 'generic'
      minChars: 1,
      maxSuggestions: 15,
      dependsOn: null,
      dependencyField: null, // Will store the reference to the dependency field
      onSelect: null,
      nextField: null,
      highlightMatches: true
    }, options);
    
    this.field = document.getElementById(this.options.fieldId);
    this.suggestionsContainer = document.getElementById(this.options.suggestionsContainerId);
    
    if (!this.field || !this.suggestionsContainer) {
      console.error(`EnhancedFieldAutocomplete: Could not find field or suggestions container for ${this.options.fieldId}`);
      return;
    }
    
    // If this field depends on another, get a reference to the dependency field
    if (this.options.dependsOn) {
      this.options.dependencyField = document.getElementById(this.options.dependsOn);
    }
    
    this.selectedIndex = -1;
    this.suggestions = [];
    this.categorizedSuggestions = {}; // For organizing suggestions by type
    this.visible = false;
    
    // Initialize
    this.init();
  }
  
  init() {
    // Set up event listeners
    this.field.addEventListener('input', () => this.onInput());
    this.field.addEventListener('keydown', (e) => this.onKeyDown(e));
    this.field.addEventListener('focus', () => this.onFocus());
    
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
    this.suggestionsContainer.style.zIndex = '1050';
    this.suggestionsContainer.style.backgroundColor = 'white';
    this.suggestionsContainer.style.border = '1px solid #ddd';
    this.suggestionsContainer.style.borderRadius = '0 0 4px 4px';
    this.suggestionsContainer.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
    this.suggestionsContainer.style.maxHeight = '350px';
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
        this.suggestionsContainer.style.width = `${this.field.offsetWidth}px`;
        this.suggestionsContainer.style.top = `${fieldRect.height}px`;
        this.suggestionsContainer.style.left = '0';
        this.suggestionsContainer.style.position = 'absolute';
      } else {
        // Fallback to absolute positioning relative to document
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;
        
        this.suggestionsContainer.style.top = `${fieldRect.bottom + scrollTop}px`;
        this.suggestionsContainer.style.left = `${fieldRect.left + scrollLeft}px`;
        this.suggestionsContainer.style.position = 'absolute';
      }
    } catch (error) {
      console.error("Error positioning dropdown:", error);
    }
  }
  
  onInput() {
    const query = this.field.value.trim();
    
    // Handle special case for model field
    if (this.options.dataType === 'model' && this.options.dependencyField) {
      const makeValue = this.options.dependencyField.value.trim();
      if (makeValue) {
        this.generateSuggestions(query);
        return;
      }
    }
    
    // Regular handling for other fields
    if (query.length < this.options.minChars) {
      this.hideSuggestions();
      return;
    }
    
    this.generateSuggestions(query);
  }
  
  onFocus() {
    // Show suggestions immediately on focus for some field types
    const value = this.field.value.trim();
    
    if (this.options.dataType === 'model' && this.options.dependencyField) {
      const makeValue = this.options.dependencyField.value.trim();
      if (makeValue) {
        // Show all models for the selected make
        this.generateSuggestions(value);
        return;
      }
    } else if (this.options.dataType === 'year' && value.length === 0) {
      // Show recent years for year field
      this.generateSuggestions(value);
      return;
    }
    
    // For other fields, only show if there's input
    if (value.length >= this.options.minChars) {
      this.generateSuggestions(value);
    }
  }
  
  onKeyDown(e) {
    if (!this.visible) return;
    
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        this.selectNextItem();
        break;
        
      case 'ArrowUp':
        e.preventDefault();
        this.selectPrevItem();
        break;
        
      case 'Enter':
        if (this.selectedIndex >= 0) {
          e.preventDefault();
          const allItems = this.suggestionsContainer.querySelectorAll('.autocomplete-item');
          if (allItems && allItems[this.selectedIndex]) {
            this.selectSuggestion(this.getSelectedSuggestion());
          }
        }
        break;
        
      case 'Escape':
        this.hideSuggestions();
        break;
        
      case 'Tab':
        this.hideSuggestions();
        break;
    }
  }
  
  selectNextItem() {
    const allItems = this.suggestionsContainer.querySelectorAll('.autocomplete-item');
    if (allItems.length === 0) return;
    
    this.selectedIndex = Math.min(this.selectedIndex + 1, allItems.length - 1);
    this.updateSelectedSuggestion();
    this.ensureSelectedVisible();
  }
  
  selectPrevItem() {
    const allItems = this.suggestionsContainer.querySelectorAll('.autocomplete-item');
    if (allItems.length === 0) return;
    
    this.selectedIndex = Math.max(this.selectedIndex - 1, -1);
    this.updateSelectedSuggestion();
    this.ensureSelectedVisible();
  }
  
  ensureSelectedVisible() {
    const selectedItem = this.suggestionsContainer.querySelector('.autocomplete-item.selected');
    if (!selectedItem) return;
    
    const containerRect = this.suggestionsContainer.getBoundingClientRect();
    const itemRect = selectedItem.getBoundingClientRect();
    
    if (itemRect.bottom > containerRect.bottom) {
      this.suggestionsContainer.scrollTop += (itemRect.bottom - containerRect.bottom);
    } else if (itemRect.top < containerRect.top) {
      this.suggestionsContainer.scrollTop -= (containerRect.top - itemRect.top);
    }
  }
  
  getSelectedSuggestion() {
    const items = this.suggestionsContainer.querySelectorAll('.autocomplete-item');
    if (this.selectedIndex >= 0 && this.selectedIndex < items.length) {
      return items[this.selectedIndex].dataset.value;
    }
    return null;
  }
  
  generateSuggestions(query) {
    this.categorizedSuggestions = {}; // Reset categories
    
    // Get dependency value if needed
    let dependencyValue = null;
    if (this.options.dependencyField) {
      dependencyValue = this.options.dependencyField.value.trim();
    }
    
    // Handle different field types
    switch (this.options.dataType) {
      case 'year':
        this.generateYearSuggestions(query);
        break;
        
      case 'make':
        this.generateMakeSuggestions(query);
        break;
        
      case 'model':
        this.generateModelSuggestions(query, dependencyValue);
        break;
        
      default:
        this.generateGenericSuggestions(query);
    }
    
    // Get an array of all suggestions for display
    const allSuggestions = [];
    for (const category in this.categorizedSuggestions) {
      if (this.categorizedSuggestions[category].length > 0) {
        allSuggestions.push(...this.categorizedSuggestions[category]);
      }
    }
    
    this.suggestions = allSuggestions.slice(0, this.options.maxSuggestions);
    
    // Display suggestions
    if (this.suggestions.length > 0) {
      this.displaySuggestions();
    } else {
      this.hideSuggestions();
    }
  }
  
  generateYearSuggestions(query) {
    const years = generateYears();
    
    if (!query) {
      // For empty query, show recent years first
      const recentYears = years.slice(-10).reverse();
      this.categorizedSuggestions['Recent Years'] = recentYears;
      return;
    }
    
    // Filter years that start with the query
    const startsWith = years.filter(year => year.startsWith(query));
    
    // Filter years that contain the query elsewhere
    const contains = years.filter(year => 
      !year.startsWith(query) && year.includes(query)
    );
    
    // Save categorized results
    if (startsWith.length > 0) {
      this.categorizedSuggestions['Years'] = startsWith;
    }
    
    if (contains.length > 0) {
      this.categorizedSuggestions['Other Matching Years'] = contains;
    }
  }
  
  generateMakeSuggestions(query) {
    const makes = Object.keys(vehicleData);
    const queryLower = query.toLowerCase();
    
    if (!query) {
      this.categorizedSuggestions['Makes'] = makes;
      return;
    }
    
    // Filter makes that start with the query
    const startsWith = makes.filter(make => 
      make.toLowerCase().startsWith(queryLower)
    );
    
    // Filter makes that contain the query elsewhere
    const contains = makes.filter(make => 
      !make.toLowerCase().startsWith(queryLower) && 
      make.toLowerCase().includes(queryLower)
    );
    
    // Check for synonym matches (like "chevy" -> "Chevrolet")
    const synonymMatches = [];
    for (const [synonym, make] of Object.entries(makeSynonyms)) {
      if (synonym.startsWith(queryLower) && !startsWith.includes(make) && !contains.includes(make)) {
        synonymMatches.push(make);
      }
    }
    
    // Save categorized results
    if (startsWith.length > 0) {
      this.categorizedSuggestions['Makes'] = startsWith;
    }
    
    if (synonymMatches.length > 0) {
      this.categorizedSuggestions['Also Known As'] = synonymMatches;
    }
    
    if (contains.length > 0) {
      this.categorizedSuggestions['Other Matching Makes'] = contains;
    }
    
    // Add fuzzy matching for typos
    if (Object.keys(this.categorizedSuggestions).length === 0 && queryLower.length >= 3) {
      const fuzzyMatches = this.getFuzzyMatches(queryLower, makes);
      if (fuzzyMatches.length > 0) {
        this.categorizedSuggestions['Did You Mean'] = fuzzyMatches;
      }
    }
  }
  
  generateModelSuggestions(query, makeValue) {
    if (!makeValue) {
      return;
    }
    
    // Normalize the make name
    const normalizedMake = this.normalizeMake(makeValue);
    if (!normalizedMake) {
      return;
    }
    
    // Get models for this make
    const models = vehicleData[normalizedMake] || [];
    if (models.length === 0) {
      return;
    }
    
    const queryLower = query.toLowerCase();
    
    // Special case for single letters like "c" in "Crown"
    if (query.length === 1) {
      // Sort all models by those that start with the letter first
      const startsWith = models.filter(model => 
        model.toLowerCase().startsWith(queryLower)
      );
      
      const contains = models.filter(model => 
        !model.toLowerCase().startsWith(queryLower) && 
        model.toLowerCase().includes(queryLower)
      );
      
      if (startsWith.length > 0) {
        this.categorizedSuggestions['Models'] = startsWith;
      }
      
      if (contains.length > 0) {
        this.categorizedSuggestions['Other Models'] = contains;
      }
      
      // If showing all, only show top matches
      if (!query) {
        this.categorizedSuggestions['Models'] = models.slice(0, this.options.maxSuggestions);
      }
    }
    // For multiple letters, prioritize exact matches
    else if (query.length > 1) {
      // Sort by exact match, starts with, contains
      const exactMatches = models.filter(model => 
        model.toLowerCase() === queryLower
      );
      
      const startsWith = models.filter(model => 
        model.toLowerCase().startsWith(queryLower) && 
        model.toLowerCase() !== queryLower
      );
      
      const contains = models.filter(model => 
        !model.toLowerCase().startsWith(queryLower) && 
        model.toLowerCase().includes(queryLower)
      );
      
      if (exactMatches.length > 0) {
        this.categorizedSuggestions['Exact Matches'] = exactMatches;
      }
      
      if (startsWith.length > 0) {
        this.categorizedSuggestions['Models'] = startsWith;
      }
      
      if (contains.length > 0) {
        this.categorizedSuggestions['Other Models'] = contains;
      }
    }
    // No query - show all models
    else {
      this.categorizedSuggestions['All Models'] = models;
    }
    
    // Special case for "Crown" in Ford - ensure Crown Victoria appears
    if (normalizedMake === "Ford" && queryLower === "crown") {
      // Check if Crown Victoria is already in the results
      let hasCrownVictoria = false;
      
      for (const category in this.categorizedSuggestions) {
        hasCrownVictoria = this.categorizedSuggestions[category].some(model => 
          model.toLowerCase() === "crown victoria"
        );
        
        if (hasCrownVictoria) break;
      }
      
      // If not found, add it to exact matches
      if (!hasCrownVictoria) {
        if (!this.categorizedSuggestions['Exact Matches']) {
          this.categorizedSuggestions['Exact Matches'] = [];
        }
        this.categorizedSuggestions['Exact Matches'].unshift("Crown Victoria");
      }
    }
  }
  
  generateGenericSuggestions(query) {
    // For generic fields, just filter the data source directly
    if (!Array.isArray(this.options.dataSource)) {
      return;
    }
    
    const queryLower = query.toLowerCase();
    
    if (!query) {
      this.categorizedSuggestions['Suggestions'] = this.options.dataSource.slice(0, this.options.maxSuggestions);
      return;
    }
    
    // Filter by starts with, then contains
    const startsWith = this.options.dataSource.filter(item => 
      item.toString().toLowerCase().startsWith(queryLower)
    );
    
    const contains = this.options.dataSource.filter(item => 
      !item.toString().toLowerCase().startsWith(queryLower) && 
      item.toString().toLowerCase().includes(queryLower)
    );
    
    if (startsWith.length > 0) {
      this.categorizedSuggestions['Matches'] = startsWith;
    }
    
    if (contains.length > 0) {
      this.categorizedSuggestions['Other Matches'] = contains;
    }
  }
  
  // Get fuzzy matches for typos
  getFuzzyMatches(query, items) {
    const matches = [];
    
    // Simple fuzzy match: Check if removing one letter gives a match
    for (let i = 0; i < query.length; i++) {
      const fuzzyQuery = query.slice(0, i) + query.slice(i + 1);
      
      if (fuzzyQuery.length < 2) continue;
      
      for (const item of items) {
        const itemLower = item.toLowerCase();
        if (itemLower.includes(fuzzyQuery) && !matches.includes(item)) {
          matches.push(item);
          
          // Limit to a few fuzzy matches
          if (matches.length >= 3) {
            return matches;
          }
        }
      }
    }
    
    return matches;
  }
  
  normalizeMake(make) {
    // Check for direct match
    if (vehicleData[make]) {
      return make;
    }
    
    // Check for case-insensitive match
    for (const vehicleMake in vehicleData) {
      if (vehicleMake.toLowerCase() === make.toLowerCase()) {
        return vehicleMake;
      }
    }
    
    // Check for synonym match
    const makeLower = make.toLowerCase();
    if (makeSynonyms[makeLower]) {
      return makeSynonyms[makeLower];
    }
    
    return null;
  }
  
  displaySuggestions() {
    // Clear container
    this.suggestionsContainer.innerHTML = '';
    
    // Counter for overall index across categories
    let globalIndex = 0;
    
    // Process each category
    for (const category in this.categorizedSuggestions) {
      const suggestions = this.categorizedSuggestions[category];
      
      if (suggestions.length === 0) continue;
      
      // Add category header
      const header = document.createElement('div');
      header.className = 'autocomplete-category';
      header.textContent = category.toUpperCase();
      header.style.padding = '5px 10px';
      header.style.fontSize = '12px';
      header.style.fontWeight = 'bold';
      header.style.color = '#666';
      header.style.backgroundColor = '#f5f5f5';
      this.suggestionsContainer.appendChild(header);
      
      // Add items for this category
      suggestions.forEach(suggestion => {
        const item = document.createElement('div');
        item.className = 'autocomplete-item';
        item.dataset.value = suggestion;
        item.dataset.index = globalIndex++;
        
        item.style.padding = '8px 12px';
        item.style.cursor = 'pointer';
        item.style.transition = 'background-color 0.2s';
        item.style.borderBottom = '1px solid #f0f0f0';
        
        // Highlight matching text if enabled
        if (this.options.highlightMatches) {
          const query = this.field.value.trim().toLowerCase();
          const suggestionText = suggestion.toString();
          const suggestionLower = suggestionText.toLowerCase();
          
          if (query && suggestionLower.includes(query)) {
            const startIndex = suggestionLower.indexOf(query);
            const beforeMatch = suggestionText.substring(0, startIndex);
            const match = suggestionText.substring(startIndex, startIndex + query.length);
            const afterMatch = suggestionText.substring(startIndex + query.length);
            
            item.innerHTML = `${beforeMatch}<strong style="font-weight:bold;color:#e53238">${match}</strong>${afterMatch}`;
          } else {
            item.textContent = suggestionText;
          }
        } else {
          item.textContent = suggestion.toString();
        }
        
        // Add event listeners
        item.addEventListener('click', () => this.selectSuggestion(suggestion));
        item.addEventListener('mouseover', () => {
          this.selectedIndex = parseInt(item.dataset.index);
          this.updateSelectedSuggestion();
        });
        
        this.suggestionsContainer.appendChild(item);
      });
    }
    
    // Position and show the container
    this.updateContainerPosition();
    this.suggestionsContainer.style.display = 'block';
    this.visible = true;
    
    // Add debug dimensions
    console.log(`Suggestions container dimensions: ${this.suggestionsContainer.offsetWidth}x${this.suggestionsContainer.offsetHeight}`);
  }
  
  updateSelectedSuggestion() {
    const items = this.suggestionsContainer.querySelectorAll('.autocomplete-item');
    
    items.forEach(item => {
      if (parseInt(item.dataset.index) === this.selectedIndex) {
        item.classList.add('selected');
        item.style.backgroundColor = '#f0f0f0';
      } else {
        item.classList.remove('selected');
        item.style.backgroundColor = '';
      }
    });
  }
  
  selectSuggestion(suggestion) {
    // Set the field value
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
}

// Initialize autocomplete instances when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  // Year field autocomplete with recent years at top
  const yearAutocomplete = new EnhancedFieldAutocomplete({
    fieldId: 'year-field',
    suggestionsContainerId: 'year-suggestions',
    dataSource: generateYears(),
    dataType: 'year',
    minChars: 0, // Show on focus
    maxSuggestions: 15,
    nextField: 'make-field',
    highlightMatches: true,
    onSelect: (year) => {
      document.getElementById('make-field').focus();
    }
  });
  
  // Make field autocomplete with fuzzy matching and synonyms
  const makeAutocomplete = new EnhancedFieldAutocomplete({
    fieldId: 'make-field',
    suggestionsContainerId: 'make-suggestions',
    dataSource: Object.keys(vehicleData),
    dataType: 'make',
    minChars: 1,
    maxSuggestions: 20,
    nextField: 'model-field',
    highlightMatches: true,
    onSelect: (make) => {
      // After selecting a make, focus on model field
      const modelField = document.getElementById('model-field');
      modelField.value = ''; // Clear the model field
      modelField.focus();
      
      // Force trigger focus to show model suggestions
      const focusEvent = new Event('focus', { bubbles: true });
      modelField.dispatchEvent(focusEvent);
    }
  });
  
  // Model field autocomplete dependent on make
  const modelAutocomplete = new EnhancedFieldAutocomplete({
    fieldId: 'model-field',
    suggestionsContainerId: 'model-suggestions',
    dataSource: [], // Will be populated based on selected make
    dataType: 'model',
    dependsOn: 'make-field',
    minChars: 0, // Show all models on focus
    maxSuggestions: 25,
    nextField: 'part-field',
    highlightMatches: true,
    onSelect: (model) => {
      // After selecting a model, focus on part field
      document.getElementById('part-field').focus();
    }
  });
  
  // Tab navigation between fields
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
  
  // Toggle between single-field and multi-field search
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