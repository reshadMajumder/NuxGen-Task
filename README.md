# Nux Device Platform

A modular device authorization platform with OTP-based email verification and payment gateway integration using **Adapter Design Pattern**.

<img width="703" height="1014" alt="activity -nuxgen drawio" src="https://github.com/user-attachments/assets/31e10b61-5d1c-48e2-a5f0-14266757a1b8" />

---

## Overview

Nux Device API enables:

- User registration with OTP verification (pluggable adapters → Email / SMS / WhatsApp / etc.)
- Secure JWT authentication with token refresh
- Device CRUD operations with authorization workflow
- Payment processing (15% of device price for authorization)
- Automatic device authorization via webhook callbacks
- Role-based access control (Admin, Staff, User)

The project is designed in an extensible way using **Adapter Pattern** for both OTP sending and Payment integration.

- NOTE: no async support, redis caching added here.

---

## Additional Resources

- **ERD**: https://drive.google.com/file/d/1txxSbk_9ONj38RVabBRO8yeWkYph-jsL/view?usp=sharing
- **Flow Chart** : https://drive.google.com/file/d/1-RgIch0Wlym72RASfYBmHbag5DEfBR9c/view?usp=sharing
- **SRS Document**: https://drive.google.com/file/d/1GAZd-qEzI8IJ7bGIjz6YuhAUi8z1ZJLp/view?usp=sharing
- **Activity-diagram** : https://drive.google.com/file/d/1kew5BY6bGmgu-9AcDRUm0uQl4euEYDt6/view?usp=sharing
- **Postman API Documentation**: https://drive.google.com/file/d/19OQYZlDQ9GagWKzkY-_Gfo8ZqW-t4vFw/view?usp=sharing


## Architecture

| Module              | Responsibilities                                  |
|---------------------|---------------------------------------------------|
| `accounts`          | Custom user model, OTP sending, JWT authentication |
| `device`            | Device CRUD, device authorization, IMEI management |
| `payments`          | Payment logic, gateway integration, webhook handling |
| `imei_authorization`| Authorized IMEI management (Admin/Staff only)     |

Each module is a separate Django app for maintainability and scalability.

---

## Technology Stack

- **Backend**: Django 5.2.4, Django REST Framework 3.16.0
- **Authentication**: JWT (SimpleJWT 5.5.0)
- **Database**: SQLite (dev) / PostgreSQL (production)
- **File Storage**: Cloudinary
- **Payment Gateway**: SSLCommerz (Adapter Pattern)
- **CORS**: django-cors-headers
- **Server**: Gunicorn

---

## Design Patterns

Both OTP and Payment modules use the **Adapter Pattern** for extensibility.

| Module   | Feature             | Pattern        | Benefits                                      |
|----------|---------------------|----------------|-----------------------------------------------|
| accounts | OTP sending         | Adapter Pattern| Switch between Email / SMS / WhatsApp easily  |
| payments | Gateway Integration | Adapter Pattern| Switch between SSLCommerz / Nagad / bKash / Stripe without code changes |

**Currently Active Adapters**

- `EmailOTPAdapter` → sends OTP via Email
- `SSLCommerzAdapter` → initializes payment with SSLCommerz sandbox gateway

**Future Adapters** (plug-in easily)

- `NagadAdapter`, `bKashAdapter`, `StripeAdapter`, `PaypalAdapter`

---

## Database Optimization

The platform includes optimized database queries with:

- **Indexes**: Strategic indexes on frequently queried fields (`is_email_verified`, `is_authorized`, `status`, `created_at`)
- **Composite Indexes**: Multi-field indexes for common filter combinations
- **Query Optimization**: `select_related()` for ForeignKey relationships to prevent N+1 queries

---

## API Features

### Pagination

All list endpoints return paginated results with 20 items per page. Response format:

```json
{
  "count": 100,
  "next": "http://api/v1/device/?page=2",
  "previous": null,
  "results": [...]
}
```

Use `?page=<number>` query parameter to navigate pages.

### Rate Limiting

The API implements rate limiting to prevent abuse:

| User Type | Rate Limit |
|-----------|------------|
| Anonymous | 100 requests/hour |
| Authenticated | 1000 requests/day |
| Auth endpoints (register/login) | 5 requests/hour |
| OTP endpoints (verify/resend) | 3 requests/hour |

When rate limit is exceeded, API returns `429 Too Many Requests` with details:
```json
{
  "detail": "Request was throttled. Expected available in 3456 seconds."
}
```

---

## API Endpoints

### Authentication (`/api/v1/accounts/`)

- `POST /register/` - User registration (sends OTP)
- `POST /verify-otp/` - Verify OTP and receive JWT tokens
- `POST /resend-otp/` - Resend OTP to email
- `POST /login/` - User login (returns JWT tokens)
- `POST /logout/` - Logout (blacklist refresh token)
- `GET /token/refresh/` - Refresh access token
- `GET /profile/` - Get user profile (authenticated)
- `PUT /profile/` - Update user profile (authenticated)

### Devices (`/api/v1/device/`)

