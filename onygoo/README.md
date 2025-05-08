# Onygoo Carpooling Application

## Project Overview

Onygoo is a carpooling application designed to connect drivers and passengers for shared rides. The project consists of:

- **Flask Backend:** Web interface with modular blueprints, JWT authentication, WTForms for secure form handling, and an admin interface using AdminLTE.
- **FastAPI Backend:** Intended as a mobile API backend for Flutter app consumption (currently pending implementation).
- **Shared Models:** SQLAlchemy models shared between Flask and FastAPI backends, using MySQL database.
- **Frontend:** Flask templates for user-facing pages and admin interface with responsive design.
- **Notifications:** Email and push notification placeholders for user communication.

## Features

- User registration, login, email verification, and password reset.
- User profile management with photo upload and rating display.
- Ride proposal, search, modification, and cancellation.
- Reservation booking, confirmation, cancellation, and payment simulation.
- Admin dashboard with user and ride management.
- JWT-based authentication and role-based access control.

## Setup Instructions

### Prerequisites

- Python 3.8+
- MySQL database
- Virtual environment (recommended)

### Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd onygoo
```

2. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure database connection and secret keys in `onygoo/config.py`.

5. Initialize the database and run migrations.

### Running the Application

- To start the Flask web backend:

```bash
python3 onygoo/run_flask.py
```

- To start the FastAPI backend (pending implementation):

```bash
python3 onygoo/run_fastapi.py
```

## API Documentation

- The FastAPI backend is intended to provide RESTful APIs for the mobile Flutter app.
- API routers and detailed documentation are pending implementation.
- Once completed, OpenAPI docs will be available at `/docs` and `/redoc`.

## Project Structure

- `onygoo/app/` - Flask backend application code
- `onygoo/fastapi_app/` - FastAPI backend application code
- `onygoo/app/templates/` - HTML templates for Flask
- `onygoo/app/static/` - Static files (CSS, JS, images)
- `onygoo/app/forms/` - WTForms form classes
- `onygoo/app/blueprints/` - Flask blueprints for modular features
- `onygoo/run_flask.py` - Script to run Flask backend
- `onygoo/run_fastapi.py` - Script to run FastAPI backend

## Next Steps

- Complete FastAPI backend API implementation with routers, Pydantic schemas, and documentation.
- Enhance frontend with additional UI/UX improvements.
- Add comprehensive tests and CI/CD pipelines.
- Deploy to production environment with HTTPS and monitoring.

## Contact

For questions or contributions, please contact the project maintainer.

---
