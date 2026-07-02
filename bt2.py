from typing import Optional, List
from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field

app = FastAPI(title="Hệ thống Quản lý Học viên")

class StudentBase(BaseModel):
    code: str = Field(..., description="Mã học viên không được trùng")
    name: str = Field(..., min_length=1, description="Tên không được rỗng")
    email: str = Field(..., min_length=1, description="Email không được rỗng")
    age: int = Field(..., gt=0, description="Tuổi phải lớn hơn 0")

class StudentCreate(StudentBase):
    pass

class StudentUpdate(StudentBase):
    pass

class StudentResponse(StudentBase):
    id: int

students = [
    {"id": 1, "code": "SV001", "name": "Nguyen Van A", "email": "a@gmail.com", "age": 20},
    {"id": 2, "code": "SV002", "name": "Tran Thi B", "email": "b@gmail.com", "age": 22},
    {"id": 3, "code": "SV003", "name": "Le Van C", "email": "c@gmail.com", "age": 18}
]

current_id = 3

@app.get("/students", response_model=List[StudentResponse])
def get_students(
    keyword: Optional[str] = Query(None, description="Tìm theo name, code hoặc email"),
    min_age: Optional[int] = Query(None, description="Tuổi tối thiểu"),
    max_age: Optional[int] = Query(None, description="Tuổi tối đa")
):
    filtered_students = students.copy()
    if keyword:
        kw = keyword.lower()
        filtered_students = [student for student in filtered_students if kw in student["name"].lower() or kw in student["code"].lower() or kw in student["email"].lower()]
    if min_age is not None:
        filtered_students = [student for student in filtered_students if student["age"] >= min_age]
    if max_age is not None:
        filtered_students = [student for student in filtered_students if student["age"] <= max_age]
    return filtered_students
@app.get("/students/{student_id}", response_model=StudentResponse)
def get_student(student_id: int):
    for student in students:
        if student["id"] == student_id:
            return student
    raise HTTPException(status_code=404, detail="Student not found")
@app.post("/students", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(student_data: StudentCreate):
    global current_id
    for s in students:
        if s["code"] == student_data.code:
            raise HTTPException(status_code=400, detail="Mã học viên (code) đã tồn tại.")
    current_id += 1
    new_student = student_data.model_dump()
    new_student["id"] = current_id
    students.append(new_student)
    return new_student
@app.put("/students/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, student_data: StudentUpdate):
    student_index = -1
    for idx, s in enumerate(students):
        if s["id"] == student_id:
            student_index = idx
            break     
    if student_index == -1:
        raise HTTPException(status_code=404, detail="Student not found")
    for s in students:
        if s["code"] == student_data.code and s["id"] != student_id:
            raise HTTPException(status_code=400, detail="Mã học viên (code) đã tồn tại ở học viên khác.")
    updated_student = student_data.model_dump()
    updated_student["id"] = student_id
    students[student_index] = updated_student
    return updated_student
@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    for idx, s in enumerate(students):
        if s["id"] == student_id:
            students.pop(idx)
            return {"message": f"Xóa thành công học viên có ID {student_id}"}
    raise HTTPException(status_code=404, detail="Student not found")