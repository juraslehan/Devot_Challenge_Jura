from fastapi import FastAPI
from .db import Base, engine

app = FastAPI(title="Home Budget API", version="0.1.0")

# Create tables on startup for now (we can switch to Alembic later)
Base.metadata.create_all(bind=engine)

@app.get("/health")
def health():
    return {"status": "ok"}
