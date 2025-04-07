# 🌟 Product Catalog

This project was generated using fastapi_template: https://github.com/s3rius/FastAPI-template

inspirated by: https://github.com/esakik/leonardo-giordani/tree/master

This project follows Hexagonal Architecture principles.

## 🏗️ Architecture

This project follows a Hexagonal Architecture (also known as Ports and Adapters) with a clean domain-driven design approach:

```
src/
├── api/                  # 🌐 API Layer (External)
│   ├── routes/           # Route handlers
│   ├── dependencies.py   # Dependency injection
│   └── app.py            # FastAPI application configuration
│
├── dummy/                # ✨ Domain Module Example
│   ├── domain/           # 🧠 Domain Layer (Core)
│   │   ├── model/        # Domain entities
│   │   ├── events/       # Domain events
│   │   ├── exceptions/   # Domain exceptions
│   │   ├── repositories/ # Repository interfaces (ports)
│   │   └── event_publisher/ # Event publisher interfaces (ports)
│   │
│   ├── application/      # 📊 Application Layer
│   │   ├── services/     # Application services
│   │   └── dtos/         # Data Transfer Objects
│   │
│   └── infrastructure/   # 🔌 Infrastructure Layer (Adapters)
│       ├── repositories/ # Repository implementations
│       │   └── postgresql/
│       │       └── model/ # Database models
│       └── event_publisher/ # Event publisher implementations
│
├── shared/               # 🔄 Shared code
│   └── database/         # Database configuration
│
└── migrations/           # 🔄 Database migrations
```

## 💻 Poetry

This project uses poetry. It's a modern dependency management tool.

To run the project use this set of commands:

```bash
poetry install
poetry run python -m product_catalog
```

This will start the server on the configured host.

You can find swagger documentation at `/api/docs`.

You can read more about poetry here: https://python-poetry.org/

## 🐳 Docker

You can start the project with docker using this command:

```bash
docker-compose up --build
```

If you want to develop in docker with autoreload and exposed ports add `-f deploy/docker-compose.dev.yml` to your docker command.
Like this:

```bash
docker-compose -f docker-compose.yml -f deploy/docker-compose.dev.yml --project-directory . up --build
```

This command exposes the web application on port 8000, mounts current directory and enables autoreload.

But you have to rebuild image every time you modify `poetry.lock` or `pyproject.toml` with this command:

```bash
docker-compose build
```

## 🔄 Migrations

### Running Migrations Through Docker

Migrations are automatically applied when starting the application with docker-compose. However, you can also run them manually:

```bash
# Apply all pending migrations
docker-compose run --rm api alembic upgrade head

# Generate a new migration
docker-compose run --rm api alembic revision --autogenerate -m "Description of changes"

# Check current migration status
docker-compose run --rm api alembic current

# Revert last migration
docker-compose run --rm api alembic downgrade -1
```

### ⚠️ Important: Model Naming and Location

For migrations to work correctly with our architecture:

1. **Locating Models**: 
   - Models should be placed in their respective domain directories: `src/<domain>/infrastructure/repositories/postgresql/model/`
   - Use the naming pattern `*_model.py` (e.g., `dummy_model.py`)

2. **Model Discovery**:
   - Models are automatically discovered by our `load_all_models()` function in `src/shared/database/model_loader.py`
   - No need to manually register models in a central location

3. **Domain Interfaces**:
   - Repository interfaces should be placed in the domain layer: `src/<domain>/domain/repositories/interfaces/`
   - This follows the Dependency Inversion Principle where the domain defines the interfaces, and infrastructure implements them

## 🧪 Running tests

If you want to run it in docker, simply run:

```bash
docker-compose run --build --rm api pytest -vv .
docker-compose down
```

For running tests on your local machine.
1. you need to start a database.

I prefer doing it with docker:
```
docker run -p "5432:5432" -e "POSTGRES_PASSWORD=product_catalog" -e "POSTGRES_USER=product_catalog" -e "POSTGRES_DB=product_catalog" postgres:16.3-bullseye
```

2. Run the pytest.
```bash
pytest -vv .
```

## ⚙️ Configuration

Create a `.env` file in the root directory for configuration variables:

```bash
PRODUCT_CATALOG_RELOAD="True"
PRODUCT_CATALOG_PORT="8000"
PRODUCT_CATALOG_ENVIRONMENT="dev"
PRODUCT_CATALOG_LOG_LEVEL="DEBUG"  # To see events in logs
```

All environment variables should start with "PRODUCT_CATALOG_" prefix.

## 🧹 Pre-commit

To install pre-commit simply run inside the shell:
```bash
pre-commit install
```

pre-commit is very useful to check your code before publishing it.
It's configured using .pre-commit-config.yaml file.

By default it runs:
* black (formats your code)
* mypy (validates types)
* ruff (spots possible bugs)

You can read more about pre-commit here: https://pre-commit.com/
