import requests
import json
import sqlite3
import datetime

BASE_URL = "http://localhost:8001"

def test_full_cascade():
    print("--- Starting Full Cascade Diagnosis ---")
    
    # 1. Login
    login_data = {"username": "admin", "password": "admin123"}
    res = requests.post(f"{BASE_URL}/auth/token", json=login_data)
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Area
    area_res = requests.post(f"{BASE_URL}/areas/", json={"name": "TEST_AREA_CASCADE", "max_capacity": 5}, headers=headers)
    area = area_res.json()
    area_id = area["id"]
    print(f"Area Created (ID: {area_id})")

    # 3. Create Student
    student_res = requests.post(f"{BASE_URL}/students/", json={
        "student_id_number": "C-CASCADE-TEST",
        "first_name": "Cascade",
        "last_name": "Test",
        "contact_email": "cascade@test.com",
        "contact_phone": "123",
        "program": "BS Nursing",
        "year_level": "2nd Year"
    }, headers=headers)
    student = student_res.json()
    student_id = student["id"]
    print(f"Student Created (ID: {student_id})")

    # 4. Create Assignment
    assign_payload = {
        "student_id": student_id,
        "area_id": area_id,
        "start_date": str(datetime.date.today()),
        "end_date": str(datetime.date.today() + datetime.timedelta(days=7)),
        "shift_start_time": "08:00:00",
        "shift_end_time": "16:00:00",
        "shift_type": "Morning"
    }
    assign_res = requests.post(f"{BASE_URL}/assignments/", json=assign_payload, headers=headers)
    assign = assign_res.json()
    assign_id = assign["id"]
    print(f"Assignment Created (ID: {assign_id})")

    # 5. Create Attendance Record
    attendance_payload = {
        "assignment_id": assign_id,
        "date": str(datetime.date.today()),
        "actual_time_in": "08:05:00",
        "actual_time_out": "16:10:00"
    }
    # Note: Attendance records might need a different endpoint, checking main.py...
    # Looks like attendance has a router.
    attend_res = requests.post(f"{BASE_URL}/attendance/", json=attendance_payload, headers=headers)
    print(f"Attendance Record Created: {attend_res.status_code}")

    # 6. Attempt student deletion (should cascade!)
    print(f"Deleting Student {student_id}...")
    del_res = requests.delete(f"{BASE_URL}/students/{student_id}", headers=headers)
    print(f"Student Delete Response: {del_res.status_code} - {del_res.text}")

    # 7. Check DB for assignments and attendance of that student
    conn = sqlite3.connect("clinical_rotation.db")
    cursor = conn.cursor()
    a_count = cursor.execute("SELECT count(*) FROM assignments WHERE student_id = ?", (student_id,)).fetchone()[0]
    att_count = cursor.execute("SELECT count(*) FROM attendance_records WHERE assignment_id = ?", (assign_id,)).fetchone()[0]
    print(f"Orphaned Assignments in DB: {a_count}")
    print(f"Orphaned Attendance in DB: {att_count}")
    
    # 8. Attempt area deletion
    print(f"Deleting Area {area_id}...")
    del_res = requests.delete(f"{BASE_URL}/areas/{area_id}", headers=headers)
    print(f"Area Delete Response: {del_res.status_code} - {del_res.text}")

    conn.close()
    print("--- Full Cascade Diagnosis Complete ---")

if __name__ == "__main__":
    test_full_cascade()
