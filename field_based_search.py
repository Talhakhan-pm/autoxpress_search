"""
Field-Based Search Implementation for Auto Parts

This module provides a field-by-field approach to auto parts search,
building optimized search queries directly from individual field values 
rather than trying to normalize a single search term.

This is the core implementation for the field-based search strategy, which:
1. Uses Year + Make + Model + Part + Engine as primary search terms
2. Falls back to simpler combinations when some fields aren't available
3. Maintains structured vehicle information for consistent processing

See FIELD_BASED_SEARCH.md for detailed documentation on the approach.
"""

class FieldSearchProcessor:
    """
    A simplified processor that takes individual fields and constructs
    optimal search terms without normalization
    """
    
    def __init__(self):
        # Engine types for better matching
        self.engine_types = [
            "v6", "v8", "v10", "v12", "i4", "i6", "v4", "inline 4", "inline 6",
            "straight 6", "boxer", "rotary", "diesel", "turbo", "supercharged", 
            "hybrid", "electric", "gas", "gasoline", "cummins", "powerstroke", 
            "duramax", "ecoboost", "hemi", "ecotec"
        ]
        
        # Engine displacement common units
        self.displacement_patterns = [
            "1.5l", "1.6l", "1.8l", "2.0l", "2.2l", "2.3l", "2.4l", "2.5l", 
            "2.7l", "3.0l", "3.5l", "3.6l", "3.7l", "3.8l", "4.0l", "4.2l", 
            "4.3l", "4.6l", "4.7l", "4.8l", "5.0l", "5.3l", "5.4l", "5.7l", 
            "5.9l", "6.0l", "6.2l", "6.4l", "6.6l", "6.7l", "7.0l", "7.3l", 
            "7.4l", "8.0l", "8.3l"
        ]
        
    def process_fields(self, fields):
        """
        Process individual fields to create structured search terms
        
        Args:
            fields: Dictionary containing year, make, model, part, and engine fields
            
        Returns:
            A dictionary containing search terms and vehicle info
        """
        # Extract fields
        year = fields.get('year', '').strip()
        make = fields.get('make', '').strip()
        model = fields.get('model', '').strip()
        part = fields.get('part', '').strip()
        engine = fields.get('engine', '').strip()
        
        # Validate fields - need at least a part and either year or make
        if not part:
            return {
                "success": False,
                "error": "A part name is required for search"
            }
            
        if not (year or make):
            return {
                "success": False,
                "error": "At least a year or make is required for search"
            }
        
        # Generate search terms based on priority
        search_terms = self._generate_search_terms(year, make, model, part, engine)
        
        # Create vehicle info structure
        vehicle_info = {
            "year": year,
            "make": make,
            "model": model,
            "part": part,
            "engine_specs": self._parse_engine_specs(engine)
        }
        
        # Return structured result
        return {
            "success": True,
            "search_terms": search_terms,
            "vehicle_info": vehicle_info,
            "confidence": 90  # High confidence for field-based search
        }
        
    def _generate_search_terms(self, year, make, model, part, engine):
        """
        Generate search terms based on field priority and combinations
        
        Returns:
            List of search terms in priority order
        """
        search_terms = []
        
        # Priority 1: Year + Make + Model + Part + Engine (if all available)
        if year and make and model and part and engine:
            search_terms.append(f"{year} {make} {model} {part} {engine}")
        
        # Priority 2: Year + Make + Model + Part (if no engine or engine not crucial)
        if year and make and model and part and not engine:
            search_terms.append(f"{year} {make} {model} {part}")
        
        # Priority 3: Year + Model + Part (if make not available)
        if year and model and part and not make:
            search_terms.append(f"{year} {model} {part}")
        
        # Priority 4: Year + Make + Part (if model not available)
        if year and make and part and not model:
            search_terms.append(f"{year} {make} {part}")
        
        # Priority 5: Make + Model + Part (if year not available)
        if make and model and part and not year:
            search_terms.append(f"{make} {model} {part}")
        
        # If engine is specified but we don't have a full search term yet
        if engine and not search_terms:
            # Try to build with available fields + engine
            fields = [f for f in [year, make, model, part] if f]
            if fields:
                search_terms.append(" ".join(fields + [engine]))
        
        # Fallback: use any non-empty fields if no search terms were generated
        if not search_terms:
            fields = [f for f in [year, make, model, part, engine] if f]
            if fields:
                search_terms.append(" ".join(fields))
        
        # Make each term unique
        return list(dict.fromkeys(search_terms))
    
    def _parse_engine_specs(self, engine_text):
        """
        Parse engine specifications from text
        
        Args:
            engine_text: Raw engine text from user input
            
        Returns:
            Dictionary with engine specifications
        """
        if not engine_text:
            return {}
            
        engine_specs = {}
        
        # Look for displacement
        for pattern in self.displacement_patterns:
            if pattern in engine_text.lower():
                engine_specs["displacement"] = pattern
                break
        
        # Look for engine type
        for engine_type in self.engine_types:
            if engine_type in engine_text.lower():
                engine_specs["type"] = engine_type
                break
        
        # If no structured info found, use full text
        if not engine_specs and engine_text:
            engine_specs["raw"] = engine_text
            
        return engine_specs


# Testing
if __name__ == "__main__":
    processor = FieldSearchProcessor()
    
    # Test with complete info
    test1 = processor.process_fields({
        "year": "2015",
        "make": "Toyota",
        "model": "Camry",
        "part": "front bumper",
        "engine": "2.5L"
    })
    
    print("Test 1 (Complete info):")
    print(f"Search Terms: {test1['search_terms']}")
    print(f"Vehicle Info: {test1['vehicle_info']}")
    print()
    
    # Test with minimal info
    test2 = processor.process_fields({
        "year": "2010",
        "make": "",
        "model": "",
        "part": "engine mount",
        "engine": ""
    })
    
    print("Test 2 (Minimal info):")
    print(f"Search Terms: {test2['search_terms']}")
    print(f"Vehicle Info: {test2['vehicle_info']}")
    print()
    
    # Test with engine specs
    test3 = processor.process_fields({
        "year": "2018",
        "make": "Ford",
        "model": "F-150",
        "part": "fuel pump",
        "engine": "3.5L EcoBoost"
    })
    
    print("Test 3 (With engine specs):")
    print(f"Search Terms: {test3['search_terms']}")
    print(f"Vehicle Info: {test3['vehicle_info']}")