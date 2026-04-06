#!/usr/bin/env python3
"""Test deletion functionality after fix"""

import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8001"

def log(msg, status="INFO"):
    print(f"[{status:^8}] {msg}")

try:
    # Step 1: Get auth token
    log("Testing login with admin credentials...")
    response = requests.post(
        f'{BASE_URL}/auth/token',
        json={'username': 'admin', 'password': 'admin123'},
        timeout=5
    )
    response.raise_for_status()
    token = response.json()['access_token']
    log("✓ Login successful - token obtained", "SUCCESS")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Step 2: Create a test student
    log("Creating test student...")
    student_data = {
        "student_id_number": "C-TEST-DEL-001",
        "first_name": "DeleteTest",
        "last_name": "Student",
        "contact_email": "delete.test@example.com",
        "contact_phone": "555-1234",
        "program": "BS Nursing",
        "year_level": "2nd Year"
    }
    
    student_res = requests.post(
        f'{BASE_URL}/students/',
        json=student_data,
        headers=headers,
        timeout=5
    )
    student_res.raise_for_status()
    student = student_res.json()
    student_id = student['id']
    log(f"✓ Test student created (ID: {student_id})", "SUCCESS")
    
    # Step 3: Delete the test student
    log(f"Attempting to delete student ID {student_id}...")
    delete_res = requests.delete(
        f'{BASE_URL}/students/{student_id}',
        headers=headers,
        timeout=5
    )
    delete_res.raise_for_status()
    log(f"✓ Student deletion successful", "SUCCESS")
    
    # Step 4: Verify student is deleted (should get 404)
    log("Verifying student is deleted...")
    verify_res = requests.get(
        f'{BASE_URL}/students/',
        headers=headers,
        timeout=5
    )
    verify_res.raise_for_status()
    students = verify_res.json()
    found = any(s['id'] == student_id for s in students)
    if not found:
        log("✓ Verified: Student successfully removed from database", "SUCCESS")
    else:
        log("✗ ERROR: Student still exists in database!", "ERROR")
    
    # Step 5: Create a test clinical area
    log("Creating test clinical area...")
    area_data = {
        "name": "TEST-DELETE-AREA",
        "max_capacity": 5
    }
    
    area_res = requests.post(
        f'{BASE_URL}/areas/',
        json=area_data,
        headers=headers,
        timeout=5
    )
    area_res.raise_for_status()
    area = area_res.json()
    area_id = area['id']
    log(f"✓ Test clinical area created (ID: {area_id})", "SUCCESS")
    
    # Step 6: Delete the test clinical area
    log(f"Attempting to delete clinical area ID {area_id}...")
    delete_area_res = requests.delete(
        f'{BASE_URL}/areas/{area_id}',
        headers=headers,
        timeout=5
    )
    delete_area_res.raise_for_status()
    log(f"✓ Clinical area deletion successful", "SUCCESS")
    
    # Step 7: Verify area is deleted
    log("Verifying clinical area is deleted...")
    verify_area_res = requests.get(
        f'{BASE_URL}/areas/',
        headers=headers,
        timeout=5
    )
    verify_area_res.raise_for_status()
    areas = verify_area_res.json()
    found = any(a['id'] == area_id for a in areas)
    if not found:
        log("✓ Verified: Clinical area successfully removed from database", "SUCCESS")
    else:
        log("✗ ERROR: Clinical area still exists in database!", "ERROR")
    
    log("\n" + "="*50)
    log("ALL TESTS PASSED ✓", "SUCCESS")
    log("="*50)
    
except requests.exceptions.ConnectionError:
    log("✗ Cannot connect to backend. Is the server running on port 8001?", "ERROR")
except requests.exceptions.HTTPError as e:
    log(f"✗ HTTP Error: {e.response.status_code} - {e.response.text}", "ERROR")
except Exception as e:
    log(f"✗ Error: {str(e)}", "ERROR")
