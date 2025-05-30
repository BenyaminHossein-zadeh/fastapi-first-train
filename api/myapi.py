from fastapi import FastAPI, Path, Query, Body, HTTPException
from typing import Optional, Tuple
from pydantic import BaseModel
import uuid
app = FastAPI()


students = [
    {
        "id": uuid.uuid4(),
        "name": "jhon",
        "age": 20,
        "class_year": "Year 12"
    },
    {
        "id": uuid.uuid4(),
        "name": "alex",
        "age": 12,
        "class_year": "Year 6"
    }, 
    {
        "id": uuid.uuid4(),
        "name": "mohammad",
        "age": 30,
        "class_year": "grajuated"
    }
]


class Student(BaseModel):
    name:str
    age:int
    class_year:str

class Update_student(BaseModel):
    name:Optional[str] = None
    age:Optional[int] = None
    class_year:Optional[str] = None


@app.get("/")
def index():
    return "hello, navigate to the docs for testing APIs"

@app.get("/get-students")
def get_student(
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

@app.get("/get-students/{student_id}")
def get_student(student_id:str = Path(...,description="ksncxkcnskcn", min_length=36, max_length=36)):
    for student in students:
        if student["id"] == student_id:
            return student
    raise HTTPException(status_code=404, detail=f"Student with ID {student_id} not found")

@app.post("/create-new-student")
def create_new_student(student:Student):
    students.append({"id":str(uuid.uuid4()) ,"name":student.name,"age":student.age,"class_year": student.class_year})
    return students

@app.put("/edit-student/{student_id}")
def edit_student(student_id: str = Path(..., description="UUID of the student", min_length=36, max_length=36), student: Update_student = Body(...)):
    for s in students:
        if str(s["id"]) == student_id:
            if student.name is not None:
                s["name"] = student.name
            if student.age is not None:
                s["age"] = student.age
            if student.class_year is not None:
                s["class_year"] = student.class_year
            return s
    raise HTTPException(status_code=404, detail=f"Student with ID {student_id} not found")

@app.delete("/remove_student/{student_id}")
def remove_student(student_id: str = Path(..., description="UUID of the student", min_length=36, max_length=36)):
    for s in students:
        if str(s["id"]) == student_id:
            students.remove(s)
            return students
    raise HTTPException(status_code=404, detail=f"Student with ID {student_id} not found")

