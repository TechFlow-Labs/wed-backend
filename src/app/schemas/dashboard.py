from pydantic import BaseModel
from typing import List
from schemas.users import UserDashboard
from schemas.budget import BudgetDashboard
from schemas.tasks import TaskDashboard
from schemas.gifts import GiftDashboard
from schemas.guests import GuestDashboard

class DashboardResponse(BaseModel):
    user: UserDashboard
    budget: BudgetDashboard
    tasks: List[TaskDashboard]
    gifts: List[GiftDashboard]
    guests: List[GuestDashboard]
