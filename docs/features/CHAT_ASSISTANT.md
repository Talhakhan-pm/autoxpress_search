# Chat Assistant Feature

## Overview

The Chat Assistant feature provides an AI-powered conversational interface that allows users to ask questions about automotive parts, get recommendations, and receive technical advice. The assistant leverages OpenAI's GPT-4 model with specialized automotive knowledge, combined with contextual awareness of the user's vehicle information and search history for more relevant responses.

## Core Components

### Backend Components

1. **Chatbot Handler** (`chatbot_handler.py`):
   - Manages message processing and response generation
   - Maintains conversation context for more relevant responses
   - Handles specialized analysis for transcript conversations
   - Formats responses with appropriate guidance and structure
   - Integrates with OpenAI API for AI-powered responses

2. **Query Templates** (`query_templates.py`):
   - Provides specialized templates for different query types
   - Detects question categories via keyword matching
   - Contains templates for compatibility, troubleshooting, installation, etc.
   - Enables consistent and complete responses for each query type

3. **Chat API** (in `app.py`):
   - Endpoint: `/api/chat`
   - Accepts chat message and conversation history
   - Returns AI-generated responses with optional suggestions
   - Processes message context for improved relevance

### Frontend Components

1. **Chat Interface** (`chatbot.js`):
   - Manages user interactions with the chat assistant
   - Handles message sending and receiving
   - Formats message display with markdown/rich text support
   - Maintains chat history in session storage
   - Provides typing indicators for user experience
   - Offers quick response buttons for common queries

2. **Chat Styling** (`chatbot.css`):
   - Styling for chat messages and interface
   - User vs. system message differentiation
   - Rich text formatting for responses
   - Animation for typing indicators
   - Responsive design for different screen sizes

## User Flow

1. **Access Chat Interface**:
   - User navigates to the "Chat Assistant" tab
   - System displays the chat interface with welcome message and quick response options

2. **Send Message**:
   - User types a message or selects a quick response button
   - Message appears in the chat as a user message
   - Typing indicator shows that the assistant is "thinking"

3. **Process Message**:
   - Frontend sends message to `/api/chat` endpoint
   - Backend detects message type and appropriate template
   - Backend processes message with contextual awareness:
     - Conversation history (up to 5 previous messages)
     - Vehicle information from other tabs
     - Part search history
   - AI generates a relevant response using the appropriate template

4. **Receive Response**:
   - Response is displayed in the chat interface
   - Formatting is applied for improved readability (paragraphs, bold, etc.)
   - The response typically includes product suggestions, prices, and follow-up questions

5. **Continue Conversation**:
   - Chat history is maintained within the session
   - User can ask follow-up questions that reference previous context
   - User can start a new topic at any time
   - All exchanges are preserved until actively cleared

## Features

### Message Type Detection

The system automatically detects different types of messages:

- **Compatibility Questions**: Parts that fit specific vehicles
- **Troubleshooting Help**: Diagnosing vehicle issues
- **Installation Guidance**: Steps for replacing parts
- **Part Comparisons**: Quality differences between options
- **Maintenance Advice**: Service intervals and recommendations
- **Price Inquiries**: Cost information for parts
- **Return Policy**: Information about returning parts
- **Transcript Analysis**: Analyzing customer conversations for sales opportunities

### Contextual Awareness

The chat assistant uses several forms of context:

- **Conversation History**: Tracks up to 5 previous messages for continuity
- **Vehicle Context**: Integrates with vehicle information from other tabs (year, make, model, engine)
- **Parts History**: Considers previously searched parts for recommendations
- **Query Type**: Adjusts response format based on message category

### Specialized Templates

Different question types receive tailored response formats:

- **Compatibility Template**: Focuses on fitment factors and verification methods
- **Troubleshooting Template**: Lists causes, diagnostics, and repair guidance
- **Installation Template**: Provides tools needed and step-by-step instructions
- **Comparison Template**: Contrasts OEM vs. aftermarket options and quality differences
- **Price Template**: Offers price ranges for different quality levels
- **Transcript Analysis Template**: Provides specialized sales guidance from conversation transcripts

