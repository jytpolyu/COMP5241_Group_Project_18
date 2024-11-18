# Project Testing Documentation

## Overview
This document outlines the testing strategy for the project, including test cases for major functionalities, expected results, and setup instructions.

## Prerequisites
1. MySQL database set up with the provided schema and test data (`sql` file).
2. Python environment with required dependencies installed (`requirements.txt`).
3. Flask application running in development mode.

---

## Testing Categories

### 1. User Management
#### 1.1 Login
- **Test Case**: Valid login credentials for both teacher and student roles.
  - **Input**: Username, Password, Role.
  - **Expected Result**: Redirect to the dashboard based on the role.
- **Test Case**: Invalid login credentials.
  - **Input**: Incorrect Username/Password/Role.
  - **Expected Result**: Error message displayed on the login page.

#### 1.2 Logout
- **Test Case**: User logs out after login.
  - **Expected Result**: Session cleared, redirect to login page.

---

### 2. Dashboard Management
#### 2.1 Teacher Dashboard
- **Test Case**: Load teacher dashboard.
  - **Expected Result**: List of assignments displayed.
- **Test Case**: Fetch dashboard data for a specific assignment.
  - **Input**: Assignment ID.
  - **Expected Result**: Assignment progress and group details as JSON.

#### 2.2 Student Dashboard
- **Test Case**: Access student-specific dashboard.
  - **Expected Result**: Redirect to the student view with relevant information displayed.

---

### 3. Group and Student Management
#### 3.1 Group Details
- **Test Case**: Search for group activities based on `group_id` and `activity_type`.
  - **Input**: Group ID and Activity Type.
  - **Expected Result**: Matching group activity records displayed as JSON.

#### 3.2 Student Details
- **Test Case**: Search for student activities based on `student_id` and `activity_type`.
  - **Input**: Student ID and Activity Type.
  - **Expected Result**: Matching student activity records displayed as JSON.

---

### 4. AI Grading
#### 4.1 Grading Page
- **Test Case**: Access AI grading page.
  - **Expected Result**: Grading interface loaded with fields for Student ID input.

#### 4.2 Grade and Feedback Generation
- **Test Case**: Submit a valid `student_id` for grading.
  - **Input**: Student ID.
  - **Expected Result**: 
    - Grade displayed.
    - Issues identified.
    - Study plan generated.
    - Suggestions provided.
- **Test Case**: Export feedback as PDF.
  - **Expected Result**: PDF file generated with all feedback.

---

### 5. Activity and Contribution Analysis
#### 5.1 Activity Details
- **Test Case**: Fetch activity details for a specific group or student.
  - **Input**: Group ID or Student ID.
  - **Expected Result**: JSON data with activity records.

#### 5.2 Contribution Summary
- **Test Case**: Retrieve contribution percentage for group members.
  - **Input**: Assignment ID.
  - **Expected Result**: Contribution details with percentages.

---

### 6. API Integration
#### 6.1 GPT-4 API
- **Test Case**: Submit a grading request with activity data.
  - **Input**: Prompt including student activities.
  - **Expected Result**: Response with grading and feedback.

#### 6.2 GitHub Data Simulation
- **Test Case**: Generate and fetch simulated GitHub activity data.
  - **Expected Result**: Activity records created and stored in the database.

---

## Testing Tools
1. **Postman**: For testing API endpoints.
2. **Browser**: For testing web interfaces.
3. **MySQL Workbench**: For verifying database entries.

---

## Test Environment
- **OS**: macOS/Linux/Windows
- **Python**: 3.8 or later
- **Database**: MySQL 8.0 or later
- **Browser**: Latest version of Chrome/Firefox

---

## Test Execution
### Steps
1. Start the Flask server.
2. Test each endpoint using the specified inputs and compare the results with expected outputs.
3. Verify database integrity for all operations.
4. Document any bugs or issues found during testing.

---

## Expected Deliverables
1. List of test cases executed with results (pass/fail).
2. Bug report with steps to reproduce and logs.
3. Summary of testing coverage and final status.
