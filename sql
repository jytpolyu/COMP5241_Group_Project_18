-- 创建用户表
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(20) UNIQUE,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL,
    github_username VARCHAR(50) NOT NULL,
    role ENUM('student', 'teacher') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建作业表
CREATE TABLE assignments (
    assignment_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    teacher_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES users(user_id)
);

-- 创建小组表
CREATE TABLE project_groups (
    group_id INT AUTO_INCREMENT PRIMARY KEY,
    assignment_id INT,
    leader_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (assignment_id) REFERENCES assignments(assignment_id),
    FOREIGN KEY (leader_id) REFERENCES users(user_id)
);

-- 创建小组成员表
CREATE TABLE group_members (
    group_member_id INT AUTO_INCREMENT PRIMARY KEY,
    group_id INT,
    student_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES project_groups(group_id),
    FOREIGN KEY (student_id) REFERENCES users(user_id)
);

-- 创建活动表
CREATE TABLE activities (
    activity_id INT AUTO_INCREMENT PRIMARY KEY,
    group_id INT,
    student_id INT,
    activity_type ENUM('commit', 'issue', 'pull_request', 'comment', 'task_completion', 'project_board', 'code_change', 'assigned_issue', 'milestone', 'bug_report') NOT NULL,
    activity_detail TEXT,
    activity_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES project_groups(group_id),
    FOREIGN KEY (student_id) REFERENCES users(user_id)
);

-- 创建视图以汇总活动数据
CREATE VIEW group_activity_summary AS
SELECT 
    g.group_id,
    g.assignment_id,
    COUNT(CASE WHEN a.activity_type = 'commit' THEN 1 END) AS commit_count,
    COUNT(CASE WHEN a.activity_type = 'issue' THEN 1 END) AS issue_count,
    COUNT(CASE WHEN a.activity_type = 'pull_request' THEN 1 END) AS pull_request_count,
    COUNT(CASE WHEN a.activity_type = 'comment' THEN 1 END) AS comment_count,
    COUNT(CASE WHEN a.activity_type = 'task_completion' THEN 1 END) AS task_completion_count,
    COUNT(CASE WHEN a.activity_type = 'project_board' THEN 1 END) AS project_board_count,
    COUNT(CASE WHEN a.activity_type = 'code_change' THEN 1 END) AS code_change_count,
    COUNT(CASE WHEN a.activity_type = 'assigned_issue' THEN 1 END) AS assigned_issue_count,
    COUNT(CASE WHEN a.activity_type = 'milestone' THEN 1 END) AS milestone_count,
    COUNT(CASE WHEN a.activity_type = 'bug_report' THEN 1 END) AS bug_report_count
FROM 
    project_groups g
JOIN 
    activities a ON g.group_id = a.group_id
GROUP BY 
    g.group_id, g.assignment_id;

-- 创建视图以汇总学生活动数据
CREATE VIEW student_activity_summary AS
SELECT 
    s.student_id,
    s.group_id,
    COUNT(CASE WHEN a.activity_type = 'commit' THEN 1 END) AS commit_count,
    COUNT(CASE WHEN a.activity_type = 'issue' THEN 1 END) AS issue_count,
    COUNT(CASE WHEN a.activity_type = 'pull_request' THEN 1 END) AS pull_request_count,
    COUNT(CASE WHEN a.activity_type = 'comment' THEN 1 END) AS comment_count,
    COUNT(CASE WHEN a.activity_type = 'task_completion' THEN 1 END) AS task_completion_count,
    COUNT(CASE WHEN a.activity_type = 'project_board' THEN 1 END) AS project_board_count,
    COUNT(CASE WHEN a.activity_type = 'code_change' THEN 1 END) AS code_change_count,
    COUNT(CASE WHEN a.activity_type = 'assigned_issue' THEN 1 END) AS assigned_issue_count,
    COUNT(CASE WHEN a.activity_type = 'milestone' THEN 1 END) AS milestone_count,
    COUNT(CASE WHEN a.activity_type = 'bug_report' THEN 1 END) AS bug_report_count
FROM 
    group_members s
JOIN 
    activities a ON s.group_id = a.group_id AND s.student_id = a.student_id
GROUP BY 
    s.student_id, s.group_id;




