from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi_pagination import add_pagination
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.middleware.cors import CORSMiddleware

from data_bridge.core.config import settings
from data_bridge.django_emr.api import django_emr_api_v2_router

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(django_emr_api_v2_router, prefix=f"/v2/django-emr")


@app.get("/")
def read_main():
    return {"message": "Deployment is live"}


# Register pagination middleware
add_pagination(app)

# Register prometheus instrumentation
Instrumentator().instrument(app).expose(app)
