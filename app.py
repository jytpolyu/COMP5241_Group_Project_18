from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from db_config import get_db_connection
import pandas as pd
import requests
import json


app = Flask(__name__)
app.secret_key = 'your_secret_key'


api_url = "https://openrouter.ai/api/v1/chat/completions"
api_key = "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"

@app.route('/')
def home():
    if 'logged_in' in session:
        if session['role'] == 'teacher':
            return redirect(url_for('teacher_dashboard'))
        else:
            return redirect(url_for('student'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM users WHERE username = %s AND password = %s AND role = %s"
        cursor.execute(query, (username, password, role))
        user = cursor.fetchone()

        cursor.close()
        connection.close()

        if user:
            session['logged_in'] = True
            session['role'] = role
            session['username'] = username
            if role == 'teacher':
                return redirect(url_for('teacher_dashboard'))
            else:
                return redirect(url_for('student'))
        else:
            return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/teacher/dashboard')
def teacher_dashboard():
    if 'logged_in' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))

    connection = get_db_connection()
    query = "SELECT DISTINCT assignment_id, title FROM assignments"
    assignments = pd.read_sql(query, connection)
    connection.close()

    return render_template('teacher_dashboard.html', assignments=assignments.to_dict(orient='records'))

@app.route('/teacher/dashboard/data/<assignment_id>')
def get_dashboard_data(assignment_id):
    if 'logged_in' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))

    connection = get_db_connection()
    query = """
    SELECT 
        g.group_id, 
        g.assignment_id,
        g.progress
    FROM 
        project_groups g
    WHERE 
        g.assignment_id = %s
    """
    df = pd.read_sql(query, connection, params=(assignment_id,))
    connection.close()

    # Calculate overall average progress
    overall_avg_progress = df['progress'].mean()

    data = df.to_dict(orient='records')

    return jsonify({'data': data, 'overall_avg_progress': overall_avg_progress})

@app.route('/teacher/dashboard/contributions/<assignment_id>')
def get_contributions(assignment_id):
    if 'logged_in' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))

    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    connection = get_db_connection()
    query = """
    SELECT 
        g.group_id,
        u.username AS member_name,
        COALESCE(SUM(a.activity_id), 0) AS contribution
    FROM 
        project_groups g
    JOIN 
        group_members gm ON g.group_id = gm.group_id
    JOIN 
        users u ON gm.student_id = u.user_id
    LEFT JOIN 
        activities a ON u.user_id = a.student_id AND a.assignment_id = g.assignment_id
    WHERE 
        g.assignment_id = %s
    GROUP BY 
        g.group_id, u.username
    ORDER BY 
        g.group_id, contribution DESC
    LIMIT %s OFFSET %s
    """
    df = pd.read_sql(query, connection, params=(assignment_id, per_page, offset))

    total_query = """
    SELECT COUNT(DISTINCT u.username) AS total
    FROM 
        project_groups g
    JOIN 
        group_members gm ON g.group_id = gm.group_id
    JOIN 
        users u ON gm.student_id = u.user_id
    WHERE 
        g.assignment_id = %s
    """
    total = pd.read_sql(total_query, connection, params=(assignment_id,)).iloc[0]['total']
    connection.close()

    # Convert int64 to int
    df['contribution'] = df['contribution'].astype(int)
    data = df.to_dict(orient='records')
    return jsonify({'data': data, 'total': int(total), 'page': page, 'per_page': per_page})

@app.route('/teacher/group')
def teacher_group():
    if 'logged_in' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))

    connection = get_db_connection()
    query = """
    SELECT 
        g.group_id, 
        a.activity_type, 
        COUNT(a.activity_id) AS activity_count
    FROM 
        project_groups g
    JOIN 
        activities a ON g.group_id = a.group_id
    GROUP BY 
        g.group_id, a.activity_type
    """
    df = pd.read_sql_query(query, connection)

    activity_types_query = "SELECT DISTINCT activity_type FROM activities"
    activity_types = pd.read_sql_query(activity_types_query, connection)
    connection.close()

    data = df.to_dict(orient='records')
    return render_template('teacher_group.html', data=data, activity_types=activity_types.to_dict(orient='records'))

