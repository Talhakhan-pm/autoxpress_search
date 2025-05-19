import os
import re
import requests
import time
import json
import random
import urllib.parse
import concurrent.futures
import traceback
import difflib
from functools import lru_cache
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI
from vehicle_validation import has_vehicle_info, get_missing_info_message
from query_processor import EnhancedQueryProcessor
from query_templates import get_template_for_message
from chatbot_handler import process_chat_message
from direct_dialpad import DialpadClient  # Using our final implementation
from datetime import datetime, timedelta

load_dotenv()

static_folder = os.path.abspath('static')
app = Flask(__name__, static_folder=static_folder, static_url_path='/static')
app.secret_key = os.getenv("FLASK_SECRET_KEY", os.urandom(24).hex())

api_key = os.getenv("OPENAI_API_KEY")
serpapi_key = os.getenv("SERPAPI_KEY")
client = OpenAI(api_key=api_key)

# Validate required API keys with better error messages
if not api_key:
    raise ValueError(
        "OPENAI_API_KEY is not set in environment variables. "
        "Please add it to your .env file or set it as an environment variable."
    )
if not serpapi_key:
    raise ValueError(
        "SERPAPI_KEY is not set in environment variables. "
        "Please add it to your .env file or set it as an environment variable. "
        "You can obtain a key at https://serpapi.com/"
    )
    
# Validate API key formats
if api_key and not api_key.startswith(('sk-', 'org-')):
    raise ValueError(
        "OPENAI_API_KEY appears to be invalid. "
        "It should start with 'sk-' or 'org-'. Please check your key."
    )

# Initialize our enhanced query processor
query_processor = EnhancedQueryProcessor()

