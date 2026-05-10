from fastapi import FastAPI
from routers import (
    auth,
    dashboard,
    tasks,
    gifts,
    gift_lists,
    guests,
    budget,
    reservations,
    vendors,
    notes,
    users,
    partner_expenses,
    special_partners,
)

app = FastAPI(title="Wedding Plan API", version="1.0")

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(tasks.router)
app.include_router(gifts.router)
app.include_router(gift_lists.router)
app.include_router(guests.router)
app.include_router(budget.router)
app.include_router(reservations.router)
app.include_router(vendors.router)
app.include_router(notes.router)
app.include_router(users.router)
app.include_router(partner_expenses.router)
app.include_router(special_partners.router)
