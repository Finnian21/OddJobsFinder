from flask import Flask, render_template, url_for, escape, request, redirect, session
from flask_mail import Mail, Message
import datetime
import pymysql
import hashlib, uuid

app = Flask(__name__)
mail=Mail(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'oddjobsfinder@gmail.com'
app.config['MAIL_PASSWORD'] = 'Rathdrum21'
app.config['MAIL_USE_TLS'] = True
mail = Mail(app)
        
@app.route('/login', methods = ['GET', 'POST'])
def login():
    db = pymysql.connect(host='oddjobsfinder.mysql.pythonanywhere-services.com', user='oddjobsfinder', passwd='Rathdrum21', db = 'oddjobsfinder$default')
    error = None
    cursor = db.cursor()

    if 'username' in session:
        return redirect("/", code=302)

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']
        sql = "SELECT * from users where username='" + username + "' and password='" + password + "'"

        cursor.execute(sql)

        if cursor.fetchone() is None:
            error = 'Invalid Credentials. Please try again.'
        else:
            session['username'] = username
            sql2 = "SELECT userType from users where username='" + username + "'"
            cursor.execute(sql2)
            results = cursor.fetchall()
            
            for row in results:
                session['user_type'] = row[0]

            return redirect("/", code=302)
    cursor.close()
    db.close()
    return render_template('login.html', error=error)

@app.route('/post_job', methods = ['GET', 'POST'])
def post_job():
    db = pymysql.connect(host='oddjobsfinder.mysql.pythonanywhere-services.com', user='oddjobsfinder', passwd='Rathdrum21', db = 'oddjobsfinder$default')
    cursor = db.cursor()
    
    if 'username' not in session:
        return redirect("/login", code=302)

    username = session['username']
    user_type = session['user_type']

    if user_type == 'Job Searcher':
        return redirect("/", code=302)

    sql = "SELECT * FROM users where username = '" + username + "'"
    cursor.execute(sql)
    results = cursor.fetchall()

    user_Id = ''

    for row in results:
        user_Id = row[0]

    the_user_Id = str(user_Id)

    if request.method == 'POST':
        title =  request.form["inputTitle"]
        description =  request.form["description"]
        duration =  request.form["duration"]
        pay =  request.form["pay"]
        catagory =  request.form["catagory"]
        resources_provided = request.form["resourcesProvided"]
        resources_required = request.form["resourcesRequired"]

        phone = ""
        email = ""
        street = ""
        town = ""
        county = ""

        checked = request.form.getlist('differentContacts')
        checked2 = request.form.getlist('differentAddress')

        if checked == ['on']:
            phone = request.form["phone"]
            email = request.form["email"]    
        else:
            sql1 = "SELECT * FROM users where userId =" + the_user_Id
            cursor.execute(sql)
            results2 = cursor.fetchall()
            
            for row in results2:
                phone = row[7]
                email = row[8]

        if checked2 == ['on']:
            street = request.form["street"]
            town = request.form["town"]
            county = request.form["county"] 

        else:
            sql2 = "SELECT street, town, county FROM users where userId =" + the_user_Id
            cursor.execute(sql2)
            results3 = cursor.fetchall()
            
            for row in results3:
                street = row[0]
                town = row[1]
                county = row[2]

        time_stamp_posted = datetime.datetime.now()

        cursor.execute("INSERT INTO jobs (title, UserID, description, duration, pay, catagory, timeStampPosted, resourcesProvided, resourcesRequired, email, phone, street, town, county) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (title, the_user_Id, description, duration, pay, catagory, time_stamp_posted, resources_provided, resources_required, email, phone, street, town, county))
        db.commit()

        cursor.execute("UPDATE users SET JobsPosted = JobsPosted + 1 WHERE userID = %s", (the_user_Id))
        db.commit()

        return redirect("/view_jobs", code=302)
    
    cursor.close()
    db.close()
    return render_template('postJob.html', results=results)

@app.route('/view_jobs', methods = ['GET', 'POST'])
def view_jobs():

    db = pymysql.connect(host='oddjobsfinder.mysql.pythonanywhere-services.com', user='oddjobsfinder', passwd='Rathdrum21', db = 'oddjobsfinder$default')
    cursor = db.cursor()

    if 'username' in session: 
        username = session['username']
        user_type = session['user_type']

        sql = "SELECT * FROM users where username ='" + username + "'"
        cursor.execute(sql)
        results = cursor.fetchall()

        for row in results:
            the_user_Id = row[0]
    else:
        username = ''
        the_user_Id = 0
        user_type = ''
    
    session['user_id'] = the_user_Id

    sql2 = "SELECT * FROM jobs INNER JOIN users ON jobs.UserID=users.userId WHERE takenFlag != '1' ORDER BY timeStampPosted DESC"
    cursor.execute(sql2)
    results2 = cursor.fetchall()
    current_time = datetime.datetime.now()
    for row in results2:
        session['job_id'] = row[2]
        elapsed_time = current_time - row[7]
    
    cursor.close()
    db.close()
    return render_template('viewJobs.html', results2 = results2, the_user_Id = the_user_Id, current_time = current_time, user_type = user_type)

@app.route('/view_job', methods = ['GET', 'POST'])
def view_job():

    db = pymysql.connect(host='oddjobsfinder.mysql.pythonanywhere-services.com', user='oddjobsfinder', passwd='Rathdrum21', db = 'oddjobsfinder$default')
    cursor = db.cursor()

    if request.method == 'POST':
        job_id = request.form['view_button']

        session['job_id'] = job_id

        sql = "SELECT * FROM jobs INNER JOIN users ON jobs.UserID=users.userId WHERE jobId = " + job_id
        cursor.execute(sql)
        results = cursor.fetchall()

        for row in results:
            session['firstname'] = row[18]
            session['job_username'] = row[20]

        session['results'] = results

        if 'username' in session:
            user_Id = session['user_id']
            user_type = session['user_type']
        else:
            user_Id = 0
            user_type = ""
        
        return render_template('viewJob.html' , results = results, user_type = user_type, user_Id = user_Id)
    cursor.close()
    db.close()
    return render_template('viewJob.html')

@app.route('/', methods = ['GET', 'POST'])
def home():
    if 'username' in session: 
        username = session['username']
        user_type = session['user_type']
    else:
        username = ''
        user_type = ''
        
    return render_template('home.html', username = username, user_type = user_type)

@app.route('/take_job', methods = ['GET', 'POST'])
def take_job():
    db = pymysql.connect(host='oddjobsfinder.mysql.pythonanywhere-services.com', user='oddjobsfinder', passwd='Rathdrum21', db = 'oddjobsfinder$default')#db = session['db']
    cursor = db.cursor()

    if 'username' in  session:
        results = session['results']
        job_id = session['job_id']
        username = session['username']
        user_id = str(session['user_id'])
        firstname = session['firstname']
        job_username = session['job_username']
        
        sql = "SELECT * FROM jobs where jobId ='" + job_id + "'"
        cursor.execute(sql)
        results = cursor.fetchall()
        
        for row in results:
            email = row[10]
            title = row[1]
        session['title'] = title

        msg = Message('Job Taken', sender = 'oddjobsfinder@gmail.com', recipients = [email])
        msg.body = "Hi, your job titled " + title + " has been taken by " + username + "."
        msg.html = render_template("/email.html", title = title, username = username, firstname=firstname)
        mail.send(msg)
        
    else:
        session['route'] = 'take_job'
        return redirect("/login", code=302)
    cursor.close()
    db.close()
    return render_template('takeJob.html', results = results)

@app.route('/decline_user', methods = ['GET', 'POST'])
def decline_user():
    db = pymysql.connect(host='oddjobsfinder.mysql.pythonanywhere-services.com', user='oddjobsfinder', passwd='Rathdrum21', db = 'oddjobsfinder$default')#db = session['db']
    cursor = db.cursor()

    job_id = session['job_id']
    user_id = str(session['user_id'])
    job_username = session['job_username']

    sql = "SELECT * FROM users where userId ='" + user_id + "'"
    cursor.execute(sql)
    results = cursor.fetchall()
    title = session['title']

    for row in results:
        email = row[8]
        firstname = row[1]

    msg = Message('Job Taken', sender = 'oddjobsfinder@gmail.com', recipients = [email])
    msg.html = render_template("/declineEmail.html", title = title, job_username = job_username, firstname=firstname)
    mail.send(msg)

    cursor.close()
    db.close()

    return redirect("/", code=302)

@app.route('/accept_user', methods = ['GET', 'POST'])
def accept_user():
    db = pymysql.connect(host='oddjobsfinder.mysql.pythonanywhere-services.com', user='oddjobsfinder', passwd='Rathdrum21', db = 'oddjobsfinder$default')#db = session['db']
    cursor = db.cursor()

    job_id = session['job_id']
    user_id = str(session['user_id'])
    job_username = session['job_username']

    sql = "SELECT * FROM users where userId ='" + user_id + "'"
    cursor.execute(sql)
    results = cursor.fetchall()
    title = session['title']

    for row in results:
        email = row[8]
        firstname = row[1]

    msg = Message('Job Taken', sender = 'oddjobsfinder@gmail.com', recipients = [email])
    msg.body = "Hi, you have been accepted."
    msg.html = render_template("/acceptEmail.html", title = title, job_username = job_username, firstname=firstname)
    mail.send(msg)

    cursor.execute("UPDATE jobs SET takerId = %s, takenFlag = '1' WHERE JobID = %s", (user_id, job_id))
    db.commit()
    
    cursor.close()
    db.close()
    return redirect("/", code=302)

@app.route('/log_out', methods = ['GET', 'POST'])
def log_out():
        session.pop('username', None)
        return redirect("/", code=302)

@app.route('/register', methods = ['GET', 'POST'])
def register():
    db = pymysql.connect(host='oddjobsfinder.mysql.pythonanywhere-services.com', user='oddjobsfinder', passwd='Rathdrum21', db = 'oddjobsfinder$default')
    cursor = db.cursor()

    if request.method == 'POST':
        firstname =  request.form["firstname"]
        lastname =  request.form["lastname"]
        username =  request.form["username"]
        user_type =  request.form["userType"]
        description = request.form['description']
        age =  request.form["age"]
        phone =  request.form["phone"]
        email =  request.form["email"]
        street = request.form["street"]
        town = request.form["town"]
        county = request.form["county"]
        password = request.form["password"]
        
        salt = uuid.uuid4().hex
        hashed_password = hashlib.sha512(password + salt)encode('utf-8').hexdigest()

        print(salt)
        print(hashed_password)

        cursor.execute("INSERT INTO users (firstName, lastName, username, userType, description, age, phone, email, street, town, county, password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (firstname, lastname, username, user_type, description, age, phone, email, street, town, county, password))
        db.commit()

        return redirect("/login", code=302)
    cursor.close()
    db.close()
    return render_template('register.html')

@app.route('/secure_id', methods = ['GET', 'POST'])
def secure_id():
    job_id = request.form['edit_button']
    session['job_id'] = job_id

    return redirect("/edit_job", code=302)

@app.route('/edit_job', methods = ['GET', 'POST'])
def edit_job():
    db = pymysql.connect(host='oddjobsfinder.mysql.pythonanywhere-services.com', user='oddjobsfinder', passwd='Rathdrum21', db = 'oddjobsfinder$default')
    cursor = db.cursor()
    
    if 'username' not in session:
        return redirect("/login", code=302)

    username = session['username']
    user_type = session['user_type']

    if user_type == 'Job Searcher':
        return redirect("/", code=302)
    
    job_id = session['job_id']
    sql = "SELECT * FROM jobs WHERE jobId = " + job_id
    cursor.execute(sql)
    results = cursor.fetchall()
        
    if request.method == 'POST':
        title =  request.form["inputTitle"]
        description =  request.form["description"]
        duration =  request.form["duration"]
        pay =  request.form["pay"]
        catagory =  request.form["catagory"]
        resources_provided = request.form["resourcesProvided"]
        resources_required = request.form["resourcesRequired"]
        phone = request.form["phone"]
        email = request.form["email"]    
        street = request.form["street"]
        town = request.form["town"]
        county = request.form["county"]
        
        cursor.execute("""UPDATE jobs SET title = %s, description = %s, duration = %s, pay = %s, catagory = %s, resourcesProvided = %s,
        resourcesRequired = %s, email = %s, phone = %s, street = %s, town = %s, county = %s WHERE JobID = %s""", (title, description, duration, pay, 
        catagory, resources_provided, resources_required, email, phone, street, town, county, job_id))
        db.commit()

        return redirect("/view_jobs", code=302)
    
    cursor.close()
    db.close()
    return render_template('editJob.html', results=results)

app.secret_key = 'super secret key'
if __name__ == '__main__':
   app.run(debug = True)