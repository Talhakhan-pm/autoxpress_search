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

# Template for return policy inquiries
RETURN_POLICY_TEMPLATE = """
The user is asking about AutoXpress's return policy. In your response:

1. Explain that AutoXpress offers a 30-day satisfaction guarantee with full refund for unused parts
2. Mention that parts must be in their original packaging and unused condition
3. Clarify that special order parts may have different return terms
4. Include AutoXpress's contact number (252-275-3786) for processing returns
5. Reference the website (https://autoxpress.us) for full return policy details

Generate a unique, conversational response that doesn't sound like a standard policy statement.
Make your response sound personalized for this specific customer.
"""

# Template for warranty script for agents
WARRANTY_TEMPLATE = """
Generate a concise sales closing script about AutoXpress warranties. The agent will read this to customers during sales calls:

1. Create 1-3 brief, persuasive sentences about:
   - 30-day money-back guarantee on all parts 
   - 1-year manufacturer warranty on most parts
2. Focus on VALUE and PEACE OF MIND these warranties provide
3. Make it sound natural for verbal delivery, not like reading policy text
4. Avoid asking for commitment or agreement
5. Do NOT include contact information or website

Create 2-3 DIFFERENT script variations so the agent can choose. Each should be 1-3 sentences only.
"""

# Template for missed call responses
MISSED_CALL_TEMPLATE = """
Choose from one of these casual, agent-style responses when a customer call is missed. Keep it under 25 words plus the signature line.

1. Apologies for missing your call—😏 we're back now and ready to get you the part you need. Text or call here and we'll get moving fast 🔧
2. Just missed your call — let's get you squared away. Call or text us now and we'll take care of it. 🛠️
3. Sorry we missed you! Let's pick up where we left off. 📞 Call us at your convenience — we're here and ready to go.

Signature (add after any message):
Contact us: (252-275-3786) or https://autoxpress.us
"""

# Template for callback requests
CALLBACK_TEMPLATE = """
Use one of these when requesting a callback about an order. Keep it short, confident, and under 25 words plus signature.

1. We've got an update on your order 🔧 — call or text us when you're free and we'll get things moving.
2. ✅ Your part is ready for the next step — reach out and we'll confirm details quickly.
3. Quick update on your request — call us and we'll wrap it up fast 💨

Signature (always include):
Contact us: (252-275-3786) or https://autoxpress.us
"""

# Template for follow-up requests
FOLLOWUP_TEMPLATE = """
Use for part-related follow-up. Should be short, friendly, and lightly persuasive. Add urgency without pressure.

1. Just checking in 👋 — need anything else for that [part]? We can wrap things up today if you're ready.
2. Any update on the [part] you were looking for? We've got options ready now 🔧
3. Still need help with that [part]? Let's finalize it — text or call and we'll get you squared away.

Signature:
Contact us: (252-275-3786) or https://autoxpress.us
"""

# Template for customer transcript analysis
TRANSCRIPT_TEMPLATE = """
As an automotive parts sales expert with SPECIFIC KNOWLEDGE of RAM trucks and OEM parts, analyze this conversation to provide PRACTICAL SALES ADVICE that addresses the customer's actual situation.

BE CONCISE AND USE CLEAR FORMATTING:
- Use 🚗 emojis to separate sections
- Use markdown for formatting: **bold text** for key info, _italics_ for emphasis
- NEVER use HTML tags like <strong> or <em> - use markdown formatting only
- Keep each section under 4-5 lines
- Use bullet points (- ) for lists
- Leave blank lines between sections

DIRECTLY ANSWER THE FOLLOWING (choose only the 3 most relevant sections):

1. 🔍 PART VERIFICATION:
   - CONFIRM or DENY if the specific part number mentioned has the features needed
   - State which vehicle models this part fits (specific years/trims)
   - List the EXACT features of this part (autodim, heated, power fold, etc.)
   - If the part is incorrect, state the CORRECT part number

2. 💰 PRICING GUIDANCE:
   - Give the ACTUAL MARKET PRICE RANGE for this specific part
   - Provide the typical dealer price vs. aftermarket price
   - Suggest a fair but profitable markup percentage

3. 🛒 CLOSING THE SALE:
   - Provide 1-2 SPECIFIC objections customers typically have about this part
   - Give word-for-word responses to overcome these objections
   - Suggest a specific upsell that typically goes with this part

4. 📦 INVENTORY & AVAILABILITY:
   - Note if this part typically has supply chain issues
   - Suggest alternative part numbers if needed
   - List compatible third-party brands that fit this application

Format your response like a practical sales guide for someone who needs to make the sale TODAY.
Include part numbers, exact prices, and specific features - not generic advice.
KEEP RESPONSE UNDER 1500 TOKENS.
"""

# Dictionary to map question types to templates
QUERY_TEMPLATES = {
    "compatibility": COMPATIBILITY_TEMPLATE,
    "troubleshooting": TROUBLESHOOTING_TEMPLATE,
    "installation": INSTALLATION_TEMPLATE,
    "comparison": COMPARISON_TEMPLATE,
    "maintenance": MAINTENANCE_TEMPLATE,
    "price": PRICE_TEMPLATE,
    "return_policy": RETURN_POLICY_TEMPLATE,
    "warranty": WARRANTY_TEMPLATE,
    "missed_call": MISSED_CALL_TEMPLATE,
    "callback": CALLBACK_TEMPLATE,
    "followup": FOLLOWUP_TEMPLATE,
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
    "warranty": [
        "warranty", "warranties", "warranty policy", "guarantee", "money-back", 
        "30-day warranty", "1-year warranty", "manufacturer warranty", "covered by", 
        "warranty coverage", "warranty period", "warranty terms"
    ],
    "return_policy": [
        "return policy", "return", "refund", "money back", "exchange", "30-day", 
        "satisfaction guarantee", "can I return", "return process", "return part"
    ],
    "missed_call": [
        "missed a call", "missed call", "call from you", "missed your call", 
        "we missed", "didn't catch your call", "couldn't answer", "please call back"
    ],
    "callback": [
        "call us back", "call back", "about your order", "order update", "order status", 
        "order question", "regarding your order", "please call", "need to speak"
    ],
    "followup": [
        "about your auto part", "part question", "part update", "part availability", 
        "compatibility check", "follow up", "follow-up", "check in", "checking in"
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