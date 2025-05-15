/**
 * Payment Link Generation Module
 * 
 * This module handles the UI and API interactions for creating Stripe payment links
 * using agent input for price and product details.
 */
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the payment link UI
    initPaymentLinkUI();
});

/**
 * Initialize the payment link creation UI and event listeners
 */
function initPaymentLinkUI() {
    const paymentLinkForm = document.getElementById('payment-link-form');
    const resetFormButton = document.getElementById('reset-payment-form');
    if (!paymentLinkForm) return;

    // Form submission handler
    paymentLinkForm.addEventListener('submit', function(event) {
        event.preventDefault();
        createPaymentLink();
    });
    
    // Reset form handler
    if (resetFormButton) {
        resetFormButton.addEventListener('click', function(event) {
            paymentLinkForm.reset();
            document.getElementById('payment-link-result').classList.add('hidden');
            
            // Focus on first field after reset
            document.getElementById('product-name').focus();
        });
    }

    // Currency is now fixed to USD in the HTML
    const currencySelect = document.getElementById('payment-currency');
    if (currencySelect) {
        // Make sure USD is selected and currency is disabled
        currencySelect.value = 'usd';
        currencySelect.disabled = true;
    }
    
    // Handle tab visibility for analytics
    const paymentLinkTab = document.getElementById('payment-link-tab');
    if (paymentLinkTab) {
        paymentLinkTab.addEventListener('shown.bs.tab', function() {
            // Focus on product name for better user experience
            setTimeout(() => {
                document.getElementById('product-name').focus();
            }, 300);
        });
    }
}

/**
 * Create a payment link using the agent input form values
 */
function createPaymentLink() {
    // Show loading state
    const submitButton = document.querySelector('#payment-link-form button[type="submit"]');
    const originalButtonText = submitButton.textContent;
    submitButton.disabled = true;
    submitButton.textContent = 'Creating Payment Link...';
    
    // Clear any previous results
    const resultContainer = document.getElementById('payment-link-result');
    resultContainer.innerHTML = '';
    resultContainer.classList.add('hidden');
    
    // Get form values
    const productName = document.getElementById('product-name').value;
    const productDescription = document.getElementById('product-description').value;
    const amount = parseFloat(document.getElementById('payment-amount').value);
    const currency = 'usd'; // Always USD
    
    // Validate amount
    if (isNaN(amount) || amount <= 0) {
        showError('Please enter a valid amount');
        resetButton();
        return;
    }
    
    // Check maximum amount
    if (amount > 4000) {
        showError('Amount cannot exceed $4,000');
        resetButton();
        return;
    }
    
    // Prepare payload
    const payload = {
        agent_input: {
            product_name: productName,
            product_description: productDescription,
            amount: amount,
            currency: currency
        }
    };
    
    // Call the API
    fetch('/api/create-payment-link', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showError(data.error);
        } else {
            showSuccess(data);
        }
    })
    .catch(error => {
        showError('An error occurred: ' + error.message);
    })
    .finally(() => {
        // Reset button state
        resetButton();
    });
    
    function resetButton() {
        submitButton.disabled = false;
        submitButton.textContent = originalButtonText;
    }
    
    function showError(message) {
        resultContainer.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle"></i>
                <div>
                    <strong>Error:</strong> ${message}
                </div>
            </div>
        `;
        resultContainer.classList.remove('hidden');
        
        // Scroll to result
        setTimeout(() => {
            resultContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }, 100);
    }
    
    function showSuccess(data) {
        // Format price (always USD now)
        const price = data.product_details.price.toFixed(2);
        // Fixed USD currency symbol
        const currencySymbol = '$';
        
        resultContainer.innerHTML = `
            <div class="alert alert-success">
                <i class="fas fa-check-circle"></i>
                <div>
                    <strong>Success!</strong> Your payment link has been created and is ready to share with your customer.
                </div>
            </div>
            <div class="payment-link-details">
                <h4><i class="fas fa-info-circle"></i> Payment Link Details</h4>
                
                <div class="payment-details-grid">
                    <div class="payment-detail-item">
                        <div class="detail-label">Product</div>
                        <div class="detail-value">${data.product_details.name}</div>
                    </div>
                    
                    <div class="payment-detail-item">
                        <div class="detail-label">Price</div>
                        <div class="detail-value">${currencySymbol} ${price}</div>
                    </div>
                    
                    ${data.product_details.description ? `
                    <div class="payment-detail-item">
                        <div class="detail-label">Description</div>
                        <div class="detail-value">${data.product_details.description}</div>
                    </div>
                    ` : ''}
                </div>
                
                <div class="payment-link-url">
                    <h5><i class="fas fa-link"></i> Share this payment link with your customer</h5>
                    <div class="url-container">
                        <a href="${data.payment_link}" target="_blank" class="payment-url">${data.payment_link}</a>
                        <div class="copy-success" id="copy-success-message">Copied!</div>
                    </div>
                    
                    <div class="url-actions">
                        <button class="url-action-btn primary" onclick="copyPaymentLink('${data.payment_link}')">
                            <i class="fas fa-copy"></i> Copy Link
                        </button>
                        <a href="${data.payment_link}" target="_blank" class="url-action-btn">
                            <i class="fas fa-external-link-alt"></i> Open Link
                        </a>
                        <button class="url-action-btn" onclick="sharePaymentLink('${data.payment_link}')">
                            <i class="fas fa-share-alt"></i> Share
                        </button>
                    </div>
                </div>
            </div>
        `;
        resultContainer.classList.remove('hidden');
        
        // Scroll to result
        setTimeout(() => {
            resultContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }, 100);
    }
}

/**
 * Copy the payment link to clipboard with visual feedback
 */
function copyPaymentLink(url) {
    navigator.clipboard.writeText(url).then(function() {
        // Show copy success message with animation
        const successMsg = document.getElementById('copy-success-message');
        if (successMsg) {
            successMsg.classList.add('show');
            setTimeout(() => {
                successMsg.classList.remove('show');
            }, 2000);
        }
    }).catch(function(err) {
        console.error('Failed to copy link: ', err);
        alert('Could not copy link: ' + err.message);
    });
}

/**
 * Share payment link using Web Share API if available
 */
function sharePaymentLink(url) {
    // Check if Web Share API is supported
    if (navigator.share) {
        navigator.share({
            title: 'Payment Link',
            text: 'Here is your payment link',
            url: url
        })
        .then(() => console.log('Link shared successfully'))
        .catch((error) => console.error('Error sharing link:', error));
    } else {
        // Fallback to copy if Web Share API is not available
        copyPaymentLink(url);
        alert('Share not supported on this browser. Link has been copied to clipboard instead.');
    }
}