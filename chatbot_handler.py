"""
Chatbot Handler Module
Processes chat messages and generates AI-powered responses
"""

import os
from openai import OpenAI
from flask import jsonify
from query_templates import get_template_for_message

def process_chat_message(data):
    """
    Process chat messages and return AI-powered responses with conversation context
    
    Args:
        data (dict): The request data containing message and context
        
    Returns:
        dict: JSON response with AI-generated message or error
    """
    try:
        # Extract data from request
        message = data.get('message', '')
        conversation_history = data.get('conversation_history', [])
        vehicle_context = data.get('vehicle_context', {})
        parts_history = data.get('parts_history', [])
        
        # Check if this is a transcript analysis request
        is_transcript = detect_transcript(message)
        
        if not message:
            return jsonify({"error": "No message provided"}), 400
        
        # Initialize OpenAI client
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Handle transcript analysis differently
        if is_transcript:
            # Format the transcript for better analysis
            formatted_message = format_transcript(message)
            
            # Create a specialized system prompt for transcript analysis
            system_prompt = """You are a SENIOR AUTOMOTIVE PARTS SPECIALIST with 20+ years of experience in the exact parts mentioned.

Your role is to provide PRACTICAL, ACCURATE sales advice based on real industry knowledge:

1. PART VERIFICATION: 
   - Identify if specific part numbers mentioned are correct for the customer's needs
   - You know which parts have which features for major vehicle brands
   - You understand OEM vs aftermarket differences for these specific parts

2. PRICING & AVAILABILITY:
   - You know current market prices for these specific parts
   - You're aware of supply chain issues affecting these components
   - You can suggest alternative parts that are compatible

3. SALES OBJECTIONS:
   - You've heard all customer objections about these parts
   - You have proven scripts that overcome these objections
   - You know which selling points are most effective

CRITICALLY IMPORTANT:
- Focus on ACCURACY over confidence - be truthful about what you know
- Provide SPECIFIC part numbers, prices, and compatibility information
- Address the EXACT part the customer is asking about
- Include warranty information and upsell opportunities"""
            
            # Use transcript template
            specialized_template = "transcript"
            
            # Override the message with the formatted version
            message = formatted_message
        else:
            # Build the standard system prompt
            system_prompt = create_system_prompt()
            
            # Get specialized template based on message content
            specialized_template = get_template_for_message(message)
        
        # Check if this is a product-specific question
        product_prompt = create_product_prompt(message)
        
        # Format vehicle context if available
        vehicle_context_prompt = create_vehicle_context_prompt(vehicle_context)
        
        # Format parts search history if available
        parts_history_prompt = create_parts_history_prompt(parts_history)
        
        # Combine all prompt components
        combined_system_prompt = (
            f"{system_prompt}\n\n"
            f"{specialized_template}\n\n"
            f"{vehicle_context_prompt}\n\n"
            f"{parts_history_prompt}"
        )
        
        # Prepare messages array with conversation history
        messages = [{"role": "system", "content": combined_system_prompt}]
        
        # Add conversation history (up to 5 previous messages)
        if conversation_history:
            # Convert conversation history to the format expected by OpenAI
            for msg in conversation_history:
                role = msg.get('role', '')
                content = msg.get('content', '')
                # Only add valid messages with proper roles
                if content and role in ['user', 'assistant']:
                    messages.append({"role": role, "content": content})
        
        # Add current user query
        current_prompt = message
        if product_prompt:
            current_prompt = f"{product_prompt}\n\nUser message: {message}"
            
        messages.append({"role": "user", "content": current_prompt})
        
        # Check if this is a company policy query that still needs varied responses
        is_policy_query = any(policy_type in message.lower() for policy_type in 
                             ["return policy", "call", "missed", "follow up", "callback"])
        
        # Call OpenAI API with conversation context
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Using faster model for quicker responses
            messages=messages,
            max_tokens=500,  # Reduced for faster responses
            temperature=0.8 if is_policy_query else 0.7  # Slightly higher temp for policy responses
        )
        
        # Extract the response text
        response_text = response.choices[0].message.content.strip()
        
        # Format the response for transcript analysis
        if is_transcript:
            response_text = format_sales_guidance_response(response_text)
        
        # Return the response
        return jsonify({"response": response_text, "is_transcript": is_transcript})
    
    except Exception as e:
        # Log the error but don't expose details to the client
        print(f"Chat API error: {e}")
        return jsonify({
            "error": "An error occurred while processing your message. Please try again later."
        }), 500


