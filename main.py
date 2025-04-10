from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from celery_worker import send_notification

app = FastAPI()

tasks = []

class Task(BaseModel):
    id: int
    title: str
    description: str = ""
    completed: bool = False
    created_at: datetime = datetime.utcnow()
    completed_at: Optional[datetime] = None

@app.post("/tasks/", response_model=Task)
def create_task(task: Task):
    tasks.append(task)
    send_notification.delay(task.title)
    return task

@app.get("/tasks/", response_model=List[Task])
def get_tasks():
    return tasks

@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    for task in tasks:
        if task.id == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")

@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, updated_task: Task):
    for index, task in enumerate(tasks):
        if task.id == task_id:
            updated_task.created_at = task.created_at  # Keep original timestamp
            updated_task.completed_at = task.completed_at  # Keep original completion time
            tasks[index] = updated_task
            return updated_task
    raise HTTPException(status_code=404, detail="Task not found")

@app.put("/tasks/{task_id}/complete")
def complete_task(task_id: int):
    for task in tasks:
        if task.id == task_id:
            task.completed = True
            task.completed_at = datetime.utcnow()
            return {"message": "Task marked as completed"}
    raise HTTPException(status_code=404, detail="Task not found")

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    for index, task in enumerate(tasks):
        if task.id == task_id:
            del tasks[index]
            return {"message": "Task deleted successfully"}
    raise HTTPException(status_code=404, detail="Task not found")

@app.get("/tasks/stats")
def get_task_stats():
    total = len(tasks)
    completed_tasks = [t for t in tasks if t.completed]
    pending = total - len(completed_tasks)

    if completed_tasks:
        total_time = sum(
            [(t.completed_at - t.created_at).total_seconds() for t in completed_tasks if t.completed_at],
            0
        )
        avg_time = total_time / len(completed_tasks)
        avg_time_str = str(timedelta(seconds=avg_time))
    else:
        avg_time_str = "N/A"

    return {
        "total_tasks": total,
        "completed_tasks": len(completed_tasks),
        "pending_tasks": pending,
        "average_completion_time": avg_time_str
    }
