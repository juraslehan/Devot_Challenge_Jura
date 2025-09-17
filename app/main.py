from fastapi import FastAPI
from .db import Base, engine
from .routers import auth

app = FastAPI(title="Home Budget API", version="0.1.0")

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)

@app.get("/health")
def health():
    return {"status": "ok"}
