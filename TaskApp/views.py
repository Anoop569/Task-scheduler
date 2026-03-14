from django.shortcuts import render
import pymysql
import base64
from datetime import datetime, timedelta
import smtplib
from threading import Thread
import time

# ================= GLOBALS =================
push_time = ""
alert_status = False


# ================= HOME =================
def index(request):
    return render(request, 'index.html')


# ================= LOAD PUSH TIME =================
def readTime():
    global push_time
    con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root123', database='taskschedule', charset='utf8')
    with con:
        cur = con.cursor()
        cur.execute("SELECT push_time FROM pushtime")
        row = cur.fetchone()
        push_time = row[0] if row else ""


# ================= GET EMAIL =================
def getEmail(username):
    con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root123', database='taskschedule', charset='utf8')
    with con:
        cur = con.cursor()
        cur.execute("SELECT email FROM signup WHERE username=%s", (username,))
        row = cur.fetchone()
        return row[0] if row else ""


# ================= SEND EMAIL =================
def executeTask(msg, email):
    print("📧 Sending reminder to:", email)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as connection:
        connection.login('kaleem202120@gmail.com', 'xyljzncebdxcubjq')
        connection.sendmail(
            from_addr='kaleem202120@gmail.com',
            to_addrs=[email],
            msg="Subject: Task Reminder\n\n" + msg
        )


# ================= NOTIFICATION LOGIC =================
def pushAlert():
    global push_time, alert_status
    if push_time == "":
        return

    h, m, s = map(int, push_time.split())

    con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root123', database='taskschedule', charset='utf8')
    with con:
        cur = con.cursor()
        cur.execute("SELECT username, title, description, due_date FROM task WHERE status='Pending'")
        tasks = cur.fetchall()

        for user, title, desc, due_date_str in tasks:
            due_time = datetime.strptime(due_date_str, "%d-%m-%Y %H:%M:%S")
            notify_time = due_time - timedelta(hours=h, minutes=m, seconds=s)
            current_time = datetime.now()

            print("Current:", current_time.strftime("%d-%m-%Y %H:%M:%S"),
                  "| Notify At:", notify_time.strftime("%d-%m-%Y %H:%M:%S"))

            if current_time.strftime("%d-%m-%Y %H:%M:%S") == notify_time.strftime("%d-%m-%Y %H:%M:%S") and not alert_status:
                email = getEmail(user)
                message = f"Title: {title}\nDescription: {desc}\nDue Date: {due_date_str}"
                executeTask(message, email)
                alert_status = True

            if current_time > notify_time:
                alert_status = False


# ================= BACKGROUND SCHEDULER =================
def scheduleTask():
    def run_scheduler():
        while True:
            pushAlert()
            time.sleep(1)

    thread = Thread(target=run_scheduler)
    thread.daemon = True
    thread.start()


# Start scheduler



# ================= AUTH =================
def Signup(request):
    return render(request, 'Signup.html')


def SignupAction(request):
    username = request.POST.get('t1')
    password = base64.b64encode(request.POST.get('t2').encode()).decode()
    contact = request.POST.get('t3')
    email = request.POST.get('t4')
    address = request.POST.get('t5')

    con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root123', database='taskschedule', charset='utf8')
    with con:
        cur = con.cursor()
        cur.execute("INSERT INTO signup VALUES(%s,%s,%s,%s,%s)", (username, password, contact, email, address))
        con.commit()

    return render(request, 'Signup.html', {'data': 'Signup successful'})


def UserLogin(request):
    return render(request, 'UserLogin.html')


def UserLoginAction(request):
    username = request.POST.get('t1')
    password = base64.b64encode(request.POST.get('t2').encode()).decode()

    con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root123', database='taskschedule', charset='utf8')
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM signup WHERE username=%s AND password=%s", (username, password))
        if cur.fetchone():
            request.session['username'] = username  # ✅ SESSION FIX
            return render(request, 'UserScreen.html', {'data': f'Welcome {username}'})

    return render(request, 'UserLogin.html', {'data': 'Invalid login'})


def ChangePassword(request):
    return render(request, 'ChangePassword.html')


def ChangePasswordAction(request):
    username = request.session.get('username')
    old_pass = base64.b64encode(request.POST.get('t1').encode()).decode()
    new_pass = base64.b64encode(request.POST.get('t2').encode()).decode()

    con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root123', database='taskschedule', charset='utf8')
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM signup WHERE username=%s AND password=%s", (username, old_pass))
        if cur.fetchone():
            cur.execute("UPDATE signup SET password=%s WHERE username=%s", (new_pass, username))
            con.commit()
            return render(request, 'ChangePassword.html', {'data': 'Password updated successfully'})
        else:
            return render(request, 'ChangePassword.html', {'data': 'Invalid old password'})


# ================= TASK MANAGEMENT =================
def CreateTask(request):
    return render(request, 'CreateTask.html')


