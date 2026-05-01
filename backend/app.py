from fastapi import FastAPI

import views.auth as views_auth
from settings import settings

app = FastAPI(
    debug=settings.debug,
    openapi_url="/api/openapi.json" if settings.debug else None,
)


@app.get("/api/healthcheck")
async def healthcheck():
    return "ok"


app.include_router(views_auth.router, prefix="/api/auth")
