/**
 * AI Analysis Response Formatter
 * 
 * This script enhances the display of AI analysis responses without interfering
 * with the core application flow.
 * 
 * It applies styling and formatting to AI responses after they are loaded into
 * the DOM by the main application.
 */

document.addEventListener('DOMContentLoaded', function() {
  // Add the stylesheet link to the head
  const cssLink = document.createElement('link');
  cssLink.rel = 'stylesheet';
  cssLink.href = '/static/css/ai-analysis.css';
  document.head.appendChild(cssLink);
  
  // Set up a MutationObserver to watch for changes to the #questions div
  const questionsContainer = document.getElementById('questions');
  
  if (questionsContainer) {
    // Function to enhance the AI response
    function enhanceAIResponse() {
      // Don't process if already enhanced
      if (questionsContainer.querySelector('.ai-analysis')) {
        return;
      }
      
      // Get the raw content - preserve existing HTML formatting
      const content = questionsContainer.innerHTML;
      
      // Check if the content already has paragraph tags
      const hasHtmlStructure = /<p>|<div>|<ul>|<ol>|<li>|<h[1-6]>/i.test(content);
      
      if (!content || content.trim() === '') {
        return;
      }
      
      // Create the enhanced container
      const enhancedContainer = document.createElement('div');
      enhancedContainer.className = 'ai-analysis ai-fade-in';
      
      // Add the header
      const header = document.createElement('div');
      header.className = 'ai-analysis-header';
      header.innerHTML = `
        <div class="ai-icon">
          <i class="fas fa-robot"></i>
        </div>
        <h2 class="ai-title">Analysis Results</h2>
      `;
      enhancedContainer.appendChild(header);
      
      // If the content already has HTML structure, handle it differently
      if (hasHtmlStructure) {
        // For pre-formatted HTML content, we'll create a wrapper and apply styling
        const contentWrapper = document.createElement('div');
        contentWrapper.className = 'ai-section';
        contentWrapper.innerHTML = content;
        
        // Apply highlighting to key terms
        const keyTerms = ['OEM', 'aftermarket', 'genuine', 'compatible', 'direct fit', 'universal'];
        keyTerms.forEach(term => {
          const regex = new RegExp(`\\b${term}\\b`, 'gi');
          contentWrapper.innerHTML = contentWrapper.innerHTML.replace(regex, `<span class="ai-highlight">$&</span>`);
        });
        
        enhancedContainer.appendChild(contentWrapper);
      } else {
        // For plain text content, process with our paragraph detection
        // First normalize line breaks by replacing \n and explicit <br> tags
        const normalizedContent = content.replace(/\n/g, '<br>').replace(/<br\s*\/?>/gi, '<br>');
        // Then split by <br> to get paragraphs
        let paragraphs = normalizedContent.split('<br>').filter(p => p.trim() !== '');
        
        // If we only have one paragraph and it's long, try to break it into sentences
        if (paragraphs.length === 1 && paragraphs[0].length > 150) {
          const sentences = paragraphs[0].split(/(?<=[.!?])\s+/);
          // Group sentences into logical paragraphs (2-3 sentences per paragraph)
          const newParagraphs = [];
          for (let i = 0; i < sentences.length; i += 2) {
            const group = sentences.slice(i, i + 2).join(' ');
            if (group.trim() !== '') {
              newParagraphs.push(group);
            }
          }
          // Only use the sentence-based paragraphs if we got a reasonable number
          if (newParagraphs.length > 1) {
            paragraphs = newParagraphs;
          }
        }
        
        // Create sections based on content patterns
        let currentSection = document.createElement('div');
        currentSection.className = 'ai-section';
        
        paragraphs.forEach((paragraph, index) => {
          // Check if this looks like a section header (ends with a colon)
          const isHeader = /:\s*$/.test(paragraph) && paragraph.length < 100;
          
          if (isHeader && currentSection.childNodes.length > 0) {
            // Add the completed section and start a new one
            enhancedContainer.appendChild(currentSection);
            currentSection = document.createElement('div');
            currentSection.className = 'ai-section';
          }
          
          // Format the paragraph
          const p = document.createElement('p');
          
          // Apply special formatting based on content
          if (isHeader) {
            p.innerHTML = `<strong>${paragraph}</strong>`;
          } else if (paragraph.toLowerCase().includes('compatible') || 
                     paragraph.toLowerCase().includes('will fit')) {
            p.className = 'ai-compatibility';
            p.innerHTML = `<div class="ai-compatibility-title">
                            <i class="fas fa-check-circle"></i> Compatibility Information
                           </div>
                           ${paragraph}`;
          } else if (paragraph.toLowerCase().includes('warning') || 
                     paragraph.toLowerCase().includes('caution') ||
                     paragraph.toLowerCase().includes('note:')) {
            p.className = 'ai-warning';
            p.innerHTML = `<div class="ai-warning-title">
                            <i class="fas fa-exclamation-triangle"></i> Important Note
                           </div>
                           ${paragraph}`;
          } else if (paragraph.toLowerCase().includes('recommend') || 
                     paragraph.toLowerCase().includes('suggest')) {
            p.className = 'ai-recommendation';
            p.innerHTML = `<i class="fas fa-lightbulb"></i> ${paragraph}`;
          } else {
            // Regular paragraph with key term highlighting
            let enhancedText = paragraph;
            
            // Highlight key terms (simple approach)
            const keyTerms = ['OEM', 'aftermarket', 'genuine', 'compatible', 'direct fit', 'universal'];
            keyTerms.forEach(term => {
              const regex = new RegExp(`\\b${term}\\b`, 'gi');
              enhancedText = enhancedText.replace(regex, `<span class="ai-highlight">$&</span>`);
            });
            
            p.innerHTML = enhancedText;
          }
          
          currentSection.appendChild(p);
          
          // For the last paragraph, make sure we add the section
          if (index === paragraphs.length - 1 && currentSection.childNodes.length > 0) {
            enhancedContainer.appendChild(currentSection);
          }
        });
      }
      
      // Replace the original content
      questionsContainer.innerHTML = '';
      questionsContainer.appendChild(enhancedContainer);
    }
    
    // Initial check
    if (questionsContainer.innerHTML.trim() !== '') {
      enhanceAIResponse();
    }
    
    // Set up a MutationObserver to watch for changes
    const observer = new MutationObserver(function(mutations) {
      mutations.forEach(function(mutation) {
        if (mutation.type === 'childList' && questionsContainer.innerHTML.trim() !== '') {
          enhanceAIResponse();
        }
      });
    });
    
    // Configure and start the observer
    observer.observe(questionsContainer, { childList: true });
    
    // Listen for tab changes to ensure proper display
    document.querySelectorAll('button[data-bs-target="#analysis-content"]').forEach(function(tab) {
      tab.addEventListener('shown.bs.tab', function() {
        enhanceAIResponse();
      });
    });
  }
});