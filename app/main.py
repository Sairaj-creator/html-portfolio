from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from app.core.config import settings
from app.routers.query import router as query_router
from app.routers.admin import router as admin_router


app = FastAPI(title=settings.app_name, default_response_class=ORJSONResponse)

app.include_router(query_router, prefix="/api")
app.include_router(admin_router, prefix="/api")


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "mock_mode": settings.mock_mode}
