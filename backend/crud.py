from sqlalchemy.orm import Session, joinedload
from . import models, schemas
from passlib.context import CryptContext
import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user_by_identifier(db: Session, identifier: str):
    # Check if identifier is student_id (username) OR contact_email
    user = db.query(models.User).filter(models.User.username == identifier).first()
    if not user:
        # Check if it matches an email in student profiles
        student = db.query(models.Student).filter(models.Student.contact_email == identifier).first()
        if student:
            user = db.query(models.User).filter(models.User.id == student.user_id).first()
    return user

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

# --- Students ---

def get_students(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Student).options(
        joinedload(models.Student.user),
        joinedload(models.Student.assignments)
    ).offset(skip).limit(limit).all()

def create_student(db: Session, student: schemas.StudentCreate):
    password_to_hash = student.password or "password123"
    hashed_password = get_password_hash(password_to_hash)
    username = student.student_id_number
    
    try:
        # Create User
        db_user = models.User(username=username, hashed_password=hashed_password, role="student", must_change_password=True)
        db.add(db_user)
        db.flush() # Get user ID without committing

        # Create Student Profile
        db_student = models.Student(
            user_id=db_user.id,
            student_id_number=student.student_id_number,
            first_name=student.first_name,
            last_name=student.last_name,
            contact_email=student.contact_email,
            contact_phone=student.contact_phone,
            program=student.program,
            year_level=student.year_level,
            status=student.status
        )
        db.add(db_student)
        db.commit()
        db.refresh(db_student)
        return db_student
    except Exception as e:
        db.rollback()
        raise e

def update_student(db: Session, student_id: int, updates: schemas.StudentUpdate):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student: return None
    update_data = updates.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(student, key, value)
    db.commit()
    db.refresh(student)
    return student

def delete_student(db: Session, student_id: int):
    """
    Delete a student and cascade delete all related records.
    - Deletes the student profile
    - Deletes all assignments for this student (which cascades to attendance records)
    - Deletes the associated user account
    """
    try:
        student = db.query(models.Student).filter(models.Student.id == student_id).first()
        if not student:
            return False
        
        # Get user_id before deleting student (we'll need it to delete the user)
        user_id = student.user_id
        
        # Delete the student profile - this will cascade delete assignments and attendance records
        # due to cascade="all, delete-orphan" on the Student.assignments relationship
        db.delete(student)
        db.flush()  # Ensure cascade operations are executed
        
        # Now delete the associated user account
        if user_id:
            user = db.query(models.User).filter(models.User.id == user_id).first()
            if user:
                db.delete(user)
        
        # Commit all changes
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error deleting student: {e}")
        return False

# --- User Profile & Security ---

def update_user_password(db: Session, user_id: int, new_password: str):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user: return None
    user.hashed_password = get_password_hash(new_password)
    user.must_change_password = False
    db.commit()
    db.refresh(user)
    return user

def update_user_profile(db: Session, user_id: int, updates: schemas.UserProfileUpdate):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user: return None
    
    # Update User-level fields (Profile Picture)
    if updates.profile_picture is not None:
        user.profile_picture = updates.profile_picture
    
    # Update Student-level fields if this user has a student profile
    student = db.query(models.Student).filter(models.Student.user_id == user_id).first()
    if student:
        if updates.first_name: student.first_name = updates.first_name
        if updates.last_name: student.last_name = updates.last_name
        if updates.contact_email: student.contact_email = updates.contact_email
        if updates.contact_phone: student.contact_phone = updates.contact_phone
    
    db.commit()
    db.refresh(user)
    return user

# --- Clinical Areas ---

def get_clinical_areas(db: Session):
    return db.query(models.ClinicalArea).all()

def create_clinical_area(db: Session, area: schemas.ClinicalAreaCreate):
    db_area = models.ClinicalArea(**area.model_dump())
    db.add(db_area)
    db.commit()
    db.refresh(db_area)
    return db_area

def update_clinical_area(db: Session, area_id: int, updates: schemas.ClinicalAreaUpdate):
    area = db.query(models.ClinicalArea).filter(models.ClinicalArea.id == area_id).first()
    if not area: return None
    update_data = updates.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(area, key, value)
    db.commit()
    db.refresh(area)
    return area

def delete_clinical_area(db: Session, area_id: int):
    """
    Delete a clinical area and cascade delete all related records.
    - Deletes the clinical area
    - Deletes all assignments for this area (which cascades to attendance records)
    due to cascade="all, delete-orphan" on the ClinicalArea.assignments relationship
    """
    try:
        area = db.query(models.ClinicalArea).filter(models.ClinicalArea.id == area_id).first()
        if not area:
            return False
        
        # Delete the area - this will cascade delete assignments and their attendance records
        # due to cascade="all, delete-orphan" on the ClinicalArea.assignments relationship
        db.delete(area)
        db.flush()  # Ensure cascade operations are executed
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error deleting clinical area: {e}")
        return False

