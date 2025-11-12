# ExamShield Licensing System

A payment-verified licensing system for ExamShield with trial mode, online verification, and device limits.

## Project Structure

```
examshieldbroadcast/
├── server/              # Flask license server
│   ├── license_server.py
│   └── config.env       # Environment configuration template
├── client/              # Client-side licensing module
│   └── license.py       # License verification and trial management
├── packaging/           # Packaging scripts and resources
├── tests/               # Test suites
├── docs/                # Documentation
│   └── setup_steps.md   # Deployment instructions
├── data/                # License database (gitignored)
├── build/               # Debian package build directory
├── examshield.py        # Main ExamShield daemon
├── build_examshield_full.sh  # Debian package builder
└── README.md            # This file
```

## Features

- **Payment-Verified Licensing**: Licenses activate only after payment confirmation via webhook
- **Trial Mode**: 7-day free trial for new installations
- **Online Verification**: Real-time license validation against server
- **Device Limits**: Individual licenses (2 devices) vs Organization licenses (unlimited)
- **Admin Tools**: Revoke and extend licenses via admin endpoints
- **Email Delivery**: Automatic license key delivery via SMTP

## Quick Start

### License Server

1. Copy `server/config.env` and configure SMTP, webhook secret, and data directory
2. Install dependencies: `pip3 install flask python-dotenv`
3. Run server: `python3 server/license_server.py`

### Client Integration

The licensing system is integrated into ExamShield:
- License verification runs on daemon startup
- Installer includes license key input field
- Trial mode activates automatically if no key provided

## License Types

- **Individual**: 2 device limit, 1 year validity
- **Organization**: Unlimited devices, 1 year validity

## API Endpoints

- `POST /register` - Register new license request
- `POST /verify` - Verify license key and device
- `POST /webhook/payment` - Payment webhook handler
- `GET /admin/revoke?key=XXX` - Revoke license
- `GET /admin/extend?key=XXX&days=365` - Extend license

## Development

See `docs/setup_steps.md` for detailed deployment and configuration instructions.

## License

Proprietary - ExamShield Licensing System

