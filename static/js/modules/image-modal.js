/**
 * Enhanced Image Modal Module with Accessibility
 * Handles image preview functionality with zoom and keyboard navigation
 */

const ImageModal = (function() {
  // Modal elements
  let imageModal;
  let modalImage;
  let closeButton;
  let loadingSpinner;
  let zoomInButton;
  let zoomOutButton;
  
  // State variables
  let currentZoom = 1;
  let currentImageSrc = '';
  let currentIndex = 0;
  let productImages = [];
  const MIN_ZOOM = 0.5;
  const MAX_ZOOM = 3;
  const ZOOM_STEP = 0.25;

  function init() {
    // Get modal elements
    imageModal = document.getElementById('imageModal');
    modalImage = document.getElementById('modalImage');
    closeButton = document.querySelector('.close-modal');
    zoomInButton = document.getElementById('zoom-in-btn');
    zoomOutButton = document.getElementById('zoom-out-btn');
    
    if (!imageModal || !modalImage) return;
    
    // Set up the modal initially hidden
    imageModal.style.display = 'none';
    
    // Add a loading indicator to the modal
    loadingSpinner = document.createElement('div');
    loadingSpinner.className = 'image-loading';
    loadingSpinner.id = 'image-loading';
    loadingSpinner.setAttribute('aria-label', 'Loading image');
    loadingSpinner.setAttribute('role', 'status');
    imageModal.appendChild(loadingSpinner);
    
    // Set up event listeners
    setupEventListeners();
  }
  
  function setupEventListeners() {
    // Handle close button click
    if (closeButton) {
      closeButton.addEventListener('click', closeModal);
    }
    
    // Close modal when clicking outside the image
    window.addEventListener('click', function(event) {
      if (event.target === imageModal) {
        closeModal();
      }
    });
    
    // Add zoom button listeners
    if (zoomInButton) {
      zoomInButton.addEventListener('click', () => zoomImage(ZOOM_STEP));
    }
    
    if (zoomOutButton) {
      zoomOutButton.addEventListener('click', () => zoomImage(-ZOOM_STEP));
    }
    
    // Add keyboard navigation
    document.addEventListener('keydown', function(event) {
      // Only handle keyboard events when modal is open
      if (imageModal.style.display !== 'flex') return;
      
      switch (event.key) {
        case 'Escape':
          closeModal();
          break;
        case 'ArrowRight':
          navigateImages(1);
          break;
        case 'ArrowLeft':
          navigateImages(-1);
          break;
        case '+':
        case '=':
          zoomImage(ZOOM_STEP);
          break;
        case '-':
          zoomImage(-ZOOM_STEP);
          break;
      }
    });
    
    // Add mouse wheel zoom support
    modalImage.addEventListener('wheel', function(e) {
      if (imageModal.style.display !== 'flex') return;
      
      e.preventDefault();
      const delta = e.deltaY > 0 ? -ZOOM_STEP : ZOOM_STEP;
      zoomImage(delta);
    });
  }
  
  // Zoom the image in or out
  function zoomImage(delta) {
    // Calculate new zoom level
    let newZoom = currentZoom + delta;
    
    // Enforce zoom limits
    if (newZoom < MIN_ZOOM) newZoom = MIN_ZOOM;
    if (newZoom > MAX_ZOOM) newZoom = MAX_ZOOM;
    
    // Only update if zoom changed
    if (newZoom !== currentZoom) {
      currentZoom = newZoom;
      
      // Apply zoom transform
      modalImage.style.transform = `scale(${currentZoom})`;
      
      // Announce zoom level for screen readers
      announceForScreenReader(`Image zoomed to ${Math.round(currentZoom * 100)}%`);
    }
  }
  
  // Navigate between images in the current product listing
  function navigateImages(direction) {
    // Only navigate if we have multiple images
    if (productImages.length <= 1) return;
    
    // Calculate new index with wrap-around
    let newIndex = currentIndex + direction;
    if (newIndex < 0) newIndex = productImages.length - 1;
    if (newIndex >= productImages.length) newIndex = 0;
    
    // Only load if different
    if (newIndex !== currentIndex) {
      currentIndex = newIndex;
      loadImage(productImages[currentIndex]);
      
      // Reset zoom when changing images
      currentZoom = 1;
      modalImage.style.transform = '';
      
      // Announce navigation for screen readers
      announceForScreenReader(`Image ${currentIndex + 1} of ${productImages.length}`);
    }
  }
  
  // Helper for screen reader announcements
  function announceForScreenReader(message) {
    const announcement = document.createElement('div');
    announcement.setAttribute('aria-live', 'polite');
    announcement.classList.add('sr-only');
    announcement.textContent = message;
    
    document.body.appendChild(announcement);
    
    // Remove after announcement is processed
    setTimeout(() => {
      document.body.removeChild(announcement);
    }, 3000);
  }
  
  function openModal(imgSrc) {
    if (!imageModal || !modalImage) return;
    
    // Reset zoom level when opening modal
    currentZoom = 1;
    modalImage.style.transform = '';
    
    // Collect all product images for navigation
    collectProductImages();
    
    // Find the index of the current image
    currentIndex = productImages.indexOf(imgSrc);
    if (currentIndex === -1 && productImages.length > 0) {
      // Image not found in collection, use first image
      currentIndex = 0;
      imgSrc = productImages[0];
    }
    
    // Save current image source
    currentImageSrc = imgSrc;
    
    // Load the image
    loadImage(imgSrc);
    
    // Show the modal
    imageModal.style.display = 'flex';
    
    // Set focus to the modal for keyboard navigation
    imageModal.focus();
    
    // Trap focus within modal
    trapFocusInModal();
  }
  
  // Collect all available product images for navigation
  function collectProductImages() {
    productImages = [];
    
    // Get all product image containers
    const containers = document.querySelectorAll('.product-image-container');
    
    containers.forEach(container => {
      const imgSrc = container.dataset.image || 
                     container.querySelector('img')?.src || 
                     '';
      
      if (imgSrc && !productImages.includes(imgSrc)) {
        productImages.push(imgSrc);
      }
    });
  }
  
  // Load an image into the modal
  function loadImage(imgSrc) {
    // Try to get a higher-quality version of the image
    const highQualityImg = getHighQualityImageUrl(imgSrc);
    
    // Set a placeholder image and fade the image 
    modalImage.src = '/static/placeholder.png';
    modalImage.style.opacity = '0.5';
    
    // Update alt text to be more descriptive
    modalImage.alt = `Product image ${currentIndex + 1} of ${productImages.length}`;
    
    // Show the loading spinner
    if (loadingSpinner) {
      loadingSpinner.style.display = 'block';
    }
    
    // Preload the high-quality image
    const img = new Image();
    
    img.onload = function() {
      modalImage.src = this.src;
      modalImage.style.opacity = '1';
      if (loadingSpinner) {
        loadingSpinner.style.display = 'none';
      }
    };
    
    img.onerror = function() {
      console.log('Failed to load high-quality image, falling back to original');
      modalImage.src = imgSrc;
      modalImage.style.opacity = '1';
      if (loadingSpinner) {
        loadingSpinner.style.display = 'none';
      }
    };
    
    img.src = highQualityImg;
  }
  
  // Close the modal
  function closeModal() {
    if (!imageModal) return;
    imageModal.style.display = 'none';
    
    // Return focus to the element that opened the modal
    // Find the container with this image
    const containers = document.querySelectorAll('.product-image-container');
    for (const container of containers) {
      if (container.dataset.image === currentImageSrc) {
        container.focus();
        break;
      }
    }
  }
  
  // Focus trap for modal
  function trapFocusInModal() {
    const focusableElements = imageModal.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    if (focusableElements.length === 0) return;
    
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];
    
    firstElement.focus();
    
    imageModal.addEventListener('keydown', function(e) {
      if (e.key === 'Tab') {
        // Shift+Tab moves backwards, regular Tab moves forwards
        if (e.shiftKey && document.activeElement === firstElement) {
          e.preventDefault();
          lastElement.focus();
        } else if (!e.shiftKey && document.activeElement === lastElement) {
          e.preventDefault();
          firstElement.focus();
        }
      }
    });
  }
  
  function getHighQualityImageUrl(url) {
    if (!url) return url;
    
    try {
      // For eBay images, try to get high quality
      if (url.includes('ebayimg.com')) {
        const imgId = url.match(/\/g\/([^/]+)\//);
        if (imgId && imgId[1]) {
          return `https://i.ebayimg.com/images/g/${imgId[1]}/s-l1600.jpg`;
        }
        
        return url.replace('/thumbs', '')
                 .replace('s-l225', 's-l1600')
                 .replace('s-l300', 's-l1600')
                 .replace('s-l400', 's-l1600');
      }
      
      // For Amazon images
      if (url.includes('amazon.com') || url.includes('images-amazon.com')) {
        return url.replace(/_SL\d+_/, '_SL1500_')
                 .replace(/_SS\d+_/, '_SL1500_');
      }
      
      // For Walmart images
      if (url.includes('walmart.com') || url.includes('walmartimages.com')) {
        return url.replace(/[?&]odnHeight=\d+/, '')
                 .replace(/[?&]odnWidth=\d+/, '')
                 .replace(/[?&]odnBg=\w+/, '');
      }
      
      return url;
    } catch (e) {
      console.error('Error processing image URL:', e);
      return url;
    }
  }
  
  // Attach event listeners to image containers with accessibility enhancements
  function attachImagePreviewListeners() {
    const containers = document.querySelectorAll('.product-image-container');
    
    containers.forEach(container => {
      if (container.getAttribute('data-has-preview-listener') === 'true') {
        return; // Skip if already has listener
      }
      
      // Add tabindex and role for keyboard accessibility
      container.setAttribute('tabindex', '0');
      container.setAttribute('role', 'button');
      container.setAttribute('aria-label', 'View larger image');
      
      container.style.cursor = 'pointer';
      container.setAttribute('data-has-preview-listener', 'true');
      
      // Add click listener
      container.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        const imgSrc = this.dataset.image || 
                       this.querySelector('img')?.src || 
                       '/static/placeholder.png';
        
        openModal(imgSrc);
      });
      
      // Add keyboard listener for Enter/Space
      container.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          
          const imgSrc = this.dataset.image || 
                         this.querySelector('img')?.src || 
                         '/static/placeholder.png';
          
          openModal(imgSrc);
        }
      });
    });
  }
  
  // Return public API
  return {
    init: init,
    openModal: openModal,
    closeModal: closeModal,
    attachImagePreviewListeners: attachImagePreviewListeners
  };
})();

// Initialize and export globally
document.addEventListener('DOMContentLoaded', function() {
  ImageModal.init();
  
  // Automatically attach listeners to any image containers on page load
  setTimeout(() => {
    ImageModal.attachImagePreviewListeners();
  }, 500);
  
  // Listen for custom event when products are displayed
  document.addEventListener('productsDisplayed', function() {
    ImageModal.attachImagePreviewListeners();
  });
});

// Expose globally 
window.openImageModal = ImageModal.openModal;
window.closeImageModal = ImageModal.closeModal;
window.attachImagePreviewListeners = ImageModal.attachImagePreviewListeners;