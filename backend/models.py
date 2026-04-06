from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, DateTime, Time
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String)  # "admin" or "student"
    must_change_password = Column(Boolean, default=False)
    profile_picture = Column(String, nullable=True) # Base64 encoded string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    student_profile = relationship("Student", back_populates="user", uselist=False, cascade="all, delete-orphan", lazy="joined")

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    student_id_number = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    contact_email = Column(String)
    contact_phone = Column(String)
    program = Column(String)
    year_level = Column(String)
    status = Column(String, default="Active") # "Active" or "Inactive"
    user = relationship("User", back_populates="student_profile")
    assignments = relationship("Assignment", back_populates="student", cascade="all, delete-orphan", lazy="joined")

class ClinicalArea(Base):
    __tablename__ = "clinical_areas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    max_capacity = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    assignments = relationship("Assignment", back_populates="area", cascade="all, delete-orphan", lazy="joined")

class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    area_id = Column(Integer, ForeignKey("clinical_areas.id"))
    start_date = Column(Date)
    end_date = Column(Date)
    shift_start_time = Column(Time)
    shift_end_time = Column(Time)
    shift_type = Column(String) # Morning, Afternoon, Night
    status = Column(String, default="Active")
    date_assigned = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    student = relationship("Student", back_populates="assignments", lazy="joined")
    area = relationship("ClinicalArea", back_populates="assignments", lazy="joined")
    attendance_records = relationship("AttendanceRecord", back_populates="assignment", cascade="all, delete-orphan", lazy="joined")

class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"))
    date = Column(Date)
    actual_time_in = Column(Time, nullable=True)
    actual_time_out = Column(Time, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    assignment = relationship("Assignment", back_populates="attendance_records", lazy="joined")