# --- Assignments ---

def get_assignments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Assignment).options(
        joinedload(models.Assignment.student),
        joinedload(models.Assignment.area)
    ).offset(skip).limit(limit).all()

def check_assignment_conflicts(db: Session, assignment: schemas.AssignmentCreate, exclude_id: int = None):
    # Rule 1: Student overlap check
    # Also considering shift times for precise overlap
    query = db.query(models.Assignment).filter(
        models.Assignment.student_id == assignment.student_id,
        models.Assignment.start_date <= assignment.end_date,
        models.Assignment.end_date >= assignment.start_date
    )
    
    # Check if student is active
    student = db.query(models.Student).filter(models.Student.id == assignment.student_id).first()
    if student and student.status == "Inactive":
        return {"conflict": True, "message": "Cannot assign an Inactive student to a rotation."}
    if exclude_id:
        query = query.filter(models.Assignment.id != exclude_id)
        
    overlapping_dates = query.all()
    
    # Check if there is an actual time overlap
    for existing in overlapping_dates:
        # If dates overlap, check times
        if (assignment.shift_start_time <= existing.shift_end_time and 
            assignment.shift_end_time >= existing.shift_start_time):
            return {"conflict": True, "message": f"Student has conflicting shift on those dates."}

    # Rule 2: Area capacity check
    area = db.query(models.ClinicalArea).filter(models.ClinicalArea.id == assignment.area_id).first()
    if not area:
        return {"conflict": True, "message": "Clinical area not found."}

    delta = assignment.end_date - assignment.start_date
    for i in range(delta.days + 1):
        day = assignment.start_date + datetime.timedelta(days=i)
        
        # Count assignments that overlap dates AND times on this specific day
        count_on_day = 0
        q2 = db.query(models.Assignment).filter(
            models.Assignment.area_id == assignment.area_id,
            models.Assignment.start_date <= day,
            models.Assignment.end_date >= day
        )
        if exclude_id:
            q2 = q2.filter(models.Assignment.id != exclude_id)
            
        for a in q2.all():
            if (assignment.shift_start_time <= a.shift_end_time and assignment.shift_end_time >= a.shift_start_time):
                count_on_day += 1

        if count_on_day >= area.max_capacity:
            return {"conflict": True, "message": f"Capacity reached for '{area.name}' on {day} during that shift."}

    return {"conflict": False, "message": "Valid"}

def create_assignment(db: Session, assignment: schemas.AssignmentCreate):
    db_assignment = models.Assignment(**assignment.model_dump())
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment

def update_assignment(db: Session, assignment_id: int, updates: schemas.AssignmentUpdate):
    assignment = db.query(models.Assignment).filter(models.Assignment.id == assignment_id).first()
    if not assignment: return None
    update_data = updates.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(assignment, key, value)
    db.commit()
    db.refresh(assignment)
    return assignment

def delete_assignment(db: Session, assignment_id: int):
    """
    Delete an assignment and cascade delete all related attendance records.
    """
    try:
        assignment = db.query(models.Assignment).filter(models.Assignment.id == assignment_id).first()
        if not assignment:
            return False
        
        # Delete the assignment - this will cascade delete attendance records
        # due to cascade="all, delete-orphan" on the Assignment.attendance_records relationship
        db.delete(assignment)
        db.flush()  # Ensure cascade operations are executed
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error deleting assignment: {e}")
        return False

# --- Attendance / Clocking ---

def get_attendance_records(db: Session, student_id: int = None):
    query = db.query(models.AttendanceRecord).options(
        joinedload(models.AttendanceRecord.assignment).joinedload(models.Assignment.student),
        joinedload(models.AttendanceRecord.assignment).joinedload(models.Assignment.area)
    )
    if student_id:
        query = query.join(models.Assignment).filter(models.Assignment.student_id == student_id)
    return query.all()

