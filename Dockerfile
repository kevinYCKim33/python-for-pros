# The Python project's official slim image. It includes the Python interpreter and 
# a minimal Debian userland, but skips compilers and most build tools. 
# The full python:3.14 image is several times larger and rarely necessary at runtime.
FROM python:3.14-slim

# Copy uv from the official image
# Multi-stage COPY --from pulls the uv and uvx binaries out of Astral's official 
# uv image and drops them into the runtime image. Pinning the uv version (0.11.6) is deliberate: 
# floating tags drift, and a uv upgrade has occasionally changed the 
# lockfile format in ways that break old uv sync invocations.

# 1. Docker pulls uv:0.11.6 from Astral's official image. Almost empty except
# for uv and uvx programs.
# 2. It copies /uv and /uvx out of that image
# 3. Puts them in the /bin/ (binary executables) in MY image
# 4. this enables docker being able to just do "uv sync" ~= npm install
COPY --from=ghcr.io/astral-sh/uv:0.11.6 /uv /uvx /bin/

# Compile bytecode for faster startup

# Tells uv to compile .pyc bytecode files during install. 
# The first request after the container starts skips the 
# compilation cost it would otherwise pay lazily.
ENV UV_COMPILE_BYTECODE=1

# Tells Python not to buffer stdout/stderr. Without it, log lines 
# can sit in a buffer for seconds and never reach the 
# container's log stream when the process crashes.

# Allows Python to output logs in real time
ENV PYTHONUNBUFFERED=1

# uv creates /app/.venv/ when it runs uv sync. Prepending the venv's bin/ to 
# PATH means fastapi, alembic, and python resolve to the venv's 
# binaries without needing uv run everywhere.
# https://app.notion.com/p/Complete-Intro-to-Linux-and-the-Command-Line-29f69ddc73658069be9beaf7ab34ee28?source=copy_link#2a769ddc736580b89458e56a1e3b9c47
# ^ really good note on what $PATH is

# TLDR instead of doing CMD ["uv", "run", "fastapi", "run"]
# now you can do CMD ["fastapi", "run"]
ENV PATH="/app/.venv/bin:$PATH"

# essentially cd /app for rest of the lines below
WORKDIR /app

# Project metadata and the lockfile. uv sync --frozen (below) refuses 
# to start if the lockfile is missing or out of sync with the toml.
# README needed as pyproject.toml states readme="README.md"
# README's really for projects to be published as a package
# so it's debatable that you don't need to have it
COPY pyproject.toml uv.lock README.md ./
# bulk of the code
COPY src ./src
# migration stuff
COPY alembic.ini ./ 
COPY alembic ./alembic
# seeds
COPY scripts ./scripts

# -frozen: enforces the lockfile exactly: no version drift between your dev machine, CI, and the image.
# -no-dev: skips the dev dependency group (Ruff, mypy, pytest, coverage)
RUN uv sync --frozen --no-dev

# just a note/label that fastapi run will run on port 8000
EXPOSE 8000

# only possible because of ENV PATH= line /bin line
# run instead of dev, not interested in hot reloading
CMD ["fastapi", "run"]

# to run multiple worker processes
# For your project: you have password hashing and JWT auth, 
# so 2 workers is a reasonable default if you deploy to 
# a single machine with 2 or more cores. 
# If you deploy to something that scales containers for you, 
# plain fastapi run with one worker is the simpler choice.
# CMD ["fastapi", "run", "--workers", "2"]

# if you want full control over timeouts, log format, dropdown to uvicorn from fastapi
# CMD ["uvicorn", "release_tracker.main:app", \
#      "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]