/**
 * Image Modal Module
 * Handles image preview functionality
 */

const ImageModal = (function() {
  let imageModal;
  let modalImage;
  let closeButton;
  let loadingSpinner;

  function init() {
    // Get modal elements
    imageModal = document.getElementById('imageModal');
    modalImage = document.getElementById('modalImage');
    closeButton = document.querySelector('.close-modal');
    
    if (!imageModal || !modalImage) return;
    
    // Set up the modal initially hidden
    imageModal.style.display = 'none';
    
    // Add CSS classes for styling
    modalImage.classList.add('modal-content');
    
    // Add a loading indicator to the modal
    loadingSpinner = document.createElement('div');
    loadingSpinner.className = 'image-loading';
    loadingSpinner.id = 'image-loading';
    imageModal.appendChild(loadingSpinner);
    
    // Set up modal styles
    imageModal.style.alignItems = 'center';
    imageModal.style.justifyContent = 'center';
    
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
    
    // Add keyboard listener to close on Escape key
    document.addEventListener('keydown', function(event) {
      if (event.key === 'Escape' && imageModal.style.display === 'block') {
        closeModal();
      }
    });
  }
  
  function openModal(imgSrc) {
    if (!imageModal || !modalImage) return;
    
    console.log('Opening modal with image:', imgSrc);
    
    // Try to get a higher-quality version of the image
    const highQualityImg = getHighQualityImageUrl(imgSrc);
    
    // Set a placeholder image and fade the image 
    modalImage.src = '/static/placeholder.png';
    modalImage.style.opacity = '0.5';
    
    // Show the loading spinner if available
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
    
    // Show the modal
    imageModal.style.display = 'flex';
  }
  
  function closeModal() {
    if (!imageModal) return;
    imageModal.style.display = 'none';
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
  
  // Attach event listeners to image containers
  function attachImagePreviewListeners() {
    console.log('Attaching image preview listeners');
    const containers = document.querySelectorAll('.product-image-container');
    
    containers.forEach(container => {
      if (container.getAttribute('data-has-preview-listener') === 'true') {
        return; // Skip if already has listener
      }
      
      container.style.cursor = 'pointer';
      container.setAttribute('data-has-preview-listener', 'true');
      
      // Add click listener
      container.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        console.log('Image container clicked');
        
        const imgSrc = this.dataset.image || 
                       this.querySelector('img')?.src || 
                       '/static/placeholder.png';
        
        openModal(imgSrc);
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