def CreateTaskAction(request):
    username = request.session.get('username')  # ✅ SESSION FIX

    title = request.POST.get('t1')
    desc = request.POST.get('t2')
    duedate = request.POST.get('t3')
    priority = request.POST.get('t4')
    tags = request.POST.get('t5')

    con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root123', database='taskschedule', charset='utf8')
    with con:
        cur = con.cursor()
        cur.execute("SELECT IFNULL(MAX(task_id),0)+1 FROM task")
        task_id = cur.fetchone()[0]

        cur.execute(
            "INSERT INTO task VALUES(%s,%s,%s,%s,%s,%s,%s,'Pending')",
            (task_id, username, title, desc, duedate, priority, tags)
        )
        con.commit()

    return render(request, 'CreateTask.html', {'data': f'Task created with ID {task_id}'})


def ViewTask(request):
    username = request.session.get('username')

    output = '<table border=1 align=center>'
    output += '<tr><th>Task ID</th><th>Username</th><th>Title</th><th>Description</th><th>Due Date</th><th>Priority</th><th>Tags</th><th>Status</th><th>Delete</th><th>Edit</th></tr>'

    con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root123', database='taskschedule', charset='utf8')
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM task WHERE username=%s", (username,))
        rows = cur.fetchall()

        for row in rows:
            output += '<tr>'
            output += f'<td>{row[0]}</td>'
            output += f'<td>{row[1]}</td>'
            output += f'<td>{row[2]}</td>'
            output += f'<td>{row[3]}</td>'
            output += f'<td>{row[4]}</td>'
            output += f'<td>{row[5]}</td>'
            output += f'<td>{row[6]}</td>'
            output += f'<td>{row[7]}</td>'
            output += f'<td><a href="DeleteTask?tid={row[0]}">Delete</a></td>'
            output += f'<td><a href="EditTask?tid={row[0]}">Edit</a></td>'
            output += '</tr>'

    output += '</table><br/>'

    return render(request, 'UserScreen.html', {'data': output})


def DeleteTask(request):
    task_id = request.GET.get('tid')

    con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root123', database='taskschedule', charset='utf8')
    with con:
        cur = con.cursor()
        cur.execute("DELETE FROM task WHERE task_id=%s", (task_id,))
        con.commit()

    return render(request, 'UserScreen.html', {'data': 'Task deleted'})


def EditTask(request):
    task_id = request.GET.get('tid')
    print("EDIT FUNCTION HIT")
    print(request.POST)

    con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root123', database='taskschedule', charset='utf8')
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM task WHERE task_id=%s", (task_id,))
        task = cur.fetchone()

    return render(request, 'EditTask.html', {'task': task})


from django.shortcuts import redirect
import pymysql

def EditTaskAction(request):
    if request.method != "POST":
        return redirect('ViewTask')

    task_id = request.POST.get('task_id')
    title = request.POST.get('t1')
    desc = request.POST.get('t2')
    duedate = request.POST.get('t3')
    priority = request.POST.get('t4')
    tags = request.POST.get('t5')

    if not task_id:
        print("ERROR: No Task ID received")
        return redirect('ViewTask')

    con = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='root123',
        database='taskschedule',
        charset='utf8'
    )

    with con:
        cur = con.cursor()

        rows = cur.execute("""
            UPDATE task 
            SET title=%s, description=%s, due_date=%s, priority=%s, tags=%s
            WHERE task_id=%s
        """, (title, desc, duedate, priority, tags, task_id))

        print("Rows affected:", rows)
        con.commit()

    return redirect('ViewTask') 


def MarkComplete(request):
    username = request.session.get('username')

    output = '<table border=1 align=center>'
    output += '<tr><th>Task ID</th><th>Title</th><th>Status</th><th>Mark Complete</th></tr>'

    con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root123', database='taskschedule', charset='utf8')
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM task WHERE username=%s AND status='Pending'", (username,))
        rows = cur.fetchall()

        for row in rows:
            output += '<tr>'
            output += f'<td>{row[0]}</td>'
            output += f'<td>{row[2]}</td>'
            output += f'<td>{row[7]}</td>'
            output += f'<td><a href="MarkCompleted?tid={row[0]}">Complete</a></td>'
            output += '</tr>'

    output += '</table><br/>'

    return render(request, 'UserScreen.html', {'data': output})


def MarkCompleted(request):
    task_id = request.GET.get('tid')

    con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root123', database='taskschedule', charset='utf8')
    with con:
        cur = con.cursor()
        cur.execute("UPDATE task SET status='Completed' WHERE task_id=%s", (task_id,))
        con.commit()

    return render(request, 'UserScreen.html', {'data': 'Task marked completed'})


# ================= NOTIFICATION =================
def NotificationTime(request):
    return render(request, 'NotificationTime.html')


def NotificationTimeAction(request):
    global push_time
    hour = request.POST.get('t1')
    minute = request.POST.get('t2')
    second = request.POST.get('t3')

    push_time = f"{hour} {minute} {second}"

    con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root123', database='taskschedule', charset='utf8')
    with con:
        cur = con.cursor()
        cur.execute("DELETE FROM pushtime")
        cur.execute("INSERT INTO pushtime VALUES(%s,%s)", (request.session.get('username'), push_time))
        con.commit()

    readTime()
    return render(request, 'UserScreen.html', {'data': 'Notification time set successfully'})
