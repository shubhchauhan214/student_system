from app.celery_worker import celery
import time

@celery.task
def student_created_task(student_id: int):
    print(f"Processing student {student_id} in background...")
    time.sleep(5)
    print(f"Student {student_id} background processing complete.")