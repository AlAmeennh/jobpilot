from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from . import models
from .routes import applications, auth, matcher

Base.metadata.create_all(bind=engine)

app = FastAPI(title="JobPilot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(applications.router)
app.include_router(matcher.router)


@app.get("/health")
def health():
    return {"status": "ok"}