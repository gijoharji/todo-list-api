from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from celery_worker import send_notification

# PostgreSQL database URL
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://new_9p3z_user:gj4BF7RIi0OkWvZppWAmIhmuJ8FUEYUz@dpg-cvrsh36uk2gs73bjhf10-a:5432/new_9p3z"

# Database setup
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

# SQLAlchemy model
class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, default="")
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

# Create DB tables
Base.metadata.create_all(bind=engine)

# Pydantic schema
class TaskSchema(BaseModel):
    id: int
    title: str
    description: str = ""
    completed: bool = False
    created_at: datetime = datetime.utcnow()
    completed_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to the To-Do List API!"}

@app.post("/tasks/", response_model=TaskSchema)
def create_task(task: TaskSchema, db: Session = Depends(get_db)):
    db_task = TaskModel(
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
    send_notification.delay(task.title)
    return db_task

@app.get("/tasks/", response_model=List[TaskSchema])
def get_tasks(db: Session = Depends(get_db)):
    return db.query(TaskModel).all()

@app.get("/tasks/{task_id}", response_model=TaskSchema)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/tasks/{task_id}", response_model=TaskSchema)
def update_task(task_id: int, updated_task: TaskSchema, db: Session = Depends(get_db)):
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    task.title = updated_task.title
    task.description = updated_task.description
    task.completed = updated_task.completed
    task.completed_at = updated_task.completed_at

    db.commit()
    db.refresh(task)
    return task

@app.put("/tasks/{task_id}/complete")
def complete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    task.completed = True
    task.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(task)
    return {"message": "Task marked as completed"}

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}

