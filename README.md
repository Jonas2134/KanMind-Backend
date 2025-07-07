# Kanmind

**Kanmind** is the backend of a Kanban board, implemented with Django and Django REST Framework.

## Features

- User management with custom User model
- Token-based authentication
- REST API for Boards, Tasks, and Users
- CORS support (open to all origins for development)

## Requirements

- Python 3.x
- Virtual environment (`venv`)
- [pip](https://pip.pypa.io/en/stable/)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Jonas2134/KanMind-Backend.git
   cd kanmind-backend
   ```
2. Create and activate a virtual environment:
    ```bash
    # Linux/macOS
    python3 -m venv env
    source venv/bin/activate
    # Windows
    python -m venv env
    env\Scripts\activate
    ```
3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. Apply database migrations:
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```
5. (Optional) Create a superuser:
    ```bash
    python manage.py createsuperuser
    ```

## Start the project

- Start the Django development server with:
    ```bash
    python manage.py runserver
    ```
- The backend is then typically available at: `http://localhost:8000/`
