from celery import Celery
import os

broker_url = os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@rabbitmq:5672//")

celery = Celery(
    "student_tasks",
    broker=broker_url,
    backend="redis://redis:6379/0"  # optional result backend
)

celery.conf.task_routes = {
    "app.tasks.*": {"queue": "student_queue"}
}