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
- Poetry (dependency management)
- Pytest + pytest-asyncio (testing)
- Black, Mypy (formatting and static analysis)

## Installation

1. Clone the repository:

   ```bash
   git clone <https://github.com/Bogdanneww/online-cinema.git>
   cd online-cinema

2. Install Poetry (if not installed):

   ```bash
   curl -sSL https://install.python-poetry.org | python -

3. Install dependencies and create virtual environment:

   ```bash
   poetry install

4. Activate the virtual environment:

   ```bash
   poetry shell
   
5. Run database migrations:

   ```bash
   alembic upgrade head

## Running the Server

   ```bash
   poetry run uvicorn main:app --reload

   After starting, the server will be available at:
   http://127.0.0.1:8000
