"""
Monika G Cafe Management System — backend entrypoint.

Run with:  uvicorn app.main:app --reload
Docs at:   http://localhost:8000/docs
"""
import socket
from fastapi import APIRouter
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.config import settings

# Import every model so create_all() can see all tables
from app import models  # noqa: F401

from app.routers import auth, menu, inventory, orders, bills, employees, reports

app = FastAPI(
    title="Monika G Cafe Management System",
    description="API for orders, billing, inventory, employees, and reporting.",
    version="1.0.0",
)

router = APIRouter()

@router.get("/test-smtp")
def test_smtp():
    try:
        socket.create_connection(("smtp.gmail.com", 587), timeout=10)
        return {"status": "Connected to Gmail SMTP"}
    except Exception as e:
        return {"status": "Failed", "error": str(e)}

app.include_router(router)

# Allow the frontend (served separately) to call this API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:3000",
        "https://monica-g-cafe-1.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(auth.router)
app.include_router(menu.router)
app.include_router(inventory.router)
app.include_router(orders.router)
app.include_router(bills.router)
app.include_router(employees.router)
app.include_router(reports.router)


@app.on_event("startup")
def on_startup():
    # Creates tables if they don't exist yet. For real schema changes later,
    # switch to Alembic migrations instead of relying on create_all().
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "Monika G Cafe Management System API is running.", "docs": "/docs"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
