from fastapi import FastAPI

from app.database import Base, engine
from app import models  # noqa: F401
from app.routers import applications_router

# Simple setup: create tables on startup. In production, use Alembic.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Credit Evaluation Service")
app.include_router(applications_router)


@app.get("/health")
def health():
    return {"status": "ok"}
