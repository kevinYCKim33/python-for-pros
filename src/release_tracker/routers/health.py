from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlmodel import select

from release_tracker.dependencies import SessionDep

router = APIRouter(tags=["meta"])


@router.get("/health", response_model=None, status_code=status.HTTP_200_OK)
def healthcheck(session: SessionDep) -> dict[str, str] | JSONResponse:
    try:
        # essentially just asking: am I connected to the database?
        session.exec(select(1))
        return {"status": "healthy"}
    except Exception:
        return JSONResponse(
            {"status": "unhealthy"},
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