# Enhanced query cleaner that uses our query processor
def clean_query(text):
    """Enhanced query cleaner for better search match with common automotive parts"""
    if not text:
        return ""
    
    # Special case for multi-field form submissions or structued data formats
    # If the text contains clear field markers (year, make, model, part format)
    year_make_model_pattern = r'\b(19|20)\d{2}\s+[A-Za-z]+\s+[A-Za-z0-9-]+\s+'
    if re.search(year_make_model_pattern, text):
        # This looks like a structured query with year, make, model already in place
        # Use it more directly with less normalization
        return text
    
    # Use the query processor to extract structured info
    result = query_processor.process_query(text)
    
    # If we have search terms from the processor, use the first one
    if result["search_terms"] and len(result["search_terms"]) > 0:
        return result["search_terms"][0]
    
    # Otherwise, continue with original logic
    original_text = text
    
    # Normalize dashes and remove filler words
    text = re.sub(r"[–—]", "-", text)
    text = re.sub(r"\bfor\b", "", text, flags=re.IGNORECASE)
    
    # Extract the year, make, and model for later reconstruction
    year_pattern = r'\b(19|20)\d{2}\b'
    year_match = re.search(year_pattern, text)
    year = year_match.group(0) if year_match else ""
    
    # Convert to lowercase for processing
    text_lower = text.lower()
    
    # Expanded part terms dictionary based on your real product data
    part_terms = {
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
        "front bumper assembly": "front bumper complete assembly with brackets",
        "rear bumper": "rear bumper cover complete assembly",
        "bumper assembly": "bumper complete assembly with brackets",
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
    
    # Check for exact part mentions first
    for part, replacement in part_terms.items():
        # Use word boundaries to match complete terms
        pattern = r'\b' + re.escape(part) + r'\b'
        if re.search(pattern, text_lower):
            # Preserve original capitalization if possible
            text = re.sub(pattern, replacement, text_lower, flags=re.IGNORECASE)
            
            # Make sure year and make/model stay with the part
            if year:
                # Remove year and add it to the beginning
                text = re.sub(year_pattern, "", text)
                text = year + " " + text
                
            # Clean up extra spaces
            text = re.sub(r"\s+", " ", text).strip()
            return text
    
    # If we didn't find a specific part pattern match, try to improve the general query
    if "oem" not in text_lower and "aftermarket" not in text_lower:
        # Add OEM for better quality results if it's not an aftermarket search
        if any(word in text_lower for word in ["genuine", "original", "factory"]):
            text += " OEM genuine"
        elif "assembly" in text_lower or "complete" in text_lower:
            text += " complete assembly"
    
    # Trim and clean spaces
    text = re.sub(r"\s+", " ", text).strip()
    
    return text

# VIN decoder helper function with caching (VINs don't change, so cache indefinitely)
@lru_cache(maxsize=500)
def decode_vin(vin):
    """Decode VIN with caching for better performance"""
    if not vin:
        return {}
    try:
        url = f'https://vpic.nhtsa.dot.gov/api/vehicles/decodevinvaluesextended/{vin}?format=json'
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        data = response.json()
        if data and data.get('Results') and len(data['Results']) > 0:
            result = data['Results'][0]
            if result.get('Make') and result.get('ModelYear'):
                # For debugging
                print(f"VIN data retrieved successfully: {result.get('ModelYear')} {result.get('Make')} {result.get('Model')}")
                # Return the whole API response to let client handle the data format
                return data
            else:
                print(f"Invalid VIN data received: Missing Make or ModelYear for VIN {vin}")
                print(f"API returned: {data}")
        else:
            print(f"No results found for VIN {vin}")
            print(f"API returned: {data}")
    except requests.exceptions.RequestException as e:
        print(f"VIN decode request error: {e}")
    except ValueError as e:
        print(f"VIN decode JSON parsing error: {e}")
    except Exception as e:
        print(f"VIN decode unexpected error: {e}")
    return {}

# Cache helper for SerpAPI results
SERPAPI_CACHE = {}
CACHE_EXPIRY = 300  # 5 minutes in seconds

def get_serpapi_cached(engine, query, query_type=None, timestamp=None, **params):
    """
    Better cache implementation for SerpAPI requests with actual TTL expiry.
    Added support for additional params.
    """
    # Create cache key from parameters
    cache_key = f"{engine}:{query}:{query_type}:{sorted(params.items())}"
    
    # Check if we have a cached result that hasn't expired
    current_time = int(time.time())
    if cache_key in SERPAPI_CACHE:
        cached_time, cached_result = SERPAPI_CACHE[cache_key]
        if current_time - cached_time < CACHE_EXPIRY:
            return cached_result
    if engine == "ebay":
        api_params = {
            "engine": "ebay",
            "ebay_domain": "ebay.com",
            "_nkw": query,
            "LH_ItemCondition": "1000" if query_type == "new" else "3000",
            "LH_BIN": "1",  # Buy It Now only
            "api_key": serpapi_key
        }
        
        # Add category parameter if in params
        if "category_id" in params:
            api_params["_sacat"] = params["category_id"]
    elif engine == "google_shopping":
        api_params = {
            "engine": "google_shopping",
            "q": query,
            "google_domain": "google.com",
            "num": 100,  # Request maximum number of results
            "api_key": serpapi_key
        }
        
        # Add product category if specified
        if "product_category" in params:
            api_params["product_category"] = params["product_category"]
    else:
        return {"error": "Invalid engine specified"}
    
    try:
        response = requests.get("https://serpapi.com/search", params=api_params, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        # Store result in cache with current timestamp
        SERPAPI_CACHE[cache_key] = (current_time, result)
        
        # Clean old entries if cache is too large (over 200 items)
        if len(SERPAPI_CACHE) > 200:
            keys_to_remove = []
            for k, (t, _) in SERPAPI_CACHE.items():
                if current_time - t > CACHE_EXPIRY:
                    keys_to_remove.append(k)
            
            # Remove expired items
            for k in keys_to_remove:
                del SERPAPI_CACHE[k]
        
        return result
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {engine} items: {e}")
        if engine == "ebay":
            return {"organic_results": []}
        else:
            return {"shopping_results": []}

def fetch_ebay_results(query_type, query, timestamp=None, part_type=None, structured_data=None):
    """
    Function to fetch eBay results for concurrent execution.
    The timestamp parameter is kept for backward compatibility but no longer used.
    """
    # Get the appropriate eBay category based on part type
    category_id = get_ebay_category_id(part_type) if part_type else None
    
    # Add debug logs to trace structured data
    print(f"[DEBUG] fetch_ebay_results - query: {query}")
    print(f"[DEBUG] fetch_ebay_results - structured_data: {structured_data}")
    
    # If we have structured data with a year, update the query string to make sure it's correct
    if structured_data and isinstance(structured_data, dict) and structured_data.get('year'):
        year = structured_data.get('year')
        make = structured_data.get('make', '')
        model = structured_data.get('model', '')
        part = structured_data.get('part', '')
        
        # Only update the query if it seems to have the wrong year
        if year not in query:
            print(f"[DEBUG] fetch_ebay_results - Fixing query to include correct year {year}")
            # Build an updated query with the correct year
            updated_query = f"{year} {make} {model} {part}".replace("  ", " ").strip()
            query = updated_query
            print(f"[DEBUG] fetch_ebay_results - Updated query: {query}")
    
    params = {}
    if category_id:
        params["category_id"] = category_id
    
    # Note: timestamp is ignored - the get_serpapi_cached function handles TTL internally
    results = get_serpapi_cached("ebay", query, query_type, **params)
    return process_ebay_results(results, query, structured_data, max_items=100)

def get_ebay_category_id(part_type):
    """Get the appropriate eBay category ID for auto parts"""
    # eBay category mappings for auto parts
    category_map = {
        "bumper": "33637",  # Car & Truck Exterior Parts & Accessories
        "front bumper": "33637",
        "bumper assembly": "33637",
        "front bumper assembly": "33637",
        "brake": "33564",  # Car & Truck Brakes
        "engine": "33615",  # Car & Truck Engines & Components
        "transmission": "33615",  # Car & Truck Engines & Components
        "suspension": "33585",  # Car & Truck Suspension & Steering
        "electrical": "33566",  # Car & Truck Electrical Components
        "cooling": "33615",  # Car & Truck Engines & Components
        "exhaust": "33577",  # Car & Truck Exhaust Parts
        "fuel": "33582",  # Car & Truck Air Intake & Fuel Delivery
        "steering": "33585",  # Car & Truck Suspension & Steering
        "body": "33637",  # Car & Truck Exterior Parts & Accessories
        "default": "6030"   # Auto Parts & Accessories
    }
    
    if not part_type:
        return category_map["default"]
    
    # Try to match part type to a category, default to general auto parts if no match
    for key, category in category_map.items():
        if key in part_type.lower():
            return category
    
    return category_map["default"]

def get_ebay_serpapi_results(query, part_type=None, structured_data=None):
    """
    Fetch eBay results using concurrent requests for new and used products.
    Uses part_type parameter to filter by auto parts category.
    """
    # Debugging output to verify the structured data is being passed correctly
    print(f"[DEBUG] eBay search - structured_data: {structured_data}")
    if structured_data and isinstance(structured_data, dict):
        print(f"[DEBUG] eBay search - Using Year from structured data: {structured_data.get('year')}")
    
    # Define tasks for concurrent execution - new and used products
    tasks = [
        ("new", query, None, part_type, structured_data),  # timestamp parameter is now None but kept for API compatibility
        ("used", query, None, part_type, structured_data)
    ]
    
    all_items = []
    
    # Use ThreadPoolExecutor for concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        # Create a mapping of futures to their tasks
        future_to_task = {
            executor.submit(fetch_ebay_results, *task): task[0]
            for task in tasks
        }
        
        # Process results as they complete
        for future in concurrent.futures.as_completed(future_to_task):
            task_type = future_to_task[future]
            try:
                items = future.result()
                all_items.extend(items)
            except Exception as e:
                print(f"Error processing {task_type} items: {e}")
    
    return all_items

def extract_vehicle_info_from_query(query, structured_data=None):
    """
    Extract vehicle information from a query string using the query processor
    
    Args:
        query: The search query text
        structured_data: Optional dictionary with structured field data (from field-based search)
        
    Returns a standardized dictionary with vehicle information that can be used
    for filtering and sorting product listings
    
    NOTE: For single-field search, this function now better handles position terms like
    "front", "rear", "left", "right" and their combinations/abbreviations.
    """
    # If we have structured data from field-based search, prioritize it
    if structured_data and isinstance(structured_data, dict):
        # Directly use the structured field data as our primary source of truth
        vehicle_info = {}
        
        # Copy all available fields from structured data
        if structured_data.get('year'):
            vehicle_info['year'] = structured_data['year']
        if structured_data.get('make'):
            vehicle_info['make'] = structured_data['make']
        if structured_data.get('model'):
            vehicle_info['model'] = structured_data['model']
        
        # Special handling for part field - preserve qualifiers like "front"
        if structured_data.get('part'):
            part = structured_data['part']
            vehicle_info['part'] = part
            
            # Extract position from part if needed (e.g. "front bumper" -> position="front", part="bumper")
            # But in field-based search we want to keep them together in the part field
            position = []
            for pos in ["front", "rear", "left", "right", "driver", "passenger"]:
                if pos in part.lower().split():
                    position.append(pos)
            
            vehicle_info['position'] = position
        else:
            vehicle_info['position'] = []
            
        # Handle engine specs
        if structured_data.get('engine'):
            vehicle_info['engine_specs'] = {
                'raw': structured_data['engine']
            }
        else:
            vehicle_info['engine_specs'] = {}
            
        return {
            "year": vehicle_info.get("year"),
            "make": vehicle_info.get("make"),
            "model": vehicle_info.get("model"),
            "part": vehicle_info.get("part"),
            "position": vehicle_info.get("position"),
            "engine_specs": vehicle_info.get("engine_specs"),
            "confidence": 90  # High confidence for structured data
        }
    
    # Otherwise fall back to query processor extraction
    processed = query_processor.process_query(query)
    vehicle_info = processed.get("vehicle_info", {})
    
    # Return standardized format
    return {
        "year": vehicle_info.get("year"),
        "make": vehicle_info.get("make"),
        "model": vehicle_info.get("model"),
        "part": vehicle_info.get("part"),
        "position": vehicle_info.get("position"),
        "engine_specs": vehicle_info.get("engine_specs"),
        "confidence": processed.get("confidence", 0)
    }

# Add this function to app.py to improve the presentation of search results

def post_process_search_results(listings, vehicle_info):
    """
    Post-processes search results to improve display and highlight exact year matches.
    
    Args:
        listings: The list of product listings
        vehicle_info: The extracted vehicle information
        
    Returns:
        Processed listings with grouping and highlighting
    """
    if not listings or not vehicle_info:
        return listings
    
    # Extract the year we're looking for
    target_year = vehicle_info.get("year")
    if not target_year:
        return listings
    
    # Group listings into categories
    exact_matches = []
    compatible_matches = []
    other_matches = []
    
    for item in listings:
        title = item.get("title", "").lower()
        
        # Check if this is an exact year match
        if re.search(r'\b' + re.escape(target_year) + r'\b', title):
            # Add an "exactYearMatch" flag for frontend highlighting
            item["exactYearMatch"] = True
            item["specialHighlight"] = True
            exact_matches.append(item)
        else:
            # Check for year ranges that include our target year
            year_ranges = re.findall(r'\b(\d{4})[- /](\d{4})\b', title)
            is_compatible = False
            
            for start_year, end_year in year_ranges:
                if int(start_year) <= int(target_year) <= int(end_year):
                    item["compatibleRange"] = f"{start_year}-{end_year}"
                    item["specialHighlight"] = False
                    compatible_matches.append(item)
                    is_compatible = True
                    break
            
            if not is_compatible:
                item["specialHighlight"] = False
                other_matches.append(item)
    
    # Return prioritized results: exact matches first, then compatible, then others
    return exact_matches + compatible_matches + other_matches

def process_ebay_results(results, query, structured_data=None, max_items=100):
    """
    Helper function to process eBay results with improved filtering.
    Now uses less restrictive matching similar to Google Shopping.
    
    Args:
        results: The raw results from SerpAPI
        query: The search query text
        structured_data: Optional structured field data (for field-based search)
        max_items: Maximum number of items to return
    """
    raw_count = len(results.get('organic_results', []))
    print(f"eBay raw results count: {raw_count}")
    processed_items = []
    
    # Debugging counters
    debug_filter_counts = {
        "bumper_guard_filtered": 0,
        "must_match_filtered": 0,
        "total_considered": 0,
        "total_accepted": 0
    }
    
    # Directly use structured data if available, especially the year
    if structured_data and isinstance(structured_data, dict) and structured_data.get('year'):
        print(f"[DEBUG] process_ebay_results - Using structured data directly: {structured_data}")
        year = structured_data.get('year')
        make = structured_data.get('make', '')
        model = structured_data.get('model', '')
        part = structured_data.get('part', '')
        
        vehicle_info = {
            "year": year,
            "make": make, 
            "model": model,
            "part": part
        }
        
        print(f"[DEBUG] process_ebay_results - Prioritizing structured data: Year: {year}, Make: {make}, Model: {model}, Part: {part}")
    else:
        # Extract vehicle info for better filtering with structured data priority
        vehicle_info = extract_vehicle_info_from_query(query, structured_data)
        year = vehicle_info.get("year")
        make = vehicle_info.get("make")
        model = vehicle_info.get("model")
        part = vehicle_info.get("part")
    
    # Debug output vehicle info
    print(f"eBay search - Vehicle info: Year: {year}, Make: {make}, Model: {model}, Part: {part}")
    
    # Create a set of must-match terms for more accurate results
    must_match = set()
    
    # Position term mapping for handling various ways positions are described
    position_mapping = {
        # Left/Right variations
        'left': ['left', 'driver', 'driver side', 'ds', 'lh', 'l/h', 'l/side'],
        'right': ['right', 'passenger', 'passenger side', 'ps', 'rh', 'r/h', 'r/side'],
        # Front/Rear variations
        'front': ['front', 'forward', 'fr', 'f/'],
        'rear': ['rear', 'back', 'rr', 'r/'],
        # Combined positions
        'front left': ['fl', 'front left', 'front driver', 'driver front', 'lf', 'left front'],
        'front right': ['fr', 'front right', 'front passenger', 'passenger front', 'rf', 'right front'],
        'rear left': ['rl', 'rear left', 'rear driver', 'driver rear', 'lr', 'left rear'],
        'rear right': ['rr', 'rear right', 'rear passenger', 'passenger rear', 'rr', 'right rear']
    }
    
    # Part term variations for common parts
    part_variations = {
        'caliper': ['caliper', 'brake caliper', 'disc caliper'],
        'strut': ['strut', 'shock strut', 'strut assembly', 'shock absorber'],
        'rotor': ['rotor', 'brake rotor', 'disc rotor', 'brake disc'],
        'bumper': ['bumper', 'bumper cover', 'bumper assembly', 'front end'],
        'headlight': ['headlight', 'head light', 'headlamp', 'head lamp']
    }
    
    # Process part terms with position awareness
    position_terms = []
    part_terms = []
    
    if part:
        part_lower = part.lower()
        
        # Check for position terms
        for position, variations in position_mapping.items():
            for var in variations:
                if var in part_lower:
                    print(f"Found position term: {var} → {position}")
                    position_terms.append(position)
                    # Remove this position term from the part text to avoid duplication
                    part_lower = part_lower.replace(var, '')
                    break
        
        # Process remaining part words
        for part_word in part_lower.split():
            if len(part_word) > 3 and part_word not in ["with", "for", "the", "and", "of", "a", "an"]:
                # Check if this word is a known part term and add its variations
                added = False
                for base_part, variations in part_variations.items():
                    if part_word in variations or any(var in part_word for var in variations):
                        print(f"Found part variation: {part_word} → {base_part}")
                        must_match.add(base_part)
                        added = True
                        break
                
                # If not a known variation, add as-is
                if not added:
                    must_match.add(part_word)
        
        # Add position terms
        for position in position_terms:
            print(f"Adding position term to must_match: {position}")
            must_match.add(position)
    
    # For makes with compound names or common variants, add alternatives
    make_alternatives = set()
    if make:
        make_lower = make.lower()
        make_alternatives.add(make_lower)
        
        # Common make abbreviations and variations
        make_variants = {
            "mercedes-benz": ["mercedes", "benz", "mb"],
            "mercedes benz": ["mercedes", "benz", "mb"],
            "mercedes": ["mercedes-benz", "benz"],
            "benz": ["mercedes-benz", "mercedes"],
            
            "chevrolet": ["chevy"],
            "chevy": ["chevrolet"],
            
            "volkswagen": ["vw"],
            "vw": ["volkswagen"],
            
            "oldsmobile": ["olds", "cutlass"],
            "olds": ["oldsmobile"],
            "cutlass": ["oldsmobile"],
            
            "pontiac": ["ponti", "firebird", "trans am"],
            "firebird": ["pontiac"],
            "trans am": ["pontiac"],
            
            "mercury": ["merc"],
            "merc": ["mercury"],
            
            "chrysler": ["mopar"],
            "mopar": ["chrysler"],
            
            "plymouth": ["plym", "barracuda", "roadrunner"],
            "plym": ["plymouth"],
            
            "cadillac": ["caddy", "deville", "eldorado"],
            "caddy": ["cadillac"],
            "deville": ["cadillac"],
            "eldorado": ["cadillac"],
            
            "bmw": ["bavarian"],
            
            "toyota": ["toy"],
            
            "mitsubishi": ["mitsu"],
            
            "ford": ["fd"],
            
            "general motors": ["gm"],
            "gm": ["general motors"],
            
            "audi": ["aud"]
        }
        
        # Add all relevant variants
        for variant_key, variant_values in make_variants.items():
            if variant_key in make_lower or any(part in make_lower for part in variant_key.split()):
                for variant in variant_values:
                    make_alternatives.add(variant)
            
    # Add model variations - this is important as sellers use different formats
    model_alternatives = set()
    if model:
        model_lower = model.lower()
        model_alternatives.add(model_lower)
        
        # Handle model variations (with/without dash)
        if "-" in model_lower:
            model_alternatives.add(model_lower.replace("-", ""))
            model_alternatives.add(model_lower.replace("-", " "))
        
        # Special handling for model numbers with/without spaces
        # E.g., 'F 150' vs 'F-150' vs 'F150'
        if re.search(r'[a-z][0-9]', model_lower) or re.search(r'[a-z][ -][0-9]', model_lower):
            # Extract letter and number components
            match = re.search(r'([a-z]+)[ -]?([0-9]+)', model_lower)
            if match:
                letter, number = match.groups()
                model_alternatives.add(f"{letter}{number}")  # F150
                model_alternatives.add(f"{letter}-{number}")  # F-150
                model_alternatives.add(f"{letter} {number}")  # F 150
        
        # Common model abbreviations and variations
        if 'series' in model_lower and not model_lower.endswith('series'):
            series_name = model_lower.replace('series', '').strip()
            model_alternatives.add(series_name)
        
        # For Mercedes models like C240, also try C Class or C-Class
        if model_lower.startswith("c") or model_lower.startswith("e") or model_lower.startswith("s"):
            if any(char.isdigit() for char in model_lower):
                class_letter = model_lower[0]
                model_alternatives.add(f"{class_letter} class")
                model_alternatives.add(f"{class_letter}-class")
        
        # For BMW models like 328i, 535i, add series variations
        bmw_series_match = re.search(r'^([0-9])([0-9]{2}[a-z]?)', model_lower)
        if bmw_series_match:
            series_num = bmw_series_match.group(1)
            model_alternatives.add(f"{series_num}-series")
            model_alternatives.add(f"{series_num} series")
        
        # Specific model variations by make
        if make:
            make_lower = make.lower()
            
            # Ford trucks
            if make_lower == "ford" and any(truck in model_lower for truck in ["f150", "f-150", "f 150"]):
                model_alternatives.add("f150")
                model_alternatives.add("f-150")
                model_alternatives.add("f 150")
                model_alternatives.add("f series")
                model_alternatives.add("f-series")
            
            # Chevy/GMC trucks
            if make_lower in ["chevrolet", "chevy", "gmc"] and "silverado" in model_lower:
                model_alternatives.add("1500")
                model_alternatives.add("2500")
                model_alternatives.add("3500")
                model_alternatives.add("silverado")
            
            # Toyota Camry/Corolla generations
            if make_lower == "toyota" and model_lower == "camry":
                model_alternatives.add("camry se")
                model_alternatives.add("camry le")
                model_alternatives.add("camry xle")
            
            # Add common trim levels for popular models
            common_trims = {
                "accord": ["lx", "ex", "exl", "touring"],
                "civic": ["lx", "ex", "si", "type r"],
                "camry": ["le", "se", "xle", "xse"],
                "corolla": ["le", "se", "xle"],
                "f-150": ["xl", "xlt", "lariat", "king ranch", "platinum"],
                "silverado": ["lt", "ltz", "z71"],
                "ram": ["1500", "2500", "3500"]
            }
            
            # Add trim variations if applicable
            for base_model, trims in common_trims.items():
                if base_model in model_lower:
                    for trim in trims:
                        if not trim in model_lower:  # Only add if not already in model name
                            model_alternatives.add(base_model)  # Add base model without trim
                            model_alternatives.add(f"{base_model} {trim}")  # Add model with trim
    
    # Build must-match set based on what's available
    # We'll require part term matches, but be more flexible with make/model
    if make and model:
        # If we have make and model, require at least one of each alternative sets, plus part
        for part_term in must_match:
            # The part term is required
            break
        else:
            # If no part terms, we still need something
            if len(part) > 3:
                must_match.add(part.lower())
    
    # We'll use these alternatives for more flexible matching
    
    # Debug output the must-match terms
    print(f"eBay search - Must match terms: {must_match}")
    
    # Check if the query is for a bumper assembly
    is_bumper_query = any(term in query.lower() for term in ["bumper", "front end"])
    
    # Set up scoring system for relevance
    for item in results.get("organic_results", []):
        if len(processed_items) >= max_items:
            break
            
        debug_filter_counts["total_considered"] += 1
        title = item.get("title", "").lower()
        
        # Debug: show what we're processing
        if debug_filter_counts["total_considered"] < 5:  # Only show first few for brevity
            print(f"eBay processing item: {title}")
        
        # Skip items that don't match our criteria
        if is_bumper_query and any(x in title for x in ["guard", "protector", "pad", "cover only", "bracket only"]):
            # Skip bumper guards/pads when looking for full bumpers
            if not any(x in title for x in ["assembly", "complete", "front end", "whole bumper"]):
                debug_filter_counts["bumper_guard_filtered"] += 1
                continue
        
        # Skip items that don't match required terms, but be more flexible
        if must_match:
            # First check for part terms with more flexible matching
            part_term_matches = 0
            title_lower = title.lower()
            
            # Check each term in must_match
            for term in must_match:
                # Simple direct match
                if term in title_lower:
                    part_term_matches += 1
                    
                # Check for position term variations
                elif term == "left" and any(x in title_lower for x in ["driver", "driver side", "driver's", "ds", "lh", "l/h", "l/s"]):
                    part_term_matches += 1
                elif term == "right" and any(x in title_lower for x in ["passenger", "passenger side", "passenger's", "ps", "rh", "r/h", "r/s"]):
                    part_term_matches += 1
                elif term == "front" and any(x in title_lower for x in ["forward", "fr", "f/", "front end"]):
                    part_term_matches += 1
                elif term == "rear" and any(x in title_lower for x in ["back", "rr", "r/", "rear end"]):
                    part_term_matches += 1
                    
                # Check for combined position terms
                elif term == "front left" and any(x in title_lower for x in ["fl", "lf", "front driver", "driver front"]):
                    part_term_matches += 1
                elif term == "front right" and any(x in title_lower for x in ["fr", "rf", "front passenger", "passenger front"]):
                    part_term_matches += 1
                elif term == "rear left" and any(x in title_lower for x in ["rl", "lr", "rear driver", "driver rear"]):
                    part_term_matches += 1
                elif term == "rear right" and any(x in title_lower for x in ["rr", "rear passenger", "passenger rear"]):
                    part_term_matches += 1
                
                # Check for common part term variations
                elif term == "caliper" and any(x in title_lower for x in ["brake caliper", "disc caliper", "brake system"]):
                    part_term_matches += 1
                elif term == "rotor" and any(x in title_lower for x in ["brake rotor", "disc rotor", "brake disc", "disc brake"]):
                    part_term_matches += 1
                elif term == "strut" and any(x in title_lower for x in ["shock", "shock absorber", "strut assembly", "suspension"]):
                    part_term_matches += 1
                elif term == "bumper" and any(x in title_lower for x in ["fascia", "front end", "bumper cover", "bumper assembly"]):
                    part_term_matches += 1
                elif term == "headlight" and any(x in title_lower for x in ["head lamp", "headlamp", "head light", "light assembly"]):
                    part_term_matches += 1
                    
            # Then check for make alternatives - we only need at least one to match
            make_match = any(make_alt in title_lower for make_alt in make_alternatives) if make_alternatives else True
            
            # Also check for model alternatives - we only need at least one to match
            model_match = any(model_alt in title_lower for model_alt in model_alternatives) if model_alternatives else True
            
            # For year, check if it's in the title OR in a range that includes our year
            year_match = False
            if year:
                if year in title:
                    year_match = True
                else:
                    # Check for year ranges (e.g., 2001-2007, 01-07, etc.)
                    year_ranges = re.findall(r'(\d{4})\s*[-–—]\s*(\d{4})', title)
                    for start_year, end_year in year_ranges:
                        if int(start_year) <= int(year) <= int(end_year):
                            year_match = True
                            break
                    
                    # Also check shortened year formats (e.g., 01-07 for 2001-2007)
                    short_ranges = re.findall(r'(\d{2})\s*[-–—]\s*(\d{2})', title)
                    for start_yr, end_yr in short_ranges:
                        # Convert to full year (assuming 21st or 20th century)
                        start_full = int("20" + start_yr if int(start_yr) < 50 else "19" + start_yr)
                        end_full = int("20" + end_yr if int(end_yr) < 50 else "19" + end_yr)
                        if start_full <= int(year) <= end_full:
                            year_match = True
                            break
            else:
                year_match = True  # No year specified, so any match
            
            # Much more lenient part term matching - require only 25% of terms to match
            # For example, if we have 4 part terms, require only 1 to match
            min_required_part_matches = max(1, len(must_match) // 4)
            
            # Debug: show more detailed matching information for first few items
            if debug_filter_counts["total_considered"] < 5:
                print(f"  - Product title: {title}")
                print(f"  - Must match terms: {must_match}")
                print(f"  - Part matches: {part_term_matches}, Make match: {make_match}, Model match: {model_match}, Year match: {year_match}")
                print(f"  - Min required part matches: {min_required_part_matches}")
                
                # Show which position terms were recognized, if any
                position_terms = [term for term in must_match if term in ["front", "rear", "left", "right", "front left", "front right", "rear left", "rear right"]]
                if position_terms:
                    print(f"  - Position terms: {position_terms}")
            
            # Define what makes a good match based on what's available - much more flexible now
            if part_term_matches >= min_required_part_matches:
                # If we have enough matching part terms, require at least one of: year, make, or model
                if not (year_match or make_match or model_match):
                    debug_filter_counts["must_match_filtered"] += 1
                    continue
            else:
                # If very few part matches, we require at least two of: year, make, model
                matches_count = sum([year_match, make_match, model_match])
                if matches_count < 2:
                    debug_filter_counts["must_match_filtered"] += 1
                    continue
                
            # Debug: show matching details for first few items
            if debug_filter_counts["total_considered"] < 5:
                print(f"  - Part matches: {part_term_matches}, Make match: {make_match}, Model match: {model_match}, Year match: {year_match}")
            
        # Extract price
        price = "Price not available"
        if isinstance(item.get("price"), dict):
            price = item.get("price", {}).get("raw", "Price not available")
        else:
            price = item.get("price", "Price not available")
            
        # Extract shipping
        shipping = "Shipping not specified"
        if isinstance(item.get("shipping"), dict):
            shipping = item.get("shipping", {}).get("raw", "Shipping not specified")
        else:
            shipping = item.get("shipping", "Shipping not specified")
            
        # Extract condition
        condition = item.get("condition", "Not specified")
        
        # Extract thumbnail image if available
        thumbnail = item.get("thumbnail", "")
            
        processed_items.append({
            "title": item.get("title"),
            "price": price,
            "shipping": shipping,
            "condition": condition,
            "link": item.get("link"),
            "source": "eBay",
            "image": thumbnail
        })
        
        debug_filter_counts["total_accepted"] += 1
    
    # Print debug summary
    print(f"eBay filtering summary:")
    print(f"  - Total raw results: {raw_count}")
    print(f"  - Total considered: {debug_filter_counts['total_considered']}")
    print(f"  - Bumper guard filtered: {debug_filter_counts['bumper_guard_filtered']}")
    print(f"  - Must-match filtered: {debug_filter_counts['must_match_filtered']}")
    print(f"  - Total accepted: {debug_filter_counts['total_accepted']}")
    print(f"eBay processed results count: {len(processed_items)}")
    
    return processed_items

def get_google_shopping_results(query, part_type=None, structured_data=None):
    """
    Fetch Google Shopping results with improved category filtering.
    Now accepts structured_data parameter directly to ensure consistency.
    """
    # Debug log for structured data
    print(f"[DEBUG] get_google_shopping_results - query: {query}")
    print(f"[DEBUG] get_google_shopping_results - structured_data passed in: {structured_data}")
    
    # Map part types to Google product categories
    product_category = None
    
    # If structured_data wasn't passed directly, try to get it from the request
    if not structured_data:
        structured_data_json = request.form.get("structured_data", "") if hasattr(request, 'form') else None
        if structured_data_json:
            try:
                structured_data = json.loads(structured_data_json)
                print(f"[DEBUG] get_google_shopping_results - structured_data from form: {structured_data}")
            except:
                pass
    
    # If we have structured data with a year but the query doesn't have it, update the query
    if structured_data and isinstance(structured_data, dict) and structured_data.get('year'):
        year = structured_data.get('year')
        if year not in query:
            print(f"[DEBUG] get_google_shopping_results - Fixing query to include correct year {year}")
            make = structured_data.get('make', '')
            model = structured_data.get('model', '') 
            part = structured_data.get('part', '')
            updated_query = f"{year} {make} {model} {part}".replace("  ", " ").strip()
            query = updated_query
            print(f"[DEBUG] get_google_shopping_results - Updated query: {query}")
    
    vehicle_info = extract_vehicle_info_from_query(query, structured_data)
    
    # Special handling for bumpers
    if part_type and "bumper" in part_type.lower():
        # For bumpers, explicitly add product category and expand query
        product_category = "5613"  # Vehicle Parts & Accessories
        
        # Create a more specific query for Google Shopping
        if vehicle_info.get("year") and vehicle_info.get("make") and vehicle_info.get("model"):
            year = vehicle_info.get("year")
            make = vehicle_info.get("make")
            model = vehicle_info.get("model")
            
            # Simplify make name for better search results
            simple_make = make
            if "mercedes" in make.lower():
                simple_make = "Mercedes"
            elif "chevrolet" in make.lower():
                simple_make = "Chevy"  
            elif "volkswagen" in make.lower():
                simple_make = "VW"
            
            # Simplify model for better matches (e.g., C240 -> C)
            simple_model = model
            if any(char.isdigit() for char in model):
                # For Mercedes models like C240, E350, etc.
                if "mercedes" in make.lower() and len(model) <= 4 and (model[0].lower() in 'cels'):
                    # Extract just the letter prefix (C, E, S, etc.)
                    prefix = model[0]
                    if prefix:
                        simple_model = prefix
                # For BMW models like 328i, 535i, etc.
                elif "bmw" in make.lower() and model[0].isdigit():
                    # Keep first digit (3, 5, 7, etc.)
                    simple_model = model[0] + " series"
            
            # Check if we already have position information in the part_type (e.g. "front bumper")
            position_prefix = ""
            if "front" in part_type.lower():
                position_prefix = "front "
            elif "rear" in part_type.lower():
                position_prefix = "rear "
                
            # Use position-specific bumper query if we have position info, or default to front bumper
            if position_prefix:
                bumper_query = f"{year} {simple_make} {simple_model} {position_prefix}bumper complete assembly"
            else:
                bumper_query = f"{year} {simple_make} {simple_model} front bumper complete assembly"  # Default to front if unspecified
            
            # Use this more precise query instead
            print(f"[DEBUG] Specialized bumper query: {bumper_query}")
            print(f"[DEBUG]   - Using year: {year}")
            print(f"[DEBUG]   - Using make: {make} (simplified to: {simple_make})")
            print(f"[DEBUG]   - Using model: {model} (simplified to: {simple_model})")
            print(f"[DEBUG]   - Using position: {position_prefix.strip() if position_prefix else 'default front'}")
            query = bumper_query
    elif part_type and "engine" in part_type.lower():
        product_category = "5613"  # Vehicle Parts & Accessories
    
    params = {}
    if product_category:
        params["product_category"] = product_category
    
    # Get cached results - the get_serpapi_cached function handles TTL internally
    results = get_serpapi_cached("google_shopping", query, **params)
    
    return process_google_shopping_results(results, query, max_items=100)

def process_google_shopping_results(results, query, max_items=100):
    """Process Google Shopping results with improved filtering"""
    processed_items = []
    
    # Extract vehicle info for better filtering
    vehicle_info = extract_vehicle_info_from_query(query)
    year = vehicle_info.get("year")
    make = vehicle_info.get("make")
    model = vehicle_info.get("model")
    part = vehicle_info.get("part")
    
    # Build a list of keywords to match
    keywords = query.lower().split()
    
    # Create a set of must-match terms for more accurate results
    must_match = set()
    
    # Add part terms as must-match with better filtering
    if part:
        part_lower = part.lower()
        
        # Skip common stop words and keep only meaningful terms
        stop_words = ["with", "for", "the", "and", "of", "a", "an", "to", "in", "on", "at"]
        
        for part_word in part_lower.split():
            if len(part_word) > 3 and part_word not in stop_words:
                must_match.add(part_word)
    
    # Check if the query is for a bumper assembly
    is_bumper_query = any(term in query.lower() for term in ["bumper", "front end"])
    
    for item in results.get("shopping_results", []):
        if len(processed_items) >= max_items:
            break
        
        title = item.get("title", "").lower()
        
        # Skip items that don't match our criteria
        if is_bumper_query and any(x in title for x in ["guard", "protector", "pad", "cover only", "bracket only"]):
            # Skip bumper guards/pads when looking for full bumpers
            if not any(x in title for x in ["assembly", "complete", "front end", "whole bumper"]):
                continue
        
        # Skip items that don't match any must-match terms (less restrictive)
        if must_match:
            # For Google Shopping, match if at least 25% of terms match to include more results
            matching_terms = sum(1 for term in must_match if term in title)
            required_matches = max(1, len(must_match) / 4)  # At least 1 or 25% of terms
            if matching_terms < required_matches:
                continue
        
        # If we have year/make/model, at least one should appear in the title (less restrictive)
        if year and make and model:
            # Accept results if any of year, make, or model appears in the title
            if (year not in title) and (make.lower() not in title) and (model.lower() not in title):
                continue
        
        # Extract and fix the link with improved error handling
        link = None
        
        # Try different possible structures for the link
        if item.get("link") and isinstance(item.get("link"), str) and item.get("link").startswith("http"):
            link = item.get("link")
        elif item.get("product_link") and isinstance(item.get("product_link"), str) and item.get("product_link").startswith("http"):
            link = item.get("product_link")
        elif item.get("link_text") and isinstance(item.get("link_text"), str) and item.get("link_text").startswith("http"):
            link = item.get("link_text")
        elif isinstance(item.get("link_object"), dict):
            potential_link = item.get("link_object", {}).get("link", "")
            if isinstance(potential_link, str) and potential_link.startswith("http"):
                link = potential_link
        
        # If still no link, create a more reliable Google search link
        if not link or link == "" or not isinstance(link, str) or not link.startswith("http"):
            product_title = item.get("title", "").replace(" ", "+")
            link = f"https://www.google.com/search?q={product_title}&tbm=shop"
        
        processed_items.append({
            "title": item.get("title"),
            "price": item.get("price", "Price not available"),
            "shipping": item.get("shipping", "Shipping not specified"),
            "condition": "New",  # Google Shopping typically shows new items
            "source": "Google Shopping",
            "link": link,  # Fixed link
            "image": item.get("thumbnail", "")
        })
    
    return processed_items
# Main route - original version for regular form submission
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Regular form submission just renders the template
        return render_template("index.html")
    return render_template("index.html")

# AI function to extract part information from search results
def extract_part_info_with_ai(part_number, search_results, include_alt=False):
    """
    Use OpenAI to extract structured part information from search results
    """
    # Create a detailed prompt with clear instructions
    prompt = f"""
You are an automotive parts expert assistant. I need your help to extract detailed information about an automotive part based on search results.

Part Number: {part_number}

Search Results:
{search_results}

Based on the search results, please extract the following information about this part number:
1. Part Name: The common name of this specific part (e.g., "Oil Cooler Tube", "Spark Plug", "Brake Pad")
2. Part Type: What type of automotive part is this? (Examples: Air Filter, Brake Pad, Oil Filter, Alternator, etc.)
3. Manufacturer: Who makes this part? Is it OEM or aftermarket?
4. Description: A brief (1-2 sentence) description of what this part is and what it does.
5. Vehicle Compatibility: List of vehicles (make, model, years) this part is compatible with. Provide at least 3-5 if available.
6. Alternative Part Numbers: List any cross-reference or alternative part numbers mentioned.

Format your response as a valid JSON object with these keys:
{{
  "part_name": "string",
  "part_type": "string",
  "manufacturer": "string",
  "description": "string",
  "compatibility": ["string", "string", "..."],
  "alternative_numbers": ["string", "string", "..."]
}}

IMPORTANT: 
- If information is not available, use reasonable defaults based on the part number.
- Make sure the JSON is valid - use double quotes and escape internal quotes if needed.
- For compatibility, format as "YEAR MAKE MODEL" (Example: "2015-2020 Toyota Camry").
- Don't include any explanations outside the JSON object.
"""

    try:
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",  # Or your preferred model
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3
        )

        # Extract JSON from response
        result_text = response.choices[0].message.content.strip()
        
        # Parse JSON
        result = json.loads(result_text)
        
        # Ensure all expected keys are present
        if "part_name" not in result:
            result["part_name"] = "Automotive Part"
        if "part_type" not in result:
            result["part_type"] = "Automotive Part"
        if "manufacturer" not in result:
            result["manufacturer"] = "Unknown"
        if "description" not in result:
            result["description"] = f"{part_number} - {result.get('part_type', 'Automotive Part')}"
        if "compatibility" not in result:
            result["compatibility"] = []
        if "alternative_numbers" not in result:
            result["alternative_numbers"] = []
        
        return result
    
    except Exception as e:
        print(f"Error extracting part information with AI: {e}")
        # Return a default structure in case of error
        return {
            "part_name": "Automotive Part",
            "part_type": "Automotive Part",
            "manufacturer": "Unknown",
            "description": f"{part_number} - Automotive Part",
            "compatibility": [],
            "alternative_numbers": []
        }

# Function to get part number search results via SerpAPI
def get_part_number_search_results(part_number, include_oem=True, exclude_wholesalers=False):
    """
    Fetch actual search results for a part number using Google Search via SerpAPI
    Returns search results snippet text that can be used for AI processing
    """
    query = part_number
    
    # Add OEM if requested
    if include_oem:
        query += " OEM automotive part"
    else:
        query += " automotive part"
    
    # Exclude wholesaler sites if requested
    if exclude_wholesalers:
        query += " -wholesaler -distributor"
    
    # Set up params for SerpAPI
    api_params = {
        "engine": "google",
        "q": query,
        "google_domain": "google.com",
        "num": 10,  # Top 10 results should be enough
        "api_key": serpapi_key
    }
    
    try:
        # Make the API request
        response = requests.get("https://serpapi.com/search", params=api_params, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        # Extract organic results
        organic_results = result.get("organic_results", [])
        
        # Format the results for processing by GPT
        formatted_results = []
        for i, res in enumerate(organic_results, 1):
            title = res.get("title", "")
            snippet = res.get("snippet", "")
            link = res.get("link", "")
            formatted_results.append(f"[{i}] {title}\nURL: {link}\nDescription: {snippet}\n")
        
        # Return joined text for GPT processing
        return "\n".join(formatted_results)
    
    except Exception as e:
        print(f"Error fetching search results: {e}")
        return ""

# Part number search route
@app.route("/api/part-number-search", methods=["POST"])
def part_number_search():
    """Search for part number information using AI and Google search results"""
    part_number = sanitize_input(request.form.get("part_number", ""))
    include_oem = request.form.get("include_oem", "true") == "true"
    include_alt = request.form.get("include_alt", "true") == "true"
    exclude_wholesalers = request.form.get("exclude_wholesalers", "false") == "true"
    auto_search_listings = request.form.get("auto_search_listings", "false") == "true"
    
    if not part_number:
        return jsonify({
            "success": False,
            "error": "No part number provided"
        })
    
    # Log the search for analytics
    print(f"Part number search: {part_number} (OEM: {include_oem}, Alt: {include_alt}, ExclWhole: {exclude_wholesalers})")
    
    try:
        # Generate search URLs for different platforms
        google_search_url = generate_google_search_url(part_number, include_oem, exclude_wholesalers)
        amazon_search_url = f"https://www.amazon.com/s?k={part_number}&i=automotive-intl-ship"
        ebay_search_url = f"https://www.ebay.com/sch/i.html?_nkw={part_number}&_sacat=6000"
        rockauto_search_url = f"https://www.rockauto.com/en/partsearch/?partnum={part_number}"
        
        # Get real search results from Google via SerpAPI
        search_results = get_part_number_search_results(part_number, include_oem, exclude_wholesalers)
        
        # Default values in case AI processing fails
        part_type = "Automotive Part"
        manufacturer = "Unknown"
        description = f"{part_number} - Automotive Part"
        compatibility = []
        alt_numbers = []
        
        # Process with AI if we have search results
        ai_processed = False
        part_name = "Automotive Part"  # Default part name
        
        if search_results:
            try:
                # Use AI to extract part information from search results
                part_info = extract_part_info_with_ai(part_number, search_results, include_alt)
                
                # Extract information from AI response if successful
                part_name = part_info.get("part_name", "Automotive Part")
                part_type = part_info.get("part_type", "Automotive Part")
                manufacturer = part_info.get("manufacturer", "Unknown")
                description = part_info.get("description", f"{part_number} - {part_type}")
                compatibility = part_info.get("compatibility", [])
                
                # Only use AI's alternative numbers if requested
                if include_alt:
                    alt_numbers = part_info.get("alternative_numbers", [])
                
                ai_processed = True
                print(f"Successfully processed part {part_number} with AI")
            except Exception as ai_error:
                print(f"AI processing failed for part {part_number}: {ai_error}")
                # We'll fall back to pattern guessing below
        
        # Fallback to pattern guessing if no search results or AI processing failed
        if not ai_processed:
            part_type = guess_part_type(part_number)
            manufacturer = guess_manufacturer(part_number)
            part_name = part_type  # Use part type as fallback part name
            description = f"{part_number} - {part_type} for various vehicle applications"
            
            # Generate some compatibility data
            compatibility = generate_compatibility_data(part_number)
            
            # Generate alternative part numbers if requested
            if include_alt:
                alt_numbers = generate_alternative_numbers(part_number)
        
        # Return the structured part information
        return jsonify({
            "success": True,
            "partNumber": part_number,
            "partName": part_name,
            "partType": part_type,
            "description": description,
            "manufacturer": manufacturer,
            "compatibility": compatibility,
            "alternativeNumbers": alt_numbers,
            "ai_enhanced": ai_processed,
            "searchUrls": {
                "google": google_search_url,
                "amazon": amazon_search_url,
                "ebay": ebay_search_url,
                "rockauto": rockauto_search_url
            }
        })
    except Exception as e:
        print(f"Error in part number search: {e}")
        return jsonify({
            "success": False,
            "error": "An error occurred processing your request"
        })

def generate_google_search_url(part_number, include_oem=True, exclude_wholesalers=False):
    """
    Generate a clean Google search URL for a part number
    Simply searches for the part number itself with no additional terms
    """
    # Just use the part number as-is, no additional terms or operators
    # URL encode the query
    encoded_query = urllib.parse.quote(part_number)

    # Return the simple search URL
    return f"https://www.google.com/search?q={encoded_query}"

@app.route("/api/part-number-listings", methods=["POST"])
def part_number_listings():
    """Search for product listings using part numbers"""
    part_number = sanitize_input(request.form.get("part_number", ""))
    alt_numbers = request.form.get("alt_numbers", "[]")
    part_type = sanitize_input(request.form.get("part_type", "Automotive Part"))

    if not part_number:
        return jsonify({
            "success": False,
            "error": "No part number provided"
        })

    try:
        # Parse alternative part numbers if provided
        alt_numbers_list = []
        try:
            alt_numbers_list = json.loads(alt_numbers)

            # Ensure it's a list and has no more than 3 items to avoid excessive API usage
            if not isinstance(alt_numbers_list, list):
                alt_numbers_list = []

            # Limit to 3 alternative part numbers
            alt_numbers_list = alt_numbers_list[:3]
        except:
            # If parsing fails, assume no alternatives
            alt_numbers_list = []

        # Log the search
        print(f"Part number listings search: {part_number}, Alternatives: {alt_numbers_list}")

        # Create a list of part numbers to search (primary + alternatives)
        search_part_numbers = [part_number] + alt_numbers_list

        # Initialize collection for listings
        all_listings = []

        # Get listings for each part number (primary first, then alternatives)
        for search_part in search_part_numbers:
            # Try to get listings from eBay first (faster and more reliable)
            try:
                # Include both original part number and a clean version (without hyphens/symbols)
                clean_search_part = re.sub(r'[^a-zA-Z0-9]', '', search_part)
                if clean_search_part != search_part:
                    formatted_search_part = f"{search_part} {clean_search_part}"
                else:
                    formatted_search_part = search_part

                ebay_results = get_ebay_serpapi_results(formatted_search_part, part_type)

                # Add source information to each listing
                for listing in ebay_results:
                    # Add information about which part number found this listing
                    listing["source_part"] = search_part
                    # Add a flag to indicate if this is from the primary part number
                    listing["is_primary"] = (search_part == part_number)

                    # Add to our results
                    all_listings.append(listing)

                # If we already have enough results, stop
                if len(all_listings) >= 20:
                    break
            except Exception as ebay_err:
                print(f"Error searching eBay for part {search_part}: {ebay_err}")

            # If we don't have enough results yet, also try Google Shopping
            if len(all_listings) < 10:
                try:
                    # Include both original part number and a clean version (without hyphens/symbols)
                    clean_search_part = re.sub(r'[^a-zA-Z0-9]', '', search_part)
                    if clean_search_part != search_part:
                        formatted_search_part = f"{search_part} {clean_search_part}"
                    else:
                        formatted_search_part = search_part

                    google_results = get_google_shopping_results(formatted_search_part, part_type)

                    # Add source information to each listing
                    for listing in google_results:
                        # Add information about which part number found this listing
                        listing["source_part"] = search_part
                        # Add a flag to indicate if this is from the primary part number
                        listing["is_primary"] = (search_part == part_number)

                        # Add to our results - only if we don't already have a similar listing
                        # Simple deduplication by checking title similarity
                        title_lower = listing["title"].lower()

                        # Check if this listing is similar to any existing one
                        is_duplicate = False
                        for existing in all_listings:
                            existing_title = existing["title"].lower()
                            # If titles are 80% similar, consider it a duplicate
                            if similar_strings(title_lower, existing_title, 0.8):
                                is_duplicate = True
                                break

                        if not is_duplicate:
                            all_listings.append(listing)

                    # If we have enough results, stop
                    if len(all_listings) >= 20:
                        break
                except Exception as google_err:
                    print(f"Error searching Google for part {search_part}: {google_err}")

        # Sort listings - primary part number listings first, then by price
        all_listings.sort(key=lambda x: (not x.get("is_primary", False), get_price_value(x.get("price", ""))))

        # Limit total number of listings to return (max 20)
        return jsonify({
            "success": True,
            "part_number": part_number,
            "alt_numbers": alt_numbers_list,
            "listings": all_listings[:20],
            "total": len(all_listings[:20])
        })
    except Exception as e:
        print(f"Error in part number listings search: {e}")
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": "An error occurred while searching for product listings. Please try again."
        })

# Helper function to check string similarity for deduplication
def similar_strings(str1, str2, threshold=0.8):
    """Check if two strings are similar enough using difflib"""
    if not str1 or not str2:
        return False

    # For very short strings, use simple matching
    if len(str1) < 10 or len(str2) < 10:
        return str1 in str2 or str2 in str1

    # For longer strings, use sequence matching
    return difflib.SequenceMatcher(None, str1, str2).ratio() > threshold

# Helper function to extract numeric price value for sorting
def get_price_value(price_str):
    """Extract numeric price value from price string"""
    if not price_str:
        return float('inf')  # Unknown prices go to the end

    # Remove non-numeric characters, keeping only digits and decimal point
    price_str = re.sub(r'[^0-9.]', '', price_str)

    try:
        return float(price_str)
    except:
        return float('inf')  # If conversion fails, move to the end

def guess_part_type(part_number):
    """Guess the part type based on part number patterns"""
    part_number_lower = part_number.lower()
    
    # Common part number prefixes
    if part_number_lower.startswith(('ac', 'air')):
        return "Air Conditioning Component"
    elif part_number_lower.startswith(('br', 'brake')):
        return "Brake Component"
    elif part_number_lower.startswith(('alt', 'altr')):
        return "Alternator"
    elif part_number_lower.startswith(('eng', 'mot')):
        return "Engine Component"
    elif part_number_lower.startswith(('oil', 'lub')):
        return "Oil System Component"
    elif part_number_lower.startswith(('tr', 'trans')):
        return "Transmission Component"
    elif part_number_lower.startswith(('sus', 'spr')):
        return "Suspension Component"
    elif part_number_lower.startswith(('exh', 'muf')):
        return "Exhaust Component"
    elif part_number_lower.startswith(('int', 'cab')):
        return "Interior Component"
    elif part_number_lower.startswith(('ele', 'elc')):
        return "Electrical Component"
    elif part_number_lower.startswith(('fil', 'flt')):
        return "Filter"
    elif part_number_lower.startswith(('sen', 'sns')):
        return "Sensor"
    
    # Default
    return "Automotive Part"

def guess_manufacturer(part_number):
    """Guess the manufacturer based on part number patterns"""
    part_number_lower = part_number.lower()
    
    # Common manufacturer prefixes
    if part_number_lower.startswith(('toy', 'to-')):
        return "Toyota"
    elif part_number_lower.startswith(('hon', 'ho-')):
        return "Honda"
    elif part_number_lower.startswith('bmw'):
        return "BMW"
    elif part_number_lower.startswith(('mb', 'mer')):
        return "Mercedes-Benz"
    elif part_number_lower.startswith(('for', 'fd-')):
        return "Ford"
    elif part_number_lower.startswith(('gm', 'chev')):
        return "General Motors"
    elif part_number_lower.startswith(('mo', 'chr')):
        return "Mopar/Chrysler"
    elif part_number_lower.startswith(('vw', 'audi')):
        return "Volkswagen/Audi"
    elif part_number_lower.startswith(('nis', 'ns-')):
        return "Nissan"
    elif part_number_lower.startswith(('sub', 'sb-')):
        return "Subaru"
    
    # Default
    return "OEM or Aftermarket"

def generate_compatibility_data(part_number):
    """Generate mock compatibility data based on part number"""
    # This would be replaced with actual database lookups or API calls
    # For this demo, we generate plausible compatibility based on patterns
    
    make = ""
    if "toy" in part_number.lower():
        make = "Toyota"
    elif "hon" in part_number.lower():
        make = "Honda"
    elif "for" in part_number.lower():
        make = "Ford"
    elif "gm" in part_number.lower() or "chev" in part_number.lower():
        make = "Chevrolet"
    else:
        # If no pattern match, pick a random make
        makes = ["Toyota", "Honda", "Ford", "Chevrolet", "Nissan", "BMW", "Mercedes"]
        make = random.choice(makes)
    
    # Generate 2-4 compatible vehicle models
    result = []
    
    if make == "Toyota":
        models = ["Camry", "Corolla", "RAV4", "Highlander", "Tacoma"]
        years = [y for y in range(2015, 2023)]
    elif make == "Honda":
        models = ["Civic", "Accord", "CR-V", "Pilot", "Odyssey"]
        years = [y for y in range(2016, 2023)]
    elif make == "Ford":
        models = ["F-150", "Escape", "Explorer", "Focus", "Mustang"]
        years = [y for y in range(2015, 2022)]
    elif make == "Chevrolet":
        models = ["Silverado", "Malibu", "Equinox", "Traverse", "Tahoe"]
        years = [y for y in range(2016, 2023)]
    elif make == "Nissan":
        models = ["Altima", "Rogue", "Sentra", "Pathfinder", "Frontier"]
        years = [y for y in range(2017, 2023)]
    elif make == "BMW":
        models = ["3 Series", "5 Series", "X3", "X5", "7 Series"]
        years = [y for y in range(2016, 2023)]
    elif make == "Mercedes":
        models = ["C-Class", "E-Class", "GLC", "GLE", "S-Class"]
        years = [y for y in range(2016, 2023)]
    else:
        models = ["Model A", "Model B", "Model C"]
        years = [y for y in range(2018, 2023)]
    
    # Select 2-4 models
    selected_models = random.sample(models, min(len(models), random.randint(2, 4)))
    
    for model in selected_models:
        # For each model, select either a single year or a range
        if random.choice([True, False]):
            # Single year
            year = random.choice(years)
            result.append(f"{year} {make} {model}")
        else:
            # Year range
            start_year = random.choice(years[:-2])  # Avoid picking the last 2 years as start
            end_idx = years.index(start_year) + random.randint(1, min(4, len(years) - years.index(start_year) - 1))
            end_year = years[end_idx]
            result.append(f"{start_year}-{end_year} {make} {model}")
    
    return result

def generate_alternative_numbers(part_number):
    """Generate alternative part numbers based on the original"""
    # In a real app, this would look up cross-references from a database
    # For this demo, we generate plausible alternatives
    
    # Remove any non-alphanumeric characters
    base = re.sub(r'[^a-zA-Z0-9]', '', part_number)
    
    # Generate alternatives
    alternatives = []
    
    # Different format with dashes
    if len(base) >= 6:
        alt1 = f"{base[:3]}-{base[3:]}"
        alternatives.append(alt1)
    
    # Manufacturer variations
    if not any(prefix in part_number.lower() for prefix in ['ac', 'alt', 'oil']):
        manufacturers = ['AC', 'TYT', 'DL', 'NAPA']
        mfr = random.choice(manufacturers)
        alt2 = f"{mfr}{base[-4:]}"
        alternatives.append(alt2)
    
    # Similar number with slight variation
    digits = re.findall(r'\d+', part_number)
    if digits:
        # Get the longest numeric part
        longest_digit = max(digits, key=len)
        # Modify one digit
        digit_list = list(longest_digit)
        pos_to_change = random.randint(0, len(digit_list) - 1)
        old_digit = digit_list[pos_to_change]
        # Ensure we change to a different digit
        new_digit = str(random.randint(0, 9))
        while new_digit == old_digit:
            new_digit = str(random.randint(0, 9))
        digit_list[pos_to_change] = new_digit
        new_digit_part = ''.join(digit_list)
        
        # Replace the original digit part with modified one
        alt3 = part_number.replace(longest_digit, new_digit_part)
        alternatives.append(alt3)
    
    return alternatives

# Callback form route
@app.route("/callbacks.html", methods=["GET"])
def callbacks():
    return render_template("callbacks.html")

# Order form route
@app.route("/orders.html", methods=["GET"])
def orders():
    return render_template("orders.html")

# Sanitize user input with comprehensive security
def sanitize_input(text):
    """
    Thoroughly sanitize user input to prevent XSS and other injection attacks.
    Handles HTML entities, tags, control characters, and restricts to safe character set.
    """
    if not text:
        return ""
        
    # Convert to string in case we get a non-string input
    text = str(text)
    
    # First pass: handle HTML entities and tags
    text = re.sub(r'<[^>]*>', '', text)  # Remove all HTML tags
    
    # Convert special characters to HTML entities to prevent XSS
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&#x27;')
    
    # Second pass: keep only allowed characters using a strict whitelist
    # This includes alphanumeric, whitespace, and common punctuation
    allowed_pattern = r'[\w\s\-.,?!@#$%^&*()_+=[\]{}|:;<>"/]'
    sanitized = ''.join(c for c in text if re.match(allowed_pattern, c))
    
    # Third pass: remove all control characters including null bytes, escape sequences, etc.
    sanitized = re.sub(r'[\x00-\x1F\x7F]', '', sanitized)
    
    # Fourth pass: normalize whitespace (replace multiple spaces with a single space)
    sanitized = re.sub(r'\s+', ' ', sanitized)
    
    return sanitized.strip()

# New endpoint for advanced query parsing
@app.route("/api/parse-query", methods=["POST"])
def parse_query():
    """Parse a query and return structured vehicle information"""
    query = sanitize_input(request.form.get("prompt", ""))
    
    if not query:
        return jsonify({
            "success": False,
            "error": "Empty query"
        })
    
    # Process the query
    result = query_processor.process_query(query)
    
    # Add result metadata
    timestamp = time.time()
    result["timestamp"] = timestamp
    result["query"] = query
    
    return jsonify({
        "success": True,
        "parsed_data": result
    })

# AJAX endpoint for GPT analysis (separated from product search)
@app.route("/api/analyze", methods=["POST"])
def analyze_query():
    """Analyze the query using GPT-4 and return optimized search terms"""
    query = sanitize_input(request.form.get("prompt", ""))
    parsed_data_json = request.form.get("parsed_data", "")
    structured_data_json = request.form.get("structured_data", "")
    
    # Try to parse the JSON if provided - first check parsed_data, then structured_data
    processed_result = None
    
    # Try parsing parsed_data first (from original format)
    if parsed_data_json:
        try:
            processed_result = json.loads(parsed_data_json)
        except:
            # If parsing fails, we'll process it again
            pass
            
    # If no parsed_data or parsing failed, try structured_data (from field-based search)
    if not processed_result and structured_data_json:
        try:
            structured_data = json.loads(structured_data_json)
            
            # If we have structured field data, use it to enhance the query
            if structured_data and isinstance(structured_data, dict):
                # If we have year/make/model/part, format it directly
                if structured_data.get('year') and structured_data.get('part'):
                    # This is a valid field-based search, format our query to prioritize what matters
                    vehicle_info = {}
                    
                    # Extract all fields with validation
                    if structured_data.get('year'):
                        vehicle_info['year'] = structured_data['year']
                    if structured_data.get('make'):
                        vehicle_info['make'] = structured_data['make']
                    if structured_data.get('model'):
                        vehicle_info['model'] = structured_data['model']
                    if structured_data.get('part'):
                        vehicle_info['part'] = structured_data['part']
                    
                    # Add empty position array for compatibility
                    vehicle_info['position'] = []
                    
                    # Handle engine specs
                    if structured_data.get('engine'):
                        vehicle_info['engine_specs'] = {'raw': structured_data['engine']}
                        
                    # Build search terms from structured data
                    search_terms = []
                    
                    # First priority: year + make + model + part + engine (if all available)
                    if all(k in vehicle_info for k in ['year', 'make', 'model', 'part']) and 'engine_specs' in vehicle_info:
                        full_term = f"{vehicle_info['year']} {vehicle_info['make']} {vehicle_info['model']} {vehicle_info['part']} {vehicle_info['engine_specs']['raw']}"
                        search_terms.append(full_term)
                    
                    # Second priority: year + make + model + part (without engine)
                    if all(k in vehicle_info for k in ['year', 'make', 'model', 'part']):
                        simple_term = f"{vehicle_info['year']} {vehicle_info['make']} {vehicle_info['model']} {vehicle_info['part']}"
                        if simple_term not in search_terms:
                            search_terms.append(simple_term)
                            
                    # Add fallback term if needed
                    if not search_terms and 'year' in vehicle_info and 'part' in vehicle_info:
                        fallback_term = f"{vehicle_info['year']} {vehicle_info.get('make', '')} {vehicle_info.get('model', '')} {vehicle_info['part']}".replace('  ', ' ').strip()
                        search_terms.append(fallback_term)
                    
                    # Create a complete result structure
                    processed_result = {
                        "search_terms": search_terms,
                        "vehicle_info": vehicle_info,
                        "confidence": 90  # High confidence for structured input
                    }
        except Exception as e:
            print(f"Error parsing structured data: {e}")
            # Continue with normal query processing
    
    if not query:
        return jsonify({
            "success": False,
            "validation_error": "Please enter a valid search query."
        })
    
    # Process with our query processor if needed
    if not processed_result:
        processed_result = query_processor.process_query(query)
    
    # Always use GPT-4 for high-quality and detailed responses
    # Check if query has sufficient vehicle information
    if not has_vehicle_info(query):
        validation_error = get_missing_info_message(query)
        return jsonify({
            "success": False,
            "validation_error": validation_error
        })

    # Extract model for prompt
    model_info = ""
    if processed_result.get("vehicle_info") and processed_result["vehicle_info"].get("model"):
        model_info = f"Model: {processed_result['vehicle_info']['model']}"

    prompt = f"""
You are an auto parts fitment expert working for a US-based parts sourcing company. The goal is to help human agents quickly identify the correct OEM part for a customer's vehicle.

The customer just said: "{query}"

Do not provide explanations, summaries, or filler text. Format everything in direct, clean bullet points.

Your job is to:
1. If anything is misspelled, auto-correct it to the best of your automotive knowledge.

2. Validate:
   - Confirm the vehicle exists in the US market.
   - If invalid, return:
     👉 This vehicle is not recognized in US-spec. Please clarify. Did you mean one of these: [list 2–3 real US models for that year/make]?
   - If valid, do NOT confirm it in a sentence. Just move on.

3. If valid:
   - List factory trims with engine options (displacement + type + drivetrain).
   - DO NOT repeat parsed info in sentence form

4. Price Range Analysis:
   - Provide a clear price range for this part based on market data
   - Format as: 💲 Expected Price Range: $XXX - $XXX
   - Distinguish between OEM and aftermarket pricing if applicable
   - For OEM parts format as: 💲 OEM Price Range: $XXX - $XXX
   - For aftermarket parts format as: 💲 Aftermarket Price Range: $XXX - $XXX
   - Indicate if the part is typically expensive or a good value

5. Ask follow-up questions, max 3:
   - Question 1: Ask about directly associated hardware needed (e.g., bumper → brackets, fog trims, sensors if applicable)
   - Question 2: Only ask follow-up if something affects fitment — like transmission type, submodel, or drivetrain. 
    Do NOT ask vague or unnecessary questions like modifications or preferences.
   - Fitment: If fitment is shared across multiple years, mention the range with platform/chassis code — you can take a guess if needed. Just say it out. No worries. 
   - If more products are involved, you can ask more questions, max 2.

6. Finish with a bolded search-optimized lookup phrase, (add a emoji of world right before the phrase):
   - Format: lowercase string including [year or range] + make + model + trim (if needed) + engine (if relevant) + oem + part name
   - Think of it as a search term for a customer to find the part. Use the most relevant keywords. Give two search terms for the same part with another name.
   - Example 1:  "🔎 2020–2022 honda civic ex oem front bumper"
   - Example 2: "🔎 2020 – 2022 honda civic ex oem bumper cover"

Here's some additional information that might help you:
Year: {processed_result["vehicle_info"].get("year") or "not specified"}
Make: {processed_result["vehicle_info"].get("make") or "not specified"}
{model_info}
Part: {processed_result["vehicle_info"].get("part") or "not specified"}
Position: {processed_result["vehicle_info"].get("position", "not specified")}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )

        questions = response.choices[0].message.content.strip()

        # Use GPT-generated search term if available, else fallback to processed query
        search_lines = [line for line in questions.split("\n") if "🔎" in line]

        if search_lines:
            # Extract the search term without the emoji
            search_term_raw = search_lines[0].replace("🔎", "").strip()
            
            # Remove any added "Fits" or year ranges that GPT might add
            search_term_raw = re.sub(r'\(Fits \d{4}-\d{4}\)', '', search_term_raw).strip()
            
            # Remove OEM since it's making the search terms too restrictive for eBay
            search_term_raw = search_term_raw.replace(" oem ", " ").replace(" OEM ", " ")
            
            # Remove "complete assembly" since we add it later for specific parts
            search_term_raw = search_term_raw.replace(" complete assembly", "").replace(" assembly", "")
            
            # Clean up any excessive spaces
            search_term_raw = re.sub(r'\s+', ' ', search_term_raw).strip()
            
            # Clean and optimize the search term
            search_term = clean_query(search_term_raw)
            
            # If there's a second search term, use it as a fallback
            fallback_term = None
            if len(search_lines) > 1:
                fallback_raw = search_lines[1].replace("🔎", "").strip()
                # Apply the same cleaning to the fallback term
                fallback_raw = re.sub(r'\(Fits \d{4}-\d{4}\)', '', fallback_raw).strip()
                fallback_raw = fallback_raw.replace(" oem ", " ").replace(" OEM ", " ")
                fallback_raw = fallback_raw.replace(" complete assembly", "").replace(" assembly", "")
                fallback_raw = re.sub(r'\s+', ' ', fallback_raw).strip()
                fallback_term = clean_query(fallback_raw)
        else:
            # Fallback to processor's search terms if no GPT search term
            if processed_result["search_terms"]:
                search_term = processed_result["search_terms"][0]
                fallback_term = processed_result["search_terms"][1] if len(processed_result["search_terms"]) > 1 else None
            else:
                # Last resort: just clean the original query
                search_term = clean_query(query)
                fallback_term = None

        return jsonify({
            "success": True,
            "questions": questions,
            "search_terms": [search_term, fallback_term] if fallback_term else [search_term]
        })
    except Exception as e:
        print(f"API error: {e}")
        
        # Fallback to our processor if GPT fails
        if processed_result["search_terms"]:
            search_terms = processed_result["search_terms"]
            model_text = ""
            if processed_result["vehicle_info"]["model"]:
                model = processed_result["vehicle_info"]["model"]
                if model.lower() in ["f-150", "f150", "f-250", "f250", "f-350", "f350"]:
                    model_text = f" {model.upper()}"
                else:
                    model_text = f" {model}"
                
            questions = f"""
- Vehicle: {processed_result["vehicle_info"]["year"] or ""} {(processed_result["vehicle_info"]["make"] or "").capitalize()}{model_text}
- Part: {processed_result["vehicle_info"]["part"] or ""}

Question 1: Do you need any associated hardware with this part?

🔎 {search_terms[0]}
"""
            if len(search_terms) > 1:
                questions += f"\n🔎 {search_terms[1]}"
                
            return jsonify({
                "success": True,
                "questions": questions,
                "search_terms": search_terms,
                "processed_locally": True
            })
        else:
            return jsonify({
                "success": False,
                "error": "An error occurred while processing your request. Please try again later."
            })

# AJAX endpoint for product search
def prioritize_exact_part_matches(listings, part_query):
    """
    Prioritizes listings that exactly match the user's part query.
    
    Args:
        listings: List of product listings
        part_query: The specific part the user searched for (e.g., "engine")
        
    Returns:
        Sorted list with exact matches first
    """
    print(f"Prioritizing {len(listings)} listings for part: '{part_query}'")
    
    exact_complete_matches = []
    exact_matches = []
    related_matches = []
    other_matches = []
    
    # Clean the part query
    clean_part = part_query.lower().strip()
    
    # Words that indicate a complete/full part
    complete_indicators = ["complete", "assembly", "full", "entire", "oem", "motor", "assembly", "unit", "module"]
    
    # Words that indicate parts or accessories
    part_indicators = ["cap", "cover", "filter", "sensor", "switch", "gasket", "seal", "bolt", "nut", "harness", "wire"]
    
    # Special case for engines
    engine_indicators = []
    if clean_part == "engine":
        engine_indicators = ["complete engine", "engine assembly", "motor assembly", 
                         "long block", "short block", "engine motor", "complete motor"]
    
    for item in listings:
        title = item.get("title", "").lower()
        
        # Special case for engines
        if clean_part == "engine" and any(indicator in title for indicator in engine_indicators):
            item["matchType"] = "exact_complete"
            item["priorityScore"] = 150  # Higher priority for complete engines
            item["isExactMatch"] = True
            exact_complete_matches.append(item)
            continue  # Skip other checks
        
        # Check for exact part name match with word boundaries
        if re.search(r'\b' + re.escape(clean_part) + r'\b', title):
            # Check if it's likely a complete part
            if any(indicator in title for indicator in complete_indicators):
                item["matchType"] = "exact_complete"
                item["priorityScore"] = 100
                item["isExactMatch"] = True
                exact_complete_matches.append(item)
            # Check if it's likely just a small part of the main component
            elif any(indicator in title for indicator in part_indicators):
                item["matchType"] = "related"
                item["priorityScore"] = 50
                item["isExactMatch"] = False
                related_matches.append(item)
            else:
                item["matchType"] = "exact"
                item["priorityScore"] = 80
                item["isExactMatch"] = True
                exact_matches.append(item)
        # Check if part name is mentioned but not as an exact match
        elif clean_part in title:
            item["matchType"] = "related"
            item["priorityScore"] = 40
            item["isExactMatch"] = False
            related_matches.append(item)
        else:
            item["matchType"] = "other"
            item["priorityScore"] = 10
            item["isExactMatch"] = False
            other_matches.append(item)
    
    print(f"Found {len(exact_complete_matches)} exact complete matches, {len(exact_matches)} exact matches, {len(related_matches)} related matches")
    
    # Return prioritized results
    return exact_complete_matches + exact_matches + related_matches + other_matches

@app.route("/api/search-products", methods=["POST"])
def search_products():
    """Search for products using the provided search term with pagination support"""
    search_term = sanitize_input(request.form.get("search_term", ""))
    original_query = sanitize_input(request.form.get("original_query", ""))
    page = int(request.form.get("page", "1"))
    page_size = int(request.form.get("page_size", "24"))  # Default to 24 products per page
    
    # Debug logs for identifying field vs single field search
    print(f"[DEBUG] search_products - search_term: {search_term}")
    print(f"[DEBUG] search_products - original_query: {original_query}")
    
    if not search_term:
        return jsonify({
            "success": False,
            "error": "No search term provided"
        })
    
    try:
        # Parse structured data if provided
        structured_data = None
        structured_data_json = request.form.get("structured_data", "")
        
        if structured_data_json:
            try:
                structured_data = json.loads(structured_data_json)
                print(f"[DEBUG] search_products - Received structured data: {structured_data}")
                
                # Validate and ensure all fields are properly formatted
                if structured_data and isinstance(structured_data, dict):
                    # Ensure year is a string
                    if 'year' in structured_data and structured_data['year']:
                        structured_data['year'] = str(structured_data['year']).strip()
                        print(f"[DEBUG] search_products - Validated year: {structured_data['year']}")
                    
                    # Ensure other fields are strings
                    for field in ['make', 'model', 'part', 'engine']:
                        if field in structured_data and structured_data[field]:
                            structured_data[field] = str(structured_data[field]).strip()
                
            except Exception as e:
                print(f"Error parsing structured data in search-products: {e}")
                # Continue with regular processing
        
        # Extract vehicle info for filtering with structured data priority
        vehicle_info = extract_vehicle_info_from_query(original_query or search_term, structured_data)
        part_type = vehicle_info.get("part")
        
        # Debug output for testing our vehicle info extraction
        print(f"[DEBUG] Field-based search: Using structured data: {structured_data is not None}")
        print(f"[DEBUG] Vehicle info extracted: Year: {vehicle_info.get('year')}, Make: {vehicle_info.get('make')}, Model: {vehicle_info.get('model')}, Part: {vehicle_info.get('part')}")
        
        # Add special case handling for engines and other major parts
        if part_type:
            if "engine" in part_type.lower():
                # Create a more specific search term for engines
                if vehicle_info.get("year") and vehicle_info.get("make") and vehicle_info.get("model"):
                    year = vehicle_info.get("year")
                    make = vehicle_info.get("make")
                    model = vehicle_info.get("model")
                    
                    # Simplify make name for better search results
                    simple_make = make
                    if "mercedes" in make.lower():
                        simple_make = "Mercedes"
                    elif "chevrolet" in make.lower():
                        simple_make = "Chevy"  
                    elif "volkswagen" in make.lower():
                        simple_make = "VW"
                    
                    # Simplify model for better matches (e.g., C240 -> C)
                    simple_model = model
                    if any(char.isdigit() for char in model):
                        # For Mercedes models like C240, E350, etc.
                        if "mercedes" in make.lower() and len(model) <= 4 and (model[0].lower() in 'cels'):
                            # Extract just the letter prefix (C, E, S, etc.)
                            prefix = model[0]
                            if prefix:
                                simple_model = prefix
                        # For BMW models like 328i, 535i, etc.
                        elif "bmw" in make.lower() and model[0].isdigit():
                            # Keep first digit (3, 5, 7, etc.)
                            simple_model = model[0] + " series"
                    
                    engine_term = f"{year} {simple_make} {simple_model} complete engine motor assembly"
                    print(f"Using engine-specific search term: {engine_term}")
                    print(f"   - Using simplified make: {simple_make}")
                    print(f"   - Using simplified model: {simple_model}")
                    search_term = engine_term
            elif "bumper" in part_type.lower() and "assembly" not in part_type.lower():
                # For bumpers, ensure we're searching for complete assemblies
                # Preserve any position qualifiers from the part_type
                position_prefix = ""
                if "front" in part_type.lower():
                    position_prefix = "front "
                elif "rear" in part_type.lower():
                    position_prefix = "rear "
                
                # Get year, make, model from vehicle_info
                year_val = vehicle_info.get("year")
                make_val = vehicle_info.get("make")
                model_val = vehicle_info.get("model")
                
                # Simplify make name for better search results
                simple_make = make_val
                if make_val and "mercedes" in make_val.lower():
                    simple_make = "Mercedes"
                elif make_val and "chevrolet" in make_val.lower():
                    simple_make = "Chevy"  
                elif make_val and "volkswagen" in make_val.lower():
                    simple_make = "VW"
                
                # Simplify model for better matches (e.g., C240 -> C)
                simple_model = model_val
                if model_val and any(char.isdigit() for char in model_val):
                    # For Mercedes models like C240, E350, etc.
                    if make_val and "mercedes" in make_val.lower() and len(model_val) <= 4 and (model_val[0].lower() in 'cels'):
                        # Extract just the letter prefix (C, E, S, etc.)
                        prefix = model_val[0]
                        if prefix:
                            simple_model = prefix
                    # For BMW models like 328i, 535i, etc.
                    elif make_val and "bmw" in make_val.lower() and model_val[0].isdigit():
                        # Keep first digit (3, 5, 7, etc.)
                        simple_model = model_val[0] + " series"
                
                if year_val and simple_make and simple_model:
                    # If we have complete vehicle info, create an optimized bumper query
                    bumper_term = f"{year_val} {simple_make} {simple_model} {position_prefix}bumper complete assembly"
                    print(f"   - Using simplified make: {simple_make}")
                    print(f"   - Using simplified model: {simple_model}")
                else:
                    # Otherwise enhance the search term
                    bumper_term = f"{search_term} complete assembly"
                
                print(f"Using bumper-specific search term: {bumper_term}")
                search_term = bumper_term
            elif any(x in part_type.lower() for x in ["transmission", "gearbox"]):
                # For transmissions
                # Get year, make, model from vehicle_info
                year_val = vehicle_info.get("year")
                make_val = vehicle_info.get("make")
                model_val = vehicle_info.get("model")
                
                # Simplify make name for better search results
                simple_make = make_val
                if make_val and "mercedes" in make_val.lower():
                    simple_make = "Mercedes"
                elif make_val and "chevrolet" in make_val.lower():
                    simple_make = "Chevy"  
                elif make_val and "volkswagen" in make_val.lower():
                    simple_make = "VW"
                
                # Simplify model for better matches (e.g., C240 -> C)
                simple_model = model_val
                if model_val and any(char.isdigit() for char in model_val):
                    # For Mercedes models like C240, E350, etc.
                    if make_val and "mercedes" in make_val.lower() and len(model_val) <= 4 and (model_val[0].lower() in 'cels'):
                        # Extract just the letter prefix (C, E, S, etc.)
                        prefix = model_val[0]
                        if prefix:
                            simple_model = prefix
                    # For BMW models like 328i, 535i, etc.
                    elif make_val and "bmw" in make_val.lower() and model_val[0].isdigit():
                        # Keep first digit (3, 5, 7, etc.)
                        simple_model = model_val[0] + " series"
                
                if year_val and simple_make and simple_model:
                    # If we have complete vehicle info, create an optimized transmission query
                    trans_term = f"{year_val} {simple_make} {simple_model} transmission complete assembly"
                    print(f"Using transmission-specific search term: {trans_term}")
                    print(f"   - Using simplified make: {simple_make}")
                    print(f"   - Using simplified model: {simple_model}")
                else:
                    # Otherwise enhance the search term
                    trans_term = f"{search_term} complete assembly"
                    print(f"Using transmission-specific search term: {trans_term}")
                
                search_term = trans_term
        
        # Try multiple search strategies (fallbacks if needed)
        all_listings = []
        
        # Determine if this is a field-based search with specific fields
        is_field_search = False
        cleaner_search_term = search_term
        
        # Parse original query for vehicle info if available
        if original_query:
            vehicle_info = extract_vehicle_info_from_query(original_query, structured_data)
            year = vehicle_info.get("year")
            make = vehicle_info.get("make")
            model = vehicle_info.get("model")
            part = vehicle_info.get("part")
        else:
            # When no original_query, try extracting from search_term
            vehicle_info = extract_vehicle_info_from_query(search_term, structured_data)
            year = vehicle_info.get("year")
            make = vehicle_info.get("make")
            model = vehicle_info.get("model")
            part = vehicle_info.get("part")
            
            # If we have fairly complete vehicle info, assume it's a field-based search
            if year and part and (make or model):
                is_field_search = True
                # Create a simpler search term for eBay based on what we have
                if year and model and part and make:
                    # For Mercedes-Benz, simplify to just Mercedes
                    if "mercedes" in make.lower():
                        simple_make = "Mercedes"
                    else:
                        simple_make = make
                        
                    # For model, just use the base part without numbers for better matches
                    # Examples: "C240" -> "C", "F-150" -> "F"
                    simple_model = model
                    if any(char.isdigit() for char in model):
                        # Extract just the letter prefix (C, E, S, F, etc.)
                        prefix = ''.join(c for c in model if not c.isdigit() and c != '-').strip()
                        if prefix:
                            simple_model = prefix
                    
                    simple_term = f"{year} {simple_make} {simple_model} {part}".replace("  ", " ").strip()
                elif year and part:
                    # Year + Part fallback (sometimes works better)
                    simple_term = f"{year} {part}"
                else:
                    simple_term = f"{year} {make} {model} {part}".replace("  ", " ").strip()
                    
                print(f"Using simpler search term for eBay: {simple_term}")
                cleaner_search_term = simple_term
                
        # Strategy 1: Direct search with term
        # Debug log for field-based search
        print(f"[DEBUG] search_products - Using search terms:")
        print(f"[DEBUG]   - cleaner_search_term: {cleaner_search_term}")
        print(f"[DEBUG]   - search_term: {search_term}")
        print(f"[DEBUG]   - structured_data: {structured_data}")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            # For eBay, use the cleaner search term without special characters/formatting
            # Always pass structured_data to ensure correct year is used
            ebay_future = executor.submit(get_ebay_serpapi_results, cleaner_search_term, part_type, structured_data)
            google_future = executor.submit(get_google_shopping_results, search_term, part_type, structured_data)
            
            ebay_listings = ebay_future.result()
            google_listings = google_future.result()
            
            # Prioritize Google listings by adding them first
            all_listings.extend(google_listings)
            all_listings.extend(ebay_listings)
        
        # If we have too few Google Shopping results for certain parts, try again with a simpler term
        if part_type and len(google_listings) < 3 and ("bumper" in part_type.lower() or "engine" in part_type.lower()):
            # Create a very simple search term
            if vehicle_info.get("year") and vehicle_info.get("make"):
                simple_term = f"{vehicle_info.get('year')} {vehicle_info.get('make')} {part_type}"
                print(f"Too few Google results, trying simplified term: {simple_term}")
                
                # Try a direct Google Shopping search with minimal filtering
                backup_results = get_serpapi_cached("google_shopping", simple_term)
                backup_items = []
                
                # Process with very minimal filtering
                for item in backup_results.get("shopping_results", []):
                    title = item.get("title", "").lower()
                    
                    # Only the most basic filtering
                    if vehicle_info.get("make") and vehicle_info.get("make").lower() not in title:
                        continue
                        
                    # Extract link and other details with proper validation
                    link = None
                    
                    # Try different possible structures for the link with validation
                    if item.get("link") and isinstance(item.get("link"), str) and item.get("link").startswith("http"):
                        link = item.get("link")
                    elif item.get("product_link") and isinstance(item.get("product_link"), str) and item.get("product_link").startswith("http"):
                        link = item.get("product_link")
                    elif item.get("link_text") and isinstance(item.get("link_text"), str) and item.get("link_text").startswith("http"):
                        link = item.get("link_text")
                    elif isinstance(item.get("link_object"), dict):
                        potential_link = item.get("link_object", {}).get("link", "")
                        if isinstance(potential_link, str) and potential_link.startswith("http"):
                            link = potential_link
                    
                    # If still no link, create a more reliable Google search link
                    if not link or link == "" or not isinstance(link, str) or not link.startswith("http"):
                        product_title = item.get("title", "").replace(" ", "+")
                        link = f"https://www.google.com/search?q={product_title}&tbm=shop"
                    
                    backup_items.append({
                        "title": item.get("title"),
                        "price": item.get("price", "Price not available"),
                        "shipping": item.get("shipping", "Shipping not specified"),
                        "condition": "New",  # Google Shopping typically shows new items
                        "source": "Google Shopping",
                        "link": link,
                        "image": item.get("thumbnail", "")
                    })
                
                # Append these items to our list
                all_listings.extend(backup_items)
                print(f"Added {len(backup_items)} additional Google Shopping items")
        
        # If we don't have enough results, try with a simplified search
        if len(all_listings) < 8 and original_query:
            # Extract core information
            info = extract_vehicle_info_from_query(original_query)
            if info["year"] and info["make"] and info["part"]:
                # Create a simpler search term
                simple_term = f"{info['year']} {info['make']} {info['part']}"
                if info["model"]:
                    simple_term = f"{info['year']} {info['make']} {info['model']} {info['part']}"
                
                print(f"Not enough results with original search. Trying simplified term: {simple_term}")
                
                # Try the simpler search term - prioritize Google Shopping
                print(f"[DEBUG] search_products - Fallback using simpler term: {simple_term}")
                print(f"[DEBUG] search_products - Fallback still using original structured data: {structured_data}")
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                    google_future = executor.submit(get_google_shopping_results, simple_term, part_type, structured_data)
                    ebay_future = executor.submit(get_ebay_serpapi_results, simple_term, part_type, structured_data)
                    
                    google_listings = google_future.result()
                    ebay_listings = ebay_future.result()
                    
                    # Add only new unique listings with improved deduplication, adding Google results first
                    existing_keys = {}  # Track existing items by both title and source
                    for idx, item in enumerate(all_listings):
                        # Create a composite key of title + first words of title for fuzzy matching
                        title_lower = item["title"].lower()
                        first_words = ' '.join(title_lower.split()[:5]) if title_lower else ""
                        key = (first_words, item.get("source", ""))
                        existing_keys[key] = idx
                    
                    # Process new items with better deduplication
                    for item in ebay_listings + google_listings:
                        title_lower = item["title"].lower()
                        first_words = ' '.join(title_lower.split()[:5]) if title_lower else ""
                        item_source = item.get("source", "")
                        key = (first_words, item_source)
                        
                        # If this exact item doesn't exist yet, add it
                        if key not in existing_keys:
                            all_listings.append(item)
                            existing_keys[key] = len(all_listings) - 1
        
        # If still not enough results and this is a bumper search, try an even more specific search
        if len(all_listings) < 12 and part_type and "bumper" in part_type.lower():
            # Extract vehicle info for specialized searches
            info = extract_vehicle_info_from_query(original_query or search_term)
            
            # For Ford F-series trucks, try a direct bumper assembly search
            if info["make"] and info["make"].lower() == "ford" and info["model"] and "f-" in info["model"].lower():
                direct_term = f"{info['year']} Ford {info['model'].upper()} front bumper assembly OEM"
            
            # Special case for classic/older vehicles
            elif info["year"] and int(info["year"]) < 2000:
                # For older vehicles, try a more specific search directly on eBay
                # eBay tends to have better inventory for classic car parts
                year_range_start = max(int(info["year"]) - 3, 1960)
                year_range_end = min(int(info["year"]) + 3, 2000)
                
                # Try with year range for better results with older vehicles
                direct_term = f"{info['year']} {info['make']} {info['model']} front bumper fits {year_range_start}-{year_range_end}"
                print(f"Trying specialized classic vehicle search: {direct_term}")
                
                # Add another specialized search for older vehicles - search directly on eBay
                # Make sure we still pass structured data even for specialized searches
                print(f"[DEBUG] search_products - Specialized classic vehicle search: {direct_term}")
                print(f"[DEBUG] search_products - Still using original structured data: {structured_data}")
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    ebay_future = executor.submit(get_ebay_serpapi_results, direct_term, "bumper", structured_data)
                    ebay_listings = ebay_future.result()
                    
                    # Create a map of existing items
                    existing_keys = {}
                    for idx, item in enumerate(all_listings):
                        title_lower = item["title"].lower()
                        first_words = ' '.join(title_lower.split()[:5]) if title_lower else ""
                        key = (first_words, item.get("source", ""))
                        existing_keys[key] = idx
                    
                    # Add unique items
                    for item in ebay_listings:
                        title_lower = item["title"].lower()
                        first_words = ' '.join(title_lower.split()[:5]) if title_lower else ""
                        item_source = item.get("source", "")
                        key = (first_words, item_source)
                        
                        if key not in existing_keys:
                            all_listings.append(item)
                            existing_keys[key] = len(all_listings) - 1
                            
                return_early = False
                
                # Continue with original search if still needed
                if info["make"] and info["make"].lower() == "ford" and info["model"] and "f-" in info["model"].lower():
                    direct_term = f"{info['year']} Ford {info['model'].upper()} front bumper assembly OEM"
                else:
                    return_early = True
                    
                if return_early:
                    # We have enough results, proceed to sorting and filtering
                    # Skip the remaining specialized searches
                    
                    # Sort by relevance score
                    all_listings = [add_relevance_score(item, search_term, vehicle_info) for item in all_listings]
                    
                    # If we have part information, prioritize exact matches
                    if part_type:
                        all_listings = prioritize_exact_part_matches(all_listings, part_type)
                    else:
                        # Sort by relevance score by default when we don't have a specific part
                        all_listings.sort(key=lambda x: x.get("relevanceScore", 0), reverse=True)
                    
                    # Add "Best Match" flag for top matches for UI highlight
                    for i, item in enumerate(all_listings):
                        if i < 4 or item.get("priorityScore", 0) > 80:
                            item["bestMatch"] = True
                        else:
                            item["bestMatch"] = False
                    
                    return jsonify({
                        "success": True,
                        "listings": all_listings,
                        "total": len(all_listings),
                        "exactMatchCount": sum(1 for item in all_listings if item.get("isExactMatch", False)),
                        "page": page,
                        "pageSize": page_size
                    })
                
                print(f"Trying direct bumper search term: {direct_term}")
                
                # Try the direct search term
                print(f"[DEBUG] search_products - Direct bumper search term: {direct_term}")
                print(f"[DEBUG] search_products - Still using original structured data: {structured_data}")
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                    ebay_future = executor.submit(get_ebay_serpapi_results, direct_term, "bumper", structured_data)
                    
                    ebay_listings = ebay_future.result()
                    
                    # Add only new unique listings with improved deduplication
                    existing_keys = {}  # Track existing items by both title and source
                    for idx, item in enumerate(all_listings):
                        # Create a composite key of title + first words of title for fuzzy matching
                        title_lower = item["title"].lower()
                        first_words = ' '.join(title_lower.split()[:5]) if title_lower else ""
                        key = (first_words, item.get("source", ""))
                        existing_keys[key] = idx
                    
                    # Process new items with better deduplication
                    for item in ebay_listings:
                        title_lower = item["title"].lower()
                        first_words = ' '.join(title_lower.split()[:5]) if title_lower else ""
                        item_source = item.get("source", "")
                        key = (first_words, item_source)
                        
                        # If this exact item doesn't exist yet, add it
                        if key not in existing_keys:
                            all_listings.append(item)
                            existing_keys[key] = len(all_listings) - 1
        
        # Function to add relevance score based on query match
        def add_relevance_score(item, query, vehicle_info):
            """Add a relevance score to each item based on how well it matches the query"""
            score = 0
            title = item.get("title", "").lower()
            
            # Add points for matching query terms
            query_terms = query.lower().split()
            for term in query_terms:
                if term in title and len(term) > 2:
                    score += 5
            
            # Check for vehicle info matches
            if vehicle_info.get("year") and vehicle_info.get("year") in title:
                score += 10
            
            if vehicle_info.get("make") and vehicle_info.get("make").lower() in title:
                score += 10
            
            if vehicle_info.get("model"):
                model = vehicle_info.get("model").lower()
                # Check for model variations (with/without hyphens)
                if model in title or model.replace("-", "") in title or model.replace("-", " ") in title:
                    score += 15
            
            if vehicle_info.get("part") and vehicle_info.get("part").lower() in title:
                score += 15
            
            # Add points for exact phrase matches
            if vehicle_info.get("make") and vehicle_info.get("model"):
                make_model = f"{vehicle_info.get('make')} {vehicle_info.get('model')}".lower()
                if make_model in title:
                    score += 20
            
            # Add points for source (prefer Google Shopping to show more Google results)
            if item.get("source") == "Google Shopping":
                score += 10  # Higher score to prioritize Google Shopping results
            
            # Add points for condition (prefer new parts)
            if "new" in item.get("condition", "").lower():
                score += 5
            
            # Add points for free shipping
            if "free" in item.get("shipping", "").lower():
                score += 3
            
            item["relevanceScore"] = score
            return item
        
        # Add relevance score to each item
        all_listings = [add_relevance_score(item, search_term, vehicle_info) for item in all_listings]
        
        # If we have part information, prioritize exact matches
        if part_type:
            all_listings = prioritize_exact_part_matches(all_listings, part_type)
        else:
            # Sort by relevance score by default when we don't have a specific part
            all_listings.sort(key=lambda x: x.get("relevanceScore", 0), reverse=True)
        
        # Add "Best Match" flag for top matches for UI highlight
        for i, item in enumerate(all_listings):
            if i < 4 or item.get("priorityScore", 0) > 80:
                item["bestMatch"] = True
            else:
                item["bestMatch"] = False
        
        return jsonify({
            "success": True,
            "listings": all_listings,
            "total": len(all_listings),
            "exactMatchCount": sum(1 for item in all_listings if item.get("isExactMatch", False)),
            "page": page,
            "pageSize": page_size
        })
    except Exception as e:
        print(f"Search products error: {e}")
        return jsonify({
            "success": False,
            "error": "An error occurred while searching for products. Please try again."
        })

# Enhanced product listing function used by API endpoints
def enhanceProductListings(listings, query, vehicleInfo):
    """
    Server-side product enhancement with basic year matching
    """
    if not listings or not isinstance(listings, list):
        return []
    
    # Extract year for matching
    year = None
    if vehicleInfo and isinstance(vehicleInfo, dict):
        year = vehicleInfo.get("year")
    
    # Add basic relevance scoring and year matching
    for listing in listings:
        if not isinstance(listing, dict):
            continue
            
        # Initialize with default values
        listing["relevanceScore"] = 0
        listing["exactYearMatch"] = False
        listing["bestMatch"] = False
        
        # Simple scoring for exact year matches
        title = listing.get("title", "").lower()
        if year and year in title:
            listing["exactYearMatch"] = True
            listing["relevanceScore"] = 50
            listing["bestMatch"] = True
    
    # Sort by exact year match first, then by relevance score
    return sorted(listings, 
                 key=lambda x: (1 if x.get("exactYearMatch", False) else 0, x.get("relevanceScore", 0)), 
                 reverse=True)

# Flask app setup
# (App is already set up in lines 15-18)

# For backward compatibility - combined analyze and search
@app.route("/api/search", methods=["POST"])
def search_api():
    """Legacy endpoint that combines analysis and search"""
    query = sanitize_input(request.form.get("prompt", ""))
    
    if not query:
        return jsonify({
            "success": False,
            "validation_error": "Please enter a valid search query."
        })
    
    # Check if query has sufficient vehicle information
    if not has_vehicle_info(query):
        validation_error = get_missing_info_message(query)
        return jsonify({
            "success": False,
            "validation_error": validation_error
        })

    # First get the analysis
    analyze_response = analyze_query()
    analyze_data = analyze_response.get_json()
    
    if not analyze_data.get("success"):
        return analyze_response
    
    # Then get the product listings
    search_term = analyze_data.get("search_terms")[0]
    
    # Create a mock request with
    # Create a mock request with the search term
    class MockForm:
        def get(self, key, default=""):
            if key == "search_term":
                return search_term
            elif key == "original_query":
                return query
            return default
    
    # Replace request.form with our mock
    orig_form = request.form
    request.form = MockForm()
    search_response = search_products()
    request.form = orig_form
    
    search_data = search_response.get_json()
    
    if not search_data.get("success"):
        return jsonify({
            "success": True,
            "questions": analyze_data.get("questions"),
            "listings": []  # Return empty listings but still success
        })
    
    return jsonify({
        "success": True,
        "questions": analyze_data.get("questions"),
        "listings": search_data.get("listings")
    })

# AJAX endpoint for VIN decoding
@app.route("/api/vin-decode", methods=["POST"])
def vin_decode_api():
    # Log all form data for debugging
    print(f"VIN decode API request form data: {request.form}")
    print(f"VIN decode API request data: {request.data}")
    print(f"VIN decode API content type: {request.content_type}")
    
    vin = sanitize_input(request.form.get("vin", ""))
    
    if not vin:
        return jsonify({"error": "No VIN provided"})
    
    # Validate VIN format (17 alphanumeric characters for modern vehicles)
    if not re.match(r'^[A-HJ-NPR-Z0-9]{17}$', vin):
        return jsonify({"error": "Invalid VIN format. VIN should be 17 alphanumeric characters (excluding I, O, and Q)."})
    
    try:
        print(f"Decoding VIN: {vin}")
        vin_info = decode_vin(vin)
        
        if not vin_info:
            print(f"VIN decode failed - empty result")
            return jsonify({"error": "Could not decode VIN. Please check the VIN and try again."})
            
        # Check if we have Results in the format expected from NHTSA API
        if vin_info.get('Results') and len(vin_info['Results']) > 0:
            result = vin_info['Results'][0]
            if not result.get('Make') or not result.get('ModelYear'):
                print(f"VIN decode failed - no Make or ModelYear found in result")
                return jsonify({"error": "Could not decode VIN. Please check the VIN and try again."})
        else:
            # For backward compatibility, check direct properties too
            if not vin_info.get('Make'):
                print(f"VIN decode failed - no Make found in result: {vin_info}")
                return jsonify({"error": "Could not decode VIN. Please check the VIN and try again."})
        
        # Ensure we have a consistent format for the frontend
        if vin_info.get('Results') and isinstance(vin_info['Results'], list) and len(vin_info['Results']) > 0:
            result = vin_info['Results'][0]
            print(f"VIN decode successful for {vin}: {result.get('Make')} {result.get('Model')}")
            
            # Check if we have the essential fields
            if not (result.get('Make') and result.get('Model') and result.get('ModelYear')):
                print(f"VIN data incomplete - Missing essential fields")
                return jsonify({"error": "VIN decoded but returned incomplete vehicle information."})
        else:
            # Non-standard response format (shouldn't happen with normal API)
            print(f"VIN decode format unexpected: {vin_info}")
            return jsonify({"error": "Unexpected response format from VIN decoder."})
        
        # Return the complete API response for the frontend to handle
        return jsonify(vin_info)
    except Exception as e:
        # Log the error but don't expose details to the client
        print(f"VIN decode error: {e}")
        return jsonify({"error": "An error occurred while decoding the VIN. Please try again later."})

# Important - keeping this route for backward compatibility with existing clients
@app.route("/vin-decode", methods=["POST"])
def vin_decode():
    return vin_decode_api()

@app.route("/api/chat", methods=["POST"])
def chat_api():
    """Process chat messages and return AI-powered responses"""
    # Delegate processing to the chatbot handler module
    return process_chat_message(request.json)

@app.route("/api/create-payment-link", methods=["POST"])
def create_payment_link():
    """Create a Stripe payment link using agent input for price and product info"""
    try:
        import stripe
        
        # Get your secret key from the environment variable
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
        
        # Get agent input parameters from request
        agent_input = request.json.get("agent_input", {})
        amount = agent_input.get("amount")
        currency = agent_input.get("currency", "usd")
        product_name = agent_input.get("product_name", "Payment")
        product_description = agent_input.get("product_description", "")
        
        # Validate amount
        if not amount or not isinstance(amount, (int, float)) or amount <= 0:
            return jsonify({"error": "Invalid amount in agent input"}), 400
            
        # Create a Product
        product = stripe.Product.create(
            name=product_name,
            description=product_description
        )
        
        # Create a Price (amount in cents)
        price = stripe.Price.create(
            product=product.id,
            unit_amount=int(amount * 100),  # Convert to cents
            currency=currency,
        )
        
        # Configure address collection - only US addresses
        billing_address_collection = "required"
        shipping_address_collection = {"allowed_countries": ["US"]}
        
        # Configure payment methods - disable Link
        payment_method_types = ["card"]
        
        # Create a Payment Link with full address collection
        payment_link = stripe.PaymentLink.create(
            line_items=[{"price": price.id, "quantity": 1}],
            billing_address_collection=billing_address_collection,
            shipping_address_collection=shipping_address_collection,
            payment_method_types=payment_method_types
        )
        
        # Return the payment link URL and details
        return jsonify({
            "success": True,
            "payment_link": payment_link.url,
            "product_details": {
                "name": product_name,
                "price": amount,
                "currency": currency,
                "description": product_description
            }
        })
        
    except ImportError:
        return jsonify({"error": "Stripe library not installed. Run 'pip install stripe'"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Dialpad Dashboard Routes
@app.route("/dialpad-dashboard", methods=["GET"])
def dialpad_dashboard():
    """Render the Dialpad call dashboard."""
    dialpad_client = DialpadClient()
    
    # Set default date range to just today (1 day)
    today = datetime.now()
    
    # Use the same date for both from and to
    default_to_date = today.strftime("%Y-%m-%d")
    default_from_date = today.strftime("%Y-%m-%d")
    
    # Render the dashboard template with empty initial data
    return render_template(
        "dialpad_dashboard.html",
        calls=[],
        agents=dialpad_client.AGENTS,
        default_from_date=default_from_date,
        default_to_date=default_to_date
    )


@app.route("/api/dialpad-calls", methods=["POST"])
def get_dialpad_calls():
    """API endpoint to fetch Dialpad call data with filtering."""
    try:
        # Initialize the Dialpad client
        dialpad_client = DialpadClient()
        
        # Get request data
        data = request.json
        agent_id = data.get("agent_id")
        call_type = data.get("call_type")
        call_status = data.get("call_status")
        
        print(f"Dialpad dashboard request with filters: agent={agent_id}, type={call_type}, status={call_status}")
        
        print(f"Received request with params: agent_id={agent_id}, call_type={call_type}, call_status={call_status}")
        
        # Convert date strings to timestamps if provided
        started_after = None
        started_before = None
        
        date_from = data.get("date_from")
        date_to = data.get("date_to")
        
        if date_from:
            # Set time to 00:00:00 and convert to milliseconds
            dt_from = datetime.fromisoformat(f"{date_from}T00:00:00")
            started_after = int(dt_from.timestamp() * 1000)
            print(f"Using date from: {date_from}, timestamp: {started_after}")
        
        if date_to:
            # Set time to 23:59:59 and convert to milliseconds
            dt_to = datetime.fromisoformat(f"{date_to}T23:59:59")
            started_before = int(dt_to.timestamp() * 1000)
            print(f"Using date to: {date_to}, timestamp: {started_before}")
            
        # Fetch call data from Dialpad API
        if agent_id and agent_id != "all":
            # Get calls for a specific agent with date filtering
            raw_calls = dialpad_client.get_calls(
                agent_id=agent_id,
                started_after=started_after,
                started_before=started_before
            )
            
            # Agent name should be added by get_calls
        else:
            # Get calls for all agents with date filtering
            raw_calls = dialpad_client.get_all_agent_calls(
                started_after=started_after,
                started_before=started_before
            )
        
        print(f"Retrieved {len(raw_calls)} total raw calls")
        
        # Format calls for display
        formatted_calls = [dialpad_client.format_call_for_display(call) for call in raw_calls]
        
        # Apply additional filters if provided
        if call_type and call_type != "all":
            formatted_calls = [call for call in formatted_calls if call["call_type"] == call_type]
        
        if call_status and call_status != "all":
            # Special case for "missed": include both truly missed and undetermined
            if call_status == "missed":
                formatted_calls = [call for call in formatted_calls if call["status"] == "missed"]
            # Special case for just "completed": only include completed
            elif call_status == "completed":
                formatted_calls = [call for call in formatted_calls if call["status"] == "completed"]
            # New status: "handled_elsewhere"  
            elif call_status == "handled_elsewhere":
                formatted_calls = [call for call in formatted_calls if call["status"] == "handled_elsewhere"]
            # Default case: exact match
            else:
                formatted_calls = [call for call in formatted_calls if call["status"] == call_status]
        
        # Sort calls by datetime (most recent first)
        formatted_calls.sort(key=lambda x: x["datetime"], reverse=True)
        
        print(f"Returning {len(formatted_calls)} formatted calls after filtering")
        
        return jsonify({
            "success": True,
            "calls": formatted_calls,
            "total_calls": len(formatted_calls)
        })
        
    except Exception as e:
        print(f"Error fetching Dialpad calls: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# Run app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5040))
    app.run(host="0.0.0.0", port=port)