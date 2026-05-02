# Contributing to CivicPath

## Code Standards

- Python 3.11+ with full type hints
- Google-style docstrings on all public functions
- Module-level docstrings listing Google Services used
- Run `ruff check .` and `black .` before committing
- All tests must pass: `pytest --cov`

## PR Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Write tests for new functionality
4. Ensure all tests pass with ≥85% coverage
5. Submit a pull request with a clear description

## Google Services

When adding a new Google Service integration:
1. Add it to `google_services_registry.py`
2. Create/update the service file in `services/`
3. Add tests in `tests/`
4. Update `GOOGLE_SERVICES.md`
5. Update the README integration table
