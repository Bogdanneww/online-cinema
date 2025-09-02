# Online Cinema

**Online Cinema** is a simple API for an online movie theater, built with FastAPI, supporting CRUD operations for movies and users, along with a password reset system.

## Features

- Manage movies (create, read, update, delete)
- Manage users
- User authentication
- Password reset via reset tokens
- Asynchronous database interaction (SQLite with SQLAlchemy Async)

## Technologies

- Python 3.13
- FastAPI
- SQLAlchemy (async)
- SQLite (in-memory for tests)
- Alembic (database migrations)
- Pytest + pytest-asyncio (testing)

## Installation

1. Clone the repository:

   ```bash
   git clone <your-repo-url>
   cd online-cinema

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   # Linux/macOS
   source .venv/bin/activate
   # Windows
   .venv\Scripts\activate

3. Install dependencies:

   ```bash
   pip install -r requirements.txt

4. Run database migrations:

   ```bash
   alembic upgrade head

## Running the Server

   ```bash
   uvicorn main:app --reload

After starting, the server will be available at:
http://127.0.0.1:8000
