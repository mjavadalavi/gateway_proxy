# Payment Gateway Proxy Service

A FastAPI-based payment gateway proxy service that provides a secure and reliable interface between merchants and payment providers (currently supporting Zarinpal).

## Features

- **Secure Payment Processing**: Handles payment transactions securely between merchants and payment gateways
- **API Key Authentication**: Each merchant has a unique API key for secure access
- **Domain Validation**: Validates callback URLs against registered merchant domains
- **Transaction Management**: Tracks and manages payment transactions
- **Asynchronous Operations**: Built with async/await for better performance
- **Comprehensive Logging**: Detailed logging of all operations and errors

## Technical Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy (async)
- **Cache**: Redis
- **Container**: Docker & Docker Compose
- **Python**: 3.11+

## Quick Start

1. Clone the repository
2. Copy `.env.example` to `.env` and configure your environment variables
3. Run `docker-compose up --build`
4. Access the API at `http://localhost:8000`
5. Access Adminer at `http://localhost:8080`

## API Documentation

### Merchant Integration

1. Register your website and get an API key
2. Use the API key in the `x-api-key` header for all requests
3. Ensure your callback URL matches your registered domain

### Payment Flow

1. **Create Payment**
   - Endpoint: `POST /api/v1/proxy-payment/create`
   - Headers: `x-api-key`
   - Body: amount, user_phone, callback_url, order_id
   - Returns: payment_url

2. **Process Payment**
   - User is redirected to payment gateway
   - Gateway processes payment
   - Gateway redirects to our callback

3. **Payment Callback**
   - Gateway calls our callback endpoint
   - We validate and redirect to merchant's callback URL
   - Merchant receives payment status

4. **Verify Payment**
   - Endpoint: `POST /api/v1/proxy-payment/verify`
   - Headers: `x-api-key`
   - Body: authority
   - Returns: payment verification result

## Environment Variables

Essential configurations in `.env`:

- `POSTGRES_*`: Database settings
- `REDIS_*`: Redis settings
- `ZARINPAL_MERCHANT_ID`: Payment gateway credentials
- `BASE_URL`: Application URL
- `PAYMENT_ENV`: sandbox/production

## Development Setup

The project uses Docker Compose with:
- FastAPI application
- PostgreSQL database
- Redis cache
- Adminer for database management

## Security

- API key authentication for merchants
- Domain validation for callbacks
- Transaction ownership verification
- Secure payment gateway integration

## Monitoring

- Comprehensive logging system
- Transaction tracking
- Error monitoring
- Payment status tracking

## License

[MIT License](LICENSE) 