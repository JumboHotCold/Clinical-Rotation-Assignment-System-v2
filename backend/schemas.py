from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import date, datetime, time

class UserBase(BaseModel):
    username: str
    role: str

class UserCreate(UserBase):
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class User(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    must_change_password: bool
    profile_picture: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class UserProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    profile_picture: Optional[str] = None

class UserPasswordUpdate(BaseModel):
    current_password: str
    new_password: str

class StudentBase(BaseModel):
    student_id_number: str
    first_name: str
    last_name: str
    contact_email: str
    contact_phone: str
    program: str
    year_level: str
    status: str = "Active"

    @field_validator('student_id_number')
    @classmethod
    def id_must_start_with_c(cls, v: str) -> str:
        if not v.startswith('C-'):
            raise ValueError('Student ID must start with "C-"')
        return v

class StudentCreate(StudentBase):
    password: Optional[str] = "password123"

class StudentUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    program: Optional[str] = None
    year_level: Optional[str] = None
    status: Optional[str] = None

class Student(StudentBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ClinicalAreaBase(BaseModel):
    name: str
    max_capacity: int

class ClinicalAreaCreate(ClinicalAreaBase):
    pass

class ClinicalAreaUpdate(BaseModel):
    name: Optional[str] = None
    max_capacity: Optional[int] = None

class ClinicalArea(ClinicalAreaBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class AssignmentBase(BaseModel):
    student_id: int
    area_id: int
    start_date: date
    end_date: date
    shift_start_time: time
    shift_end_time: time
    shift_type: str
    status: str = "Active"

class AssignmentCreate(AssignmentBase):
    pass

class AssignmentUpdate(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    shift_start_time: Optional[time] = None
    shift_end_time: Optional[time] = None
    shift_type: Optional[str] = None
    status: Optional[str] = None

class Assignment(AssignmentBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    date_assigned: Optional[datetime] = None
    student: Optional[Student] = None
    area: Optional[ClinicalArea] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class AttendanceRecordBase(BaseModel):
    assignment_id: int
    date: date
    actual_time_in: Optional[time] = None
    actual_time_out: Optional[time] = None

class AttendanceRecordCreate(AttendanceRecordBase):
    pass

class AttendanceRecordUpdate(BaseModel):
    actual_time_in: Optional[time] = None
    actual_time_out: Optional[time] = None

class AttendanceRecord(AttendanceRecordBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    user_id: int
    must_change_password: bool