@app.route('/teacher/group/search')
def search_group():
    if 'logged_in' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))

    search_term = request.args.get('search_term', '')
    activity_type = request.args.get('activity_type', '')

    connection = get_db_connection()
    query = """
    SELECT 
        g.group_id, 
        a.activity_type, 
        COUNT(a.activity_id) AS activity_count
    FROM 
        project_groups g
    JOIN 
        activities a ON g.group_id = a.group_id
    WHERE 
        g.group_id LIKE %s AND a.activity_type LIKE %s
    GROUP BY 
        g.group_id, a.activity_type
    """
    df = pd.read_sql_query(query, connection, params=(f'%{search_term}%', f'%{activity_type}%'))

    connection.close()

    data = df.to_dict(orient='records')
    return jsonify({'data': data})

@app.route('/teacher/group/info')
def group_info():
    if 'logged_in' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))

    connection = get_db_connection()
    query = """
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
        g.group_id, u1.username
    """
    df = pd.read_sql(query, connection)
    connection.close()

    data = df.to_dict(orient='records')
    return jsonify(data)

@app.route('/teacher/student')
def teacher_student():
    if 'logged_in' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))

    connection = get_db_connection()
    query = """
    SELECT 
        u.user_id AS student_id, 
        a.activity_type, 
        COUNT(a.activity_id) AS activity_count
    FROM 
        users u
    JOIN 
        activities a ON u.user_id = a.student_id
    WHERE 
        u.role = 'student'
    GROUP BY 
        u.user_id, a.activity_type
    """
    df = pd.read_sql_query(query, connection)

    activity_types_query = "SELECT DISTINCT activity_type FROM activities"
    activity_types = pd.read_sql_query(activity_types_query, connection)
    connection.close()

    data = df.to_dict(orient='records')
    return render_template('teacher_student.html', data=data, activity_types=activity_types.to_dict(orient='records'))

@app.route('/teacher/student/search')
def search_student():
    if 'logged_in' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))

    search_term = request.args.get('search_term', '')
    activity_type = request.args.get('activity_type', '')

    connection = get_db_connection()
    query = """
    SELECT 
        u.user_id AS student_id, 
        a.activity_type, 
        COUNT(a.activity_id) AS activity_count
    FROM 
        users u
    JOIN 
        activities a ON u.user_id = a.student_id
    WHERE 
        u.role = 'student' AND u.user_id LIKE %s AND a.activity_type LIKE %s
    GROUP BY 
        u.user_id, a.activity_type
    """
    df = pd.read_sql_query(query, connection, params=(f'%{search_term}%', f'%{activity_type}%'))

    connection.close()

    data = df.to_dict(orient='records')
    return jsonify({'data': data})

@app.route('/teacher/ai')
def teacher_ai():
    if 'logged_in' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))

    return render_template('teacher_ai.html')

@app.route('/ask_gpt4', methods=['POST'])
def ask_gpt4():
    if 'logged_in' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))

    data = request.get_json()
    student_id = data.get('student_id')

    connection = get_db_connection()
    query = """
    SELECT 
        a.activity_type, 
        COUNT(a.activity_id) AS activity_count
    FROM 
        activities a
    WHERE 
        a.student_id = %s
    GROUP BY 
        a.activity_type
    """
    df = pd.read_sql_query(query, connection, params=(student_id,))
    connection.close()

    student_activities = df.to_dict(orient='records')

    total_activities = sum([activity['activity_count'] for activity in student_activities])
    average_score = 50
    student_score = (total_activities / average_score) * 50

    prompt = f"Student activities: {json.dumps(student_activities)}. The average activity count is 50. Please grade the student based on their activity count. The student's score is {student_score}."

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    payload = {
        "model": "gpt-4",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 100,
    }

    response = requests.post(api_url, headers=headers, json=payload)
    response_data = response.json()

    print(response_data)  # 打印响应数据以便调试

    if 'choices' in response_data and len(response_data['choices']) > 0:
        answer = response_data['choices'][0]['message']['content']
    else:
        answer = "Sorry, I couldn't get an answer from GPT-4."

    return jsonify({'answer': answer, 'score': student_score})


@app.route('/student')
def student():
    if 'logged_in' not in session or session['role'] != 'student':
        return redirect(url_for('login'))

    return render_template('student.html')

if __name__ == '__main__':
    app.run(debug=True)