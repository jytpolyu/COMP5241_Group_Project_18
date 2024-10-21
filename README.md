# COMP5241_Group_Project_18
## Information
Group members:  
Xiaodong Lin  
Zhenwei Zhou  
Yutong Jiang  
Lan Luo  
Yuhao Bao  


### Development Documentation

#### Project Overview

This project is a Flask-based web application designed to help teachers manage student and group activities and grade students using the GPT-4 API. The application includes the following main features:

1. User login and role management
2. Student and group activity management
3. Grading students using the GPT-4 API

#### Environment Setup

1. **Install Dependencies**:
   ```shell
   pip install flask pymysql pandas requests mysql-connector-python
   ```

2. **Database Configuration**:
   Ensure that the MySQL database is configured and includes the following tables:
   - `users`
   - `activities`
   - `project_groups`
   - `group_members`

3. **API Credentials**:
   Create a `credentials.json` file in the project root directory with the following content:
   ```json
   {
       "api_key": "your_api_key_here"
   }
   ```

#### Project Structure

```
project/
│
├── app.py
├── credentials.json
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── teacher_student.html
│   ├── teacher_group.html
│   ├── teacher_ai.html
│   └── student.html
└── static/
    └── style.css
```

#### API Endpoints

##### User Login

- **URL**: `/login`
- **Method**: `GET`, `POST`
- **Description**: User login page supporting both teacher and student roles.

##### Student Management

- **URL**: `/teacher/student`
- **Method**: `GET`
- **Description**: Displays all student activity data with frontend pagination.

- **URL**: `/teacher/student/search`
- **Method**: `GET`
- **Parameters**:
  - `search_term`: Student ID search keyword
  - `activity_type`: Activity type
- **Description**: Searches for student activity data based on search criteria.

##### Group Management

- **URL**: `/teacher/group`
- **Method**: `GET`
- **Description**: Displays all group activity data with frontend pagination.

- **URL**: `/teacher/group/search`
- **Method**: `GET`
- **Parameters**:
  - `search_term`: Group ID search keyword
  - `activity_type`: Activity type
- **Description**: Searches for group activity data based on search criteria.

- **URL**: `/teacher/group/info`
- **Method**: `GET`
- **Description**: Retrieves group leader and member information.

##### AI Grading

- **URL**: `/teacher/ai`
- **Method**: `GET`
- **Description**: Displays the AI grading page.

- **URL**: `/ask_gpt4`
- **Method**: `POST`
- **Parameters**:
  - `student_id`: Student ID
- **Description**: Retrieves activity data for the specified student and grades them using the GPT-4 API.

#### Database Query Example

Retrieve group leader and member information:
```sql
SELECT 
    g.group_id, 
    u1.username AS leader_name, 
    GROUP_CONCAT(u2.username SEPARATOR ', ') AS member_names
FROM 
    project_groups g
JOIN 
    users u1 ON g.leader_id = u1.user_id
JOIN 
    group_members gm ON g.group_id = gm.group_id
JOIN 
    users u2 ON gm.student_id = u2.user_id
GROUP BY 
    g.group_id, u1.username;
```

#### Frontend Pagination Example

Implement frontend pagination in `teacher_student.html` and `teacher_group.html`:
```javascript
function updateTableAndPagination(data) {
    var tableBody = document.getElementById('tableBody');
    tableBody.innerHTML = '';
    var totalPages = Math.ceil(data.length / perPage);
    var currentPage = 1;

    function renderTable(page) {
        tableBody.innerHTML = '';
        var start = (page - 1) * perPage;
        var end = start + perPage;
        var pageData = data.slice(start, end);

        pageData.forEach(function(item) {
            var tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${item.id}</td>
                <td>${item.type}</td>
                <td>${item.count}</td>
            `;
            tableBody.appendChild(tr);
        });
    }

    function renderPagination() {
        var pagination = document.getElementById('pagination');
        pagination.innerHTML = '';

        for (var i = 1; i <= totalPages; i++) {
            var li = document.createElement('li');
            li.classList.add('page-item');
            if (i === currentPage) {
                li.classList.add('active');
            }
            li.innerHTML = `<a class="page-link" href="#" data-page="${i}">${i}</a>`;
            pagination.appendChild(li);
        }

        var pageLinks = pagination.querySelectorAll('.page-link');
        pageLinks.forEach(function(link) {
            link.addEventListener('click', function(event) {
                event.preventDefault();
                currentPage = parseInt(this.getAttribute('data-page'));
                renderTable(currentPage);
                renderPagination();
            });
        });
    }

    renderTable(currentPage);
    renderPagination();
}
```

#### AI Grading Example

Implement interaction with the GPT-4 API in `teacher_ai.html`:
```javascript
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('askButton').addEventListener('click', function() {
        var studentId = document.getElementById('studentIdInput').value;
        var answerOutput = document.getElementById('answerOutput');
        var scoreOutput = document.getElementById('scoreOutput');
        answerOutput.innerHTML = 'Loading...';
        scoreOutput.innerHTML = '';

        fetch('/ask_gpt4', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ student_id: studentId })
        })
        .then(response => response.json())
        .then(data => {
            answerOutput.innerHTML = data.answer;
            scoreOutput.innerHTML = 'Score: ' + data.score;
        })
        .catch(error => {
            answerOutput.innerHTML = 'Error: ' + error.message;
        });
    });
});
```

### Conclusion

With the implementation of the above interfaces and features, teachers can easily manage student and group activities and grade students using the GPT-4 API. The frontend pagination ensures smooth data display, and the AI grading feature enhances the intelligence and automation of grading.