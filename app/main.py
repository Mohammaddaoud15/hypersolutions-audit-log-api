import time

from fastapi import FastAPI, Request

from app.core.auth import hash_password
from app.core.logger import logger, setup_logging
from app.database import SessionLocal
from app.models import User, UserRole
from app.routes import auth, logs

setup_logging()


def create_admin_if_missing():
    db = SessionLocal()
    try:
        admin_exists = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if not admin_exists:
            admin = User(
                username="admin",
                hashed_password=hash_password("admin123"),
                role=UserRole.ADMIN,
            )
            db.add(admin)
            db.commit()
            logger.info("Default admin user ('admin') created successfully.")
    finally:
        db.close()


app = FastAPI(
    title="HyperSolutions Audit Log API",
    description="Compliance Audit Log Management System",
    version="0.1.0",
)

create_admin_if_missing()

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
