from fastapi import FastAPI

from settings import settings

app = FastAPI(
    debug=settings.debug,
    openapi_url="/api/openapi.json" if settings.debug else None,
)


@app.get("/api/healthcheck")
async def healthcheck():
    return "ok"
