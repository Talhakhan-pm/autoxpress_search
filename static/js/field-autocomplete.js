/**
 * AutoXpress Enhanced Field-Based Autocomplete
 * Inspired by the single-field autoxpress.js implementation
 */

// Vehicle data for autocomplete - using the updated inventory
const vehicleData = {
  "Acura": ["ILX", "MDX", "RDX", "TLX", "NSX", "RLX", "TSX", "Integra", "ZDX", "TL", "RL", "CSX", "RSX", "Legend", "Vigor"],

  "Alfa Romeo": ["Giulia", "Stelvio", "4C", "Spider", "Giulietta", "164", "GTV", "MiTo"],

  "Aston Martin": ["DB11", "Vantage", "DBS", "DBX", "DB9", "Rapide", "Vanquish", "DB7", "Virage", "Lagonda", "DB5", "DB4"],

  "Audi": ["A3", "A4", "A5", "A6", "A7", "A8", "Q3", "Q5", "Q7", "Q8", "e-tron", "TT", "R8", "S3", "S4", "S5", "S6", "S7", "S8", "RS3", "RS5", "RS7", "SQ5", "SQ7", "SQ8", "A4 Allroad", "A6 Allroad", "Allroad", "A3 Sportback", "80", "90", "100", "200", "V8", "Cabriolet", "Coupe Quattro", "A3 e-tron", "A3 Quattro", "A4 Avant", "A4 Quattro", "A5 Cabriolet", "A5 Coupe", "A5 Sportback", "A6 Avant", "A6 Quattro", "A7 Sportback", "A7 Quattro", "A8 L", "A8 Quattro", "e-tron GT", "e-tron Sportback", "Q3 Sportback", "Q4 e-tron", "Q5 Sportback", "Q5 e-tron", "Q8 e-tron", "RS Q3", "RS Q8", "RS3 Sportback", "RS4", "RS4 Avant", "RS6", "RS6 Avant", "TT RS", "TT Coupe", "TT Roadster", "TT Quattro", "R8 Spyder", "R8 V10", "R8 V10 Plus", "S3 Sedan", "S4 Avant", "S4 Sedan", "S5 Cabriolet", "S5 Coupe", "S5 Sportback", "SQ7 TFSI", "SQ8 TFSI", "RS5 Coupe", "RS5 Sportback", "RS7 Sportback", "SQ5 Sportback"],

  "Bentley": ["Continental", "Bentayga", "Flying Spur", "Azure", "Arnage", "Brooklands", "Mulsanne"],

  "BMW": ["3-Series", "5-Series", "7-Series", "X1", "X3", "X5", "X7", "M3", "M5", "Z4", "i4", "i7", "iX", "M8", "X3M", "X5M", "330i", "530i", "740i", "X3 xDrive30i", "X5 xDrive40i", "335i", "328i", "325i", "540i", "535i", "M340i", "M550i", "Z3", "8-Series", "6-Series", "4-Series", "2-Series", "1-Series", "X2", "X4", "X6", "i3", "i8", "M2", "M4", "M6", "M235i", "M240i", "X4M", "X6M", "320i", "340i", "550i", "750i", "840i", "M440i", "iX3", "i5", "i8 Roadster", "Z8", "M Roadster", "M Coupe", "X5 M Competition", "M3 Competition", "M5 Competition", "M4 Competition", "iX M60", "i7 M70", "318i", "318is", "323i", "325Ci", "325xi", "328Ci", "328xi", "330Ci", "330xi", "335d", "335xi", "518i", "520i", "525i", "525xi", "528i", "528xi", "530xi", "535d", "535xi", "545i", "550xi", "740e", "740iL", "745i", "745Li", "750iL", "750Li", "760i", "760Li", "840Ci", "850i", "850Ci", "850CSi", "M2 Competition", "M6 Gran Coupe", "M760i", "M760Li", "M8 Gran Coupe", "X1 sDrive28i", "X1 xDrive28i", "X2 M35i", "X3 M40i", "X4 M40i", "X5 M50i", "X5 xDrive35i", "X5 xDrive40i", "X5 xDrive45e", "X5 xDrive50i", "X6 M50i", "X6 xDrive35i", "X6 xDrive40i", "X6 xDrive50i", "X7 M50i", "X7 xDrive40i", "X7 xDrive50i", "Z4 M40i", "Z4 sDrive30i", "i4 eDrive40", "i4 M50", "i7 xDrive60", "iX xDrive50"],

  "Buick": ["Enclave", "Encore", "Envision", "LaCrosse", "Regal", "Verano", "Cascada", "LeSabre", "Century", "Skylark", "Park Avenue", "Riviera", "Roadmaster", "Electra", "Rainier", "Rendezvous", "Terraza", "Lucerne", "Special", "Super", "Limited", "Estate Wagon", "Invicta", "Wildcat", "Grand National", "GSX", "Apollo", "Centurion", "Skyhawk", "Somerset", "Reatta", "Grand Sport", "Roadmaster Estate", "Special Deluxe", "Super Estate Wagon", "50", "60", "70", "80", "90", "Eight", "Sport Wagon", "Apollo", "Estate", "Electra 225", "Opel", "GNX", "Regal T-Type", "Regal GS"],

  "Cadillac": ["CT4", "CT5", "CT6", "XT4", "XT5", "XT6", "Escalade", "ATS", "CTS", "XTS", "SRX", "STS", "DTS", "Eldorado", "Seville", "DeVille", "Fleetwood", "Allante", "Brougham", "Catera", "Series 60", "Series 61", "Series 62", "Series 63", "Series 65", "Series 70", "Series 75", "Series 80", "Series 90", "Calais", "Commercial Chassis", "Coupe de Ville", "Sedan de Ville", "Eldorado Biarritz", "Eldorado Brougham", "Eldorado Seville", "Escalade ESV", "Escalade EXT", "Sixty Special", "Fleetwood 75", "Fleetwood Brougham", "Fleetwood Limousine", "Cimarron", "Type V-63", "Coupe", "Convertible", "Custom", "Roadster", "Town Car", "Victoria"],

  "Chevrolet": ["Silverado", "Camaro", "Corvette", "Malibu", "Equinox", "Tahoe", "Suburban", "Colorado", "Traverse", "Blazer", "Impala", "Spark", "Trax", "Bolt", "Trailblazer", "Cavalier", "Cobalt", "Cruze", "Sonic", "Aveo", "S10", "Monte Carlo", "Nova", "El Camino", "Chevelle", "Caprice", "Bel Air", "Avalanche", "Astro", "Express", "SSR", "HHR", "Silverado HD", "Volt", "Bolt EUV", "Corvette Z06", "Corvette ZR1", "Silverado 1500", "Silverado 2500", "Silverado 3500", "Lumina", "Beretta", "Prizm", "Tracker", "Uplander", "Venture", "Camaro SS", "Camaro ZL1", "Corvette Stingray", "Corvette Grand Sport", "Delray", "Biscayne", "Deluxe", "Fleetline", "Styleline", "210", "150", "Nomad", "Bel Air Nomad", "Kingswood", "Parkwood", "Brookwood", "Yeoman", "Sedan Delivery", "Townsman", "Beauville", "Greenbrier", "Corvair", "Chevy II", "Laguna", "Vega", "Monza", "Chevette", "Citation", "Celebrity", "Spectrum", "Sprint", "Corsica", "Spectrum", "Corvette 1953-1962", "Corvette Sting Ray", "Corvette 1968-1982", "Impala SS"],

  "Chrysler": ["300", "Pacifica", "Voyager", "Town & Country", "PT Cruiser", "Sebring", "200", "Concorde", "Crossfire", "Aspen", "Cirrus", "Imperial", "LHS", "New Yorker", "Fifth Avenue", "Cordoba", "Newport", "LeBaron", "Airflow", "Airstream", "Crown Imperial", "C-300", "300B", "300C", "300D", "300E", "300F", "300G", "300H", "300J", "300K", "300L", "Windsor", "Saratoga", "300M", "New Yorker Brougham", "Royal", "Highlander", "Town and Country Wagon", "St. Regis", "Executive", "Letter Series", "Valiant", "E-Class", "Laser", "Conquest", "TC by Maserati", "Nassau", "Daytona", "Prowler", "Plainsman", "Turbine Car", "Special", "Deluxe", "Custom", "Convertible"],

  "Dodge": ["Charger", "Challenger", "Durango", "Journey", "Grand Caravan", "Ram", "Viper", "Neon", "Avenger", "Dart", "Nitro", "Caliber", "Intrepid", "Stealth", "Magnum", "Stratus", "Shadow", "Dynasty", "Spirit", "Colt", "Daytona", "Caravan", "Omni", "Custom", "D Series", "Coronet", "Polara", "Monaco", "Super Bee", "Diplomat", "Royal", "Wayfarer", "Meadowbrook", "Kingsway", "D100", "D150", "D250", "D350", "W100", "W150", "W250", "W350", "Ramcharger", "Tradesman", "Sportsman", "St. Regis", "600", "400", "Aries", "Aspen", "Mirada", "Lancer", "Series 116", "Series 117", "Series 118", "Series 126", "Charger Daytona", "Coronet Super Bee", "440", "880", "330", "024", "Rampage", "Raider", "Demon", "Monaco Brougham", "Charger R/T", "Coronet R/T", "La Femme", "Sierra", "Meadowbrook", "Wayfarer", "Main Street Taxi", "D15", "D24"],

  "Ferrari": ["F8", "Roma", "Portofino", "SF90", "812", "488", "458", "F12", "California", "LaFerrari", "Enzo", "F430", "360", "550", "355", "348", "Testarossa", "F40", "F50"],

  "Fiat": ["500", "500X", "500L", "124 Spider", "500e", "500 Abarth", "500c"],

  "Ford": ["F-150", "Mustang", "Explorer", "Escape", "Edge", "Ranger", "Bronco", "Expedition", "Focus", "Fusion", "Taurus", "EcoSport", "Maverick", "F-250", "F-350", "Fiesta", "Crown Victoria", "Flex", "Transit", "Five Hundred", "Freestyle", "Excursion", "E-Series", "E-150", "E-250", "E-350", "Thunderbird", "Probe", "Contour", "Tempo", "Escort", "GT", "Model A", "Model T", "Fairlane", "Falcon", "Galaxie", "Bronco Sport", "F-450", "F-550", "Explorer Sport Trac", "Transit Connect", "Windstar", "Aerostar", "Aspire", "Festiva", "Mustang Mach-E", "Lightning", "Super Duty", "Shelby GT500", "Shelby GT350", "Country Sedan", "Country Squire", "Crestline", "Custom", "Custom 500", "Customline", "Deluxe", "Fairlane 500", "Galaxie 500", "LTD", "LTD II", "Mainline", "Police Interceptor", "Ranch Wagon", "Ranchero", "Starliner", "Sunliner", "Torino", "Victoria", "Pinto", "Mustang Boss 302", "Mustang Boss 429", "Mustang Mach 1", "Mustang Shelby GT", "Fairmont", "Granada", "Courier", "Econoline", "Club Wagon", "F-100", "P-350", "Coupe", "Sedan", "Convertible", "Woody", "Squire"],

  "Genesis": ["G70", "G80", "G90", "GV70", "GV80", "GV60"],

  "GMC": ["Sierra", "Yukon", "Acadia", "Terrain", "Canyon", "Savana", "Hummer EV", "Jimmy", "Envoy", "Sonoma", "Safari", "Syclone", "Typhoon", "Suburban", "Sprint", "Rally", "Vandura", "S15", "C1500", "C2500", "C3500", "K1500", "K2500", "K3500", "Caballero", "Carryall", "Forward Control", "New Look Bus", "Old Look Bus", "P Forward Control", "PD Series", "General", "Panel Truck", "Pickup", "S-15 Jimmy", "Cabover", "Astro", "Brigadier", "Topkick", "Handi-Van", "Handi-Bus", "Series 100", "Series 150", "Series 250", "Series 280", "Series 370", "Series 450", "Series 550", "Series 620", "Series 630", "Series 660", "Series 720", "Series 730", "Series 930", "Truck", "Chevette", "Value Van", "Stepvan"],

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

  "Mercedes-Benz": ["C-Class", "E-Class", "S-Class", "A-Class", "GLC", "GLE", "GLS", "G-Class", "CLA", "CLS", "SL", "SLK", "AMG GT", "EQS", "EQE", "C300", "E350", "S500", "GLC300", "GLE350", "GLE450", "G550", "C43 AMG", "E63 AMG", "S63 AMG", "C63 AMG", "GLC43 AMG", "ML350", "ML550", "GL450", "GL550", "GLA", "GLB", "SLC", "CLK", "Sprinter", "Metris", 
  // C-Class specific models
  "C180", "C200", "C220", "C230", "C240", "C250", "C270", "C280", "C300", "C320", "C350", "C400", "C450", "C55 AMG", "C32 AMG", "C36 AMG", "C43 AMG", "C63 AMG", 
  // E-Class specific models
  "E220", "E240", "E250", "E280", "E300", "E320", "E350", "E400", "E420", "E430", "E500", "E550", "E55 AMG", "E63 AMG",
  // S-Class specific models  
  "S320", "S350", "S400", "S420", "S430", "S500", "S550", "S560", "S580", "S600", "S63 AMG", "S65 AMG",
  // SLK/SL models
  "SLK230", "SLK320", "SLK350", "SLK55 AMG", "SL320", "SL350", "SL500", "SL550", "SL55 AMG", "SL63 AMG", "SL65 AMG", "SLR", "SLS", 
  // CL models
  "CL500", "CL550", "CL600", "CL63 AMG", "CL65 AMG", 
  // CLK models
  "CLK320", "CLK350", "CLK430", "CLK500", "CLK55 AMG", "CLK550", "CLK63 AMG", 
  // SUV/Crossover models
  "GLK350", "ML320", "ML350", "ML430", "ML500", "ML55 AMG", "ML63 AMG", "GL320", "GL350", "GL450", "GL500", "GL550", "GL63 AMG", "G500", "G550", "G55 AMG", "G63 AMG", "G65 AMG", "GLA250", "GLA35 AMG", "GLA45 AMG", "GLB250", "GLC43", "GLC63", "GLE43", "GLE53", "GLE63", "GLS450", "GLS550", "GLS580", "GLS63", 
  // Maybach models
  "Maybach S560", "Maybach S580", "Maybach S600", "Maybach S650", "Maybach GLS600", 
  // Other models
  "R350", "R500", "CLA250", "CLA35 AMG", "CLA45 AMG", "CLS400", "CLS500", "CLS550", "CLS55 AMG", "CLS63 AMG", "S550e", "EQB", "EQC", "EQA", "190E", "300E", "300CE", "300TE", "400E", "500E"],

  "MINI": ["Cooper", "Countryman", "Clubman", "Paceman", "Coupe", "Roadster", "Cooper S", "John Cooper Works", "Cooper SE", "Hardtop", "Convertible"],

  "Mitsubishi": ["Outlander", "Eclipse Cross", "Mirage", "Outlander Sport", "Lancer", "Galant", "Eclipse", "Endeavor", "Diamante", "3000GT", "Montero", "Raider", "Expo", "Precis", "Mighty Max"],

  "Nissan": ["Altima", "Sentra", "Maxima", "Rogue", "Pathfinder", "Murano", "Armada", "Frontier", "Titan", "Kicks", "Versa", "Juke", "Leaf", "Z", "370Z", "350Z", "240SX", "GT-R", "Cube", "Xterra", "Quest"],

  "Pontiac": ["Firebird", "GTO", "Grand Prix", "Trans Am", "Bonneville", "Grand Am", "Fiero", "Sunfire", "Solstice", "Sunbird", "LeMans", "Montana", "Aztek", "G6", "G8", "Vibe", "Torrent", "Catalina", "Laurentian", "Parisienne", "Star Chief", "Chieftain", "Super Chief", "Streamliner", "Ventura", "Safari", "Phoenix", "6000", "Sunbird", "J2000", "T1000", "Astre", "Beaumont", "Strato Chief", "Tempest", "2+2", "Can Am", "Executive", "Torpedo", "Silver Streak", "Coupe", "Custom"],

  "Oldsmobile": ["Cutlass", "88", "98", "442", "Toronado", "Alero", "Aurora", "Bravada", "Intrigue", "Silhouette", "Achieva", "Cutlass Supreme", "Cutlass Ciera", "Firenza", "Custom Cruiser", "Delmont", "Delta 88", "Dynamic", "Fiesta", "F-85", "Jetstar", "Starfire", "Super 88", "Vista Cruiser", "Calais", "Omega", "Hurst/Olds", "Rallye 350", "Ninety-Eight", "Holiday", "Special", "Standard", "Series 60", "Series 70", "Series 80", "Series 90", "Touring Sedan", "Jet Star", "Wagon", "Coupe", "Hardtop"],

  "Mercury": ["Cougar", "Grand Marquis", "Marauder", "Marquis", "Meteor", "Milan", "Monarch", "Montego", "Monterey", "Mountaineer", "Mystique", "Park Lane", "Sable", "Topaz", "Tracer", "Villager", "Mariner", "Montclair", "Colony Park", "Comet", "Commuter", "Bobcat", "Brougham", "Capri", "Cyclone", "Eight", "Lynx", "LN7", "M-Series", "Medalist", "Monterey Custom", "Monterey S-55", "S-55", "Turnpike Cruiser", "Voyager", "Zephyr", "Custom", "Station Wagon", "Sedan", "Coupe", "Convertible"],

  "Plymouth": ["Barracuda", "Belvedere", "Duster", "Fury", "GTX", "Horizon", "Laser", "Neon", "Prowler", "Road Runner", "Satellite", "Valiant", "Volare", "Acclaim", "Caravelle", "Champ", "Colt", "Conquest", "Cricket", "Gran Fury", "Reliant", "Sapporo", "Sundance", "Turismo", "Breeze", "Cambridge", "Cranbrook", "Concord", "Deluxe", "Plaza", "Savoy", "Superbird", "Suburban", "Special", "Special Deluxe", "Business", "Commercial", "Convertible", "Coupe", "Sedan", "Pickup"],

  "Porsche": ["911", "Cayenne", "Macan", "Panamera", "Taycan", "Boxster", "Cayman", "928", "944", "968", "914", "356", "912", "718"],

  "Ram": ["1500", "2500", "3500", "ProMaster", "ProMaster City", "Dakota"],

  "Rolls-Royce": ["Phantom", "Ghost", "Wraith", "Dawn", "Cullinan", "Silver Shadow", "Silver Spur", "Corniche", "Camargue", "Silver Seraph"],

  "Subaru": ["Outback", "Forester", "Crosstrek", "Impreza", "Legacy", "Ascent", "WRX", "BRZ", "STI", "WRX STI", "Baja", "Tribeca", "SVX", "Justy", "Loyale", "Sambar"],

  "Tesla": ["Model 3", "Model S", "Model X", "Model Y", "Cybertruck", "Roadster"],

  "Toyota": ["Camry", "Corolla", "RAV4", "Tacoma", "Highlander", "4Runner", "Prius", "Tundra", "Sienna", "Avalon", "Sequoia", "Venza", "C-HR", "Land Cruiser", "FJ Cruiser", "86", "GR86", "Supra", "Mirai", "Matrix", "Yaris", "Echo", "Celica", "Crown", "Corolla Cross", "bZ4X", "GR Corolla", "Camry Solara", "Cressida", "Tercel", "Paseo", "T100", "Previa"],

  "Volkswagen": ["Jetta", "Passat", "Tiguan", "Atlas", "Golf", "ID.4", "Taos", "Arteon", "GTI", "Beetle", "Touareg", "Rabbit", "CC", "Eos", "GLI", "R32", "Golf R", "Corrado", "Scirocco", "Thing", "Karmann Ghia", "Type 1", "Type 2", "Type 3", "Vanagon", "New Beetle", "Cabrio", "Phaeton", "Routan"],

  "Volvo": ["XC90", "XC60", "XC40", "S60", "S90", "V60", "V90", "C40", "C30", "S40", "S80", "V40", "V50", "V70", "850", "740", "940", "960", "240", "Amazon", "P1800", "PV444", "PV544", "C70"]
};

