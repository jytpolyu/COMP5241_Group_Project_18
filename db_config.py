import mysql.connector

def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='150218',
        database='githubClassroom'
    )
    return connection