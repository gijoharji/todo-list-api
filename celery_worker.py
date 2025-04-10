<<<<<<< HEAD
# celery_worker.py

=======
>>>>>>> c5dff36 (Initial commit: FastAPI + Celery + Redis)
from celery import Celery

celery_app = Celery(
    "worker",
<<<<<<< HEAD
    broker="redis://localhost:6379/0",   # Redis broker
    backend="redis://localhost:6379/0"   # Redis result backend
=======
    broker="redis://localhost:6379/0",  # Redis as the broker
    backend="redis://localhost:6379/0"
>>>>>>> c5dff36 (Initial commit: FastAPI + Celery + Redis)
)

@celery_app.task
def send_notification(task_title: str):
    print(f"📬 Notification sent for task: {task_title}")
