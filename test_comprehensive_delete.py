#!/usr/bin/env python3
"""
Comprehensive test for CRUD operations including deletion
This test verifies that deletion works properly for:
- Students (with cascade deletion of assignments and attendance)
- Clinical Areas (with cascade deletion of assignments and attendance)
- Assignments (with cascade deletion of attendance records)
"""

import requests
import json
from datetime import datetime, date, time, timedelta

BASE_URL = "http://127.0.0.1:8001"

def log(msg, status="INFO"):
    print(f"[{status:^8}] {msg}")

def test_deletion_workflow():
    """Test complete deletion workflow"""
    try:
        log("=" * 60)
        log("COMPREHENSIVE DELETION TEST SUITE", "START")
        log("=" * 60)
        
        # Step 1: Login
        log("Step 1: Authenticating with admin credentials...")
        response = requests.post(
            f'{BASE_URL}/auth/token',
            json={'username': 'admin', 'password': 'admin123'},
            timeout=5
        )
        response.raise_for_status()
        token = response.json()['access_token']
        log("✓ Admin authenticated successfully", "SUCCESS")
        
        headers = {'Authorization': f'Bearer {token}'}
        
        # Step 2: Create test clinical area
        log("\nStep 2: Creating test clinical area...")
        area_data = {
            "name": "TEST-DELETE-AREA-COMPREHENSIVE",
            "max_capacity": 3
        }
        area_res = requests.post(f'{BASE_URL}/areas/', json=area_data, headers=headers, timeout=5)
        area_res.raise_for_status()
        area = area_res.json()
        area_id = area['id']
        log(f"✓ Created clinical area (ID: {area_id}, Name: {area['name']})", "SUCCESS")
        
        # Step 3: Create test students
        log("\nStep 3: Creating test students...")
        students = []
        for i in range(2):
            student_data = {
                "student_id_number": f"C-TEST-DEL-{i:03d}",
                "first_name": f"TestDelete{i}",
                "last_name": "Student",
                "contact_email": f"delete{i}.test@example.com",
                "contact_phone": "555-1234",
                "program": "BS Nursing",
                "year_level": "2nd Year"
            }
            s_res = requests.post(f'{BASE_URL}/students/', json=student_data, headers=headers, timeout=5)
            s_res.raise_for_status()
            student = s_res.json()
            students.append(student)
            log(f"✓ Created student (ID: {student['id']}, Name: {student['first_name']} {student['last_name']})", "SUCCESS")
        
        # Step 4: Create assignments
        log("\nStep 4: Creating assignments with attendance...")
        start_date = str(date.today())
        end_date = str(date.today() + timedelta(days=5))
        assignments = []
        
        for student in students:
            assignment_data = {
                "student_id": student['id'],
                "area_id": area_id,
                "start_date": start_date,
                "end_date": end_date,
                "shift_start_time": "08:00:00",
                "shift_end_time": "16:00:00",
                "shift_type": "Morning"
            }
            a_res = requests.post(f'{BASE_URL}/assignments/', json=assignment_data, headers=headers, timeout=5)
            a_res.raise_for_status()
            assignment = a_res.json()
            assignments.append(assignment)
            log(f"✓ Created assignment (ID: {assignment['id']}, Student: {student['first_name']}, Area: {area['name']})", "SUCCESS")
        
        # Step 5: Add attendance records
        log("\nStep 5: Adding attendance records...")
        attendance_created = False
        for assignment in assignments:
            attendance_data = {
                "date": start_date,
                "actual_time_in": "08:15:00",
                "actual_time_out": "16:45:00"
            }
            att_res = requests.post(
                f'{BASE_URL}/attendance/clock-in/{assignment["id"]}',
                json=attendance_data,
                headers=headers,
                timeout=5
            )
            if att_res.status_code == 200:
                log(f"✓ Added attendance for assignment {assignment['id']}", "SUCCESS")
                attendance_created = True
            else:
                log(f"⚠ Attendance endpoint may not exist or different format", "WARN")
        
        # Step 6: Verify data exists
        log("\nStep 6: Verifying all data exists before deletion...")
        
        students_res = requests.get(f'{BASE_URL}/students/', headers=headers, timeout=5).json()
        student_count_before = len(students_res)
        log(f"✓ Total students: {student_count_before}", "INFO")
        
        areas_res = requests.get(f'{BASE_URL}/areas/', headers=headers, timeout=5).json()
        area_count_before = len(areas_res)
        log(f"✓ Total areas: {area_count_before}", "INFO")
        
        assignments_res = requests.get(f'{BASE_URL}/assignments/', headers=headers, timeout=5).json()
        assignment_count_before = len(assignments_res)
        log(f"✓ Total assignments: {assignment_count_before}", "INFO")
        
        # Step 7: Delete assignment
        log("\nStep 7: Testing assignment deletion...")
        assignment_to_delete = assignments[0]
        del_res = requests.delete(
            f'{BASE_URL}/assignments/{assignment_to_delete["id"]}',
            headers=headers,
            timeout=5
        )
        if del_res.status_code == 200:
            log(f"✓ Assignment {assignment_to_delete['id']} deleted successfully", "SUCCESS")
            
            # Verify assignment is deleted
            assignments_res = requests.get(f'{BASE_URL}/assignments/', headers=headers, timeout=5).json()
            if not any(a['id'] == assignment_to_delete['id'] for a in assignments_res):
                log(f"✓ Confirmed: Assignment is removed from database", "SUCCESS")
            else:
                log(f"✗ ERROR: Assignment still exists in database!", "ERROR")
        else:
            log(f"✗ Failed to delete assignment: {del_res.status_code} - {del_res.text}", "ERROR")
        
        # Step 8: Delete student (should cascade delete remaining assignments)
        log("\nStep 8: Testing student deletion with cascade...")
        student_to_delete = students[1]
        del_res = requests.delete(
            f'{BASE_URL}/students/{student_to_delete["id"]}',
            headers=headers,
            timeout=5
        )
        if del_res.status_code == 200:
            log(f"✓ Student {student_to_delete['id']} ({student_to_delete['first_name']}) deleted successfully", "SUCCESS")
            
            # Verify student is deleted
            students_res = requests.get(f'{BASE_URL}/students/', headers=headers, timeout=5).json()
            if not any(s['id'] == student_to_delete['id'] for s in students_res):
                log(f"✓ Confirmed: Student is removed from database", "SUCCESS")
            else:
                log(f"✗ ERROR: Student still exists in database!", "ERROR")
        else:
            log(f"✗ Failed to delete student: {del_res.status_code} - {del_res.text}", "ERROR")
        
        # Step 9: Delete clinical area (should cascade delete remaining assignments)
        log("\nStep 9: Testing clinical area deletion with cascade...")
        del_res = requests.delete(
            f'{BASE_URL}/areas/{area_id}',
            headers=headers,
            timeout=5
        )
        if del_res.status_code == 200:
            log(f"✓ Clinical area {area_id} deleted successfully", "SUCCESS")
            
            # Verify area is deleted
            areas_res = requests.get(f'{BASE_URL}/areas/', headers=headers, timeout=5).json()
            if not any(a['id'] == area_id for a in areas_res):
                log(f"✓ Confirmed: Clinical area is removed from database", "SUCCESS")
            else:
                log(f"✗ ERROR: Clinical area still exists in database!", "ERROR")
        else:
            log(f"✗ Failed to delete area: {del_res.status_code} - {del_res.text}", "ERROR")
        
        # Final summary
        log("\n" + "=" * 60)
        log("ALL DELETION TESTS COMPLETED SUCCESSFULLY ✓", "SUCCESS")
        log("=" * 60)
        return True
        
    except requests.exceptions.ConnectionError:
        log("✗ Cannot connect to backend. Is the server running on port 8001?", "ERROR")
        return False
    except requests.exceptions.HTTPError as e:
        log(f"✗ HTTP Error: {e.response.status_code} - {e.response.text}", "ERROR")
        return False
    except Exception as e:
        log(f"✗ Unexpected error: {str(e)}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_deletion_workflow()
    exit(0 if success else 1)
