# Python for Professional Developers Course from Master.dev

This is a companion repo for the [Python for Professional Developers course](https://master.dev/courses/pro-python/) from [Master.dev](https://master.dev/). 

The notes for the course can be found on this course website: [python-pros.netlify.app](https://python-pros.netlify.app/)



## Running locally

```bash
uv sync
cp .env.example .env                 # then fill in JWT_SECRET_KEY
docker compose up -d db              # Postgres on localhost:5432
uv run alembic upgrade head          # create / update the schema
uv run scripts/seed.py               # sample data (--reset to wipe and reload)
uv run fastapi dev                   # http://127.0.0.1:8000
```

- API docs: `/docs`
- Demo dashboard: `/app`
- Health check: `/health`

Quality checks:

```bash
uv run ruff check . && uv run ruff format --check .
uv run mypy .
uv run coverage run -m pytest && uv run coverage report
```
