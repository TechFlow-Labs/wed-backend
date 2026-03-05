from fastapi import FastAPI
from routers import auth, dashboard, tasks, gifts, guests, budget

app = FastAPI(title="Wedding Plan API", version="1.0")

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(tasks.router)
app.include_router(gifts.router)
app.include_router(guests.router)
app.include_router(budget.router)
