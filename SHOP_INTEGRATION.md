# Shop Integration Guide - adulsportfolio.vercel.app/shop

This guide shows you how to integrate ExamShield licensing with your shop at `adulsportfolio.vercel.app/shop`.

## Overview

Your shop integration uses the following flow:
1. **Shop Page**: `https://adulsportfolio.vercel.app/shop` - Where customers discover ExamShield
2. **Registration**: `https://https://examshield-license-server.onrender.com/register-page` - Customer registration (proxied via Vercel)
3. **Payment**: `https://https://examshield-license-server.onrender.com/payment?key=ES-XXXXX` - Payment processing (proxied via Vercel)
4. **Success**: `https://examshield-license-server.onrender.com/success?key=ES-XXXXX` - Confirmation page (proxied via Vercel)
5. **License Server**: `https://examshield-license-erver.onrender.com` - Backend API

## Integration Setup

### 1. Add Registration Button to Shop Page

Add a "Buy Now" or "Get License" button on your shop page that links to the registration page:

```html
<!-- Individual License -->
<a href="https://https://examshield-license-server.onrender.com/register-page" 
   class="buy-button">
   Buy Individual License ($99.99)
</a>

<!-- Organization License -->
<a href="https://https://examshield-license-server.onrender.com/register-page?type=organization" 
   class="buy-button">
   Buy Organization License ($299.99)
</a>
```

### 2. Registration Flow

When customers click the button:
1. They're redirected to: `https://https://examshield-license-server.onrender.com/register-page`
2. Vercel proxies this to: `https://examshield-license-erver.onrender.com/register-page`
3. Customer fills out the registration form (name, email, license type)
4. System generates a license key
5. Customer is automatically redirected to payment page

### 3. Payment Flow

After registration:
1. Customer is redirected to: `https://https://examshield-license-server.onrender.com/payment?key=ES-XXXXX`
2. Payment options shown:
   - Razorpay (Card/UPI) - if configured
   - Stripe - if configured
   - Test Payment - for testing
   - Free Trial - 7-day trial option
3. After successful payment, customer is redirected to success page

### 4. Success Page

After payment:
1. Customer sees: `https://examshield-license-server.onrender.com/success?key=ES-XXXXX`
2. Success page shows:
   - License key
   - Download link to shop: `https://adulsportfolio.vercel.app/shop`
   - Installation instructions
3. Email is sent with complete license details

### 5. Email Integration

License activation emails include:
- License key
- Download link: `https://adulsportfolio.vercel.app/shop`
- Activation date and expiry
- Installation instructions

## URLs Configuration

All URLs are already configured in the system:

### Vercel Configuration (`vercel.json`)
- All API endpoints proxy to: `https://examshield-license-erver.onrender.com`
- Accessible via: `https://adulsportfolio.vercel.app/*`

### Server Configuration (`server/license_server.py`)
- All email templates reference: `https://adulsportfolio.vercel.app/shop`
- Download links point to shop page

### Success Page (`server/success.html`)
- Download button links to: `https://adulsportfolio.vercel.app/shop`
- "Register Another License" links to: `/register-page`

## Shop Page HTML Example

Here's a simple example of how to add ExamShield to your shop page:

```html
<!DOCTYPE html>
<html>
<head>
    <title>ExamShield - Secure Exam Environment</title>
</head>
<body>
    <div class="product">
        <h1>ExamShield</h1>
        <p>Secure exam environment with USB monitoring and Telegram alerts</p>
        
        <div class="pricing">
            <div class="plan">
                <h2>Individual License</h2>
                <p class="price">$99.99</p>
                <ul>
                    <li>2 devices</li>
                    <li>1 year validity</li>
                    <li>Full features</li>
                </ul>
                <a href="https://https://examshield-license-server.onrender.com/register-page?type=individual" 
                   class="btn btn-primary">
                   Buy Now
                </a>
            </div>
            
            <div class="plan">
                <h2>Organization License</h2>
                <p class="price">$299.99</p>
                <ul>
                    <li>Unlimited devices</li>
                    <li>1 year validity</li>
                    <li>Full features</li>
                    <li>Priority support</li>
                </ul>
                <a href="https://https://examshield-license-server.onrender.com/register-page?type=organization" 
                   class="btn btn-primary">
                   Buy Now
                </a>
            </div>
        </div>
        
        <div class="download-section">
            <h2>Download ExamShield</h2>
            <p>After purchase, download the installer from your email or:</p>
            <a href="/shop/download" class="btn">Download Now</a>
        </div>
    </div>
</body>
</html>
```

