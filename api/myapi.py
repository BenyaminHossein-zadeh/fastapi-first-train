from fastapi import FastAPI, Path, Query, HTTPException, Form
from typing import Optional, Tuple
import uuid
app = FastAPI()


students = [
    {
        "id": "1",
        "name": "jhon",
        "age": 20,
        "class_year": "Year 12"
    },
    {
        "id": "2",
        "name": "alex",
        "age": 12,
        "class_year": "Year 6"
    }, 
    {
        "id": "3",
        "name": "mohammad",
        "age": 30,
        "class_year": "grajuated"
    }
]

@app.get("/")
def index():
    return {"name" : "first Data"}

@app.get("/get-students")
def get_student():
    return students

@app.get("/get-students/{student_id}")
def get_student(student_id:str = Path(...,description="ksncxkcnskcn", min_length=36, max_length=36)):
    for student in students:
        if student["id"] == student_id:
            return student
    raise HTTPException(status_code=404, detail=f"Student with ID {student_id} not found")

@app.post("/create-new-student")
def create_new_student(
    name:str = Form(..., min_length=1, max_length=100, description="Student name"),
    age:int = Form(..., ge=0, le=150, description="Student age"),
    class_year:str = Form(..., min_length=1, max_length=50, description="Student class year")

    ):
    students.append({"id":str(uuid.uuid4()) ,"name":name,"age":age,"class_year": class_year})
    return students


@app.get("/get-filtered-students")
def get_students(
    name: Optional[str] = Query(None, description="Filter by student name (case-insensitive partial match)"),
    age_range: Optional[Tuple[int, int]] = Query(None, description="Filter by age range [min_age, max_age], inclusive")
):
    filtered_students = students.copy()

    if name:
        filtered_students = [
            student for student in filtered_students
            if name.lower() in student["name"].lower()
        ]

    if age_range:
        if len(age_range) != 2:
            raise HTTPException(status_code=400, detail="age_range must contain exactly two integers [min_age, max_age]")
        if age_range[0] > age_range[1]:
            raise HTTPException(status_code=400, detail="Invalid age_range: min_age must be <= max_age")
        filtered_students = [
            student for student in filtered_students
            if age_range[0] <= student["age"] <= age_range[1]
        ]

    return filtered_students