### Rich Message Formatting

Responses include formatting for improved readability:

- **Markdown Support**: Bold text, italics, and lists
- **Emojis**: Visual section separators
- **Paragraph Structure**: Clear breaks between topic sections
- **Bulleted Lists**: Organized presentation of options or steps

### Session Persistence

- Chat history is saved to session storage
- Conversations persist during the session
- User can clear history if desired
- History is displayed when returning to the chat tab

## Implementation Details

### Chat Message Processing

1. **Message Submission Flow**:
   ```javascript
   function processMessage(message) {
       // Show typing indicator
       showTypingIndicator();
       
       // Get conversation context for better responses
       const conversationContext = getConversationContext(5);
       
       // Get user vehicle context if available
       let vehicleContext = {};
       if (typeof getVehicleContext === 'function') {
           vehicleContext = getVehicleContext();
       }
       
       // Get parts search history if available
       let partsHistory = [];
       if (typeof getPartsHistory === 'function') {
           partsHistory = getPartsHistory();
       }
       
       // Prepare request data
       const requestData = {
           message: message,
           timestamp: new Date().toISOString(),
           conversation_history: conversationContext,
           vehicle_context: vehicleContext,
           parts_history: partsHistory
       };
       
       // Send request to backend
       fetch('/api/chat', {
           method: 'POST',
           headers: {
               'Content-Type': 'application/json'
           },
           body: JSON.stringify(requestData)
       })
       .then(response => response.json())
       .then(data => {
           // Handle the response
           // ...
       });
   }
   ```

2. **Backend Processing Flow**:
   ```python
   def process_chat_message(data):
       """Process chat messages and return AI-powered responses"""
       try:
           # Extract data from request
           message = data.get('message', '')
           conversation_history = data.get('conversation_history', [])
           vehicle_context = data.get('vehicle_context', {})
           parts_history = data.get('parts_history', [])
           
           # Check if this is a transcript analysis request
           is_transcript = detect_transcript(message)
           
           # Initialize OpenAI client
           client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
           
           # Handle different message types
           if is_transcript:
               # Format transcript with specialized processing
               # ...
           else:
               # Build standard system prompt
               system_prompt = create_system_prompt()
               specialized_template = get_template_for_message(message)
           
           # Format context prompts
           vehicle_context_prompt = create_vehicle_context_prompt(vehicle_context)
           parts_history_prompt = create_parts_history_prompt(parts_history)
           
           # Combine all prompt components
           combined_system_prompt = f"{system_prompt}\n\n{specialized_template}\n\n{vehicle_context_prompt}\n\n{parts_history_prompt}"
           
           # Create messages array with conversation history
           messages = [{"role": "system", "content": combined_system_prompt}]
           for msg in conversation_history:
               # Add valid history messages
               # ...
           
           # Add current query
           messages.append({"role": "user", "content": message})
           
           # Call OpenAI API
           response = client.chat.completions.create(
               model="gpt-4-turbo",
               messages=messages,
               max_tokens=1500,  # Allows for comprehensive responses
               temperature=0.7   # Balanced creativity and determinism
           )
           
           # Process and return the response
           response_text = response.choices[0].message.content.strip()
           return jsonify({"response": response_text, "is_transcript": is_transcript})
       
       except Exception as e:
           # Error handling
           # ...
   ```

### Template Selection System

The system uses keyword matching to determine the appropriate template:

```python
def get_query_type(message):
    """Determine the type of query based on keywords in the message"""
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
```

### Transcript Detection System

The chat assistant can detect when users are asking for analysis of a customer conversation:

