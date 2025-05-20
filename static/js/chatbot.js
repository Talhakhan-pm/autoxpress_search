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
            
            // Get the response text
            let responseText = data.response;
            
            // Check if the response appears to be truncated (ends with a non-punctuation character)
            const seemsTruncated = responseText.length > 800 && 
                                  !responseText.endsWith('.') && 
                                  !responseText.endsWith('!') && 
                                  !responseText.endsWith('?') &&
                                  !responseText.endsWith('"') &&
                                  !responseText.endsWith(')');
            
            // If truncated, add a note about possible truncation
            if (seemsTruncated) {
                responseText += "\n\n⚠️ *This response may have been truncated due to length limitations. Please ask for more details if needed.*";
            }
            
            // Check if this is a transcript analysis response
            if (data.is_transcript) {
                // Add transcript analysis response with special formatting
                addTranscriptAnalysis(responseText);
            } else {
                // Add regular system response to chat
                addSystemMessage(responseText);
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
        // First sanitize any potentially unsafe HTML tags
        let safeText = text
            .replace(/<script/gi, "&lt;script")
            .replace(/<iframe/gi, "&lt;iframe")
            .replace(/<img/gi, "&lt;img")
            .replace(/<on/gi, "&lt;on");
        
        // Handle strong/bold conversion - convert HTML tags to markdown first
        safeText = safeText.replace(/<strong>(.*?)<\/strong>/gi, '**$1**');
        safeText = safeText.replace(/<b>(.*?)<\/b>/gi, '**$1**');
        
        // Handle emphasis/italic conversion
        safeText = safeText.replace(/<em>(.*?)<\/em>/gi, '_$1_');
        safeText = safeText.replace(/<i>(.*?)<\/i>/gi, '_$1_');
        
        // Now split into paragraphs
        const paragraphs = safeText.split(/\n\n+/);
        
        // Process each paragraph separately
        const processedParagraphs = paragraphs.map(paragraph => {
            // Skip processing empty paragraphs
            if (!paragraph.trim()) return '';
            
            let processed = paragraph;
            
            // Convert URLs to clickable links
            processed = processed.replace(
                /(\b(https?|ftp|file):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/ig,
                '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
            );
            
            // Convert markdown headings (must be at start of line)
            if (/^###\s/.test(processed)) {
                processed = processed.replace(/^###\s(.*?)$/gm, '<h3>$1</h3>');
                return processed; // Return early as it's already wrapped
            }
            if (/^##\s/.test(processed)) {
                processed = processed.replace(/^##\s(.*?)$/gm, '<h2>$1</h2>');
                return processed; // Return early as it's already wrapped
            }
            if (/^#\s/.test(processed)) {
                processed = processed.replace(/^#\s(.*?)$/gm, '<h1>$1</h1>');
                return processed; // Return early as it's already wrapped
            }
            
            // Convert markdown bold - do this BEFORE escaping HTML
            processed = processed.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            
            // Convert markdown italic - do this BEFORE escaping HTML
            processed = processed.replace(/_(.*?)_/g, '<em>$1</em>');
            processed = processed.replace(/\*(.*?)\*/g, '<em>$1</em>'); // Alternative style
            
            // Handle lists - first check if this paragraph contains a list
            if (/^- /m.test(processed)) {
                // Split into lines
                const lines = processed.split('\n');
                let inList = false;
                let listItems = [];
                let nonListContent = [];
                
                lines.forEach(line => {
                    if (line.trim().startsWith('- ')) {
                        if (!inList) {
                            // Start a new list
                            inList = true;
                            listItems = [];
                        }
                        // Add to current list (removing the dash)
                        // Don't escape HTML here to preserve bold/italic formatting inside list items
                        let itemContent = line.trim().substring(2);
                        listItems.push(itemContent);
                    } else {
                        if (inList) {
                            // End current list
                            inList = false;
                            // Convert list items to HTML
                            const listHtml = '<ul>' + listItems.map(item => `<li>${item}</li>`).join('') + '</ul>';
                            nonListContent.push(listHtml);
                        }
                        // Add non-list line (don't escape to preserve formatting)
                        if (line.trim()) {
                            nonListContent.push(line);
                        }
                    }
                });
                
                // Handle case where list is at the end
                if (inList) {
                    const listHtml = '<ul>' + listItems.map(item => `<li>${item}</li>`).join('') + '</ul>';
                    nonListContent.push(listHtml);
                }
                
                // Combine everything back
                return nonListContent.join('<br>');
            }
            
            // Handle numbered lists
            if (/^\d+\. /m.test(processed)) {
                // Split into lines
                const lines = processed.split('\n');
                let inList = false;
                let listItems = [];
                let nonListContent = [];
                
                lines.forEach(line => {
                    if (/^\d+\. /.test(line.trim())) {
                        if (!inList) {
                            // Start a new list
                            inList = true;
                            listItems = [];
                        }
                        // Add to current list (removing the number and dot)
                        // Don't escape HTML to preserve formatting
                        let itemContent = line.trim().replace(/^\d+\.\s*/, '');
                        listItems.push(itemContent);
                    } else {
                        if (inList) {
                            // End current list
                            inList = false;
                            // Convert list items to HTML
                            const listHtml = '<ol>' + listItems.map(item => `<li>${item}</li>`).join('') + '</ol>';
                            nonListContent.push(listHtml);
                        }
                        // Add non-list line (don't escape to preserve formatting)
                        if (line.trim()) {
                            nonListContent.push(line);
                        }
                    }
                });
                
                // Handle case where list is at the end
                if (inList) {
                    const listHtml = '<ol>' + listItems.map(item => `<li>${item}</li>`).join('') + '</ol>';
                    nonListContent.push(listHtml);
                }
                
                // Combine everything back
                return nonListContent.join('<br>');
            }
            
            // Convert single newlines within this paragraph to <br>
            // Note: no longer escaping HTML here to preserve formatting
            processed = processed.replace(/\n/g, '<br>');
            
            // Wrap regular text in paragraph
            return `<p>${processed}</p>`;
        });
        
        // Join processed paragraphs
        return processedParagraphs.join('');
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