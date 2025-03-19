# api package initialization
from app.api.query import router as query_router

# Export the routers
__all__ = ["query_router"]
