from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, dashboard, tasks, gifts, guests, budget, reservations, vendors, notes, users, partner_expenses

app = FastAPI(title="Wedding Plan API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://wedapp.techflowlabs.gr",
        "https://preview.main.wedapp.techflowlabs.gr",
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_origin_regex=r"^https://[a-zA-Z0-9-]+\.preview\.techflowlabs\.gr$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
