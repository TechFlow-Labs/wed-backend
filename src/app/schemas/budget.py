from pydantic import BaseModel
from datetime import datetime

class BudgetDashboard(BaseModel):
    total_budget: float
    updated_at: datetime

    class Config:
        from_attributes = True

class BudgetUpdate(BaseModel):
    total_budget: float
