import os
import re
import requests
import time
import json
import concurrent.futures
from functools import lru_cache
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI
from vehicle_validation import has_vehicle_info, get_missing_info_message
from query_processor import EnhancedQueryProcessor

load_dotenv()

static_folder = os.path.abspath('static')
app = Flask(__name__, static_folder=static_folder, static_url_path='/static')
app.secret_key = os.getenv("FLASK_SECRET_KEY", os.urandom(24).hex())

api_key = os.getenv("OPENAI_API_KEY")
serpapi_key = os.getenv("SERPAPI_KEY")
client = OpenAI(api_key=api_key)

# Validate required API keys
if not api_key:
    raise ValueError("OPENAI_API_KEY is not set in environment variables")
if not serpapi_key:
    raise ValueError("SERPAPI_KEY is not set in environment variables")

# Initialize our enhanced query processor
query_processor = EnhancedQueryProcessor()

# Enhanced query cleaner that uses our query processor
def clean_query(text):
    """Enhanced query cleaner for better search match with common automotive parts"""
    if not text:
        return ""
    
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
                return result
            else:
                print(f"Invalid VIN data received: Missing Make or ModelYear for VIN {vin}")
        else:
            print(f"No results found for VIN {vin}")
    except requests.exceptions.RequestException as e:
        print(f"VIN decode request error: {e}")
    except ValueError as e:
        print(f"VIN decode JSON parsing error: {e}")
    except Exception as e:
        print(f"VIN decode unexpected error: {e}")
    return {}

# Cache results for 5 minutes (300 seconds)
@lru_cache(maxsize=100)
def get_serpapi_cached(engine, query, query_type=None, timestamp=None, **params):
    """
    Cache wrapper for SerpAPI requests. Timestamp is used to invalidate cache after 5 minutes.
    Added support for additional params.
    """
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
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {engine} items: {e}")
        if engine == "ebay":
            return {"organic_results": []}
        else:
            return {"shopping_results": []}

def fetch_ebay_results(query_type, query, timestamp, part_type=None):
    """
    Function to fetch eBay results for concurrent execution.
    Added part_type parameter to specify auto parts category.
    """
    # Get the appropriate eBay category based on part type
    category_id = get_ebay_category_id(part_type) if part_type else None
    
    params = {}
    if category_id:
        params["category_id"] = category_id
    
    results = get_serpapi_cached("ebay", query, query_type, timestamp, **params)
    return process_ebay_results(results, query, max_items=12)  # Increased max items

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