```python
def detect_transcript(message):
    """Detect if a message appears to be a customer conversation transcript"""
    # Check for explicit markers
    explicit_markers = ["transcript:", "conversation:", "customer said:"]
    if any(message.lower().startswith(marker) for marker in explicit_markers):
        return True
        
    # Check for transcript-like indicators
    indicators = [
        # Pattern of back-and-forth conversation
        ": " in message and message.count(": ") > 1,
        
        # Common transcript markers
        "customer:" in message.lower(),
        
        # Speech patterns
        len(message) > 100 and message.count('"') >= 2,
        
        # Multiple first-person sentences
        message.count(". I") > 1
    ]
    
    # If at least two indicators are true, treat as transcript
    return sum(indicators) >= 2
```

### Message Formatting

The chat assistant formats messages for improved readability:

```javascript
function formatMessageText(text) {
    // First handle any HTML to prevent XSS
    let safeText = text
        .replace(/<script/gi, "&lt;script")
        .replace(/<iframe/gi, "&lt;iframe");
    
    // Convert HTML tags to markdown
    safeText = safeText.replace(/<strong>(.*?)<\/strong>/gi, '**$1**');
    safeText = safeText.replace(/<em>(.*?)<\/em>/gi, '_$1_');
    
    // Split into paragraphs
    const paragraphs = safeText.split(/\n\n+/);
    
    // Process each paragraph separately
    const processedParagraphs = paragraphs.map(paragraph => {
        // Convert markdown formatting to HTML
        // Convert links to clickable elements
        // Format lists properly
        // ...
    });
    
    // Join processed paragraphs
    return processedParagraphs.join('');
}
```

### Chat History Management

The chat history is maintained in session storage:

```javascript
// Save chat history to session storage
function saveChatHistory() {
    sessionStorage.setItem('chatHistory', JSON.stringify(chatHistory));
}

// Load chat history from session storage
function loadChatHistory() {
    const savedHistory = sessionStorage.getItem('chatHistory');
    if (savedHistory) {
        try {
            chatHistory = JSON.parse(savedHistory);
            
            // Display messages from history
            chatHistory.forEach(item => {
                // Display each message
                // ...
            });
        } catch (e) {
            // Handle errors
            console.error('Error loading chat history:', e);
            sessionStorage.removeItem('chatHistory');
            chatHistory = [];
        }
    }
}
```

## UI Components

### Chat Message Container

- Message bubbles with different styling for user vs. system
- Timestamp display for each message
- Rich text formatting within messages
- Auto-scrolling to new messages

### Input Area

- Text input field for user messages
- Send button with appropriate states
- Quick response buttons for common queries
- Clear chat history button

### Typing Indicator

- Animated dots indicating the system is processing
- Provides visual feedback during API calls
- Improves perceived responsiveness

### Quick Response Options

- Pre-defined common questions for fast interaction
- Dynamically updates based on conversation context
- Helps users discover assistant capabilities

## Error Handling

1. **Network Issues**:
   - Handles API request failures
   - Provides user-friendly error messages
   - Allows retry without losing message

2. **API Errors**:
   - Handles OpenAI API errors
   - Provides fallback responses
   - Logs errors for troubleshooting

3. **Session Storage Issues**:
   - Handles corrupted chat history
   - Provides recovery mechanism
   - Preserves current session on errors

## Technical Requirements

- **OpenAI API Key**: Required for backend AI processing
- **Web Browser**: Modern browser with:
  - Session Storage support
  - ECMAScript 2015+ support
  - CSS3 support
- **Backend Environment**:
  - Python 3.6+ with Flask
  - OpenAI Python library

## Usage Examples

### Basic Part Question

**User**: "What brake pads would you recommend for a 2018 Toyota Camry?"

**Assistant**: 
```
🚗 For your 2018 Toyota Camry, I recommend **OEM Toyota brake pads** or high-quality aftermarket options like **Akebono ProACT** or **Brembo Premium Ceramic**.

💰 Price ranges to expect:
- OEM Toyota: **$60-90** per axle
- Akebono ProACT: **$45-65** per axle
- Brembo Premium: **$50-75** per axle

⚙️ All these options offer excellent dust control and minimal noise, with the OEM providing the most consistent performance. The aftermarket options may last slightly longer in some driving conditions.

🔧 Will you be installing these yourself or having a shop do the work?

📞 For help or a quote, call AutoXpress at 252-275-3786 or visit https://autoxpress.us
```

