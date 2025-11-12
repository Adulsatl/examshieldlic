# Duplicate Registration/Trial Prevention

## Overview

The system now prevents the same email from registering multiple times or getting multiple free trials.

## How It Works

### Server-Side Protection

1. **Registration Check**: When a user tries to register, the server checks if the email already exists in the license database.

2. **Email Normalization**: All emails are converted to lowercase and trimmed to ensure consistent matching.

3. **Three Scenarios**:
   - **Email not found**: New registration allowed
   - **Email exists with active license**: Registration blocked, user directed to use existing license
   - **Email exists with pending payment**: Registration blocked, user directed to complete existing payment

### API Response Examples

#### New Registration (Allowed)
```json
{
  "success": true,
  "license_key": "ES-XXXXX",
  "payment_url": "/payment?key=ES-XXXXX",
  "message": "Registration successful. Redirecting to payment..."
}
```

#### Duplicate Registration - Active License
```json
{
  "error": "This email already has an active license",
  "existing_key": "ES-XXXXX",
  "message": "Please use your existing license key or contact support."
}
```
Status Code: **409 Conflict**

#### Duplicate Registration - Pending Payment
```json
{
  "error": "This email already has a pending registration",
  "existing_key": "ES-XXXXX",
  "payment_url": "/payment?key=ES-XXXXX",
  "message": "You have a pending registration. Please complete payment or contact support."
}
```
Status Code: **409 Conflict**

## Trial Eligibility Check

### New Endpoint: `/check-trial-eligibility`

Check if an email is eligible for free trial before starting one.

**Request:**
```json
POST /check-trial-eligibility
{
  "email": "user@example.com"
}
```

**Response (Eligible):**
```json
{
  "eligible": true,
  "message": "Email is eligible for free trial"
}
```

**Response (Not Eligible):**
```json
{
  "eligible": false,
  "reason": "Email already registered",
  "has_active": true,
  "has_pending": false
}
```

## Client-Side Protection

The client license module also checks trial eligibility before starting a trial:

```python
# Check eligibility before starting trial
if email and not check_trial_eligibility(email):
    return None  # Not eligible
```

## Database Tracking

Each registration is marked with:
- `trial_used: true` - Indicates this email has used registration
- Email stored in lowercase for consistent matching
- All registrations tracked regardless of payment status

## Testing

### Test Duplicate Prevention

1. **Register first time:**
```bash
curl -X POST http://localhost:8080/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","name":"Test User","device_type":"individual"}'
```

2. **Try to register again with same email:**
```bash
curl -X POST http://localhost:8080/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","name":"Test User 2","device_type":"individual"}'
```

Expected: **409 Conflict** with error message

### Test Trial Eligibility

```bash
curl -X POST http://localhost:8080/check-trial-eligibility \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com"}'
```

## Implementation Details

### Email Matching

- All emails are normalized: `.strip().lower()`
- Case-insensitive matching
- Whitespace trimmed

### Registration Flow

1. User submits registration form
2. Server normalizes email
3. Server checks database for existing email
4. If found:
   - Check if active → Block, show existing key
   - Check if pending → Block, redirect to payment
5. If not found:
   - Create new registration
   - Mark `trial_used: true`
   - Return payment URL

### Security Considerations

- Email is the primary identifier (no password required for registration)
- Server-side validation prevents bypass
- Client-side checks are optional (server is source of truth)
- All checks are case-insensitive

## Edge Cases Handled

1. **Email variations**: `User@Example.com` = `user@example.com` = `user@example.com `
2. **Pending payments**: User can't create new registration while payment is pending
3. **Active licenses**: User must use existing license, can't create duplicate
4. **Offline mode**: Client allows trial if server unreachable (server will still block on registration)

## Admin Override

If needed, admins can manually modify the database to allow re-registration, but this should be done carefully and only in exceptional circumstances.

## Summary

✅ **Prevents duplicate registrations**
✅ **Prevents multiple free trials per email**
✅ **Case-insensitive email matching**
✅ **Handles pending payments**
✅ **Clear error messages for users**
✅ **Trial eligibility API endpoint**

The system ensures each email can only have one registration and one free trial, maintaining fair usage and preventing abuse.