## Testing the Integration

### 1. Test Registration
```
Visit: https://https://examshield-license-server.onrender.com/register-page
```

### 2. Test Payment Flow
```
1. Register a test license
2. You'll be redirected to: https://https://examshield-license-server.onrender.com/payment?key=ES-XXXXX
3. Use "Test Payment" button to simulate payment
4. You'll be redirected to success page
```

### 3. Test Email Delivery
```
1. Complete registration and payment
2. Check email for license details
3. Verify download link points to: https://adulsportfolio.vercel.app/shop
```

## Payment Provider Setup

### Razorpay (Recommended for India)
1. Get Razorpay API keys from dashboard
2. Set in Render environment variables:
   - `RAZORPAY_KEY_ID=your_key_id`
   - `RAZORPAY_KEY_SECRET=your_key_secret`
3. Configure webhook in Razorpay:
   - URL: `https://examshield-license-erver.onrender.com/webhook/payment`
   - Events: `payment.captured`
4. Copy webhook secret to: `WEBHOOK_SECRET` in Render

### Stripe (For International)
1. Get Stripe API keys
2. Set in Render environment variables:
   - `STRIPE_KEY=your_stripe_key`
   - `STRIPE_SECRET=your_stripe_secret`
3. Configure webhook in Stripe:
   - URL: `https://examshield-license-erver.onrender.com/webhook/payment`
   - Events: `payment_intent.succeeded`

## Customer Journey

1. **Discovery**: Customer visits `https://adulsportfolio.vercel.app/shop`
2. **Selection**: Customer clicks "Buy Now" for desired license type
3. **Registration**: Customer fills registration form at `/register-page`
4. **Payment**: Customer completes payment at `/payment?key=ES-XXXXX`
5. **Confirmation**: Customer sees success page with license key
6. **Email**: Customer receives email with license details and download link
7. **Download**: Customer downloads from shop page or email link
8. **Installation**: Customer installs ExamShield and enters license key

## Admin Dashboard

Monitor sales and manage licenses:
```
URL: https://https://examshield-license-server.onrender.com/admin
Secret: Set in ADMIN_SECRET environment variable
```

Features:
- View all licenses
- See revenue statistics
- Revoke licenses
- Extend license expiry
- Export reports

## Support

For issues or questions:
1. Check admin dashboard for license status
2. Verify webhook delivery in payment provider dashboard
3. Check Render logs for server errors
4. Verify Vercel deployment is active

## Next Steps

1. ✅ Deploy `vercel.json` to Vercel
2. ✅ Add "Buy Now" buttons to shop page
3. ✅ Configure payment provider (Razorpay/Stripe)
4. ✅ Test registration and payment flow
5. ✅ Verify email delivery
6. ✅ Add download section to shop page
7. ✅ Set up admin dashboard access

## Quick Reference

- **Shop**: https://adulsportfolio.vercel.app/shop
- **Register**: https://https://examshield-license-server.onrender.com/register-page
- **Payment**: https://https://examshield-license-server.onrender.com/payment?key=ES-XXXXX
- **Success**: https://examshield-license-server.onrender.com/success?key=ES-XXXXX
- **Admin**: https://https://examshield-license-server.onrender.com/admin
- **License Server**: https://examshield-license-erver.onrender.com

