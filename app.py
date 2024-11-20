from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from db_config import get_db_connection
import pandas as pd
import requests
import json
import random
import datetime
import time
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from flask import send_file
import io

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
            session['user_id'] = user['user_id']
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
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # 获取每个小组成员的活动总数
    query = """
    SELECT g.group_id, u.username as member_name, COUNT(a.activity_id) as contribution_count
    FROM activities a
    JOIN users u ON a.student_id = u.user_id
    JOIN project_groups g ON a.group_id = g.group_id
    WHERE a.assignment_id = %s
    GROUP BY g.group_id, u.username
    """
    cursor.execute(query, (assignment_id,))
    contributions = cursor.fetchall()

    # 获取每个小组的活动总数
    query_group_total = """
    SELECT g.group_id, COUNT(a.activity_id) as group_total_count
    FROM activities a
    JOIN project_groups g ON a.group_id = g.group_id
    WHERE a.assignment_id = %s
    GROUP BY g.group_id
    """
    cursor.execute(query_group_total, (assignment_id,))
    group_totals = cursor.fetchall()
    group_totals_dict = {group['group_id']: group['group_total_count'] for group in group_totals}

    # 计算每个小组成员的贡献百分比
    for contribution in contributions:
        group_id = contribution['group_id']
        group_total_count = group_totals_dict.get(group_id, 1)  # 防止除以0
        contribution['contribution_percentage'] = (contribution['contribution_count'] / group_total_count) * 100

    # 按贡献百分比降序排序，并确保同一组的成员显示在一起
    contributions.sort(key=lambda x: (x['group_id'], -x['contribution_percentage']))

    cursor.close()
    connection.close()

    return jsonify({'contributions': contributions})

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
# def ask_gpt4():
#     if 'logged_in' not in session or session['role'] != 'teacher':
#         return redirect(url_for('login'))

#     data = request.get_json()
#     student_id = data.get('student_id')

#     connection = get_db_connection()
#     query = """
#     SELECT 
#         a.activity_type, 
#         COUNT(a.activity_id) AS activity_count
#     FROM 
#         activities a
#     WHERE 
#         a.student_id = %s
#     GROUP BY 
#         a.activity_type
#     """
#     df = pd.read_sql_query(query, connection, params=(student_id,))
#     connection.close()

#     student_activities = df.to_dict(orient='records')

#     total_activities = sum([activity['activity_count'] for activity in student_activities])
#     average_score = 50
#     student_score = (total_activities / average_score) * 50

#     prompt = f"Student activities: {json.dumps(student_activities)}. The average activity count is 50. Please grade the student based on their activity count. The student's score is {student_score}."

#     headers = {
#         'Authorization': f'Bearer {api_key}',
#         'Content-Type': 'application/json'
#     }

#     payload = {
#         "model": "gpt-4",
#         "messages": [{"role": "user", "content": prompt}],
#         "max_tokens": 100,
#     }

#     response = requests.post(api_url, headers=headers, json=payload)
#     response_data = response.json()

#     print(response_data)  # 打印响应数据以便调试

#     if 'choices' in response_data and len(response_data['choices']) > 0:
#         answer = response_data['choices'][0]['message']['content']
#     else:
#         answer = "Sorry, I couldn't get an answer from GPT-4."

#     return jsonify({'answer': answer, 'score': student_score})


