from celery import Celery

celery_app = Celery(
    "worker",
    broker="redis://<render-redis-url>:6379/0",  # Use the Render Redis URL
    backend="redis://<render-redis-url>:6379/0"
)

@celery_app.task
def send_notification(task_title: str):
    print(f"📬 Notification sent for task: {task_title}")
