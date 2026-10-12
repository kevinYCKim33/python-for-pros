import logging
import time
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from release_tracker.routers import auth, projects, tasks

from .config import configure_logging, get_settings

# could probably inject level from .env
configure_logging(debug=get_settings().debug)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="Release Tracker API",
    description="An API for tracking project milestones and developer tasks.",
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


# let's use the new router
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(tasks.router)


# We state that Project names must be unique
# any time there's an integrity error upon trying to commit to the
# backend, this exception handler kicks in
# by default it returns 500, but it should really be 400
# and let users know to pick a unique name for the project


# any duplicate errors (user emails, project names)
# get handled here
@app.exception_handler(IntegrityError)
def handle_integrity_error(request: Request, exc: IntegrityError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "Data conflict occurred (e.g., duplicate entry)."},
    )


@app.get("/")
def read_root() -> dict[str, str]:
    logger.info("Hello World!!!")
    return {
        "app": "Release Tracker API",
        "docs": "/docs",
    }