def create_system_prompt():
    """Create the base system prompt for the chatbot"""
    return """You are AutoXpress Chat Assistant, an expert in automotive parts and repairs representing AutoXpress company. 

Your goals are to:
1. Provide accurate information about auto parts, vehicle compatibility, and repair procedures
2. Give specific, actionable advice that helps users find the right parts for their vehicles
3. Be conversational but concise, keeping responses under 200 words
4. Acknowledge when you don't have specific information about a particular product
5. Always mention you are from AutoXpress in your responses
6. Include the AutoXpress website (https://autoxpress.us) and phone number (252-275-3786) when discussing orders, appointments, or customer service

When discussing parts:
- Explain compatibility with different vehicle models when relevant
- Distinguish between OEM and aftermarket options
- Mention installation difficulty when appropriate
- Discuss durability and quality considerations
- Address common issues or benefits

For company policies:
- Return Policy: Explain that AutoXpress offers a 30-day satisfaction guarantee with full refund for unused parts
- Missed Calls: Offer to have an AutoXpress representative call them back by taking their contact info
- Callbacks: Mention that AutoXpress typically returns calls within 1 business day
- Follow-ups: Suggest scheduling follow-up appointments for installation verification or part performance

For each response about company policies, generate unique, personalized text that conveys the policy information without repeating the exact same wording.

Format your responses clearly with short paragraphs and occasional bullet points for complex information.
"""


def create_product_prompt(message):
    """Create a specialized prompt for product-specific questions"""
    product_prompt = ""
    if "tell me more about this product:" in message.lower():
        # Extract product details from the message
        product_info = message.split(":", 1)[1].strip() if ":" in message else ""
        if product_info:
            product_prompt = f"""
            The user is asking about a specific product: {product_info}
            
            Provide specific information about this product, considering:
            - Its compatibility with different vehicle models
            - Whether it's OEM or aftermarket
            - Installation difficulty
            - Expected durability
            - Common issues or benefits
            """
    return product_prompt


def create_vehicle_context_prompt(vehicle_context):
    """Format vehicle context information for the prompt"""
    vehicle_context_prompt = ""
    if vehicle_context and any(vehicle_context.values()):
        vehicle_info = []
        if vehicle_context.get('year'): 
            vehicle_info.append(f"Year: {vehicle_context['year']}")
        if vehicle_context.get('make'): 
            vehicle_info.append(f"Make: {vehicle_context['make']}")
        if vehicle_context.get('model'): 
            vehicle_info.append(f"Model: {vehicle_context['model']}")
        if vehicle_context.get('engine'): 
            vehicle_info.append(f"Engine: {vehicle_context['engine']}")
        if vehicle_context.get('vin'): 
            vehicle_info.append(f"VIN: {vehicle_context['vin']}")
            
        if vehicle_info:
            vehicle_context_prompt = f"""
            USER'S VEHICLE INFORMATION:
            {', '.join(vehicle_info)}
            
            Reference this vehicle information when appropriate in your responses, 
            especially for compatibility questions.
            """
    return vehicle_context_prompt


def create_parts_history_prompt(parts_history):
    """Format parts search history for the prompt"""
    parts_history_prompt = ""
    if parts_history and len(parts_history) > 0:
        parts_list = ', '.join(parts_history[:5])  # Use up to 5 most recent parts
        parts_history_prompt = f"""
        USER'S RECENT PART SEARCHES:
        {parts_list}
        
        Consider these part interests when providing recommendations or examples.
        """
    return parts_history_prompt


