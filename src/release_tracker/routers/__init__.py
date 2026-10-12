# re-export each router under a distinct name so main.py can do
# `from .routers import auth_router, ...` instead of `auth.router`, `projects.router`, ...
from .auth import router as auth_router
from .health import router as health_router
from .projects import router as projects_router
from .tasks import router as tasks_router

__all__ = ["auth_router", "health_router", "projects_router", "tasks_router"]
