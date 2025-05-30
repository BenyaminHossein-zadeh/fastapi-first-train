from fastapi import FastAPI, Path, Query, HTTPException, Form
from typing import Optional, List
import uuid
import uvicorn

app = FastAPI()

students = [
    {
        "id": str(uuid.uuid4()), 
        "name": "John",
        "age": 20,
        "class_year": "Year 12"
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Alex", 
        "age": 12,
        "class_year": "Year 6"
    }, 
    {
        "id": str(uuid.uuid4()),
        "name": "Mohammad", 
        "age": 30,
        "class_year": "Graduated" 
    }
]

@app.get("/")
def index():
    return {"message": "Welcome to the Student API"}

@app.get("/get-students")
def get_students():
    return students

@app.get("/get-students/{student_id}")
def get_student(student_id: str = Path(..., description="The UUID of the student", min_length=36, max_length=36)):
    for student in students:
        if student["id"] == student_id:
            return student
    raise HTTPException(status_code=404, detail=f"Student with ID {student_id} not found")

@app.post("/create-new-student")
def create_new_student(
    name: str = Form(..., min_length=1, max_length=100, description="Student name"),
    age: int = Form(..., ge=0, le=150, description="Student age"),
    class_year: str = Form(..., min_length=1, max_length=50, description="Student class year")
):
    new_student = {
        "id": str(uuid.uuid4()),
        "name": name.strip(),
        "age": age,
        "class_year": class_year.strip()
    }
    students.append(new_student)
    return new_student

@app.get("/get-filtered-students")
def get_filtered_students(
    name: Optional[str] = Query(None, description="Filter by student name (case-insensitive partial match)"),
    age_range: Optional[List[int]] = Query(None, description="Filter by age range [min_age, max_age], inclusive")
):
    result = students[:]
    if name:
        result = [s for s in result if name.lower() in s["name"].lower()]
    if age_range:
        if len(age_range) != 2 or age_range[0] > age_range[1]:
            raise HTTPException(400, "age_range must be [min, max] with min <= max")
        result = [s for s in result if age_range[0] <= s["age"] <= age_range[1]]
    return result

# For Vercel deployment
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)