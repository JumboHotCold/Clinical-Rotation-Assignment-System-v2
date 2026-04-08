# Area Students Feature - Quick Start Testing Guide

## Prerequisites
- Backend running on `http://localhost:8000`
- Frontend running on `http://localhost:5173`
- Database populated with areas and student assignments

## Quick Start Steps

### 1. Start the Backend
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

### 2. Start the Frontend
```bash
cd frontend
npm install
npm run dev
```

### 3. Login as Admin
- **URL**: http://localhost:5173/login
- **Username**: `admin`
- **Password**: `admin123`

### 4. Test Admin Features

#### Access Area Assignments Tab
1. Navigate to Admin Dashboard
2. Look for the new "Area Assignments" tab (with Users icon)
3. Click to open the new tab

#### Expected Features in Admin View
- ✅ See all clinical areas
- ✅ View all students assigned to each area
- ✅ Students grouped by schedule (shift type, time, date)
- ✅ Click area to expand/collapse
- ✅ Click schedule to expand/collapse and see students
- ✅ See student details: name, ID, program, year level, contact info
- ✅ Search by student name, ID number, or area name
- ✅ Filter by area name, student name, or date
- ✅ Loading indicator while fetching data

#### Test Search Functionality
1. In the search box, type a student name (e.g., "Jane")
2. Results should filter in real-time
3. Try searching by student ID number (e.g., "C-2023")
4. Try searching by area name (e.g., "ER")

#### Test Filter Functionality
1. Select "Filter: By Area Name" from dropdown
2. Type area name in search box
3. Results show only matching areas
4. Try "Filter: By Student Name"
5. Try "Filter: By Date" and select a date


### 5. Test Student Features

#### Login as Student
1. Logout from Admin account
2. Login with student account:
   - **Username**: `C-2023-001`
   - **Password**: `password123`

#### Access Co-Students View
1. Navigate to Student Dashboard
2. In the "Active Assignments" section, look for "View Co-Students →" button
3. Click button to toggle to co-students view
4. Should show only the areas this student is assigned to
5. Click "← Back to Assignments" to return to assignments view

#### Expected Features in Student View
- ✅ See only their assigned areas (not other areas)
- ✅ See only schedules they're assigned to (not all schedules in area)
- ✅ See co-students in each schedule
- ✅ No access to other areas or schedules
- ✅ Full search and filter functionality available
- ✅ Same visual layout as admin view

#### Verify Permission Enforcement
1. Try accessing: `http://localhost:8000/docs#/areas/get_area_students_areas__area_id__students_get`
2. If logged in as student, can only access areas they're assigned to
3. If try to access unauthorized area ID, should get 403 Forbidden error


### 6. Test Edge Cases

#### Test with No Assignments
1. Create a new student account
2. Assign them to an area
3. Switch to that new student account
4. Should see the "View Co-Students" button
5. Should show their assigned area

#### Test with Multiple Assignments
1. Create a student assigned to multiple areas
2. Login as that student
3. Click "View Co-Students"
4. Should see all their assigned areas
5. Should see different co-students for each area/schedule

#### Test with Empty Search Results
1. Search for non-existent student name
2. Should show "No matching schedules found" message
3. Clear search to restore results


### 7. API Testing (Using Postman or curl)

#### Test Admin Access - Get All Students in Area 1
```bash
curl -X GET "http://localhost:8000/areas/1/students" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

Expected Response:
- ✅ Status 200
- ✅ JSON with area data and students grouped by schedule

#### Test Student Access - Get Co-Assignees
```bash
curl -X GET "http://localhost:8000/students/me/coassignees" \
  -H "Authorization: Bearer YOUR_STUDENT_TOKEN"
```

Expected Response:
- ✅ Status 200
- ✅ JSON with only student's assigned areas

#### Test Permission - Student accessing unauthorized area
```bash
curl -X GET "http://localhost:8000/areas/2/students" \
  -H "Authorization: Bearer STUDENT_TOKEN_WITHOUT_ASSIGNMENT"
```

Expected Response:
- ✅ Status 403
- ❌ Message: "You don't have access to this area"


### 8. Performance Testing

#### Test with Large Dataset
1. Create 50+ students
2. Assign them to 5+ areas across different schedules
3. Test page load time
4. Test search responsiveness
5. Verify data loads completely

#### Test Search Performance
1. Type in search box gradually (letter by letter)
2. Should see instant filtering without lag
3. No console errors for failed requests


### 9. Visual Testing

#### UI Elements Check
- ✅ Area cards display correctly
- ✅ Icons render properly
- ✅ Expandable sections work smoothly
- ✅ Colors match the system design (pink gradient)
- ✅ Student count badge shows correct numbers
- ✅ Status badges show Active/Inactive correctly
- ✅ Responsive layout on mobile devices

#### Cross-browser Testing
- Test on Chrome, Firefox, Safari, Edge
- Verify all features work consistently
- Check responsive design on mobile/tablet


### 10. Common Issues & Solutions

**Issue**: "No areas found" message
- **Solution**: Create areas first, then assign students to them

**Issue**: Students not appearing in area view
- **Solution**: Check that assignments are marked as "Active" in database

**Issue**: Search not working
- **Solution**: Check browser console for errors, refresh page

**Issue**: Permission denied error
- **Solution**: Verify student is actually assigned to the area they're trying to access

**Issue**: Slow page load
- **Solution**: Check database queries in backend logs, may need optimization


### 11. Success Criteria

Feature is complete when:
- ✅ Admin can view all students in all areas grouped by schedule
- ✅ Students can view only their assigned areas and co-students
- ✅ Search/filter works for all filter types
- ✅ UI is responsive and matches design
- ✅ No console errors or 404s in network tab
- ✅ Permission checks enforce role-based access
- ✅ Performance is acceptable with large datasets
- ✅ All backend endpoints return correct data format


## Rollback Instructions (If Needed)

If you need to remove these changes:

1. **Backend**:
   - Remove the two new functions from `crud.py`
   - Remove the new endpoint from `areas.py` and `students.py`
   - Remove the new schemas from `schemas.py`

2. **Frontend**:
   - Delete `AreaStudentsView.jsx` component file
   - Remove the import from `AdminDashboard.jsx`
   - Remove the new tab from Admin dashboard
   - Remove the import from `StudentDashboard.jsx`
   - Remove the toggle button and co-students view from Student dashboard

3. **Database**:
   - No schema changes needed (only uses existing tables)


## Documentation Files

- **Main Documentation**: `AREA_STUDENTS_FEATURE_IMPLEMENTATION.md`
- **Testing Guide**: This file
- **Code Changes Summary**:
  - Backend: 4 files modified
  - Frontend: 3 files modified (1 new component)
