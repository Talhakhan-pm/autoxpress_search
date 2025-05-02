/**
 * Lazy Loader Module
 * Handles lazy loading of images and optimization techniques
 */

const LazyLoader = (function() {
  // Configuration
  const config = {
    rootMargin: '200px 0px', // Load images 200px before they come into view
    threshold: 0.1,          // Start loading when 10% of the element is visible
    placeholderColor: '#f0f0f0',
    loadingClass: 'lazy-loading',
    loadedClass: 'lazy-loaded'
  };
  
  // IntersectionObserver instance
  let observer = null;
  
  /**
   * Initialize the lazy loader
   */
  function initialize() {
    // Reset any existing observer
    if (observer) {
      observer.disconnect();
      observer = null;
    }
    
    try {
      // Check if IntersectionObserver is supported
      if ('IntersectionObserver' in window) {
        observer = new IntersectionObserver(onIntersection, {
          rootMargin: config.rootMargin,
          threshold: config.threshold
        });
        
        // Find all lazy load elements
        const lazyElements = document.querySelectorAll('[data-src], [data-background]');
        lazyElements.forEach(element => {
          // Mark element as loading and add to observer
          element.classList.add(config.loadingClass);
          observer.observe(element);
        });
        
        console.log(`LazyLoader initialized with ${lazyElements.length} elements`);
      } else {
        // Fall back to loading all images immediately
        loadAllImmediately();
        console.warn('LazyLoader: IntersectionObserver not supported, loaded all images immediately');
      }
    } catch (e) {
      console.error('Error initializing LazyLoader:', e);
      // Attempt to load all images as fallback
      try {
        loadAllImmediately();
      } catch (loadError) {
        console.error('Failed to load images immediately:', loadError);
      }
    }
  }
  
  /**
   * Handle intersection events
   * @param {Array} entries - Intersection entries
   */
  function onIntersection(entries) {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        // Element is now visible, load it
        loadElement(entry.target);
        
        // Stop observing this element
        observer.unobserve(entry.target);
      }
    });
  }
  
  /**
   * Load a specific element's image
   * @param {Element} element - Element to load
   */
  function loadElement(element) {
    let performanceMark = null;
    
    // Start performance monitoring if available
    if (window.PerformanceMonitor) {
      performanceMark = window.PerformanceMonitor.startMeasure('imageLazyLoading', {
        src: element.dataset.src || element.dataset.background,
        elementType: element.tagName
      });
    }
    
    // Handle different element types
    if (element.dataset.src) {
      // For <img> elements
      const imgSrc = element.dataset.src;
      
      // Create a new image to preload
      const img = new Image();
      
      img.onload = function() {
        element.src = imgSrc;
        element.classList.remove(config.loadingClass);
        element.classList.add(config.loadedClass);
        
        // End performance monitoring
        if (performanceMark && window.PerformanceMonitor) {
          window.PerformanceMonitor.endMeasure(performanceMark, {
            success: true,
            width: img.width,
            height: img.height
          });
        }
      };
      
      img.onerror = function() {
        // Handle error - maybe show a placeholder or error indicator
        element.classList.remove(config.loadingClass);
        element.classList.add('lazy-error');
        
        // End performance monitoring with error
        if (performanceMark && window.PerformanceMonitor) {
          window.PerformanceMonitor.endMeasure(performanceMark, {
            success: false,
            error: 'Failed to load image'
          });
        }
      };
      
      // Start loading
      img.src = imgSrc;
    } else if (element.dataset.background) {
      // For elements with background images
      const bgSrc = element.dataset.background;
      
      // Create a new image to preload
      const img = new Image();
      
      img.onload = function() {
        element.style.backgroundImage = `url(${bgSrc})`;
        element.classList.remove(config.loadingClass);
        element.classList.add(config.loadedClass);
        
        // End performance monitoring
        if (performanceMark && window.PerformanceMonitor) {
          window.PerformanceMonitor.endMeasure(performanceMark, {
            success: true,
            width: img.width,
            height: img.height
          });
        }
      };
      
      img.onerror = function() {
        element.classList.remove(config.loadingClass);
        element.classList.add('lazy-error');
        
        // End performance monitoring with error
        if (performanceMark && window.PerformanceMonitor) {
          window.PerformanceMonitor.endMeasure(performanceMark, {
            success: false,
            error: 'Failed to load background image'
          });
        }
      };
      
      // Start loading
      img.src = bgSrc;
    }
  }
  
  /**
   * Load all images immediately (fallback for browsers without IntersectionObserver)
   * @param {Element} container - Container with elements to load (defaults to document)
   */
  function loadAllImmediately(container = document) {
    try {
      const lazyElements = container.querySelectorAll('[data-src], [data-background]');
      console.log(`Loading ${lazyElements.length} images immediately`);
      
      lazyElements.forEach(element => {
        try {
          loadElement(element);
        } catch (elementError) {
          console.warn('Error loading element immediately:', elementError);
          // Last resort - try to set src directly from data-src
          if (element.tagName === 'IMG' && element.dataset.src) {
            element.src = element.dataset.src;
          }
        }
      });
    } catch (e) {
      console.error('Failed to load images immediately:', e);
    }
  }
  
  /**
   * Set up lazy loading for elements added dynamically
   * @param {Element} container - Container with new elements
   */
  function refreshElements(container = document) {
    try {
      // Ensure we have an observer
      if (!observer) {
        initialize();
      }
      
      if (!observer) {
        // If initialization failed, load images immediately instead
        loadAllImmediately(container);
        return;
      }
      
      // Find all new lazy load elements
      const lazyElements = container.querySelectorAll('[data-src], [data-background]');
      console.log('Found ' + lazyElements.length + ' lazy elements to observe');
      
      // Process each element
      lazyElements.forEach(element => {
        try {
          if (!element.classList.contains(config.loadedClass)) {
            // Mark element as loading and add to observer
            element.classList.add(config.loadingClass);
            observer.observe(element);
          }
        } catch (elementError) {
          console.warn('Error observing element:', elementError);
          // Try to load this element immediately as fallback
          try {
            loadElement(element);
          } catch (loadError) {
            console.error('Failed to load element:', loadError);
          }
        }
      });
    } catch (e) {
      console.error('Error refreshing lazy elements:', e);
      // Fallback to loading all immediately
      try {
        loadAllImmediately(container);
      } catch (fallbackError) {
        console.error('Complete failure in image loading system:', fallbackError);
      }
    }
  }
  
  /**
   * Convert product image URLs to lazy loading format
   * @param {string} html - HTML string containing images to convert
   * @returns {string} HTML with lazy loading images
   */
  function convertProductImagesToLazy(html) {
    if (!html) return html;
    
    // Replace image src with data-src
    let lazyHtml = html.replace(
      /<img([^>]*)src="([^"]+)"([^>]*)>/gi,
      function(match, before, src, after) {
        // Skip if already has data-src attribute
        if (match.includes('data-src=')) return match;
        
        // Use placeholder for src and add data-src
        return `<img${before}src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1 1'%3E%3C/svg%3E" data-src="${src}"${after} class="${config.loadingClass}">`;
      }
    );
    
    // Convert div backgrounds to data-background
    lazyHtml = lazyHtml.replace(
      /<div([^>]*)style="([^"]*)(background-image:\s*url\(['"]?([^'")]+)['"]?\))([^"]*)"([^>]*)>/gi,
      function(match, before, stylesBefore, bgImage, url, stylesAfter, after) {
        // Skip if already has data-background attribute
        if (match.includes('data-background=')) return match;
        
        // Create a clean style without the background-image
        const newStyle = stylesBefore + stylesAfter;
        const styleAttr = newStyle.trim() ? ` style="${newStyle}"` : '';
        
        // Use data-background for lazy loading
        return `<div${before}${styleAttr} data-background="${url}"${after} class="${config.loadingClass}">`;
      }
    );
    
    return lazyHtml;
  }
  
  // Listen for DOM updates to handle dynamically added content
  document.addEventListener('DOMContentLoaded', initialize);
  
  // Listen for specific events when products are loaded
  document.addEventListener('productsDisplayed', function() {
    refreshElements();
  });
  
  // Listen for page content updates
  document.addEventListener('contentUpdated', function(e) {
    // Refresh either specific container or entire document
    const container = e.detail && e.detail.container ? e.detail.container : document;
    refreshElements(container);
  });
  
  // Initialize immediately to handle cases where DOM is already loaded
  initialize();
  
  // Public API
  return {
    initialize,
    refreshElements,
    loadElement,
    convertProductImagesToLazy
  };
})();

// Export globally
window.LazyLoader = LazyLoader;