- `GET /` - List devices (filter by `is_authorized` query param, paginated)
- `POST /` - Create new device
- `GET /<id>/` - Get device details
- `PUT /<id>/` - Update device
- `DELETE /<id>/` - Delete device

### Payments (`/api/v1/payments/`)

- `POST /create/` - Create payment (requires `device_id`)
- `GET /list/` - List payments (filter by `status`, `device_id`, `user_id`, paginated)
- `POST /webhook/` - Payment webhook (SSLCommerz callback, no throttling)
- `GET /success/` - Payment success page
- `GET /fail/` - Payment failure page
- `GET /cancel/` - Payment cancellation page

### IMEI Authorization (`/api/v1/imei/`)

- `GET /` - List authorized IMEIs (Admin/Staff only, paginated)
- `POST /` - Add authorized IMEI (Admin/Staff only)
- `DELETE /<id>/` - Delete authorized IMEI (Admin only)

---

## Features

### 1. User Management

- Registration with email and password
- OTP verification via email (adapter pattern)
- JWT-based authentication with refresh tokens
- Profile management (view and update)
- Email verification required before login

### 2. Role-Based Access Control

- **Admin**: Full access to all resources
- **Staff**: Can manage devices and view payments
- **User**: Can only manage their own devices and payments

### 3. Device Management

- Add, edit, delete devices
- Automatic IMEI authorization check on creation
- Filter devices by authorization status
- Device ownership validation

### 4. Payment System

- Initiate payment (15% of device price)
- SSLCommerz gateway integration (adapter pattern)
- Webhook endpoint for automatic verification
- Device automatically authorized after successful payment
- Payment status tracking (pending, success, failed)

### 5. Security

- JWT token authentication
- OTP verification before token issuance
- Role-based endpoint permissions
- Token blacklisting on logout
- CORS configuration for API access

### 6. API Performance & Protection

- **Pagination**: All list endpoints paginated (20 items per page)
- **Rate Limiting**: Built-in throttling to prevent abuse
  - Anonymous users: 100 requests/hour
  - Authenticated users: 1000 requests/day
  - Authentication endpoints (register/login): 5 requests/hour
  - OTP endpoints (verify/resend): 3 requests/hour

---

## Installation & Setup

### Prerequisites

- Python 3.8+
- PostgreSQL (for production)
- Cloudinary account (for file storage)
- SSLCommerz account (for payments)
- SMTP server credentials (for email)

### Steps

1. **Clone the repository**
   ```bash
   git clone <repo_url>
   cd NuxGen-task/core
   ```

2. **Create virtual environment**
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file**
   ```env
   # Django Settings
   SECRET_KEY=your-secret-key
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1

   # Database (Production)
   DB_NAME=your_db_name
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_HOST=localhost
   DB_PORT=5432
   DB_SSLMODE=require

   # Email Configuration
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   EMAIL_USE_TLS=True

   # Cloudinary
   cloud_name=your-cloud-name
   api_key=your-api-key
   api_secret=your-api-secret

   # SSLCommerz
   SSL_STORE_ID=your-store-id
   SSL_STORE_PASSWORD=your-store-password
   SSL_SANDBOX_URL=https://sandbox.sslcommerz.com/gwprocess/v4/api.php

   # Public Domain (use ngrok HTTPS URL in development)
   PUBLIC_DOMAIN=https://your-domain.com
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser** (optional)
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000/api/v1/`

---

## Environment Variables

Required environment variables for `.env` file:

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | Generated key |
| `DEBUG` | Debug mode | `True` or `False` |
| `ALLOWED_HOSTS` | Allowed hosts | `localhost,127.0.0.1` |
| `EMAIL_HOST` | SMTP server | `smtp.gmail.com` |
| `EMAIL_PORT` | SMTP port | `587` |
| `EMAIL_HOST_USER` | Email address | `your-email@gmail.com` |
| `EMAIL_HOST_PASSWORD` | Email password/app password | `your-password` |
| `cloud_name` | Cloudinary cloud name | `your-cloud-name` |
| `api_key` | Cloudinary API key | `your-api-key` |
| `api_secret` | Cloudinary API secret | `your-api-secret` |
| `SSL_STORE_ID` | SSLCommerz store ID | `your-store-id` |
| `SSL_STORE_PASSWORD` | SSLCommerz store password | `your-store-password` |
| `PUBLIC_DOMAIN` | Public domain for webhooks | `https://your-domain.com` |

---

## Workflow

1. **User Registration**: User registers → OTP sent via email
2. **OTP Verification**: User verifies OTP → JWT tokens issued
3. **Device Creation**: User adds device → IMEI checked against authorized list
4. **Payment Initiation**: User creates payment → Redirected to SSLCommerz
5. **Payment Webhook**: SSLCommerz calls webhook → Device auto-authorized
6. **Device Management**: User can manage their authorized devices

---

## Contributing

1. Use Adapter Pattern for new OTP or Payment integrations
2. Follow modular app structure (accounts, device, payments, imei_authorization)
3. Write unit tests for new functionality
4. Use environment variables instead of hardcoding credentials
5. Follow Django REST Framework best practices
6. Optimize database queries with `select_related()` and `prefetch_related()`

---

## License

MIT License © 2025

---