### Transcript Analysis

**User**: "Can you analyze this customer conversation? Customer: I need wheel bearings for my F150. Agent: What year is your truck? Customer: It's a 2015, and I think it's the front ones making noise."

**Assistant**:
```
Here's my analysis of the customer conversation:

🔍 PART VERIFICATION:
The customer needs **front wheel bearings** for a **2015 Ford F150**. The correct parts would be **Timken HA590435** for the driver side and **Timken HA590030** for the passenger side. These are complete hub assemblies which is what this vehicle uses (not traditional bearings).

💰 PRICING GUIDANCE:
- OEM Ford price: **$175-225** per side
- Timken (premium): **$120-150** per side
- Moog (mid-range): **$90-110** per side
A fair markup would be 20-25% above your cost.

🛒 CLOSING THE SALE:
Common objection: "That's more expensive than I expected"
Response: "These are complete hub assemblies, not just bearings. They include the bearing, hub, and ABS sensor all pre-assembled for easier installation and better reliability."

Suggest selling both sides even if only one is making noise, as they typically wear at similar rates.

📞 For help or a quote, call AutoXpress at 252-275-3786 or visit https://autoxpress.us
```

## Future Enhancements

Potential improvements for future versions:

1. **Enhanced Integration**:
   - Deeper integration with product database
   - Direct linking to product search results from chat
   - Ability to add products to cart from the chat

2. **UI Improvements**:
   - Image support in chat messages
   - Voice input option
   - Message categorization and filtering
   - Chat history export

3. **Functionality Expansion**:
   - Guided diagnostic workflows
   - Integration with customer account history
   - Multi-language support
   - Voice output option
   - PDF manual/document search

4. **Performance Optimizations**:
   - Response caching for common questions
   - Reduced token usage for cost efficiency
   - Parallel processing of lengthy requests
   - Local model integration for basic queries

## API Reference

### Chat API

**Endpoint:** `/api/chat`  
**Method:** POST  

**Request Format:**
```json
{
  "message": "What brake pads do you recommend for a 2018 Toyota Camry?",
  "timestamp": "2023-05-18T14:30:00.000Z",
  "conversation_history": [
    {
      "role": "user",
      "content": "I need help with my car",
      "timestamp": "2023-05-18T14:29:00.000Z"
    },
    {
      "role": "assistant",
      "content": "I'd be happy to help with your car. What specific information do you need?",
      "timestamp": "2023-05-18T14:29:30.000Z"
    }
  ],
  "vehicle_context": {
    "year": "2018",
    "make": "Toyota",
    "model": "Camry",
    "engine": "2.5L",
    "vin": "4T1B11HK5JU123456"
  },
  "parts_history": [
    "oil filter",
    "air filter"
  ]
}
```

**Response Format:**
```json
{
  "response": "🚗 For your 2018 Toyota Camry, I recommend OEM Toyota brake pads or high-quality aftermarket options like Akebono ProACT or Brembo Premium Ceramic.\n\n💰 Price ranges to expect:\n- OEM Toyota: $60-90 per axle\n- Akebono ProACT: $45-65 per axle\n- Brembo Premium: $50-75 per axle\n\n⚙️ All these options offer excellent dust control and minimal noise, with the OEM providing the most consistent performance. The aftermarket options may last slightly longer in some driving conditions.\n\n🔧 Will you be installing these yourself or having a shop do the work?\n\n📞 For help or a quote, call AutoXpress at 252-275-3786 or visit https://autoxpress.us",
  "is_transcript": false
}
```

**Error Response:**
```json
{
  "error": "An error occurred while processing your message. Please try again later."
}
```