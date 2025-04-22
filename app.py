import os
import re
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI
from vehicle_validation import has_vehicle_info, get_missing_info_message
static_folder = os.path.abspath('static')
app = Flask(__name__, static_folder=static_folder, static_url_path='/static')

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
serpapi_key = os.getenv("SERPAPI_KEY")
client = OpenAI(api_key=api_key)

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "auto-parts-assistant-key")
print("🧪 SERPAPI_KEY loaded:", serpapi_key)

# 🔧 Smart query cleaner for better search match
def clean_query(text):
    # Normalize dashes
    text = re.sub(r"[–—]", "-", text)

    # Remove weak filler words
    text = re.sub(r"\bfor\b", "", text, flags=re.IGNORECASE)

    # Replace vague phrases with stronger keywords
    text = text.lower()
    text = text.replace("oem timing kit", "timing belt kit with water pump")
    text = text.replace("timing kit", "timing belt kit with water pump")
    text = text.replace("assembly", "complete assembly")
    text = text.replace("radiator assembly", "radiator with fan and shroud")

    # Trim and clean spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text

# VIN decoder helper function
def decode_vin(vin):
    if not vin:
        return {}
    try:
        url = f'https://vpic.nhtsa.dot.gov/api/vehicles/decodevinvaluesextended/{vin}?format=json'
        response = requests.get(url)
        data = response.json()
        if data and data['Results']:
            result = data['Results'][0]
            if result.get('Make') and result.get('ModelYear'):
                return result
    except Exception as e:
        print(f"VIN decode error: {e}")
    return {}

def get_ebay_serpapi_results(query):
    print("🔥 SerpAPI called with:", query)

    # First, get new items
    new_params = {
        "engine": "ebay",
        "ebay_domain": "ebay.com",
        "_nkw": query,
        "LH_ItemCondition": "1000",  # New items
        "LH_BIN": "1",               # Buy It Now only
        "api_key": serpapi_key
    }
    
    # Then, get used items
    used_params = {
        "engine": "ebay",
        "ebay_domain": "ebay.com",
        "_nkw": query,
        "LH_ItemCondition": "3000",  # Used items
        "LH_BIN": "1",               # Buy It Now only
        "api_key": serpapi_key
    }
    
    try:
        # Get new items
        new_response = requests.get("https://serpapi.com/search", params=new_params)
        new_results = new_response.json()
        
        # Get used items
        used_response = requests.get("https://serpapi.com/search", params=used_params)
        used_results = used_response.json()
        
        # Process both sets of results
        new_items = process_ebay_results(new_results, query, max_items=3)
        used_items = process_ebay_results(used_results, query, max_items=3)
        
        # Combine the results
        all_items = new_items + used_items
        return all_items
        
    except Exception as e:
        print("SerpAPI error:", e)
        return []

def process_ebay_results(results, query, max_items=3):
    """Helper function to process eBay results"""
    processed_items = []
    keywords = query.lower().split()
    
    for item in results.get("organic_results", []):
        if len(processed_items) >= max_items:
            break
            
        title = item.get("title", "").lower()
        if any(kw in title for kw in keywords):
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
                
            processed_items.append({
                "title": item.get("title"),
                "price": price,
                "shipping": shipping,
                "condition": condition,
                "link": item.get("link")
            })
    
    return processed_items
# Main GPT Assistant route - original version for regular form submission
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Regular form submission just renders the template
        return render_template("index.html")
    return render_template("index.html")

# AJAX endpoint for GPT Assistant
@app.route("/api/search", methods=["POST"])
def search_api():
    query = request.form.get("prompt", "").strip()
    
    # Check if query has sufficient vehicle information
    if not has_vehicle_info(query):
        validation_error = get_missing_info_message(query)
        return jsonify({
            "success": False,
            "validation_error": validation_error
        })

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
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )

        questions = response.choices[0].message.content.strip()

        # Use GPT-generated search term if available, else fallback to cleaned query
        search_lines = [line for line in questions.split("\n") if "🔎" in line]
        search_term = clean_query(search_lines[0].replace("🔎", "").strip()) if search_lines else clean_query(query)
        print("🧼 Final search term used:", search_term)

        listings = get_ebay_serpapi_results(search_term)

        return jsonify({
            "success": True,
            "questions": questions,
            "listings": listings
        })
    except Exception as e:
        print(f"API error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        })

# AJAX endpoint for VIN decoding
@app.route("/api/vin-decode", methods=["POST"])
def vin_decode_api():
    vin = request.form.get("vin", "").strip()
    
    if not vin:
        return jsonify({"error": "No VIN provided"})
    
    try:
        vin_info = decode_vin(vin)
        
        if not vin_info or not vin_info.get('Make'):
            return jsonify({"error": "Could not decode VIN. Please check the VIN and try again."})
        
        # Return the VIN information as JSON
        return jsonify(vin_info)
    except Exception as e:
        print(f"VIN decode error: {e}")
        return jsonify({"error": f"An error occurred: {str(e)}"})

# For backward compatibility - redirect old routes to the API endpoints
@app.route("/vin-decode", methods=["POST"])
def vin_decode():
    return vin_decode_api()

# Run app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5040))
    app.run(host="0.0.0.0", port=port)