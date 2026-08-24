from fastapi import FastAPI

app = FastAPI(
    title="HyperSolutions Audit Log API",
    description="Compliance Audit Log Management System",
    version="0.1.0",
)

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": "Audit Log API"}