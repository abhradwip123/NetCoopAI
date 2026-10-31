from fastapi import FastAPI

from backend.routes.diagnosis import router as diagnosis_router
from backend.database import Base, engine
from backend import models

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="NetCoop AI",
    description="Multi-agent network fault diagnosis system",
    version="1.0.0",
)

app.include_router(
    diagnosis_router,
    prefix="/api",
    tags=["Diagnosis"],
)


@app.get("/")
def root():
    return {
        "message": "NetCoop AI API is running",
        "docs": "/docs",
    }