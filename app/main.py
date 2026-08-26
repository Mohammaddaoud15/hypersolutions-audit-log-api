from fastapi import FastAPI

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

