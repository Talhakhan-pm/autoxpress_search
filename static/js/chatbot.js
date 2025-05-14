/**
 * Chatbot functionality for AutoXpress
 * Handles user interactions with the chat assistant
 */

// Store the chat history in session storage
let chatHistory = [];

// Initialize the chatbot functionality
document.addEventListener('DOMContentLoaded', function() {
    // Cache DOM elements
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');
    const clearChatBtn = document.getElementById('clear-chat');
    const quickResponseBtns = document.querySelectorAll('.quick-response-btn');

    // Load chat history from session storage if available
    loadChatHistory();

    // Listen for form submissions
    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const message = chatInput.value.trim();
        
        if (message) {
            // Add user message to chat
            addUserMessage(message);
            
            // Clear input field
            chatInput.value = '';
            
            // Process the message and get a response
            processMessage(message);
        }
    });

    // Listen for quick response button clicks
    quickResponseBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const message = this.dataset.message;
            if (message) {
                // Set the message in the input field
                chatInput.value = message;
                
                // Trigger form submission
                chatForm.dispatchEvent(new Event('submit'));
            }
        });
    });

    // Listen for clear chat button
    clearChatBtn.addEventListener('click', function() {
        if (confirm('Are you sure you want to clear the chat history?')) {
            clearChat();
        }
    });

    // Optional: Add "typing" indicator when assistant is responding
    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'chat-typing';
        typingDiv.innerHTML = `
            <div class="typing-indicator">
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
            </div>
        `;
        typingDiv.id = 'typing-indicator';
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function removeTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    // Process the user message and generate a response
    // Get conversation context for better AI responses
    function getConversationContext(messageCount = 5) {
        // Get the last N messages from chat history
        const contextMessages = chatHistory.slice(-messageCount);
        return contextMessages.map(msg => ({
            role: msg.type === 'user' ? 'user' : 'assistant',
            content: msg.message,
            timestamp: msg.timestamp
        }));
    }

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
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Remove typing indicator
            removeTypingIndicator();
            
            // Check if this is a transcript analysis response
            if (data.is_transcript) {
                // Add transcript analysis response with special formatting
                addTranscriptAnalysis(data.response);
            } else {
                // Add regular system response to chat
                addSystemMessage(data.response);
            }
        })
        .catch(error => {
            // Remove typing indicator
            removeTypingIndicator();
            
            // Add error message to chat
            addSystemMessage("I'm sorry, I couldn't process your request. Please try again later.");
            console.error('Error:', error);
        });
    }

    // Add a user message to the chat
    function addUserMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat-message user-message';
        
        const time = new Date();
        const formattedTime = time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        messageDiv.innerHTML = `
            <div class="message-content">
                <p>${escapeHtml(message)}</p>
            </div>
            <span class="message-time">${formattedTime}</span>
        `;
        
        chatMessages.appendChild(messageDiv);
        
        // Auto scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Add to chat history
        chatHistory.push({
            type: 'user',
            message: message,
            timestamp: time.toISOString()
        });
        
        // Save to session storage
        saveChatHistory();
    }

    // Add a system message to the chat
    function addSystemMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat-message system-message';
        
        const time = new Date();
        const formattedTime = time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        // Format the message with rich text
        const formattedMessage = formatMessageText(message);
        
        messageDiv.innerHTML = `
            <div class="message-content">
                ${formattedMessage}
            </div>
            <span class="message-time">${formattedTime}</span>
        `;
        
        chatMessages.appendChild(messageDiv);
        
        // Auto scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Add to chat history
        chatHistory.push({
            type: 'system',
            message: message,
            timestamp: time.toISOString()
        });
        
        // Save to session storage
        saveChatHistory();
    }
    
    // Add a transcript analysis to the chat - now uses standard message formatting
    function addTranscriptAnalysis(message) {
        // Just use the standard system message function instead of special formatting
        addSystemMessage(message);
    }
    
    // Helper function to format transcript content
    function formatContent(content) {
        // Convert bullet lists to HTML lists
        if (content.includes('- ')) {
            const listItems = content.split('\n').filter(line => line.trim().startsWith('- '));
            if (listItems.length > 0) {
                let html = '<ul>';
                for (const item of listItems) {
                    const itemText = item.replace(/^-\s*/, '').trim();
                    html += `<li>${itemText}</li>`;
                }
                html += '</ul>';
                return html;
            }
        }
        
        // Format regular content with paragraphs
        return content.split('\n').filter(line => line.trim()).map(line => `<p>${line}</p>`).join('');
    }

    // Format message text with markdown-like features
    function formatMessageText(text) {
        // First handle any HTML to prevent XSS
        let formattedText = text;
        
        // Convert links to clickable elements
        formattedText = formattedText.replace(
            /(\b(https?|ftp|file):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/ig,
            '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
        );
        
        // Convert markdown headings
        formattedText = formattedText.replace(/^### (.*?)$/gm, '<h3>$1</h3>');
        formattedText = formattedText.replace(/^## (.*?)$/gm, '<h2>$1</h2>');
        formattedText = formattedText.replace(/^# (.*?)$/gm, '<h1>$1</h1>');
        
        // Convert markdown bold
        formattedText = formattedText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Convert markdown italic
        formattedText = formattedText.replace(/\*(.*?)\*/g, '<em>$1</em>');
        
        // Convert markdown lists (simple implementation)
        let listConverted = false;
        if (formattedText.includes('- ')) {
            formattedText = formattedText.replace(/^- (.*?)$/gm, '<li>$1</li>');
            listConverted = true;
        }
        if (listConverted) {
            formattedText = formattedText.replace(/(<li>.*?<\/li>\s*)+/gs, '<ul>$&</ul>');
        }
        
        // Convert markdown numbered lists
        let numberedListConverted = false;
        if (/^\d+\. /.test(formattedText)) {
            formattedText = formattedText.replace(/^\d+\. (.*?)$/gm, '<li>$1</li>');
            numberedListConverted = true;
        }
        if (numberedListConverted) {
            formattedText = formattedText.replace(/(<li>.*?<\/li>\s*)+/gs, '<ol>$&</ol>');
        }
        
        // Add paragraph breaks (preserve HTML)
        if (!listConverted && !numberedListConverted) {
            formattedText = formattedText.replace(/\n\n+/g, '</p><p>');
            if (!formattedText.startsWith('<')) {
                formattedText = '<p>' + formattedText;
            }
            if (!formattedText.endsWith('>')) {
                formattedText += '</p>';
            }
        }
        
        return formattedText;
    }
    
    // For backward compatibility
    function convertLinks(text) {
        return formatMessageText(text);
    }

    // Escape HTML to prevent XSS
    function escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

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
                    if (item.type === 'user') {
                        // Don't use addUserMessage to avoid duplicating in the history array
                        const messageDiv = document.createElement('div');
                        messageDiv.className = 'chat-message user-message';
                        
                        const time = new Date(item.timestamp);
                        const formattedTime = time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                        
                        messageDiv.innerHTML = `
                            <div class="message-content">
                                <p>${escapeHtml(item.message)}</p>
                            </div>
                            <span class="message-time">${formattedTime}</span>
                        `;
                        
                        chatMessages.appendChild(messageDiv);
                    } else if (item.type === 'system') {
                        // Don't use addSystemMessage to avoid duplicating in the history array
                        const messageDiv = document.createElement('div');
                        messageDiv.className = 'chat-message system-message';
                        
                        const time = new Date(item.timestamp);
                        const formattedTime = time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                        
                        // Format the message with rich text
                        const formattedMessage = formatMessageText(item.message);
                        
                        messageDiv.innerHTML = `
                            <div class="message-content">
                                ${formattedMessage}
                            </div>
                            <span class="message-time">${formattedTime}</span>
                        `;
                        
                        chatMessages.appendChild(messageDiv);
                    }
                });
                
                // Auto scroll to bottom
                chatMessages.scrollTop = chatMessages.scrollHeight;
            } catch (e) {
                console.error('Error loading chat history:', e);
                // Clear corrupted history
                sessionStorage.removeItem('chatHistory');
                chatHistory = [];
            }
        }
    }

    // Clear the chat
    function clearChat() {
        // Clear the chat messages from the DOM
        // Keep the welcome message
        while (chatMessages.children.length > 1) {
            chatMessages.removeChild(chatMessages.lastChild);
        }
        
        // Clear chat history (except welcome message)
        const welcomeMessage = chatHistory.length > 0 ? chatHistory[0] : null;
        chatHistory = welcomeMessage ? [welcomeMessage] : [];
        saveChatHistory();
    }
});

// Add a function to handle product references from search results
function referProductToChat(productName, productId) {
    const chatInput = document.getElementById('chat-input');
    chatInput.value = `Tell me more about this product: ${productName} (ID: ${productId})`;
    
    // Focus the input
    chatInput.focus();
    
    // Switch to chat tab
    document.getElementById('chatbot-tab').click();
}