@app.route('/ask_gpt4', methods=['POST'])
def ask_gpt4():
    if 'logged_in' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))

    data = request.get_json()
    student_id = data.get('student_id')

    # 获取学生活动数据
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

    # GPT-4 Prompt
    prompt = f"""
    Student activities: {json.dumps(student_activities)}. 
    The average activity count is 50. 
    1. Grade the student based on their activity count. The student's score is {student_score}.
    2. Analyze the student's code contributions and identify common issues (if any).
    3. Generate a personalized study plan to improve their performance.
    4. Provide specific improvement suggestions based on lower-performing dimensions.
    """

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    payload = {
        "model": "gpt-4",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 300,
    }

    response = requests.post(api_url, headers=headers, json=payload)
    response_data = response.json()

    if 'choices' in response_data and len(response_data['choices']) > 0:
        answer = response_data['choices'][0]['message']['content']
    else:
        answer = "Sorry, I couldn't get an answer from GPT-4."

    try:
        grade, issues, study_plan, suggestions = answer.split("\n\n")
    except ValueError:
        grade = answer
        issues = "No issues detected or response incomplete."
        study_plan = "No study plan available."
        suggestions = "No suggestions available."

    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    import io

    # buffer = io.BytesIO()
    # pdf = canvas.Canvas(buffer, pagesize=letter)
    # pdf.drawString(100, 750, f"Feedback Report for Student ID: {student_id}")
    # pdf.drawString(100, 720, f"Score: {student_score}")
    # pdf.drawString(100, 690, "Grade:")
    # pdf.drawString(120, 670, grade)

    # pdf.drawString(100, 640, "Code Issues:")
    # pdf.drawString(120, 620, issues)

    # pdf.drawString(100, 590, "Study Plan:")
    # pdf.drawString(120, 570, study_plan)

    # pdf.drawString(100, 540, "Suggestions:")
    # pdf.drawString(120, 520, suggestions)

    # pdf.save()
    # buffer.seek(0)

    # pdf_filename = f"feedback_{student_id}.pdf"
    # pdf_path = f"./static/reports/{pdf_filename}"

    # with open(pdf_path, "wb") as f:
    #     f.write(buffer.getvalue())

    # return jsonify({
    #     'grade': grade,
    #     'issues': issues,
    #     'study_plan': study_plan,
    #     'suggestions': suggestions,
    #     'score': student_score,
    #     'pdf_link': f"/static/reports/{pdf_filename}"  
    # })
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import simpleSplit
    import io

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)

    # 设置标题样式
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(100, 750, f"Feedback Report for Student ID: {student_id}")

    # 设置分数部分样式
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(100, 720, f"Score: {student_score:.2f}")

    # 设置内容样式
    pdf.setFont("Helvetica", 12)

    # 定义自动换行函数
    def draw_multiline_text(pdf, text, x, y, max_width):
        lines = simpleSplit(text, pdf._fontname, pdf._fontsize, max_width)
        for line in lines:
            pdf.drawString(x, y, line)
            y -= 15  # 每行间距
        return y

    # 输出 Grade
    pdf.drawString(100, 690, "Grade:")
    pdf.setFont("Helvetica-Oblique", 12)
    y_position = draw_multiline_text(pdf, grade, 120, 675, 400)

    # 输出 Code Issues
    pdf.setFont("Helvetica", 12)
    pdf.drawString(100, y_position - 15, "Code Issues:")
    pdf.setFont("Helvetica-Oblique", 12)
    y_position = draw_multiline_text(pdf, issues, 120, y_position - 30, 400)

    # 输出 Study Plan
    pdf.setFont("Helvetica", 12)
    pdf.drawString(100, y_position - 15, "Study Plan:")
    pdf.setFont("Helvetica-Oblique", 12)
    y_position = draw_multiline_text(pdf, study_plan, 120, y_position - 30, 400)

    # 输出 Suggestions
    pdf.setFont("Helvetica", 12)
    pdf.drawString(100, y_position - 15, "Suggestions:")
    pdf.setFont("Helvetica-Oblique", 12)
    y_position = draw_multiline_text(pdf, suggestions, 120, y_position - 30, 400)

    # 添加页脚
    pdf.setFont("Helvetica", 10)
    pdf.drawString(100, 50, "Generated by Feedback System | Confidential")

    # 保存并写入缓冲区
    pdf.save()
    buffer.seek(0)

    pdf_filename = f"feedback_{student_id}.pdf"
    pdf_path = f"./static/reports/{pdf_filename}"

    with open(pdf_path, "wb") as f:
        f.write(buffer.getvalue())

    return jsonify({
        'grade': grade,
        'issues': issues,
        'study_plan': study_plan,
        'suggestions': suggestions,
        'score': student_score,
        'pdf_link': f"/static/reports/{pdf_filename}"  
    })




@app.route('/student')
def student():
    if 'logged_in' not in session or session['role'] != 'student':
        return redirect(url_for('login'))

    return render_template('student.html')

@app.route('/teacher/manage_students')
def teacher_manage():
    if 'logged_in' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    return render_template('manage_student.html')

@app.route('/teacher/select_course', methods=['GET', 'POST'])
def select_course():
    if 'logged_in' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))

    connection = get_db_connection()
    courses = pd.read_sql_query("SELECT * FROM courses", connection)
    connection.close()

    if request.method == 'POST':
        selected_course_id = request.form['course_id']
        session['current_course_id'] = selected_course_id

        return redirect(url_for('teacher_dashboard'))

    return render_template('select_course.html', courses=courses.to_dict(orient='records'))

@app.route('/get_courses')
def get_courses():
    if 'logged_in' not in session or session['role'] != 'teacher':
        return jsonify({'courses': []})

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # 获取当前教师的课程
    query = """
    SELECT c.course_id, c.course_name
    FROM courses c
    JOIN teacher_courses tc ON c.course_id = tc.course_id
    WHERE tc.teacher_id = %s
    """
    print(query)
    cursor.execute(query, (session['user_id'],))
    courses = cursor.fetchall()

    cursor.close()
    connection.close()
    print("courses", courses)
    return jsonify({'courses': courses})

