# app/main.py

from fastapi import FastAPI
from app.routes import router

app = FastAPI(
    title="KYC Validation Engine",
    description="Multi-source KYC consistency and validation system",
    version="1.0.0"
)

app.include_router(router)