def get_ebay_serpapi_results(query, part_type=None):
    """
    Fetch eBay results using concurrent requests.
    Added part_type parameter to filter by auto parts category.
    """
    # Use timestamp for cache invalidation every 5 minutes
    cache_timestamp = int(time.time() / 300)
    
    # Define tasks for concurrent execution - now including part type
    tasks = [
        ("new", query, cache_timestamp, part_type),
        ("used", query, cache_timestamp, part_type)
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

def extract_year_make_model_from_query(query):
    """Extract year, make, and model from a query string to use for filtering results"""
    processed = query_processor.process_query(query)
    vehicle_info = processed.get("vehicle_info", {})
    
    return {
        "year": vehicle_info.get("year"),
        "make": vehicle_info.get("make"),
        "model": vehicle_info.get("model"),
        "part": vehicle_info.get("part")
    }

def process_ebay_results(results, query, max_items=15):
    """
    Helper function to process eBay results with improved filtering.
    Increased max_items from 3 to 5.
    """
    processed_items = []
    
    # Extract vehicle info for better filtering
    vehicle_info = extract_year_make_model_from_query(query)
    year = vehicle_info.get("year")
    make = vehicle_info.get("make")
    model = vehicle_info.get("model")
    part = vehicle_info.get("part")
    
    # Build a list of keywords to match
    keywords = query.lower().split()
    
    # Create a set of must-match terms for more accurate results
    must_match = set()
    
    # Add part terms as must-match
    if part:
        for part_word in part.lower().split():
            if len(part_word) > 3:  # Only add meaningful words (skip 'for', 'the', etc.)
                must_match.add(part_word)
    
    # Add make/model as must-match if available
    if make and len(make) > 2:
        must_match.add(make.lower())
    if model and len(model) > 2:
        must_match.add(model.lower())
    
    # Check if the query is for a bumper assembly
    is_bumper_query = any(term in query.lower() for term in ["bumper", "front end"])
    
    # Set up scoring system for relevance
    for item in results.get("organic_results", []):
        if len(processed_items) >= max_items:
            break
            
        title = item.get("title", "").lower()
        
        # Skip items that don't match our criteria
        if is_bumper_query and any(x in title for x in ["guard", "protector", "pad", "cover only", "bracket only"]):
            # Skip bumper guards/pads when looking for full bumpers
            if not any(x in title for x in ["assembly", "complete", "front end", "whole bumper"]):
                continue
        
        # Check if all must-match terms are in the title
        if must_match and not all(term in title for term in must_match):
            continue
            
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
    
    return processed_items

def get_google_shopping_results(query, part_type=None):
    """
    Fetch Google Shopping results.
    Added part_type parameter for better category filtering.
    """
    # Use timestamp for cache invalidation every 5 minutes
    cache_timestamp = int(time.time() / 300)
    
    # Map part types to Google product categories
    product_category = None
    if part_type:
        if "bumper" in part_type.lower():
            product_category = "5613"  # Vehicle Parts & Accessories
    
    params = {}
    if product_category:
        params["product_category"] = product_category
    
    results = get_serpapi_cached("google_shopping", query, timestamp=cache_timestamp, **params)
    
    # Debug: Print the structure of the first result if available
    if results and results.get("shopping_results") and len(results.get("shopping_results")) > 0:
        print("First Google Shopping result structure:")
        first_result = results.get("shopping_results")[0]
        print(f"Keys available: {list(first_result.keys())}")
        if "link" in first_result:
            print(f"Link type: {type(first_result['link'])}, Value: {first_result['link']}")
    
    return process_google_shopping_results(results, query, max_items=5)  # Increased max items

def process_google_shopping_results(results, query, max_items=12):
    """Process Google Shopping results with improved filtering"""
    processed_items = []
    
    # Extract vehicle info for better filtering
    vehicle_info = extract_year_make_model_from_query(query)
    year = vehicle_info.get("year")
    make = vehicle_info.get("make")
    model = vehicle_info.get("model")
    part = vehicle_info.get("part")
    
    # Build a list of keywords to match
    keywords = query.lower().split()
    
    # Create a set of must-match terms for more accurate results
    must_match = set()
    
    # Add part terms as must-match
    if part:
        for part_word in part.lower().split():
            if len(part_word) > 3:  # Only add meaningful words (skip 'for', 'the', etc.)
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
        
        # Skip items that don't match all must-match terms
        if must_match and not all(term in title for term in must_match):
            continue
        
        # If we have year/make/model, make sure they appear in the title
        if year and make and model:
            # At least make or model should appear in the title
            if make.lower() not in title and model.lower() not in title:
                continue
            
            # Year should be mentioned somewhere
            if year not in title:
                # Skip items without year match
                continue
        
        # Extract and fix the link
        link = None
        
        # Try different possible structures for the link
        if item.get("link"):
            link = item.get("link")
        elif item.get("product_link"):
            link = item.get("product_link")
        elif item.get("link_text") and item.get("link_text").startswith("http"):
            link = item.get("link_text")
        elif isinstance(item.get("link_object"), dict):
            link = item.get("link_object", {}).get("link", "")
        
        # If still no link, create a Google search link
        if not link or link == "":
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

# Sanitize user input
def sanitize_input(text):
    if not text:
        return ""
    # Remove any potentially harmful characters
    sanitized = re.sub(r'[^\w\s\-.,?!@#$%^&*()_+=[\]{}|:;<>"/]', '', text)
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
    
    # Try to parse the JSON if provided
    processed_result = None
    if parsed_data_json:
        try:
            processed_result = json.loads(parsed_data_json)
        except:
            # If parsing fails, we'll process it again
            pass
    
    if not query:
        return jsonify({
            "success": False,
            "validation_error": "Please enter a valid search query."
        })
    
    # Process with our query processor if needed
    if not processed_result:
        processed_result = query_processor.process_query(query)
    
    # Check if we have enough confidence to skip GPT-4
    if processed_result["confidence"] >= 80:
        # We have high confidence in our parsed data, so use it directly
        search_terms = processed_result["search_terms"]
        
        # Create a GPT-like response format
        part = processed_result["vehicle_info"]["part"] or "part"
        make = processed_result["vehicle_info"]["make"] or "vehicle"
        model_text = ""
        if processed_result["vehicle_info"]["model"]:
            model = processed_result["vehicle_info"]["model"]
            # Format model if it's a Ford F-series
            if model.lower() in ["f-150", "f150", "f-250", "f250", "f-350", "f350"]:
                model_text = f" {model.upper()}"
            else:
                model_text = f" {model.capitalize()}"
                
        year = processed_result["vehicle_info"]["year"] or "recent"
        
        # Simple template response that includes properly formatted model information
        questions = f"""
- {year} {make.capitalize()}{model_text} with {part}
        
Question 1: Do you need any associated hardware or accessories with this {part}?

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
    
    # Otherwise proceed with GPT-4 for more complex understanding
    # Check if query has sufficient vehicle information
    if not has_vehicle_info(query):
        validation_error = get_missing_info_message(query)
        return jsonify({
            "success": False,
            "validation_error": validation_error
        })

    # Extract model for prompt
    model_info = ""
    if processed_result["vehicle_info"]["model"]:
        model_info = f"Model: {processed_result['vehicle_info']['model'] or 'not specified'}"

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

4. Ask follow-up questions, max 3:
   - Question 1: Ask about directly associated hardware needed (e.g., bumper → brackets, fog trims, sensors if applicable)
   - Question 2: Only ask follow-up if something affects fitment — like transmission type, submodel, or drivetrain. 
    Do NOT ask vague or unnecessary questions like modifications or preferences.
   - Fitment: If fitment is shared across multiple years, mention the range with platform/chassis code — you can take a guess if needed. Just say it out. No worries. 
   - If more products are involved, you can ask more questions, max 2.

5. Finish with a bolded search-optimized lookup phrase, (add a emoji of world right before the phrase):
   - Format: lowercase string including [year or range] + make + model + trim (if needed) + engine (if relevant) + oem + part name
   - Think of it as a search term for a customer to find the part. Use the most relevant keywords. Give two search terms for the same part with another name.
   - Example 1:  "🔎 2020–2022 honda civic ex oem front bumper"
   - Example 2: "🔎 2020 – 2022 honda civic ex oem bumper cover"

Here's some additional information that might help you:
Year: {processed_result["vehicle_info"]["year"] or "not specified"}
Make: {processed_result["vehicle_info"]["make"] or "not specified"}
{model_info}
Part: {processed_result["vehicle_info"]["part"] or "not specified"}
Position: {processed_result["vehicle_info"]["position"] or "not specified"}
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
            
            # Clean and optimize the search term
            search_term = clean_query(search_term_raw)
            
            # If there's a second search term, use it as a fallback
            fallback_term = None
            if len(search_lines) > 1:
                fallback_term = clean_query(search_lines[1].replace("🔎", "").strip())
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
@app.route("/api/search-products", methods=["POST"])
def search_products():
    """Search for products using the provided search term with pagination support"""
    search_term = sanitize_input(request.form.get("search_term", ""))
    original_query = sanitize_input(request.form.get("original_query", ""))
    page = int(request.form.get("page", "1"))
    page_size = int(request.form.get("page_size", "24"))  # Default to 24 products per page
    
    if not search_term:
        return jsonify({
            "success": False,
            "error": "No search term provided"
        })
    
    try:
        # Extract part type for category filtering
        vehicle_info = extract_year_make_model_from_query(original_query or search_term)
        part_type = vehicle_info.get("part")
        
        # Try multiple search strategies (fallbacks if needed)
        all_listings = []
        
        # Strategy 1: Direct search with original term
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            ebay_future = executor.submit(get_ebay_serpapi_results, search_term, part_type)
            google_future = executor.submit(get_google_shopping_results, search_term, part_type)
            
            ebay_listings = ebay_future.result()
            google_listings = google_future.result()
            
            all_listings.extend(ebay_listings)
            all_listings.extend(google_listings)
        
        # If we don't have enough results, try with a simplified search
        if len(all_listings) < 8 and original_query:
            # Extract core information
            info = extract_year_make_model_from_query(original_query)
            if info["year"] and info["make"] and info["part"]:
                # Create a simpler search term
                simple_term = f"{info['year']} {info['make']} {info['part']}"
                if info["model"]:
                    simple_term = f"{info['year']} {info['make']} {info['model']} {info['part']}"
                
                print(f"Not enough results with original search. Trying simplified term: {simple_term}")
                
                # Try the simpler search term
                with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                    ebay_future = executor.submit(get_ebay_serpapi_results, simple_term, part_type)
                    google_future = executor.submit(get_google_shopping_results, simple_term, part_type)
                    
                    ebay_listings = ebay_future.result()
                    google_listings = google_future.result()
                    
                    # Add only new unique listings
                    existing_titles = {item["title"].lower() for item in all_listings}
                    for item in ebay_listings + google_listings:
                        if item["title"].lower() not in existing_titles:
                            all_listings.append(item)
                            existing_titles.add(item["title"].lower())
        
        # If still not enough results and this is a bumper search, try an even more specific search
        if len(all_listings) < 12 and part_type and "bumper" in part_type.lower():
            # For Ford F-150 and similar models, try a direct bumper assembly search
            info = extract_year_make_model_from_query(original_query or search_term)
            if info["make"] and info["make"].lower() == "ford" and info["model"] and "f-" in info["model"].lower():
                direct_term = f"{info['year']} Ford {info['model'].upper()} front bumper assembly OEM"
                
                print(f"Trying direct bumper search term: {direct_term}")
                
                # Try the direct search term
                with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                    ebay_future = executor.submit(get_ebay_serpapi_results, direct_term, "bumper")
                    
                    ebay_listings = ebay_future.result()
                    
                    # Add only new unique listings
                    existing_titles = {item["title"].lower() for item in all_listings}
                    for item in ebay_listings:
                        if item["title"].lower() not in existing_titles:
                            all_listings.append(item)
                            existing_titles.add(item["title"].lower())
        
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
            
            # Add points for source (prefer eBay for auto parts generally)
            if item.get("source") == "eBay":
                score += 5
            
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
        
        # Sort by relevance score by default
        all_listings.sort(key=lambda x: x.get("relevanceScore", 0), reverse=True)
        
        # Add an exact match flag for frontend use
        for item in all_listings:
            if item.get("relevanceScore", 0) > 40:
                item["exactMatch"] = True
        
        return jsonify({
            "success": True,
            "listings": all_listings,
            "total": len(all_listings),
            "page": page,
            "pageSize": page_size
        })
    except Exception as e:
        print(f"Search products error: {e}")
        return jsonify({
            "success": False,
            "error": "An error occurred while searching for products. Please try again."
        })

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
    vin = sanitize_input(request.form.get("vin", ""))
    
    if not vin:
        return jsonify({"error": "No VIN provided"})
    
    # Validate VIN format (17 alphanumeric characters for modern vehicles)
    if not re.match(r'^[A-HJ-NPR-Z0-9]{17}$', vin):
        return jsonify({"error": "Invalid VIN format. VIN should be 17 alphanumeric characters (excluding I, O, and Q)."})
    
    try:
        vin_info = decode_vin(vin)
        
        if not vin_info or not vin_info.get('Make'):
            return jsonify({"error": "Could not decode VIN. Please check the VIN and try again."})
        
        # Return the VIN information as JSON
        return jsonify(vin_info)
    except Exception as e:
        # Log the error but don't expose details to the client
        print(f"VIN decode error: {e}")
        return jsonify({"error": "An error occurred while decoding the VIN. Please try again later."})

# For backward compatibility - redirect old routes to the API endpoints
@app.route("/vin-decode", methods=["POST"])
def vin_decode():
    return vin_decode_api()

# Run app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5040))
    app.run(host="0.0.0.0", port=port)