from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from celery_worker import send_notification

# PostgreSQL database URL (replace <password> with your actual password)
SQLALCHEMY_DATABASE_URL = "postgres://new_9p3z_user:<password>@dpg-cvrsh36uk2gs73bjhf10-a:5432/new_9p3z"

# Database setup
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

# Pydantic model for task
class Task(BaseModel):
    id: int
    title: str
    description: str = ""
    completed: bool = False
    created_at: datetime = datetime.utcnow()
    completed_at: Optional[datetime] = None

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to the To-Do List API!"}

# Create a task and add to the database
@app.post("/tasks/", response_model=Task)
def create_task(task: Task, db: Session = Depends(get_db)):
    # Save task to database
    db_task = Task(
        id=task.id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        created_at=task.created_at,
        completed_at=task.completed_at
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    # Send notification task via Celery
    send_notification.delay(task.title)
    
    return db_task

# Retrieve all tasks
@app.get("/tasks/", response_model=List[Task])
def get_tasks(db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    return tasks

# Retrieve a single task by ID
@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# Update a task
@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, updated_task: Task, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.title = updated_task.title
    task.description = updated_task.description
    task.completed = updated_task.completed
    task.completed_at = updated_task.completed_at
    
    db.commit()
    db.refresh(task)
    
    return task

# Mark a task as completed
@app.put("/tasks/{task_id}/complete")
def complete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.completed = True
    task.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(task)
    
    return {"message": "Task marked as completed"}

# Delete a task
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    
    return {"message": "Task deleted successfully"}