-- 插入用户数据
INSERT INTO users (student_id, username, password, github_username, role) VALUES
('S001', 'student1', 'password1', 'github_student1', 'student'),
('S002', 'student2', 'password2', 'github_student2', 'student'),
('S003', 'student3', 'password3', 'github_student3', 'student'),
('S004', 'student4', 'password4', 'github_student4', 'student'),
('S005', 'student5', 'password5', 'github_student5', 'student'),
('S006', 'student6', 'password6', 'github_student6', 'student'),
('S007', 'student7', 'password7', 'github_student7', 'student'),
('S008', 'student8', 'password8', 'github_student8', 'student'),
('S009', 'student9', 'password9', 'github_student9', 'student'),
('S010', 'student10', 'password10', 'github_student10', 'student'),
('S011', 'student11', 'password11', 'github_student11', 'student'),
('S012', 'student12', 'password12', 'github_student12', 'student'),
('S013', 'student13', 'password13', 'github_student13', 'student'),
('S014', 'student14', 'password14', 'github_student14', 'student'),
('S015', 'student15', 'password15', 'github_student15', 'student'),
('S016', 'student16', 'password16', 'github_student16', 'student'),
('S017', 'student17', 'password17', 'github_student17', 'student'),
('S018', 'student18', 'password18', 'github_student18', 'student'),
('S019', 'student19', 'password19', 'github_student19', 'student'),
('S020', 'student20', 'password20', 'github_student20', 'student'),
('T001', 'teacher1', 'password21', 'github_teacher1', 'teacher'),
('T002', 'teacher2', 'password22', 'github_teacher2', 'teacher');

-- 插入作业数据
INSERT INTO assignments (title, description, teacher_id) VALUES
('Assignment 1', 'Description for assignment 1', 21),
('Assignment 2', 'Description for assignment 2', 22);

-- 插入小组数据
INSERT INTO project_groups (assignment_id, leader_id) VALUES
(1, 1),
(1, 2),
(1, 3),
(2, 4),
(2, 5);

-- 插入小组成员数据
INSERT INTO group_members (group_id, student_id) VALUES
(1, 1),
(1, 6),
(1, 11),
(2, 2),
(2, 7),
(2, 12),
(3, 3),
(3, 8),
(3, 13),
(4, 4),
(4, 9),
(4, 14),
(5, 5),
(5, 10),
(5, 15),
(1, 16),
(2, 17),
(3, 18),
(4, 19),
(5, 20);

-- 插入活动数据
INSERT INTO activities (group_id, student_id, activity_type, activity_detail, activity_date) VALUES
(1, 1, 'commit', 'Initial commit', '2023-10-01 10:00:00'),
(1, 6, 'issue', 'Found a bug', '2023-10-02 11:00:00'),
(1, 11, 'pull_request', 'Added new feature', '2023-10-03 12:00:00'),
(2, 2, 'comment', 'Reviewed PR', '2023-10-04 13:00:00'),
(2, 7, 'task_completion', 'Completed task 1', '2023-10-05 14:00:00'),
(2, 12, 'project_board', 'Updated project board', '2023-10-06 15:00:00'),
(3, 3, 'code_change', 'Refactored code', '2023-10-07 16:00:00'),
(3, 8, 'assigned_issue', 'Assigned issue #5', '2023-10-08 17:00:00'),
(3, 13, 'milestone', 'Reached milestone 1', '2023-10-09 18:00:00'),
(4, 4, 'bug_report', 'Reported a bug', '2023-10-10 19:00:00'),
(4, 9, 'commit', 'Fixed bug', '2023-10-11 20:00:00'),
(4, 14, 'issue', 'Opened issue #10', '2023-10-12 21:00:00'),
(5, 5, 'pull_request', 'Merged PR #15', '2023-10-13 22:00:00'),
(5, 10, 'comment', 'Commented on issue #20', '2023-10-14 23:00:00'),
(5, 15, 'task_completion', 'Completed task 2', '2023-10-15 09:00:00'),
(1, 16, 'project_board', 'Updated project board', '2023-10-16 10:00:00'),
(2, 17, 'code_change', 'Optimized code', '2023-10-17 11:00:00'),
(3, 18, 'assigned_issue', 'Assigned issue #25', '2023-10-18 12:00:00'),
(4, 19, 'milestone', 'Reached milestone 2', '2023-10-19 13:00:00'),
(5, 20, 'bug_report', 'Reported another bug', '2023-10-20 14:00:00'),
(1, 1, 'commit', 'Added new module', '2023-10-21 15:00:00'),
(1, 6, 'issue', 'Found another bug', '2023-10-22 16:00:00'),
(1, 11, 'pull_request', 'Fixed issue #30', '2023-10-23 17:00:00'),
(2, 2, 'comment', 'Reviewed PR #35', '2023-10-24 18:00:00'),
(2, 7, 'task_completion', 'Completed task 3', '2023-10-25 19:00:00'),
(2, 12, 'project_board', 'Updated project board again', '2023-10-26 20:00:00'),
(3, 3, 'code_change', 'Refactored code again', '2023-10-27 21:00:00'),
(3, 8, 'assigned_issue', 'Assigned issue #40', '2023-10-28 22:00:00'),
(3, 13, 'milestone', 'Reached milestone 3', '2023-10-29 23:00:00'),
(4, 4, 'bug_report', 'Reported a critical bug', '2023-10-30 09:00:00'),
(4, 9, 'commit', 'Fixed critical bug', '2023-10-31 10:00:00');


-- 修改活动表，添加 assignment_id 列
ALTER TABLE activities ADD COLUMN assignment_id INT;

-- 更新外键约束
ALTER TABLE activities ADD FOREIGN KEY (assignment_id) REFERENCES assignments(assignment_id);