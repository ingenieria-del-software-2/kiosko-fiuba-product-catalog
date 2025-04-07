# Testing

This directory contains various tests for the product catalog service. The tests use pytest with pytest-asyncio for testing asynchronous code.

## Test Structure

The test directory is organized as follows:

- `api/`: Tests for the HTTP API endpoints
- `products/`: Tests for the domain model and application services
  - `application/`: Tests for application services
  - `domain/`: Tests for domain entities and value objects
  - `infrastructure/`: Tests for infrastructure implementations
- `integration/`: Integration tests with external services
- `performance/`: Performance tests

## Running Tests

### Running all tests

To run all tests in the Docker container:

```bash
docker-compose exec api pytest -xvs
```

### Running specific tests

To run a specific test file:

```bash
docker-compose exec api pytest -xvs /app/tests/path/to/test_file.py
```

To run a specific test:

```bash
docker-compose exec api pytest -xvs /app/tests/path/to/test_file.py::test_function_name
```

## Test Configuration

Test configuration is managed through the `pytest.ini` file, which includes:

- Registration of custom markers (e.g., `asyncio`)
- Test path configuration
- Asyncio behavior settings

## Testing Approach

### Unit Tests

Unit tests focus on testing individual components in isolation. For application services and domain model tests, dependencies are mocked to isolate the unit being tested.

### API Tests

API tests focus on testing the HTTP interface. These tests use FastAPI's TestClient and mock the service layer to isolate API behavior testing from business logic.

### Mocking Strategy

- Use `unittest.mock.AsyncMock` for asynchronous dependencies
- Override FastAPI dependencies with proper async functions that return mocks
- Configure return values or side effects on mocks to simulate different scenarios

## Known Issues

- Some API error handling tests expect 500 status codes with `not found` in the detail message, even though they should ideally return 404 errors. This reflects the current implementation which could be improved.

## Conventions

- Test files are named with a `test_` prefix
- Test functions use `test_` prefix
- Test classes use `Test` prefix
- Use pytest fixtures for test setup and reusable test data
- Include docstrings explaining the purpose of each test function 