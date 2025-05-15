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
    if (!paymentLinkForm) return;

    paymentLinkForm.addEventListener('submit', function(event) {
        event.preventDefault();
        createPaymentLink();
    });

    // Initialize currency selector with common options
    const currencySelect = document.getElementById('payment-currency');
    if (currencySelect) {
        const currencies = [
            { code: 'usd', name: 'US Dollar ($)' },
            { code: 'eur', name: 'Euro (€)' },
            { code: 'gbp', name: 'British Pound (£)' },
            { code: 'cad', name: 'Canadian Dollar (CA$)' },
            { code: 'aud', name: 'Australian Dollar (A$)' },
            { code: 'jpy', name: 'Japanese Yen (¥)' }
        ];

        currencies.forEach(currency => {
            const option = document.createElement('option');
            option.value = currency.code;
            option.textContent = currency.name;
            currencySelect.appendChild(option);
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
    const currency = document.getElementById('payment-currency').value;
    
    // Validate amount
    if (isNaN(amount) || amount <= 0) {
        showError('Please enter a valid amount');
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
                <strong>Error:</strong> ${message}
            </div>
        `;
        resultContainer.classList.remove('hidden');
    }
    
    function showSuccess(data) {
        resultContainer.innerHTML = `
            <div class="alert alert-success">
                <strong>Success!</strong> Payment link created.
            </div>
            <div class="payment-link-details">
                <h4>Payment Link Details</h4>
                <p><strong>Product:</strong> ${data.product_details.name}</p>
                <p><strong>Price:</strong> ${data.product_details.currency.toUpperCase()} ${data.product_details.price.toFixed(2)}</p>
                ${data.product_details.description ? `<p><strong>Description:</strong> ${data.product_details.description}</p>` : ''}
                <div class="payment-link-url">
                    <p><strong>Payment Link:</strong></p>
                    <a href="${data.payment_link}" target="_blank" class="payment-url">${data.payment_link}</a>
                    <button class="copy-link-btn" onclick="copyPaymentLink('${data.payment_link}')">
                        Copy Link
                    </button>
                </div>
            </div>
        `;
        resultContainer.classList.remove('hidden');
    }
}

/**
 * Copy the payment link to clipboard
 */
function copyPaymentLink(url) {
    navigator.clipboard.writeText(url).then(function() {
        alert('Payment link copied to clipboard');
    }).catch(function(err) {
        console.error('Failed to copy link: ', err);
    });
}