@app.route('/validate_login', methods=['POST'])
def validate_login():
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
        session['user_id'] = user['user_id']
        session['username'] = username
        session['role'] = role
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'failure'})

@app.route('/get_activity_details')
def get_activity_details():
    group_id = request.args.get('group_id')
    activity_type = request.args.get('activity_type')

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
    SELECT activity_id, activity_type, activity_date, activity_detail
    FROM activities
    WHERE group_id = %s AND activity_type = %s
    """
    cursor.execute(query, (group_id, activity_type))
    activities = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify({'activities': activities})

@app.route('/get_student_activity_details')
def get_student_activity_details():
    student_id = request.args.get('student_id')
    if not student_id:
        return jsonify({'activities': []})

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
    SELECT student_id, activity_id, activity_type, activity_date, activity_detail
    FROM activities
    WHERE student_id = %s
    """
    cursor.execute(query, (student_id,))
    activities = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify({'activities': activities})

def calculate_activity_score(activity_type):
    score_map = {
        'commit': 10,
        'issue': 5,
        'pull_request': 8,
        'comment': 2,
        'task_completion': 7,
        'project_board': 3,
        'code_change': 6,
        'assigned_issue': 4,
        'milestone': 9,
        'bug_report': 5
    }
    return score_map.get(activity_type, 0)

@app.route('/update_score_map', methods=['POST'])
def update_score_map():
    new_score_map = request.json
    # 更新 calculate_activity_score 函数中的 score_map
    global calculate_activity_score
    def calculate_activity_score(activity_type):
        return new_score_map.get(activity_type, 0)
    return jsonify({'status': 'success'})

@app.route('/get_dashboard_data_v2/<assignment_id>')
def get_dashboard_data_v2(assignment_id):
    print("assignment_id", assignment_id)
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # 获取所有活动数据
    cursor.execute("""
    SELECT student_id, activity_type
    FROM activities
    WHERE assignment_id = %s
    """, (assignment_id,))
    activities = cursor.fetchall()

    # 计算每个学生的总分数和活动次数
    student_scores = {}
    student_activity_counts = {}
    for activity in activities:
        student_id = activity['student_id']
        activity_type = activity['activity_type']
        score = calculate_activity_score(activity_type)

        if student_id not in student_scores:
            student_scores[student_id] = 0
            student_activity_counts[student_id] = 0

        student_scores[student_id] += score
        student_activity_counts[student_id] += 1

    # 获取最好的学生（总活动分数最高）
    best_student = max(student_scores, key=student_scores.get, default=None)

    # 获取最差的学生（总活动分数最低）
    worst_student = min(student_scores, key=student_scores.get, default=None)

    # 获取最懒的学生（活动次数最少）
    most_lazy_student = min(student_activity_counts, key=student_activity_counts.get, default=None)

    # 获取最喜欢拖延的学生（最后一次活动日期最晚）
    cursor.execute("""
    SELECT student_id, MAX(activity_date) as last_activity_date
    FROM activities
    WHERE assignment_id = %s
    GROUP BY student_id
    ORDER BY last_activity_date DESC
    LIMIT 1
    """, (assignment_id,))
    most_ddl_fighter = cursor.fetchone()

    cursor.close()
    connection.close()

    return jsonify({
        'best_student': best_student,
        'worst_student': worst_student,
        'most_lazy_student': most_lazy_student,
        'most_ddl_fighter': most_ddl_fighter['student_id'] if most_ddl_fighter else None
    })

