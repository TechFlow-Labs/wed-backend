from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session
from database.db import get_session
from models import Tasks, User
from schemas.schemas import TaskCreate, TaskDashboard, UpdateTask
from utils.security import get_current_user
from typing import List
from uuid import UUID


router = APIRouter(prefix="/tasks", tags=["Tasks"])


# CREATE A TASK


@router.post("/", response_model=TaskDashboard, status_code=status.HTTP_201_CREATED)
def create_task(task_in: TaskCreate, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):

    new_task = Tasks(
        user_id = current_user.id,
        title = task_in.title,
        description = task_in.description,
        notes = task_in.notes,
        due_date = task_in.due_date,
        is_completed = task_in.is_completed
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task




# GET ALL TASKS FROM THE CURRENT USER

@router.get("/", response_model = List[TaskDashboard], status_code = status.HTTP_200_OK)
def reveal_task(db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    tasks = db.query(Tasks).filter(Tasks.user_id == current_user.id).all()
    return tasks



@router.patch("/{task_id}", response_model=TaskDashboard, status_code = status.HTTP_200_OK)
def update_task(task_id: UUID, task_update: UpdateTask, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):

    # Βρίσκουμε το Task (πρέπει να ανήκει και στον χρήστη!)
    db_task = db.query(Tasks).filter(Tasks.id == task_id, Tasks.user_id == current_user.id).first()

    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)

    db.commit()
    db.refresh(db_task)
    return db_task




@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: UUID, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):

    db_task = db.query(Tasks).filter(Tasks.id == task_id, Tasks.user_id == current_user.id).first()

    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    # Διαγραφή από το session
    db.delete(db_task)
    db.commit()
    return None
