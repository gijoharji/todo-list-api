# celery_worker.py

from celery import Celery

celery_app = Celery(
    "worker",
    broker="redis://localhost:6379/0",   # Redis broker
    backend="redis://localhost:6379/0"   # Redis result backend
)

@celery_app.task
def send_notification(task_title: str):
    print(f"📬 Notification sent for task: {task_title}")
