import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, dashboard, tasks, gifts, guests, budget, reservations, vendors, notes, users, partner_expenses

app = FastAPI(title="Wedding Plan API", version="1.0")

# ALLOWED_ORIGINS: comma-separated list of frontend origins, e.g.
# "https://ssr.example.com,https://app.example.com"
# Defaults to '*' (open) when not set — set explicitly in production.
_raw = os.getenv("ALLOWED_ORIGINS", "")
_origins = [o.strip() for o in _raw.split(",") if o.strip()] or ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=_origins != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Length", "Content-Range", "x-summary-file-name"],
)

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(tasks.router)
app.include_router(gifts.router)
app.include_router(guests.router)
app.include_router(budget.router)
app.include_router(reservations.router)
app.include_router(vendors.router)
app.include_router(notes.router)
app.include_router(users.router)
app.include_router(partner_expenses.router)
