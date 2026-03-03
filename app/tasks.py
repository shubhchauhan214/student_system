from app.celery_worker import celery
from app.database import SessionLocal
from app import models
from app.email_service import send_welcome_email
import logging

@celery.task
def student_created_task(student_id: int):
    db = SessionLocal()

    student = db.query(models.Student).filter(models.Student.id==student_id).first()

    if student:
        send_welcome_email(student.email, student.name)

    db.close()