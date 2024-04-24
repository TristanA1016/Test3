from flask import Flask, render_template, request, jsonify
import sqlite3
import uuid
import datetime
app = Flask(__name__, template_folder='templates', static_folder='static')


def init_db():
    conn = sqlite3.connect('planner.db')
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    with open('schema.sql', 'r') as f:
        sql_commands = f.read()
    cursor.executescript(sql_commands)
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

def add_user_to_db(username, email, password):
    conn = sqlite3.connect('planner.db')
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Users (Username, Email, Password) VALUES (?, ?, ?)", (username, email, password))
    conn.commit()
    conn.close()

def add_task_to_db(task_title, task_description, user_id, priority, due_date, status, category):
    conn = sqlite3.connect('planner.db')
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    cursor.execute("SELECT MAX(TaskID) FROM Tasks")
    max_task_id = cursor.fetchone()[0]
    next_task_id = 1 if max_task_id is None else max_task_id + 1

    cursor.execute("INSERT INTO Tasks (TaskID, UserID, Title, Description, Priority, DueDate, Status, Category) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   (next_task_id, user_id, task_title, task_description, priority, due_date, status, category))
    conn.commit()
    conn.close()


def add_event_to_db(event_title, start_time, end_time, user_id, category):
    conn = sqlite3.connect('planner.db')
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    cursor.execute("SELECT MAX(EventID) FROM Events")
    max_event_id = cursor.fetchone()[0]
    next_event_id = 1 if max_event_id is None else max_event_id + 1

    cursor.execute("INSERT INTO Events (EventID, UserID, Title, StartTime, EndTime, Category) VALUES (?, ?, ?, ?, ?, ?)",
                   (next_event_id, user_id, event_title, start_time, end_time, category))
    conn.commit()
    conn.close()


def get_all_users_from_db():
    conn = sqlite3.connect('planner.db')
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users")
    users = cursor.fetchall()
    conn.close()
    return users

def get_all_tasks_from_db():
    conn = sqlite3.connect('planner.db')
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Tasks")
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def get_all_events_from_db():
    conn = sqlite3.connect('planner.db')
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Events")
    events = cursor.fetchall()
    conn.close()
    return events

def authenticate_user(username, password):
    conn = sqlite3.connect('planner.db')
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    cursor.execute("SELECT Password FROM Users WHERE Username = ?", (username,))
    stored_password = cursor.fetchone()
    conn.close()
    if stored_password and stored_password[0] == password:
        return True
    else:
        return False

def update_user_profile(user_id, username, email, password):
    conn = sqlite3.connect('planner.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE Users SET Username=?, Email=?, Password=? WHERE UserID=?", (username, email, password, user_id))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.json
    username = data.get('userName')
    email = data.get('email')
    password = data.get('password')
    if username and email and password:
        try:
            add_user_to_db(username, email, password)
            return jsonify({'success': True}), 200
        except:
            return jsonify({'success': False}), 500
    else:
        return jsonify({'success': False}), 400

@app.route('/authenticate_user', methods=['POST'])
def login():
    data = request.json
    username = data.get('userName')
    password = data.get('password')
    if username and password:
        conn = sqlite3.connect('planner.db')
        cursor = conn.cursor()
        cursor.execute("SELECT UserID, Password FROM Users WHERE Username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        if authenticate_user(username, password):
            return jsonify({'success': True, 'message': 'Login successful', 'userID': result[0]}), 200
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    else:
        return jsonify({'success': False, 'message': 'Username and password are required'}), 400


@app.route('/edit_profile', methods=['POST'])
def edit_profile():
    data = request.json
    user_id = data.get('userID')
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    if user_id and username and email and password:
        try:
            update_user_profile(user_id, username, email, password)
            return jsonify({'success': True}), 200
        except:
            return jsonify({'success': False}), 500
    else:
        return jsonify({'success': False, 'message': 'Missing required parameters'}), 400



@app.route('/add_task', methods=['POST'])
def add_task():
    data = request.json
    task_title = data.get('taskTitle')
    task_description = data.get('taskDescription')
    user_id = data.get('userIDTask')
    priority = data.get('priority')
    due_date = data.get('dueDate')
    status = data.get('status')
    category = data.get('categoryTask')
    if task_title and user_id:
        try:
            add_task_to_db(task_title, task_description, user_id, priority, due_date, status, category)
            return jsonify({'success': True}), 200
        except:
            return jsonify({'success': False}), 500
    else:
        return jsonify({'success': False}), 400

@app.route('/add_event', methods=['POST'])
def add_event():
    data = request.json
    event_title = data.get('eventTitle')
    start_time = data.get('startTime')
    end_time = data.get('endTime')
    user_id = data.get('userIDEvent')
    category = data.get('categoryEvent')
    if event_title and user_id:
        try:
            add_event_to_db(event_title, start_time, end_time, user_id, category)
            return jsonify({'success': True}), 200
        except:
            return jsonify({'success': False}), 500
    else:
        return jsonify({'success': False}), 400
    
@app.route('/get_all_users', methods=['GET'])
def get_all_users():
    users = get_all_users_from_db()
    return jsonify(users)

@app.route('/get_all_tasks', methods=['GET'])
def get_all_tasks():
    tasks = get_all_tasks_from_db()
    return jsonify(tasks)

@app.route('/get_all_events', methods=['GET'])
def get_all_events():
    events = get_all_events_from_db()
    print('Fetched events:', events)
    return jsonify(events)

@app.route('/get_user_tasks', methods=['GET'])
def get_user_tasks():
    user_id = request.args.get('userID')
    conn = sqlite3.connect('planner.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Tasks WHERE UserID = ?", (user_id,))
    tasks = cursor.fetchall()
    conn.close()
    return jsonify(tasks)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