// Generate years for autocomplete (1950 to current year + 1)
const generateYears = () => {
  const years = [];
  const currentYear = new Date().getFullYear();
  for (let year = 1950; year <= currentYear + 1; year++) {
    years.push(year.toString());
  }
  return years;
};

// Make synonyms for normalization
const makeSynonyms = {
  "chevy": "Chevrolet",
  "vw": "Volkswagen",
  "mercedes": "Mercedes-Benz",
  "benz": "Mercedes-Benz",
  "olds": "Oldsmobile",
  "cutlass": "Oldsmobile",
  "ponti": "Pontiac",
  "firebird": "Pontiac",
  "trans am": "Pontiac",
  "merc": "Mercury",
  "mopar": "Chrysler",
  "plym": "Plymouth",
  "barracuda": "Plymouth",
  "roadrunner": "Plymouth",
  "caddy": "Cadillac",
  "deville": "Cadillac",
  "eldorado": "Cadillac"
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

  /**
 * Optimized version of the updateContainerPosition function
 * Improves performance by using CSS variables and throttling updates
 */
  updateContainerPosition() {
    if (!this.field) return;

    try {
      // Get the field position
      const fieldRect = this.field.getBoundingClientRect();
      
      // Use CSS variables for positioning - this improves performance
      // by avoiding direct style manipulations and leveraging browser optimizations
      this.suggestionsContainer.style.setProperty('--field-bottom', `${fieldRect.bottom}px`);
      this.suggestionsContainer.style.setProperty('--field-left', `${fieldRect.left}px`);
      this.suggestionsContainer.style.setProperty('--field-width', `${this.field.offsetWidth}px`);
      
      // Make sure the container is visible if suggestions are being shown
      if (this.visible) {
        this.suggestionsContainer.style.display = 'block';
      }
    } catch (error) {
      console.error("Error positioning dropdown:", error);
    }
  }

  /**
   * Optimized styleContainer method
   * Uses a more efficient approach with CSS variables
   */
  styleContainer() {
    // Add a class for styling instead of inline styles
    this.suggestionsContainer.classList.add('autocomplete-suggestions-container');
    
    // Set initial CSS variables
    this.suggestionsContainer.style.setProperty('--field-width', `${this.field.offsetWidth}px`);
    
    // Only define the styles that can't be easily set in CSS
    Object.assign(this.suggestionsContainer.style, {
      display: 'none'
    });
    
    // Inject a stylesheet for better performance
    if (!document.getElementById('autocomplete-styles')) {
      const stylesheet = document.createElement('style');
      stylesheet.id = 'autocomplete-styles';
      
      stylesheet.textContent = `
        .autocomplete-suggestions-container {
          position: fixed;
          width: var(--field-width);
          top: var(--field-bottom);
          left: var(--field-left);
          z-index: 1050; /* Use a reasonable z-index that doesn't break stacking contexts */
          background-color: white;
          border: 1px solid #ddd;
          border-radius: 0 0 4px 4px;
          box-shadow: 0 4px 12px rgba(0,0,0,0.3);
          max-height: 350px;
          overflow-y: auto;
        }
        
        /* Add transitions for smoother experience */
        .autocomplete-item {
          transition: background-color 0.15s ease;
        }
      `;
      
      document.head.appendChild(stylesheet);
    }

    // Position under the input field
    this.updateContainerPosition();

    // Add optimized event listeners with throttling
    const throttledUpdate = this.throttle(() => this.updateContainerPosition(), 100);
    window.addEventListener('resize', throttledUpdate);
    window.addEventListener('scroll', throttledUpdate, true);
  }
  
  /**
   * Helper function to throttle frequent updates
   * Improves performance by limiting how often a function can execute
   */
  throttle(func, limit) {
    let inThrottle;
    return function() {
      const args = arguments;
      const context = this;
      if (!inThrottle) {
        func.apply(context, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
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
        if (this.visible) {
          // If there's a selected item, select it 
          if (this.selectedIndex >= 0) {
            e.preventDefault();
            const allItems = this.suggestionsContainer.querySelectorAll('.autocomplete-item');
            if (allItems && allItems[this.selectedIndex]) {
              this.selectSuggestion(this.getSelectedSuggestion());
            }
          }
          // If no item is selected but there are suggestions, select the first one
          else {
            const firstItem = this.suggestionsContainer.querySelector('.autocomplete-item');
            if (firstItem) {
              e.preventDefault();
              const suggestion = firstItem.dataset.value;
              this.selectSuggestion(suggestion);
            } else {
              this.hideSuggestions();
            }
          }
        }
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
    
    // Special handling for alphanumeric model variants (like C240, E350, 330i, X5, etc.)
    if (
      (normalizedMake === "Mercedes-Benz" && queryLower.match(/^[a-z][0-9]{2,3}$/i)) ||
      (normalizedMake === "BMW" && (
        queryLower.match(/^[0-9]{3}i$/i) || // 328i, 530i, etc
        queryLower.match(/^[mx][0-9]$/i) || // X3, M3, etc
        queryLower.match(/^[mx][0-9][0-9]?[a-z]?$/i) // X5M, M40i, etc
      ))
    ) {
      // If user types something like "c240" or "330i", prioritize showing the exact model
      const exactModelMatch = models.find(model => 
        model.toLowerCase() === queryLower
      );
      
      if (exactModelMatch) {
        this.categorizedSuggestions['Exact Match'] = [exactModelMatch];
        
        // For Mercedes, add the appropriate class too
        if (normalizedMake === "Mercedes-Benz" && queryLower.match(/^[a-z]/i)) {
          const classLetter = queryLower.charAt(0).toUpperCase();
          const className = classLetter + "-Class";
          if (models.includes(className)) {
            this.categorizedSuggestions['Model Classes'] = [className];
          }
        }
        // For BMW, add the appropriate series
        else if (normalizedMake === "BMW" && queryLower.match(/^[0-9]/i)) {
          const seriesNumber = queryLower.charAt(0);
          const seriesName = seriesNumber + "-Series";
          if (models.includes(seriesName)) {
            this.categorizedSuggestions['Model Series'] = [seriesName];
          }
        }
        
        return;
      }
    }

    // Get parent class pattern from query (like "C" from "C240")
    let parentClass = null;
    if (normalizedMake === "Mercedes-Benz" && queryLower.match(/^[a-z]/i)) {
      // Extract the first letter as the class (C-Class, E-Class, etc)
      parentClass = queryLower.charAt(0).toUpperCase() + "-Class";
    }
    
    // Special case for single letters like "c" in "C-Class"
    if (query.length === 1) {
      // Sort all models by those that start with the letter first
      const startsWith = models.filter(model =>
        model.toLowerCase().startsWith(queryLower)
      );
      
      // If it's a Mercedes letter class (C, E, S, etc)
      if (parentClass && normalizedMake === "Mercedes-Benz") {
        // Find all models with that first letter
        const classModels = models.filter(model => 
          model.toLowerCase().startsWith(queryLower) && 
          model.match(/^[a-z][0-9]{2,3}/i) // Match C123, E350 type patterns
        );
        
        if (classModels.length > 0) {
          this.categorizedSuggestions['Specific Models'] = classModels;
        }
        
        // Always show the parent class as first option
        this.categorizedSuggestions['Model Classes'] = [parentClass];
      }

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

    // Position and size the container properly
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
document.addEventListener('DOMContentLoaded', function () {
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