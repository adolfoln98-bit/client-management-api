# FastAPI Client Management API

A REST API built with FastAPI that demonstrates authentication, authorization, resource ownership, validation, testing, and backend best practices.

## Features

### Authentication & Security

* User registration
* User login with JWT authentication
* Password hashing with bcrypt
* Protected endpoints
* Environment variable configuration

### Authorization

* Role-based access control (RBAC)
* User and admin roles
* Resource ownership validation

### Client Management

* Full CRUD operations
* Filtering by name and age
* Pagination
* Sorting
* Input validation with Pydantic

### Testing

* Automated tests with Pytest
* Authentication tests
* Authorization tests
* Ownership tests
* CRUD tests
* Coverage reporting with pytest-cov

## Tech Stack

* Python
* FastAPI
* SQLite
* Pydantic
* JWT
* Passlib (bcrypt)
* Pytest
* Python-dotenv

## Project Structure

```text
.
├── dependencies/
├── routes/
├── services/
├── tests/
├── db.py
├── main.py
├── models.py
├── security.py
├── requirements.txt
└── README.md
```

## Installation

```bash
git clone <repository-url>
cd fastapi-client-management-api

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file using `.env.example` as reference:

```env
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=data/clientes.db
```

## Run the Application

```bash
uvicorn main:app --reload
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## Run Tests

```bash
pytest
```

Coverage report:

```bash
pytest --cov
```

## Learning Objectives

This project was built to practice:

* REST API development
* Authentication and authorization
* FastAPI architecture
* Testing with Pytest
* Environment management
* Backend development best practices

## Future Improvements

* PostgreSQL support
* Docker containerization
* CI/CD with GitHub Actions
* Cloud deployment
* Database migrations
* API versioning
