import re
import json
from functools import lru_cache

class EnhancedQueryProcessor:
    """
    Enhanced query processor that can handle various input formats
    and extract structured vehicle and part information.
    Updated to properly handle structured data from multiple fields.
    """
    
    def __init__(self):
        # Load vehicle data (in production, this would be from your database)
        self.vehicle_makes = ["acura", "amc", "buick", "cadillac", "chevrolet", "chevy", 
                             "chrysler", "dodge", "eagle", "ford", "geo", "gmc", "honda", 
                             "hummer", "hyundai", "infiniti", "isuzu", "jeep", "kia", 
                             "lexus", "lincoln", "mazda", "mercury", "mitsubishi", 
                             "nissan", "oldsmobile", "plymouth", "pontiac", "ram", 
                             "saturn", "scion", "studebaker", "subaru", "tesla", 
                             "toyota", "volkswagen", "vw"]
        
        # Common synonyms for makes
        self.make_synonyms = {
            "chevy": "chevrolet",
            "vw": "volkswagen",
            "mercedes": "mercedes-benz"
        }
        
        # Load part terminology dictionary
        self.part_terms = self._load_part_terms()
        
        # Normalized common part categories for better matching
        self.part_categories = {
            "bumper": ["bumper", "bumper assembly", "bumper cover", "front bumper", "rear bumper", "bumper complete assembly", "front end assembly"],
            "brake": ["brake pad", "brake pads", "brake rotor", "brake rotors", "brake caliper", "brake kit"],
            "filter": ["oil filter", "air filter", "fuel filter", "cabin filter", "filter"],
            "engine": ["engine", "motor", "powertrain"],
            "transmission": ["transmission", "gearbox", "trans"],
            "suspension": ["shock", "strut", "spring", "control arm", "sway bar", "tie rod"],
            "electrical": ["alternator", "battery", "starter", "spark plug", "ignition coil"],
            "cooling": ["radiator", "water pump", "thermostat", "cooling fan", "coolant"],
            "exhaust": ["muffler", "catalytic converter", "exhaust pipe", "exhaust manifold"],
            "fuel": ["fuel pump", "fuel injector", "fuel tank", "fuel line"],
            "steering": ["steering wheel", "steering rack", "power steering", "steering column"],
            "body": ["door", "hood", "trunk", "fender", "quarter panel", "bumper", "mirror", "grille"]
        }
        
        # Common vehicle models by make
        self.make_models = {
            "ford": ["f-150", "f150", "f-250", "f250", "f-350", "f350", "mustang", "explorer", "escape", "fusion", "focus", "edge", "expedition", "ranger", "bronco", "taurus"],
            "chevrolet": ["silverado", "camaro", "malibu", "equinox", "tahoe", "suburban", "colorado", "traverse", "blazer", "impala", "corvette"],
            "chevy": ["silverado", "camaro", "malibu", "equinox", "tahoe", "suburban", "colorado", "traverse", "blazer", "impala", "corvette"],
            "toyota": ["camry", "corolla", "rav4", "highlander", "tacoma", "tundra", "4runner", "sienna", "prius", "avalon", "sequoia", "yaris"],
            "honda": ["civic", "accord", "cr-v", "crv", "pilot", "odyssey", "fit", "hr-v", "hrv", "ridgeline", "passport"],
            "nissan": ["altima", "sentra", "rogue", "maxima", "pathfinder", "murano", "frontier", "titan", "kicks", "versa", "armada"],
            "jeep": ["wrangler", "grand cherokee", "cherokee", "compass", "renegade", "gladiator"]
            # Add more makes and models as needed
        }

        # Model formatting preferences (for more accurate search queries)
        self.model_formatting = {
            "f-150": "F-150",
            "f150": "F-150",
            "f-250": "F-250",
            "f250": "F-250",
            "f-350": "F-350",
            "f350": "F-350"
        }
        
        # Year range patterns for Ford trucks (common fitment ranges)
        self.year_range_patterns = {
            "ford": {
                "f-150": {
                    "2009-2014": "12th generation",
                    "2015-2020": "13th generation",
                    "2004-2008": "11th generation"
                }
            }
        }

    def _load_part_terms(self):
        """Load the expanded part terms dictionary"""
        return {
            # Engine components
            "engine wire harness": "engine wiring harness oem",
            "engine wiring harness": "engine wiring harness oem",
            "wire harness": "wiring harness oem",
            "wiring harness": "wiring harness oem",
            "engine mount": "engine motor mount",
            "timing chain kit": "timing chain set complete",
            "timing belt kit": "timing belt kit with water pump",
            "water pump": "water pump with gasket",
            "fuel pump": "fuel pump assembly oem",
            "high pressure fuel pump": "high pressure fuel pump oem",
            "fuel injector": "fuel injectors set",
            "oil pan": "oil pan with gasket set",
            "thermostat": "thermostat with housing",
            "engine splash shield": "engine splash shield underbody cover",
            
            # Transmission components
            "transmission kit": "transmission rebuild kit complete",
            "transmission oil pipe": "transmission oil cooler lines",
            "transmission hose": "transmission cooler line hose",
            "clutch kit": "clutch kit with flywheel",
            
            # Exterior body parts
            "front bumper": "front bumper cover complete assembly",
            "rear bumper": "rear bumper cover complete assembly",
            "bumper assembly": "bumper complete assembly with brackets",
            "front bumper assembly": "front bumper complete assembly with brackets",
            "chrome bumper": "chrome front bumper complete",
            "fender liner": "fender liner splash shield",
            "headlight": "headlight assembly complete",
            "headlight assembly": "headlight assembly complete oem style",
            "taillight": "tail light assembly complete",
            "grille": "front grille complete assembly",
            "hood": "hood panel assembly",
            "door panel": "door panel complete",
            "mirror": "side mirror assembly",
            "side mirror": "side mirror power assembly complete",
            
            # Brake system
            "brake caliper": "brake caliper with bracket",
            "brake rotor": "brake rotor disc",
            "brake pad": "brake pads set",
            "master cylinder": "brake master cylinder",
            
            # Suspension & Steering
            "control arm": "control arm with ball joint",
            "trailing arm": "trailing arm suspension kit",
            "shock": "shock absorber strut assembly",
            "strut assembly": "strut assembly complete",
            "wheel bearing": "wheel bearing and hub assembly",
            "hub assembly": "wheel hub bearing assembly",
            "power steering": "power steering pump",
            "steering column": "steering column assembly",
            
            # Electrical components
            "alternator": "alternator oem replacement",
            "starter": "starter motor oem",
            "window switch": "power window master switch",
            "master window switch": "power window master control switch",
            
            # HVAC
            "radiator": "radiator complete with fans",
            "radiator assembly": "radiator with fan shroud assembly",
            "ac condenser": "ac condenser with receiver drier",
            "blower motor": "hvac blower motor with fan",
            
            # Wheels
            "rim": "wheel rim replacement",
            "rims": "wheel rims set",
            "hub cap": "hub caps set",
        }
    
    def normalize_query(self, query):
        """Normalize the query text (lowercase, remove excess whitespace, etc.)"""
        if not query:
            return ""
        
        # Convert to lowercase
        query = query.lower()
        
        # Replace special characters with spaces
        query = re.sub(r"[–—]", "-", query)
        
        # Remove common filler words that don't add meaning
        query = re.sub(r"\b(for|a|the|my|an|this|that|to|on|in|with)\b", " ", query)
        
        # Clean up whitespace
        query = re.sub(r"\s+", " ", query).strip()
        
        return query
    
    def extract_vehicle_info(self, query):
        """
        Extract structured vehicle information from query
        Returns a dict with year, make, model, and part
        """
        normalized = self.normalize_query(query)
        
        result = {
            "year": self._extract_year(normalized),
            "make": self._extract_make(normalized),
            "model": self._extract_model(normalized),
            "part": self._extract_part(normalized),
            "position": self._extract_position(normalized),
            "engine_specs": self._extract_engine_specs(normalized),
            "original_query": query,
            "normalized_query": normalized
        }
        
        # Additional fields that might be useful
        result["search_confidence"] = self._calculate_confidence(result)
        
        # Add year range information for specific models (useful for parts compatibility)
        if result["year"] and result["make"] and result["model"]:
            result["year_range"] = self._get_year_range(result["year"], result["make"], result["model"])
        
        return result
    
    def process_structured_data(self, structured_data):
        """
        Process structured data from multi-field input
        Returns a dict with extracted vehicle information
        """
        # Process structured data directly if provided
        result = {
            "year": structured_data.get("year", "").strip(),
            "make": structured_data.get("make", "").strip(),
            "model": structured_data.get("model", "").strip(),
            "part": structured_data.get("part", "").strip(),
            "original_query": "",  # Will be constructed below
            "normalized_query": ""  # Will be constructed below
        }
        
        # Extract engine specs if available
        engine = structured_data.get("engine", "").strip()
        if engine:
            result["engine_specs"] = self._parse_engine_string(engine)
        else:
            result["engine_specs"] = None
        
        # Extract position information from part field (if applicable)
        part = result["part"]
        if part:
            # Check for position indicators in part name
            position_terms = ["front", "rear", "driver", "passenger", "left", "right", "upper", "lower"]
            positions = []
            for term in position_terms:
                if term in part.lower():
                    positions.append(term)
            
            result["position"] = positions if positions else None
        else:
            result["position"] = None
        
        # Construct a normalized query string from structured data
        query_parts = []
        if result["year"]: query_parts.append(result["year"])
        if result["make"]: query_parts.append(result["make"])
        if result["model"]: query_parts.append(result["model"])
        if result["part"]: query_parts.append(result["part"])
        if engine: query_parts.append(engine)
        
        constructed_query = " ".join(query_parts)
        result["original_query"] = constructed_query
        result["normalized_query"] = self.normalize_query(constructed_query)
        
        # Calculate confidence based on fields present
        result["search_confidence"] = self._calculate_structured_confidence(result)
        
        # Add year range information for specific models (useful for parts compatibility)
        if result["year"] and result["make"] and result["model"]:
            result["year_range"] = self._get_year_range(result["year"], result["make"], result["model"])
        
        return result
    
    def _parse_engine_string(self, engine_str):
        """Parse engine string to extract specifications"""
        specs = {}
        
        # Check for displacement
        displacement_match = re.search(r'(\d+\.\d+)L', engine_str, re.IGNORECASE)
        if displacement_match:
            specs["displacement"] = displacement_match.group(0)
        else:
            # Try to match formats like 5.3, 2.0 without the L
            displacement_match = re.search(r'(\d+\.\d+)', engine_str)
            if displacement_match:
                specs["displacement"] = displacement_match.group(0) + "L"
        
        # Check for engine type (V6, V8, I4, etc.)
        engine_type_match = re.search(r'(V[468]|I[346]|Straight[346]|Inline[346])', engine_str, re.IGNORECASE)
        if engine_type_match:
            specs["type"] = engine_type_match.group(0)
        
        # Check for turbo/supercharged
        if re.search(r'turbo', engine_str, re.IGNORECASE):
            specs["forced_induction"] = "turbo"
        elif re.search(r'supercharged', engine_str, re.IGNORECASE):
            specs["forced_induction"] = "supercharged"
        
        # Check for fuel type
        if re.search(r'diesel', engine_str, re.IGNORECASE):
            specs["fuel_type"] = "diesel"
        elif re.search(r'gas|gasoline', engine_str, re.IGNORECASE):
            specs["fuel_type"] = "gas"
        
        return specs if specs else None
    
    def _calculate_structured_confidence(self, result):
        """Calculate confidence score for structured data"""
        confidence = 0
        
        # Add points for each field with data
        if result["year"] and len(result["year"]) == 4:
            confidence += 25
        if result["make"]:
            confidence += 25
        if result["model"]:
            confidence += 20
        if result["part"]:
            confidence += 25
        if result["engine_specs"]:
            confidence += 5
        
        return min(confidence, 100)
    
    def _extract_year(self, query):
        """Extract vehicle year from query"""
        # Match 4-digit years from 1900-2099
        year_match = re.search(r'\b(19|20)\d{2}\b', query)
        if year_match:
            return year_match.group(0)
        
        # Match 2-digit years and convert to 4 digits
        short_year_match = re.search(r'\b\d{2}\b', query)
        if short_year_match:
            year = short_year_match.group(0)
            if int(year) > 50:  # Assume 19xx for years > 50
                return "19" + year
            else:  # Assume 20xx for years <= 50
                return "20" + year
        
        return None
    
    def _extract_make(self, query):
        """Extract vehicle make from query"""
        words = query.split()
        
        # Check for exact make matches
        for make in self.vehicle_makes:
            if make in query.split() or f" {make} " in f" {query} ":
                return make
        
        # Check for synonyms
        for synonym, make in self.make_synonyms.items():
            if synonym in query.split() or f" {synonym} " in f" {query} ":
                return make
        
        return None
    
    def _extract_model(self, query):
        """Extract vehicle model from query"""
        # Get the make first to narrow down model search
        make = self._extract_make(query)
        if not make:
            # Try to extract model without make if possible, but with lower confidence
            for make_name, models in self.make_models.items():
                for model in models:
                    if re.search(r'\b' + re.escape(model) + r'\b', query):
                        return model
            return None
            
        # Check if we have models for this make
        models = self.make_models.get(make, [])
        if not models:
            return None
        
        query_lower = query.lower()
            
        # Try to find models with exact word boundaries first - improved matching
        for model in models:
            if re.search(r'\b' + re.escape(model) + r'\b', query):
                return model
        
        # Then try less strict matching
        for model in models:
            if model in query:
                return model
                
        # Special case handling for F-series trucks due to varying formats (F-150, F150, etc.)
        if make == "ford" and re.search(r'\bf[-\s]?[0-9]{2,3}\b', query, re.IGNORECASE):
            match = re.search(r'\bf[-\s]?([0-9]{2,3})\b', query, re.IGNORECASE)
            if match:
                model_num = match.group(1)
                return f"f-{model_num}"
                
        return None
    
    def _extract_engine_specs(self, query):
        """Extract engine displacement and other specifications"""
        specs = {}
        
        # Extract engine displacement (e.g., 5.3L, 2.0L, 350ci, etc.)
        displacement_match = re.search(r'\b(\d+\.\d+)L\b', query, re.IGNORECASE)
        if displacement_match:
            specs["displacement"] = displacement_match.group(1) + "L"
        else:
            # Try to match formats like 5.3, 2.0 without the L
            displacement_match = re.search(r'\b(\d+\.\d+)\b', query)
            if displacement_match:
                specs["displacement"] = displacement_match.group(1) + "L"
                
        # Look for engine types (V6, V8, I4, etc.)
        engine_type_match = re.search(r'\b(V[468]|I[346]|Straight[346]|Inline[346])\b', query, re.IGNORECASE)
        if engine_type_match:
            specs["type"] = engine_type_match.group(0)
            
        # Look for turbo/supercharged
        if re.search(r'\bturbo\b', query, re.IGNORECASE):
            specs["forced_induction"] = "turbo"
        elif re.search(r'\bsupercharged\b', query, re.IGNORECASE):
            specs["forced_induction"] = "supercharged"
            
        # Look for diesel/gas
        if re.search(r'\bdiesel\b', query, re.IGNORECASE):
            specs["fuel_type"] = "diesel"
        elif re.search(r'\bgas|gasoline\b', query, re.IGNORECASE):
            specs["fuel_type"] = "gas"
            
        return specs if specs else None
    
    def _extract_part(self, query):
        """Extract part information from query"""
        # Check for compound parts first (like "front bumper assembly")
        # This is important to handle multi-word parts correctly
        compound_parts = [
            "front bumper assembly",
            "rear bumper assembly",
            "bumper assembly",
            "headlight assembly",
            "tail light assembly",
            "strut assembly",
            "wheel hub assembly",
            "radiator assembly",
            "engine wire harness",
            "engine wiring harness",
            "front end assembly"
        ]
        
        for part in compound_parts:
            if part in query:
                return part
        
        # Then check for exact matches in part terms dictionary
        for part, replacement in self.part_terms.items():
            pattern = r'\b' + re.escape(part) + r'\b'
            if re.search(pattern, query):
                return part
        
        # Then check for generic part categories
        for category, part_list in self.part_categories.items():
            for part in part_list:
                if part in query:
                    return part
        
        # If no specific part found, try to extract the remainder after vehicle info
        year = self._extract_year(query)
        make = self._extract_make(query)
        model = self._extract_model(query)
        engine_specs = self._extract_engine_specs(query)
        
        if any([year, make, model]):
            # Get what's left after removing vehicle info
            remaining = query
            
            if year:
                remaining = remaining.replace(year, '')
            if make:
                remaining = remaining.replace(make, '')
            if model:
                remaining = remaining.replace(model, '')
            if engine_specs and "displacement" in engine_specs:
                remaining = re.sub(r'\b' + re.escape(engine_specs["displacement"]) + r'\b', '', remaining, flags=re.IGNORECASE)
                
            # Clean up and return what's left as the likely part
            remaining = re.sub(r'\s+', ' ', remaining).strip()
            if remaining:
                return remaining
        
        return None
    
    def _extract_position(self, query):
        """Extract position information like 'front', 'rear', 'driver side', etc."""
        positions = []
        
        position_terms = {
            "front": ["front", "forward"],
            "rear": ["rear", "back"],
            "left": ["left", "driver", "driver's", "driver side"],
            "right": ["right", "passenger", "passenger's", "passenger side"],
            "upper": ["upper", "top"],
            "lower": ["lower", "bottom"],
            "inner": ["inner", "inside"],
            "outer": ["outer", "outside"]
        }
        
        for position, terms in position_terms.items():
            for term in terms:
                pattern = r'\b' + re.escape(term) + r'\b'
                if re.search(pattern, query):
                    positions.append(position)
                    break
        
        return positions if positions else None
    
    def _get_year_range(self, year, make, model):
        """Get the year range for specific model generations"""
        if not all([year, make, model]):
            return None
            
        # Convert to lowercase for lookup
        make_lower = make.lower()
        model_lower = model.lower()
        year_int = int(year)
        
        # Check if we have info for this make/model
        if make_lower in self.year_range_patterns and model_lower in self.year_range_patterns[make_lower]:
            ranges = self.year_range_patterns[make_lower][model_lower]
            
            for year_range, gen_info in ranges.items():
                start_year, end_year = map(int, year_range.split('-'))
                if start_year <= year_int <= end_year:
                    return {
                        "range": year_range,
                        "generation": gen_info
                    }
        
        return None
    
    def _calculate_confidence(self, result):
        """Calculate a confidence score for the extracted information"""
        confidence = 0
        
        # Add points for each field we successfully extracted
        if result["year"]:
            confidence += 25  # Reduced from 30 to account for model
        if result["make"]:
            confidence += 25  # Reduced from 30 to account for model
        if result["model"]:
            confidence += 15  # Add points for model detection
        if result["part"]:
            confidence += 25  # Reduced from 30 to account for model
        if result["position"]:
            confidence += 5   # Reduced from 10 to account for engine specs
        if result["engine_specs"]:
            confidence += 5   # Add points for engine specs
        
        return min(confidence, 100)
    
    def generate_search_terms(self, vehicle_info):
        """
        Generate optimized search terms based on extracted vehicle information
        Returns a list of search terms in decreasing order of specificity
        """
        search_terms = []
        
        year = vehicle_info.get("year")
        make = vehicle_info.get("make")
        model = vehicle_info.get("model")
        part = vehicle_info.get("part")
        position = vehicle_info.get("position")
        engine_specs = vehicle_info.get("engine_specs")
        original_query = vehicle_info.get("original_query", "")
        
        # Format model properly if we have a preferred format
        formatted_model = None
        if model and model.lower() in self.model_formatting:
            formatted_model = self.model_formatting[model.lower()]
        else:
            formatted_model = model
            
        # Format make properly (capitalize)
        formatted_make = make.capitalize() if make else None
        
        # Get engine displacement if available
        engine_disp = None
        if engine_specs and "displacement" in engine_specs:
            engine_disp = engine_specs["displacement"]
        
        # Generate year range if available
        year_range = None
        if "year_range" in vehicle_info and vehicle_info["year_range"]:
            year_range = vehicle_info["year_range"].get("range")
        
        # Generate exact match for the original query (important for precise matching)
        if original_query:
            # Check if query already contains 'oem', if not add it
            if 'oem' not in original_query.lower():
                search_terms.append(f"{original_query} oem")
            else:
                search_terms.append(original_query)
        
        # If we have all information, generate a complete search term
        if year and make and part:
            # Most specific search terms first
            
            # 1. Search term with model properly formatted (very specific)
            if formatted_model:
                term1 = f"{year} {formatted_make} {formatted_model}"
                if position:
                    term1 += f" {' '.join(position)}"
                term1 += f" {part} oem"
                search_terms.append(term1)
            
            # 2. Search term with year range for better compatibility
            if year_range:
                term2 = f"{year_range} {formatted_make}"
                if formatted_model:
                    term2 += f" {formatted_model}"
                if position:
                    term2 += f" {' '.join(position)}"
                term2 += f" {part} oem"
                search_terms.append(term2)
            
            # 3. Search using the part terminology mapping with model
            if part in self.part_terms and formatted_model:
                enhanced_part = self.part_terms[part]
                term3 = f"{year} {formatted_make} {formatted_model}"
                if engine_disp:
                    term3 += f" {engine_disp}"
                term3 += f" {enhanced_part}"
                search_terms.append(term3)
            
            # 4. Fallback to basic year/make/part if we don't have model
            if not formatted_model:
                term4 = f"{year} {formatted_make}"
                if position:
                    term4 += f" {' '.join(position)}"
                term4 += f" {part} oem"
                search_terms.append(term4)
                
                # Also try with enhanced part terms if available
                if part in self.part_terms:
                    enhanced_part = self.part_terms[part]
                    term5 = f"{year} {formatted_make} {enhanced_part}"
                    search_terms.append(term5)
        
        # Fallback search terms with less information
        if make and part and not search_terms:
            term6 = f"{formatted_make}"
            if formatted_model:
                term6 += f" {formatted_model}"
            if year:
                term6 += f" {year}"
            if engine_disp:
                term6 += f" {engine_disp}"
            if position:
                term6 += f" {' '.join(position)}"
            term6 += f" {part} oem"
            
            if term6 not in search_terms:
                search_terms.append(term6)
        
        # If we still don't have enough info, just use the normalized query
        if not search_terms and vehicle_info.get("normalized_query"):
            search_terms.append(vehicle_info.get("normalized_query") + " oem")
        
        # Ensure we have unique search terms
        return list(dict.fromkeys(search_terms))
    
    def process_query(self, query, structured_data=None):
        """
        Main processing function that takes a raw query and returns structured results
        with extracted information and optimized search terms.
        
        Now supports structured data input from multi-field form.
        """
        # Use structured data if provided, otherwise extract from query
        if structured_data:
            vehicle_info = self.process_structured_data(structured_data)
        else:
            vehicle_info = self.extract_vehicle_info(query)
            
        search_terms = self.generate_search_terms(vehicle_info)
        
        result = {
            "vehicle_info": vehicle_info,
            "search_terms": search_terms,
            "confidence": vehicle_info.get("search_confidence", 0)
        }
        
        return result