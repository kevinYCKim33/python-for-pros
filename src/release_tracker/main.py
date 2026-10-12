import logging
import time
from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import IntegrityError

from . import __version__
from .config import configure_logging, get_settings
from .routers import auth_router, health_router, projects_router, tasks_router

APP_NAME = "Release Tracker API"
logger = logging.getLogger(__name__)
# folder holding the dashboard's index.html / app.js / styles.css
static_dir = Path(__file__).resolve().parent / "static"


# lifespan: code before `yield` runs once on startup, code after runs once on shutdown
# replaces calling configure_logging() at import time, so just importing main
# (e.g. in tests) no longer has the side effect of reconfiguring logging
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    # could probably inject level from .env
    configure_logging(debug=get_settings().debug)
    yield


app = FastAPI(
    title=APP_NAME,
    version=__version__,  # shows up in /docs
    description="An API for tracking project milestones and developer tasks.",
    lifespan=lifespan,
)


@app.middleware("http")
async def log_requests(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = (time.perf_counter() - start_time) * 1000

    logger.info(
        "%s %s completed in %.2fms with status code %s",
        request.method,
        request.url.path,
        process_time,
        response.status_code,
    )
    return response


# serves /app/static/app.js, /app/static/styles.css etc. straight off disk
app.mount("/app/static", StaticFiles(directory=static_dir), name="app-static")

# let's use the new router
app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(tasks_router)
app.include_router(health_router)


# We state that Project names must be unique
# any time there's an integrity error upon trying to commit to the
# backend, this exception handler kicks in
# by default it returns 500, but it should really be 400
# and let users know to pick a unique name for the project


# any duplicate errors (user emails, project names)
# get handled here
@app.exception_handler(IntegrityError)
def handle_integrity_error(request: Request, exc: IntegrityError) -> JSONResponse:
    logger.warning(
        "IntegrityError handled method=%s path=%s",
        request.method,
        request.url.path,
    )
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "Data conflict occurred (e.g., duplicate entry)."},
    )


# demo dashboard; include_in_schema=False keeps it out of /docs
@app.get("/app", include_in_schema=False)
@app.get("/app/", include_in_schema=False)
def frontend_dashboard() -> FileResponse:
    logger.info("Serving dashboard")
    return FileResponse(static_dir / "index.html")


@app.get("/", tags=["meta"])
def read_root() -> dict[str, str]:
    logger.debug("Serving root metadata")
    return {
        "app": APP_NAME,
        "version": __version__,
        "docs": "/docs",
        "health": "/health",
    }
