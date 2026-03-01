from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas
from app.redis_client import redis_client
import json
import logging
from app.tasks import student_created_task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/students", tags=["Students"])

# CREATE
@router.post("/", response_model=schemas.StudentResponse)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):

    new_student = crud.create_student(db, student)

    if not new_student:
        raise HTTPException(status_code=400, detail="Invalid")

    # 1️⃣ Set individual cache
    redis_client.setex(
        f"student:{new_student.id}",
        60,
        json.dumps({
            "id": new_student.id,
            "name": new_student.name,
            "email": new_student.email
        })
    )
    logger.info(f"Individual cache created for student:{new_student.id}")

    # 2️⃣ Smart add into list cache (if exists)
    cached_list = redis_client.get("students_list")

    if cached_list:
        students_list = json.loads(cached_list)

        students_list.append({
            "id": new_student.id,
            "name": new_student.name,
            "email": new_student.email
        })

        redis_client.setex("students_list", 60, json.dumps(students_list))
        logger.info("SMART CACHE ADD: student appended to students_list")

        student_created_task.delay(new_student.id)
    logger.info(f"Task sent to RabbitMQ for student:{new_student.id}")

    return new_student

# GET ALL
@router.get("/", response_model=list[schemas.StudentResponse])
def get_students(db: Session = Depends(get_db)):

    cache_key = "students_list"
    cached_data = redis_client.get(cache_key)

    if cached_data:
        logger.info("CACHE HIT - students_list from Redis")
        return json.loads(cached_data)

    logger.info("CACHE MISS - Fetching students from DB")

    students = crud.get_students(db)

    students_data = [
        {"id": s.id, "name": s.name, "email": s.email}
        for s in students
    ]

    redis_client.setex(cache_key, 60, json.dumps(students_data))
    logger.info("students_list stored in Redis (TTL=60s)")

    return students_data

# GET BY ID (Per-student cache)
@router.get("/{student_id}", response_model=schemas.StudentResponse)
def get_student(student_id: int, db: Session = Depends(get_db)):

    cache_key = f"student:{student_id}"
    cached_student = redis_client.get(cache_key)

    if cached_student:
        logger.info(f"CACHE HIT - student:{student_id}")
        return json.loads(cached_student)

    logger.info(f"CACHE MISS - Fetching student:{student_id} from DB")

    student = crud.get_student_by_id(db, student_id)

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    redis_client.setex(
        cache_key,
        60,
        json.dumps({
            "id": student.id,
            "name": student.name,
            "email": student.email
        })
    )

    logger.info(f"student:{student_id} stored in Redis")

    return student

# DELETE
@router.delete("/{student_id}", response_model=schemas.StudentResponse)
def delete_student(student_id: int, db: Session = Depends(get_db)):

    student = crud.delete_student(db, student_id)

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # 1️⃣ Delete individual cache
    redis_client.delete(f"student:{student_id}")
    logger.info(f"Individual cache deleted for student:{student_id}")

    # 2️⃣ Smart remove from list cache
    cached_list = redis_client.get("students_list")

    if cached_list:
        students_list = json.loads(cached_list)

        students_list = [
            s for s in students_list if s["id"] != student_id
        ]

        redis_client.setex("students_list", 60, json.dumps(students_list))
        logger.info("SMART CACHE REMOVE: student removed from students_list")

    return student
