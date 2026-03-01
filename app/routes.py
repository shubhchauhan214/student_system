from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas
from app.redis_client import redis_client
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/students", tags=["Students"])

@router.post("/", response_model=schemas.StudentResponse)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):

    new_student = crud.create_student(db, student)

    if not new_student:
        raise HTTPException(status_code=400, detail="Invalid")

    redis_client.delete("students_list")
    logger.info("CACHE INVALIDATED after CREATE")

    return new_student
    
@router.get("/", response_model=list[schemas.StudentResponse])
def get_students(db: Session = Depends(get_db)):

    cache_key = "students_list"

    cached_data = redis_client.get(cache_key)

    if cached_data:
        logger.info("CACHE HIT - Data coming from Redis")
        return json.loads(cached_data)

    logger.info("CACHE MISS - Fetching from Database")

    students = crud.get_students(db)

    students_data = [
        {
            "id": student.id,
            "name": student.name,
            "email": student.email
        }
        for student in students
    ]

    redis_client.setex(
        cache_key,
        60,
        json.dumps(students_data)
    )

    logger.info("Data stored in Redis with TTL = 60 seconds")

    return students_data

@router.get("/{student_id}", response_model=schemas.StudentResponse)
def get_student(student_id: int, db: Session=Depends(get_db)):
    student=crud.get_student_by_id(db, student_id)

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@router.delete("/{student_id}", response_model=schemas.StudentResponse)
def delete_student(student_id: int, db: Session = Depends(get_db)):

    student = crud.delete_student(db, student_id)

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    redis_client.delete("students_list")
    logger.info("CACHE INVALIDATED after DELETE")

    return student
