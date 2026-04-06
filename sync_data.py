
import sqlite3

def sync():
    conn = sqlite3.connect('clinical_rotation.db')
    cursor = conn.cursor()
    
    print("--- Database Sync & Cleanup ---")
    
    # 1. Find and delete assignments with no existing students
    cursor.execute("SELECT id, student_id FROM assignments")
    assignments = cursor.fetchall()
    for ass_id, stu_id in assignments:
        cursor.execute("SELECT id FROM students WHERE id = ?", (stu_id,))
        if not cursor.fetchone():
            print(f"Deleting orphaned assignment {ass_id} (Missing Student {stu_id})")
            cursor.execute("DELETE FROM assignments WHERE id = ?", (ass_id,))
            
    # 2. Find and delete assignments with no existing clinical areas
    cursor.execute("SELECT id, area_id FROM assignments")
    assignments = cursor.fetchall()
    for ass_id, area_id in assignments:
        cursor.execute("SELECT id FROM clinical_areas WHERE id = ?", (area_id,))
        if not cursor.fetchone():
            print(f"Deleting orphaned assignment {ass_id} (Missing Facility {area_id})")
            cursor.execute("DELETE FROM assignments WHERE id = ?", (ass_id,))
            
    # 3. Find and delete attendance records with no existing assignments
    cursor.execute("SELECT id, assignment_id FROM attendance_records")
    attends = cursor.fetchall()
    for att_id, ass_id in attends:
        cursor.execute("SELECT id FROM assignments WHERE id = ?", (ass_id,))
        if not cursor.fetchone():
            print(f"Deleting orphaned attendance {att_id} (Missing Assignment {ass_id})")
            cursor.execute("DELETE FROM attendance_records WHERE id = ?", (att_id,))
            
    # 4. Ensure all students have 'Active' status if None
    cursor.execute("UPDATE students SET status = 'Active' WHERE status IS NULL")
    
    conn.commit()
    conn.close()
    print("Sync complete!")

if __name__ == "__main__":
    sync()
