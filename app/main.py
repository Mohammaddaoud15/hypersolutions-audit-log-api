import time

from fastapi import FastAPI, Request

from app.core.logger import logger
from app.routes import auth, logs

app = FastAPI(
    title="HyperSolutions Audit Log API",
    description="Compliance Audit Log Management System",
    version="0.1.0",
)

app.include_router(auth.router)
app.include_router(logs.router)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": "Audit Log API"}


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    logger.info(
        f"Method: {request.method} Path: {request.url.path} "
        f"Status: {response.status_code} Duration: {duration:.4f}s"
    )
    return response
