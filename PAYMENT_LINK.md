# Payment Link Generation Feature

## Overview

The payment link generation feature allows AutoXpress agents to quickly create customized payment links using Stripe. This feature enables agents to accept payments from customers remotely, perfect for phone orders or remote transactions. Agents can specify product details, amount, and optionally add descriptions to create professional payment links that can be shared with customers.

## Core Components

### Backend Components

1. **Payment Link API** (`app.py`):
   - Endpoint: `/api/create-payment-link`
   - Method: POST
   - Handles payment link creation through Stripe API
   - Creates a product, price, and payment link in Stripe
   - Returns the generated payment link URL and product details

2. **Stripe Integration**:
   - Uses the Stripe Python library for API communication
   - Creates products, prices, and payment links
   - Configures address collection, payment methods, and currencies

### Frontend Components

1. **Payment Link UI** (`payment-link.js`):
   - Handles form input and validation
   - Communicates with the backend API
   - Displays success/error messages
   - Provides utilities for copying and sharing links

2. **Payment Link Template** (`index.html`):
   - Form inputs for product name, description, and amount
   - Static USD currency selection (fixed to USD)
   - Copy, open, and share buttons for payment links
   - Success/error message display

3. **Payment Link Styling** (`payment-link.css`):
   - Styling for the payment link form
   - Success/error message styling
   - Payment link display styling
   - Copy button and share functionality styling

## User Flow

1. **Access Payment Link Tab**:
   - User navigates to the "Payment Link" tab in the application
   - The form is loaded with empty fields and USD selected as currency

2. **Enter Payment Details**:
   - User enters a product name (required)
   - User enters an optional product description
   - User enters the payment amount (required, max $4,000)

3. **Generate Payment Link**:
   - User clicks "Generate Payment Link" button
   - Form validation occurs:
     - Validates required fields are completed
     - Verifies amount is a positive number less than $4,000
   - The application displays a loading state

4. **API Request**:
   - Frontend sends a request to `/api/create-payment-link` with:
     - Product name
     - Product description (if provided)
     - Amount (in USD)
     - Currency (always 'usd')

5. **Display Results**:
   - On success: Shows payment link with copy, open, and share options
   - On error: Shows error message with details

6. **Share Payment Link**:
   - User can copy the link to clipboard
   - User can open the link in a new tab
   - User can share the link via Web Share API (if supported by browser)

## Features

### Product Configuration

- **Product Name**: Required field for identifying the product
- **Product Description**: Optional field providing details about the product
- **Amount**: Required field specifying the payment amount (up to $4,000)
- **Currency**: Fixed to USD for all transactions

### Payment Link Settings

- **Address Collection**:
  - Billing address: Required
  - Shipping address: Limited to US addresses

- **Payment Methods**:
  - Card payments only (Link payment method disabled)

### Link Sharing

- **Copy to Clipboard**: One-click copying with visual feedback
- **Open in New Tab**: Direct access to view the payment page
- **Web Share API**: Native sharing on supported browsers (falls back to copy)

## Implementation Details

### Payment Link Creation Process

1. **Frontend Validation**:
   ```javascript
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
   ```

2. **Backend Processing**:
   ```python
   # Create a product in Stripe
   product = stripe.Product.create(
       name=product_name,
       description=product_description
   )
   
   # Create a price for the product
   price = stripe.Price.create(
       product=product.id,
       unit_amount=int(amount * 100),  # Convert to cents
       currency=currency
   )
   
   # Configure address collection
   billing_address_collection = "required"
   shipping_address_collection = {"allowed_countries": ["US"]}
   
   # Configure payment methods
   payment_method_types = ["card"]
   
   # Create a Payment Link
   payment_link = stripe.PaymentLink.create(
       line_items=[{"price": price.id, "quantity": 1}],
       billing_address_collection=billing_address_collection,
       shipping_address_collection=shipping_address_collection,
       payment_method_types=payment_method_types
   )
   ```

3. **Response Handling**:
   ```javascript
   // Display success information
   resultContainer.innerHTML = `
       <div class="alert alert-success">
           <i class="fas fa-check-circle"></i>
           <div>
               <strong>Success!</strong> Your payment link has been created and is ready to share with your customer.
           </div>
       </div>
       <div class="payment-link-details">
           <!-- Payment details display -->
       </div>
   `;
   ```

### Copying and Sharing

```javascript
// Copy to clipboard
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
    });
}

// Web Share API implementation
function sharePaymentLink(url) {
    // Check if Web Share API is supported
    if (navigator.share) {
        navigator.share({
            title: 'Payment Link',
            text: 'Here is your payment link',
            url: url
        });
    } else {
        // Fallback to copy if Web Share API is not available
        copyPaymentLink(url);
        alert('Share not supported on this browser. Link has been copied to clipboard instead.');
    }
}
```

## UI Components

### Form Fields

- **Product Name Field**: Text input for product name
- **Description Field**: Textarea for optional product description
- **Amount Field**: Numeric input with validation for payment amount
- **Currency Selector**: Dropdown fixed to USD currency
- **Submit Button**: "Generate Payment Link" with loading state

### Result Display

- **Success State**: 
  - Success message with check icon
  - Product details summary
  - Payment link display with copy button
  - Share and open buttons

- **Error State**:
  - Error message with warning icon
  - Error details

## Error Handling

1. **Validation Errors**:
   - Empty product name
   - Invalid amount format
   - Amount exceeding maximum ($4,000)

2. **API Errors**:
   - Stripe API errors
   - Connection issues
   - Server errors

3. **Browser Support**:
   - Clipboard API fallbacks
   - Web Share API fallbacks

## Technical Requirements

- **Stripe API Key**: Required in backend environment
- **Stripe Python Library**: Required for backend integration
- **Modern Browser Features**:
  - Clipboard API for copying
  - Web Share API for sharing (optional)

## Security Considerations

- Stripe API key is stored securely on the server side
- Payment links use Stripe's secure infrastructure
- No sensitive payment information is handled directly by the application
- Address validation is handled by Stripe's checkout flow
- Maximum amount limit ($4,000) helps prevent potential fraud or errors

## Future Enhancements

Potential improvements for future versions:

1. **Multiple Items**: Allow adding multiple products to a single payment link
2. **Recurring Payments**: Add support for subscription-based payment links
3. **Payment Link Management**: View, edit, and disable existing payment links
4. **Customer Management**: Associate payment links with customer records
5. **Payment Status Tracking**: Track payment status and completion
6. **Custom Branding**: Add branding options to payment pages
7. **Multiple Currencies**: Support for additional currencies beyond USD
8. **Payment Link Analytics**: Track views, conversions, and other metrics

## API Reference

### Create Payment Link API

**Endpoint**: `/api/create-payment-link`

**Method**: POST

**Request Format**:
```json
{
  "agent_input": {
    "product_name": "2018 Toyota Camry Brake Pads",
    "product_description": "OEM brake pads for front wheels",
    "amount": 89.99,
    "currency": "usd"
  }
}
```

**Response Format (Success)**:
```json
{
  "success": true,
  "payment_link": "https://buy.stripe.com/example_payment_link",
  "product_details": {
    "name": "2018 Toyota Camry Brake Pads",
    "price": 89.99,
    "currency": "usd",
    "description": "OEM brake pads for front wheels"
  }
}
```

**Response Format (Error)**:
```json
{
  "error": "Error message details"
}
```