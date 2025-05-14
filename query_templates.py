# Query Templates for Chatbot
# These templates help structure responses for different types of automotive questions

# Base template for all automotive questions
GENERAL_TEMPLATE = """
Provide a helpful response about automotive parts or repair. 
Be concise and accurate, focusing on practical information.
"""

# Template for compatibility questions
COMPATIBILITY_TEMPLATE = """
The user is asking about part compatibility. In your response:

1. Explain what factors determine compatibility (year, make, model, trim, engine)
2. Discuss the specific compatibility concerns for this part type
3. Mention if OEM vs aftermarket affects compatibility
4. Suggest how the user can verify compatibility for their specific vehicle
5. Include any warnings about incorrect fitment issues

Example compatibility factors to consider:
- Exact dimensions and mounting points
- Electrical connectors and wiring requirements
- Computer/ECU integration requirements
- Manufacturing variations between model years
"""

# Template for troubleshooting help
TROUBLESHOOTING_TEMPLATE = """
The user needs help diagnosing or fixing an issue. In your response:

1. List possible causes for the symptoms described, from most to least common
2. Explain simple diagnostic steps they can take to identify the problem
3. Discuss which parts might need replacement and their approximate price range
4. Mention if this is a DIY-friendly repair or requires professional help
5. Include any safety warnings relevant to this issue

Make sure to acknowledge that proper diagnosis requires physical inspection of the vehicle.
"""

# Template for installation guidance
INSTALLATION_TEMPLATE = """
The user needs help installing or replacing a part. In your response:

1. List the tools required for this job
2. Outline the step-by-step process in clear, numbered steps
3. Mention any specific torque specifications or critical adjustments
4. Highlight common mistakes to avoid during installation
5. Include any calibration or reset procedures needed after installation

Focus on clarity and safety, mentioning when certain steps might require professional assistance.
"""

# Template for part quality/comparison questions
COMPARISON_TEMPLATE = """
The user is asking about part quality or comparing options. In your response:

1. Explain the key differences between OEM and aftermarket options
2. Compare economy vs premium options and their typical price differences
3. Discuss how material quality affects durability
4. Mention specific brands known for quality in this part category
5. Explain the typical lifespan expectations for different quality levels

Be balanced in your assessment, acknowledging that higher price doesn't always guarantee better performance.
"""

# Template for maintenance advice
MAINTENANCE_TEMPLATE = """
The user is asking about maintenance for a part or system. In your response:

1. Explain the recommended maintenance interval and why it matters
2. Describe warning signs that maintenance is needed
3. Outline the consequences of neglecting this maintenance
4. Discuss if preventative replacement makes sense for this part
5. Mention any seasonal considerations for this maintenance task

Focus on helping the user make informed decisions about their vehicle's care.
"""

# Template for price inquiries
PRICE_TEMPLATE = """
The user is asking about pricing for a part or repair. In your response:

1. Provide approximate price ranges for economy, mid-range, and premium options
2. Compare dealer/OEM pricing vs aftermarket alternatives
3. Mention factors that affect pricing (vehicle make, model year, etc.)
4. Discuss whether used or remanufactured parts are viable options
5. Note any additional parts typically needed for a complete repair

Be clear that prices vary by location and time, and these are just general guidelines.
"""

# Template for customer transcript analysis
TRANSCRIPT_TEMPLATE = """
As an automotive parts sales expert with SPECIFIC KNOWLEDGE of RAM trucks and OEM parts, analyze this conversation to provide PRACTICAL SALES ADVICE that addresses the customer's actual situation.

DIRECTLY ANSWER THE FOLLOWING:

1. PART VERIFICATION:
   - CONFIRM or DENY if the specific part number mentioned (e.g., 68263849AK) has the features the customer wants
   - State which RAM truck models this part fits (specific years/trims)
   - List the EXACT features of this part (autodim, heated, power fold, etc.)
   - If the part is incorrect, state the CORRECT part number for what they need

2. PRICING GUIDANCE:
   - Give the ACTUAL MARKET PRICE RANGE for this specific part (not arbitrary numbers)
   - Provide the typical dealer price vs. aftermarket price
   - List any common price-match policies relevant to this part
   - Suggest a fair but profitable markup percentage

3. CLOSING THE SALE:
   - Provide 2-3 SPECIFIC objections customers typically have about this exact part
   - Give word-for-word responses to overcome these objections
   - Suggest a specific upsell based on what typically fails/needs replacement alongside this part
   - Recommend exact warranty terms that should be offered

4. INVENTORY & AVAILABILITY:
   - Note if this part typically has supply chain issues or backorders
   - Suggest alternative part numbers if the requested one is unavailable
   - List compatible third-party brands that fit this application
   - Indicate typical shipping/delivery timeframes for this part

Format your response like a practical sales guide for someone who needs to make the sale TODAY.
Include part numbers, exact prices, and specific features - not generic advice.
"""

# Dictionary to map question types to templates
QUERY_TEMPLATES = {
    "compatibility": COMPATIBILITY_TEMPLATE,
    "troubleshooting": TROUBLESHOOTING_TEMPLATE,
    "installation": INSTALLATION_TEMPLATE,
    "comparison": COMPARISON_TEMPLATE,
    "maintenance": MAINTENANCE_TEMPLATE,
    "price": PRICE_TEMPLATE,
    "transcript": TRANSCRIPT_TEMPLATE,
    "general": GENERAL_TEMPLATE
}

# Keywords that suggest question type
QUERY_KEYWORDS = {
    "compatibility": [
        "fit", "fits", "compatible", "work with", "compatibility", "fitment", 
        "interchange", "interchangeable", "same as", "match", "matches"
    ],
    "troubleshooting": [
        "problem", "issue", "not working", "broken", "fails", "failure", "diagnose",
        "diagnostic", "check", "testing", "test", "symptoms", "troubleshoot", "fix"
    ],
    "installation": [
        "install", "replace", "removal", "remove", "change", "changing", "guide",
        "instructions", "steps", "procedure", "how to", "diy", "torque", "tighten"
    ],
    "comparison": [
        "better", "best", "quality", "difference", "versus", "vs", "compare",
        "comparison", "brand", "recommendation", "recommend", "suggested", "prefer"
    ],
    "maintenance": [
        "maintenance", "service", "interval", "schedule", "regular", "preventative",
        "prevent", "care", "protect", "extend life", "longevity", "how often"
    ],
    "price": [
        "cost", "price", "expensive", "cheap", "affordable", "deal", "discount",
        "oem price", "aftermarket price", "how much", "worth", "value", "pricing"
    ],
    "transcript": [
        "transcript", "conversation", "customer said", "dialogue", "chat log",
        "call", "talked", "speaking", "spoke", "customer", "said", "mentioned"
    ]
}

def get_query_type(message):
    """
    Determine the type of query based on keywords in the message
    """
    message = message.lower()
    
    # Count keyword matches for each category
    category_scores = {}
    for category, keywords in QUERY_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in message)
        category_scores[category] = score
    
    # Get the category with the highest score, defaulting to general
    if not category_scores or max(category_scores.values()) == 0:
        return "general"
    
    return max(category_scores.items(), key=lambda x: x[1])[0]

def get_template_for_message(message):
    """
    Get the appropriate template for a given message
    """
    query_type = get_query_type(message)
    return QUERY_TEMPLATES.get(query_type, GENERAL_TEMPLATE)