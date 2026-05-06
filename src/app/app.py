import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, dashboard, tasks, gifts, guests, budget, reservations, vendors, notes, users, partner_expenses

app = FastAPI(title="Wedding Plan API", version="1.0")

default_origins = "http://localhost:3000,http://localhost:8081,http://localhost:19006"
cors_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ALLOWED_ORIGINS", default_origins).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}


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
