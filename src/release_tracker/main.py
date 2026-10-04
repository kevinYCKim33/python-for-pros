from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from .routers import projects  # some subtle namespacing going on

app = FastAPI(
    title="Release Tracker API",
    description="An API for tracking project milestones and developer tasks.",
)


# let's use the new router
app.include_router(projects.router)


# We state that Project names must be unique
# any time there's an integrity error upon trying to commit to the
# backend, this exception handler kicks in
# by default it returns 500, but it should really be 400
# and let users know to pick a unique name for the project
@app.exception_handler(IntegrityError)
def handle_integrity_error(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "Data conflict occurred (e.g., duplicate entry)."},
    )


@app.get("/")
def read_root() -> dict[str, str]:
    return {
        "app": "Release Tracker API",
        "docs": "/docs",
    }