@app.route('/get_chart_data/<assignment_id>')
def get_chart_data(assignment_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # 获取所有活动数据
    cursor.execute("""
    SELECT student_id, activity_type, COUNT(*) as activity_count
    FROM activities
    WHERE assignment_id = %s
    GROUP BY student_id, activity_type
    """, (assignment_id,))
    activities = cursor.fetchall()

    # 组织数据
    student_activity_details = {}
    activity_types = set()
    for activity in activities:
        student_id = activity['student_id']
        activity_type = activity['activity_type']
        activity_count = activity['activity_count']
        activity_types.add(activity_type)

        if student_id not in student_activity_details:
            student_activity_details[student_id] = {}
        student_activity_details[student_id][activity_type] = activity_count

    # 计算统计信息
    activity_stats = {activity_type: {'max': 0, 'min': float('inf'), 'sum': 0, 'count': 0} for activity_type in activity_types}
    for student_id, activities in student_activity_details.items():
        for activity_type, count in activities.items():
            activity_stats[activity_type]['max'] = max(activity_stats[activity_type]['max'], count)
            activity_stats[activity_type]['min'] = min(activity_stats[activity_type]['min'], count)
            activity_stats[activity_type]['sum'] += count
            activity_stats[activity_type]['count'] += 1

    for activity_type, stats in activity_stats.items():
        stats['avg'] = stats['sum'] / stats['count'] if stats['count'] > 0 else 0

    cursor.close()
    connection.close()

    return jsonify({
        'student_activity_details': student_activity_details,
        'activity_stats': activity_stats
    })

@app.route('/get_students', methods=['GET'])
def get_students():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) as total FROM users WHERE role = 'student'")
    total = cursor.fetchone()['total']

    cursor.execute("""
        SELECT student_id, username, github_username, role, created_at, current_course_id, github_email
        FROM users
        WHERE role = 'student'
        LIMIT %s OFFSET %s
    """, (per_page, offset))
    students = cursor.fetchall()
    cursor.close()
    connection.close()

    return jsonify({
        'students': students,
        'total': total,
        'page': page,
        'per_page': per_page
    })

@app.route('/get_student/<student_id>', methods=['GET'])
def get_student(student_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT student_id, username, github_username, role, created_at, current_course_id, github_email FROM users WHERE student_id = %s", (student_id,))
    student = cursor.fetchone()
    cursor.close()
    connection.close()
    return jsonify({'student': student})

@app.route('/add_student', methods=['POST'])
def add_student():
    student_data = request.json
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO users (student_id, username, password, github_username, role, created_at, current_course_id, github_email)
        VALUES (%s, %s, %s, %s, %s, NOW(), %s, %s)
    """, (student_data['student_id'], student_data['username'], student_data['password'], student_data['github_username'], student_data['role'], student_data['current_course_id'], student_data['github_email']))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({'status': 'success'})

@app.route('/update_student/<student_id>', methods=['PUT'])
def update_student(student_id):
    student_data = request.json
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE users
        SET username = %s, github_username = %s, role = %s, current_course_id = %s, github_email = %s
        WHERE student_id = %s
    """, (student_data['username'], student_data['github_username'], student_data['role'], student_data['current_course_id'], student_data['github_email'], student_id))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({'status': 'success'})

@app.route('/delete_student/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM users WHERE student_id = %s", (student_id,))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({'status': 'success'})

@app.route('/get_student_info', methods=['GET'])
def get_student_info():
    student_id = session.get('user_id')
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT username, password, github_username, github_email FROM users WHERE user_id = %s", (student_id,))
    student = cursor.fetchone()
    cursor.close()
    connection.close()
    return jsonify(student)

@app.route('/update_student_info', methods=['PUT'])
def update_student_info():
    student_id = session.get('user_id')
    student_data = request.json
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE users
        SET password = %s, github_username = %s, github_email = %s
        WHERE user_id = %s
    """, (student_data['password'], student_data['github_username'], student_data['github_email'], student_id))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({'status': 'success'})


@app.route('/fetch_github_data', methods=['POST'])
def fetch_github_data():
    # 模拟从 GitHub 接口读取数据
    time.sleep(5)  # 模拟延迟

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # 获取有效的 assignment_id
    cursor.execute("SELECT assignment_id FROM assignments")
    assignments = cursor.fetchall()
    assignment_ids = [assignment['assignment_id'] for assignment in assignments]

    # 生成随机的假数据
    activity_types = ['commit', 'pull_request', 'issue', 'comment']
    activity_details = ['Fixed a bug', 'Added a new feature', 'Opened an issue', 'Commented on an issue']
    github_data = []

    for i in range(10):  # 生成10条假数据
        student_id = random.randint(1, 20)
        activity_type = random.choice(activity_types)
        activity_detail = random.choice(activity_details)
        activity_date = datetime.date.today() - datetime.timedelta(days=random.randint(0, 30))
        group_id = random.randint(1, 5)
        assignment_id = random.choice(assignment_ids)  # 使用有效的 assignment_id
        github_data.append({
            'student_id': student_id,
            'activity_type': activity_type,
            'activity_detail': activity_detail,
            'activity_date': activity_date,
            'group_id': group_id,
            'assignment_id': assignment_id
        })

    for activity in github_data:
        cursor.execute("""
            INSERT INTO activities (group_id, student_id, activity_type, activity_detail, activity_date, created_at, assignment_id)
            VALUES (%s, %s, %s, %s, %s, NOW(), %s)
        """, (activity['group_id'], activity['student_id'], activity['activity_type'], activity['activity_detail'], activity['activity_date'], activity['assignment_id']))
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True)


