import logging

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy import text

from release_tracker.dependencies import SessionDep

logger = logging.getLogger(__name__)

router = APIRouter(tags=["meta"])


# k8s call this endpoint to see whether container is ready to receive traffic
@router.get("/health", response_model=None, status_code=status.HTTP_200_OK)
def healthcheck(session: SessionDep) -> dict[str, str] | JSONResponse:
    try:
        # essentially just asking: am I connected to the database?
        # text("SELECT 1") is plain SQL, no ORM involved
        session.execute(text("SELECT 1"))
        logger.debug("Healthcheck requested")
        return {"status": "healthy"}
    except Exception:
        logger.warning("Healthcheck failed: database unreachable")
        return JSONResponse(
            {"status": "unhealthy"},
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