def clock_in(db: Session, assignment_id: int, date_val: datetime.date, time_in: datetime.time):
    # Check if a record already exists
    record = db.query(models.AttendanceRecord).filter(
        models.AttendanceRecord.assignment_id == assignment_id,
        models.AttendanceRecord.date == date_val
    ).first()
    
    if record:
        record.actual_time_in = time_in
        db.commit()
        db.refresh(record)
        return record
        
    new_record = models.AttendanceRecord(
        assignment_id=assignment_id,
        date=date_val,
        actual_time_in=time_in
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record

def clock_out(db: Session, assignment_id: int, date_val: datetime.date, time_out: datetime.time):
    record = db.query(models.AttendanceRecord).filter(
        models.AttendanceRecord.assignment_id == assignment_id,
        models.AttendanceRecord.date == date_val
    ).first()
    
    if not record:
        # If they forgot to clock in, we create a record with just time_out
        record = models.AttendanceRecord(
            assignment_id=assignment_id,
            date=date_val,
            actual_time_out=time_out
        )
        db.add(record)
    else:
        record.actual_time_out = time_out
        
    db.commit()
    db.refresh(record)
    return record

# --- Area Students & Schedules ---

def get_students_by_area(db: Session, area_id: int):
    """
    Get all students assigned to a specific area, grouped by their schedule.
    Returns AreaStudentsSchedule with students grouped by shift time.
    """
    # Get the area
    area = db.query(models.ClinicalArea).filter(models.ClinicalArea.id == area_id).first()
    if not area:
        return None
    
    # Get all active assignments for this area
    assignments = db.query(models.Assignment).options(
        joinedload(models.Assignment.student).joinedload(models.Student.user),
        joinedload(models.Assignment.area)
    ).filter(
        models.Assignment.area_id == area_id,
        models.Assignment.status == "Active"
    ).all()
    
    # Group assignments by schedule (shift_type, start_time, end_time, start_date, end_date)
    schedule_groups = {}
    
    for assignment in assignments:
        # Create a key for the schedule
        schedule_key = (
            assignment.shift_type,
            str(assignment.shift_start_time),
            str(assignment.shift_end_time),
            str(assignment.start_date),
            str(assignment.end_date)
        )
        
        if schedule_key not in schedule_groups:
            schedule_groups[schedule_key] = {
                'shift_type': assignment.shift_type,
                'shift_start_time': assignment.shift_start_time,
                'shift_end_time': assignment.shift_end_time,
                'start_date': assignment.start_date,
                'end_date': assignment.end_date,
                'students': []
            }
        
        # Add student info to this schedule
        student_info = {
            'id': assignment.student.id,
            'first_name': assignment.student.first_name,
            'last_name': assignment.student.last_name,
            'student_id_number': assignment.student.student_id_number,
            'program': assignment.student.program,
            'year_level': assignment.student.year_level,
            'contact_email': assignment.student.contact_email,
            'contact_phone': assignment.student.contact_phone,
            'assignment_id': assignment.id,
            'start_date': assignment.start_date,
            'end_date': assignment.end_date,
            'shift_start_time': assignment.shift_start_time,
            'shift_end_time': assignment.shift_end_time,
            'shift_type': assignment.shift_type,
            'status': assignment.status
        }
        schedule_groups[schedule_key]['students'].append(student_info)
    
    # Convert to list of ScheduleGroup objects
    schedules = list(schedule_groups.values())
    
    # Sort schedules by start_date and then by shift_start_time
    schedules.sort(key=lambda x: (x['start_date'], x['shift_start_time']))
    
    return {
        'area_id': area.id,
        'area_name': area.name,
        'max_capacity': area.max_capacity,
        'schedules': schedules
    }

def get_student_coassignees(db: Session, student_id: int):
    """
    Get all areas where a student is assigned and their co-students for each area/schedule.
    Returns a list of AreaStudentsSchedule objects filtered to only show the student's assignments and co-students.
    """
    # Get all active assignments for this student
    student_assignments = db.query(models.Assignment).options(
        joinedload(models.Assignment.area),
        joinedload(models.Assignment.student)
    ).filter(
        models.Assignment.student_id == student_id,
        models.Assignment.status == "Active"
    ).all()
    
    if not student_assignments:
        return []
    
    result = []
    
    # For each assignment area, get all co-students
    for assignment in student_assignments:
        area_id = assignment.area_id
        
        # Check if we already processed this area
        area_exists = any(r['area_id'] == area_id for r in result)
        if area_exists:
            continue
        
        # Get the full area data with all students
        area_data = get_students_by_area(db, area_id)
        
        if area_data:
            # Filter schedules to only include ones where this student is assigned
            filtered_schedules = []
            
            for schedule in area_data['schedules']:
                # Check if this student is in this schedule
                student_in_schedule = any(s['id'] == student_id for s in schedule['students'])
                
                if student_in_schedule:
                    filtered_schedules.append(schedule)
            
            area_data['schedules'] = filtered_schedules
            result.append(area_data)
    
    return result