def detect_transcript(message):
    """
    Detect if a message appears to be a customer conversation transcript
    
    Args:
        message (str): The user's message
        
    Returns:
        bool: True if this appears to be a transcript, False otherwise
    """
    # If message explicitly starts with markers, immediately return true
    explicit_markers = ["transcript:", "conversation:", "customer said:", "analyze this conversation:"]
    if any(message.lower().startswith(marker) for marker in explicit_markers):
        return True
        
    # Force detection for messages containing specific phrases
    force_markers = [
        "I've got", "got an old", "gonna put", "looking for one to replace", 
        "the motors junk", "drive line", "customer told me", "customer called",
        "customer wants", "transcript"
    ]
    
    if any(marker in message.lower() for marker in force_markers) and len(message) > 100:
        return True
    
    # Check for transcript-like indicators
    indicators = [
        # Pattern of back-and-forth conversation
        ": " in message and message.count(": ") > 1,
        
        # Common transcript markers
        any(marker in message.lower() for marker in ["transcript", "conversation", "customer said"]),
        
        # Check for speech patterns
        "I said" in message or "they said" in message or "customer:" in message.lower(),
        
        # Long message with quotation marks suggesting dialogue
        len(message) > 200 and message.count('"') >= 2,
        
        # Check for multiple sentences with first-person pronouns
        message.count(". I") > 1 or message.count(". He") > 1 or message.count(". She") > 1,
        
        # Check for rambling speech patterns with filler words
        len(message) > 100 and any(filler in message.lower() for filler in ["um", "uh", "like", "y'know", "gonna", "wanna"]),
        
        # Check for automotive terms in a long message
        len(message) > 100 and any(term in message.lower() for term in ["engine", "motor", "transmission", "jeep", "ford", "chevy"]),
        
        # Has word "transcript" explicitly 
        "transcript" in message.lower()
    ]
    
    # If at least two indicators are true, treat as transcript
    return sum(indicators) >= 2


def format_transcript(message):
    """
    Format and clean a transcript for better analysis
    
    Args:
        message (str): The transcript text
        
    Returns:
        str: Formatted transcript ready for analysis
    """
    # Check if the transcript appears to be just pasted with no explanation
    if not message.lower().startswith(("transcript", "conversation", "here", "this is", "analyze")):
        # Add a clear header to help model understand context
        message = "SALES CALL TRANSCRIPT FROM CUSTOMER:\n\n" + message
    
    # Clean up common transcript issues
    formatted = message.replace("Customer:", "\nCustomer:").replace("Agent:", "\nAgent:")
    formatted = formatted.replace("Rep:", "\nAgent:").replace("Sales:", "\nAgent:")
    
    # Add paragraph breaks at likely sentence boundaries to improve readability
    if "Customer:" not in formatted and "Agent:" not in formatted:
        # This is likely a raw transcript without markers
        # Add paragraph breaks at sentence endings
        for pattern in [". ", "! ", "? ", ". I", ". He", ". She", ". The", ". My", ". It"]:
            formatted = formatted.replace(pattern, pattern + "\n")
    
    # Add explicit instructions for analyzing as a sales opportunity
    formatted += """

ANALYZE THIS CUSTOMER CONVERSATION FOR SALES OPPORTUNITIES:
- Make BOLD, SPECIFIC recommendations about what parts to sell
- State EXACT prices and product specifications (even if guessing)
- Give me AGGRESSIVE sales tactics specifically for this customer
- Provide SPECIFIC upsell opportunities with exact price points
- DO NOT hedge with "maybe" or "check" - be CONFIDENT and DIRECT
- The agent knows your assertions may not be 100% accurate
"""
    
    return formatted


def format_sales_guidance_response(response_text):
    """
    Format the sales guidance response for better readability
    
    Args:
        response_text (str): The raw response from the AI
        
    Returns:
        str: Formatted response with improved structure
    """
    # Ensure section headers are properly formatted
    sections = [
        ("KEY VEHICLE INFORMATION", "🚗 VEHICLE DETAILS"),
        ("CUSTOMER NEEDS", "🔍 CUSTOMER NEEDS"),
        ("SALES GUIDANCE", "💼 SALES GUIDANCE"),
        ("PRODUCT RECOMMENDATIONS", "🛒 PRODUCT RECOMMENDATIONS"),
        ("NEXT QUESTIONS", "❓ SUGGESTED QUESTIONS"),
        ("RED FLAGS", "⚠️ IMPORTANT CONSIDERATIONS")
    ]
    
    formatted = response_text
    for old_header, new_header in sections:
        formatted = formatted.replace(old_header, new_header)
    
    # Add a helpful introduction
    if not formatted.startswith("Here's my analysis"):
        formatted = "Here's my analysis of the customer conversation:\n\n" + formatted
    
    return formatted