from fastapi import FastAPI, Path, Query, HTTPException, Depends, Form
from typing import Optional, List
import uuid
import uvicorn
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
import logging
from fastapi.logger import logger

# Configure logging
logging.basicConfig(level=logging.INFO)
logger.setLevel(logging.INFO)

# FastAPI app
app = FastAPI()

# SQLAlchemy setup
DATABASE_URL = os.getenv("POSTGRES_URL")
if not DATABASE_URL:
    logger.error("POSTGRES_URL environment variable not set")
    raise ValueError("POSTGRES_URL environment variable not set")

# Add SSL for Neon
engine = create_engine(DATABASE_URL, connect_args={"sslmode": "require"})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Student model for Postgres
class StudentDB(Base):
    __tablename__ = "students"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    class_year = Column(String(50), nullable=True)  # Allow null for flexibility

# Create tables
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Failed to create database tables: {str(e)}")
    raise

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Student API"}

@app.get("/get-students")
def get_students(db: Session = Depends(get_db)):
    try:
        students = db.query(StudentDB).all()
        return [{"id": s.id, "name": s.name, "age": s.age, "class_year": s.class_year} for s in students]
    except Exception as e:
        logger.error(f"Error retrieving students: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/get-students/{student_id}")
def get_student(
    student_id: str = Path(..., description="The UUID of the student", min_length=36, max_length=36),
    db: Session = Depends(get_db)
):
    try:
        student = db.query(StudentDB).filter(StudentDB.id == student_id).first()
        if student:
            return {"id": student.id, "name": student.name, "age": student.age, "class_year": student.class_year}
        raise HTTPException(status_code=404, detail=f"Student with ID {student_id} not found")
    except Exception as e:
        logger.error(f"Error retrieving student {student_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/create-new-student")
def create_new_student(
    name: str = Form(..., min_length=1, max_length=100, description="Name"),
    age: int = Form(..., ge=5, le=150, description="Age"),
    class_year: str = Form(..., min_length=1, max_length=50, description="Class year"),
    db: Session = Depends(get_db)
):
    try:
        new_student = StudentDB(
            name=name.strip(),
            age=age,
            class_year=class_year.strip()
        )
        db.add(new_student)
        db.commit()
        db.refresh(new_student)
        logger.info(f"Created student: {new_student.id}")
        return {
            "id": new_student.id,
            "name": new_student.name,
            "age": new_student.age,
            "class_year": new_student.class_year
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating student: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create student: {str(e)}")

@app.get("/filter-students")
def filter_students(
    name: Optional[str] = Query(None, description="Filter by name (case-insensitive)"),
    age_range: Optional[List[int]] = Query(None, description="Filter by age range [min, max]"),
    db: Session = Depends(get_db)
):
    try:
        query = db.query(StudentDB)
        if name:
            query = query.filter(StudentDB.name.ilike(f"%{name}%"))
        if age_range:
            if len(age_range) != 2 or age_range[0] > age_range[1]:
                raise HTTPException(400, "age_range must be [min, max] with min <= max")
            query = query.filter(StudentDB.age.between(age_range[0], age_range[1]))
        students = query.all()
        return [{"id": s.id, "name": s.name, "age": s.age, "class_year": s.class_year} for s in students]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error filtering students: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)