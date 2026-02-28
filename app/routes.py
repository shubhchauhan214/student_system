from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas

router = APIRouter(prefix="/students", tags=["Students"])

@router.post("/", response_model=schemas.StudentResponse)
def create_student(student: schemas.StudentCreate, db: Session=Depends(get_db)):
    new_student = crud.create_student(db, student)

    if not new_student:
        raise HTTPException(status_code=400, detail="Invalid")
    
@router.get("/", response_model=list[schemas.StudentResponse])
def get_students(db: Session=Depends(get_db)):
    students=crud.get_students(db)
    return students

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
    return student
