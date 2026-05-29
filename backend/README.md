## Alembic (Database migrations)

This backend uses Alembic to manage database schema migrations. Alembic is configured to read the project's `DATABASE_URL` from `core.config.Settings` (which in turn reads the `.env` file when you run commands from the `backend` directory).

Typical workflow (run from the `backend` folder):

1. Activate your virtual environment.

   PowerShell:

   & ".\.venv\Scripts\Activate.ps1"

   or (Windows cmd):

   .venv\Scripts\activate

2. Create an autogenerate migration (inspect `backend/alembic/env.py` for configuration):

   python -m alembic revision --autogenerate -m "describe change"

3. Apply migrations:

   python -m alembic upgrade head

4. Show current revision:

   python -m alembic current

Notes:
- Alembic's `env.py` uses `core.config.settings` so ensure `backend/.env` is set with `DATABASE_URL` (or set the env var) before running revisions or upgrades.
- By default this repo keeps Alembic files under `backend/alembic`.

## Running tests (database)

The repository includes a small pytest suite under `backend/database/tests/` which runs against an in-memory SQLite database (so it won't touch your development Postgres DB).

From the project root, with your venv activated, run:

python -m pytest backend/database/tests -q

If you don't have test dependencies installed, run:

python -m pip install -r backend/requirements.txt
