from sqlalchemy.orm import Session
from app import models, schemas

def create_student(db: Session, student: schemas.StudentCreate):
    db_student = models.Student(**student.dict())
    db.add(db_student)
    db.commit
    db.refresh(db_student)
    return db_student

def get_students(db: Session):
    return db.query(models.Student).all()

def get_student_by_id(db: Session, student_id:int):
    return db.query(models.Student).filter(models.Student.id== student_id).first()

def delete_student(db: Session, student_id: int):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if student:
        db.delete(student)
        db.commit()

    return student
