from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

executor = ThreadPoolExecutor()

def send_notification(title: str):
    with open("message_queue.txt", "a") as f:
        f.write(f"{datetime.utcnow()} - Notification sent for: {title}\n")
    print(f"📬 Notification sent for: {title}")

