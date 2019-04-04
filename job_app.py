from flask import Flask, render_template, url_for, escape, request, redirect, session, flash
from flask_mail import Mail, Message
import datetime
import pymysql
import hashlib, uuid
import random
import crypt

app = Flask(__name__)
mail=Mail(app)

#db = pymysql.connect(host='oddjobsfinder.mysql.pythonanywhere-services.com', user='oddjobsfinder', passwd='Rathdrum21', db = 'oddjobsfinder$default')

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

        cursor.execute("SELECT salt from users Where username = '" + username + "'")
        results = cursor.fetchall()

        for row in results:
            the_salt = row[0]

        password = hashlib.sha256(password.encode()+ the_salt.encode()).hexdigest()

        sql = "SELECT * from users where username='" + username + "' and password='" + password + "'"
        cursor.execute(sql)

        if cursor.fetchone() is None:
            error = 'Invalid Credentials. Please try again.'
        else:
            session['username'] = username
            sql2 = "SELECT userId, userType from users where username='" + username + "'"
            cursor.execute(sql2)
            results = cursor.fetchall()
            
            for row in results:
                session['user_type'] = row[1]
                session['user_id'] = row[0]

            if 'url' in session:
                return redirect(session['url'], code=302)

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
    
    #session['user_id'] = the_user_Id

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

@app.route('/view_taken_jobs', methods = ['GET', 'POST'])
def view_taken_jobs():

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
        
        session['user_id'] = the_user_Id

        sql2 = "SELECT * FROM jobs INNER JOIN users ON jobs.UserID=users.userId WHERE takerId = '" + str(the_user_Id) + "'ORDER BY timeStampPosted DESC"
        cursor.execute(sql2)
        results2 = cursor.fetchall()
        
        current_time = datetime.datetime.now()

        for row in results2:
            session['job_id'] = row[2]
            elapsed_time = current_time - row[7]

        return render_template('viewTakenJobs.html', results2 = results2, the_user_Id = the_user_Id, current_time = current_time, user_type = user_type)
    
    else:
        session['url'] = '/view_taken_jobs'
        return redirect("/login", code=302)

    cursor.close()
    db.close()

    return render_template('viewTakenJobs.html')

@app.route('/view_my_jobs', methods = ['GET', 'POST'])
def view_my_jobs():

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
        
        session['user_id'] = the_user_Id

        sql2 = "SELECT * FROM jobs INNER JOIN users ON jobs.UserID=users.userId WHERE jobs.userId = '" + str(the_user_Id) + "' ORDER BY timeStampPosted DESC"
        print(sql2)
        cursor.execute(sql2)
        results2 = cursor.fetchall()
        
        current_time = datetime.datetime.now()

        for row in results2:
            session['job_id'] = row[2]
            elapsed_time = current_time - row[7]

        return render_template('viewMyJobs.html', results2 = results2, the_user_Id = the_user_Id, current_time = current_time, user_type = user_type)
    
    else:
        session['url'] = '/view_my_jobs'
        return redirect("/login", code=302)

    cursor.close()
    db.close()

    return render_template('viewMyJobs.html')

@app.route('/view_applied_users', methods = ['GET', 'POST'])
def view_applied_users():

    db = pymysql.connect(host='oddjobsfinder.mysql.pythonanywhere-services.com', user='oddjobsfinder', passwd='Rathdrum21', db = 'oddjobsfinder$default')
    cursor = db.cursor()

    if 'username' in session: 
        username = session['username']
        user_type = session['user_type']
        user_id = str(session['user_id'])
        job_id = str(session['job_id'])

        sql2 = "SELECT * FROM jobRequests INNER JOIN users ON jobRequests.userID=users.userId WHERE jobRequests.jobId = '" + job_id + "'"
        cursor.execute(sql2)
        results2 = cursor.fetchall()

        return render_template('viewAppliedUsers.html', results2 = results2)
    
    else:
        session['url'] = '/view_applied_users'
        return redirect("/login", code=302)

    cursor.close()
    db.close()

    return render_template('viewAppliedUsers.html')

@app.route('/secure_job_id', methods = ['GET', 'POST'])
def secure_job_id():
    
    if request.method == 'POST':
        job_id = request.form['view_button']
        session['job_id'] = job_id
        return redirect("/view_job", code = 302)

@app.route('/view_job', methods = ['GET', 'POST'])
def view_job():
    db = pymysql.connect(host='oddjobsfinder.mysql.pythonanywhere-services.com', user='oddjobsfinder', passwd='Rathdrum21', db = 'oddjobsfinder$default')
    cursor = db.cursor()

    job_id = session['job_id']
    sql = "SELECT * FROM jobs INNER JOIN users ON jobs.UserID=users.userId WHERE jobId = " + str(job_id)
    cursor.execute(sql)
    results = cursor.fetchall()

    for row in results:
        session['firstname'] = row[18]
        session['job_username'] = row[20]

    session['results'] = results

    if 'username' in session:
        username = session['username']
        user_Id = session['user_id']
        user_type = session['user_type']
    else:
        user_Id = 0
        user_type = ""
        username = ""
    
    cursor.execute("SELECT * FROM jobRequests WHERE userId = %s AND jobId = %s", (user_Id, job_id))
    take_count = cursor.fetchone()

    if request.method == 'POST':
        body =  request.form["comment"]
        time_stamp_posted = datetime.datetime.now()

        cursor.execute("""INSERT INTO comments (userId, jobId, body, timePosted) 
        VALUES (%s, %s, %s, %s)""", (user_Id, job_id, body, time_stamp_posted))
        db.commit()

        return redirect("/view_job", code = 302)

    sql2 = "SELECT * FROM comments INNER JOIN users ON comments.UserID=users.userId WHERE jobId = '" + str(job_id) + "'ORDER BY timePosted DESC"
    cursor.execute(sql2)
    results2 = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('viewJob.html' , results=results, results2=results2, user_type = user_type, user_Id = user_Id, take_count = take_count, username = username)

@app.route('/', methods = ['GET', 'POST'])
def home():
    db = pymysql.connect(host='oddjobsfinder.mysql.pythonanywhere-services.com', user='oddjobsfinder', passwd='Rathdrum21', db = 'oddjobsfinder$default')
    cursor = db.cursor()
    
    if 'username' in session: 
        username = session['username']
        user_type = session['user_type']
        sql = "SELECT * FROM users Where username = '" + username + "'"
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            session['user_id'] = row[0]
    else:
        username = ''
        user_type = ''

    cursor.close()
    db.close()
        
    return render_template('home.html', username = username, user_type = user_type)

@app.route('/take_job', methods = ['GET', 'POST'])
def take_job():
    db = pymysql.connect(host='oddjobsfinder.mysql.pythonanywhere-services.com', user='oddjobsfinder', passwd='Rathdrum21', db = 'oddjobsfinder$default')#db = session['db']
    cursor = db.cursor()

    if 'username' in  session:

        if session['user_type'] == 'Job Poster':
            return redirect('/', code=302)

        results = session['results']
        job_id = session['job_id']
        username = session['username']
        user_id = str(session['user_id'])
        firstname = session['firstname']
        job_username = session['job_username']

        cursor.execute("SELECT * FROM jobRequests WHERE userId = %s AND jobId = %s", (user_id, job_id))
        take_count = cursor.fetchone()

        if take_count is not None:
            return redirect("/view_jobs", code = 302)
        
        sql = "SELECT * FROM jobs where jobId ='" + str(job_id) + "'"
        cursor.execute(sql)
        results = cursor.fetchall()
        
        for row in results:
            email = row[10]
            title = row[1]
        session['title'] = title

        msg = Message('Job Taken', sender = 'oddjobsfinder@gmail.com', recipients = [email])
        msg.body = "Hi, your job titled " + title + " has been taken by " + username + "."
        msg.html = render_template("/email.html", title=title, username=username, firstname=firstname, job_id=job_id, user_id=user_id)
        mail.send(msg)

        cursor.execute("INSERT INTO jobRequests (jobID, userId) VALUES (%s, %s)", (job_id, user_id))
        db.commit()

    else:
        session['url'] = '/take_job'
        return redirect("/login", code=302)

    cursor.close()
    db.close()

    return render_template('takeJob.html', results = results)

@app.route('/accept_user', methods = ['GET', 'POST'])
def accept_user():

    db = pymysql.connect(host='oddjobsfinder.mysql.pythonanywhere-services.com', user='oddjobsfinder', passwd='Rathdrum21', db = 'oddjobsfinder$default')#db = session['db']
    cursor = db.cursor()
    applicant_id = request.form['accept_button']
    job_id = session['job_id']

    print(session['username'])
"""
    sql = "SELECT * FROM jobs where jobId ='" + str(job_id) + "'"
    cursor.execute(sql)
    results = cursor.fetchall()

    for row in results:
        title = row[1]
    
    msg = Message('Accepted', sender = 'oddjobsfinder@gmail.com', recipients = [email])
    msg.html = render_template("/acceptEmail", title=title, username=username, firstname=firstname)
    mail.send(msg)
"""

    return "sent"

@app.route('/log_out', methods = ['GET', 'POST'])
def log_out():
        session.pop('username', None)
        session.pop('url', None)
        return redirect("/", code=302)

@app.route('/register', methods = ['GET', 'POST'])
def register():
    db = pymysql.connect(host='oddjobsfinder.mysql.pythonanywhere-services.com', user='oddjobsfinder', passwd='Rathdrum21', db = 'oddjobsfinder$default')
    cursor = db.cursor()
    error = None

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
        
        the_salt = crypt.mksalt(crypt.METHOD_SHA256)
        password = hashlib.sha256(password.encode()+ the_salt.encode()).hexdigest()
        
        cursor.execute("SELECT salt from users Where username = '" + username + "'")
        
        if cursor.fetchone() is not None:
            error = 'Credentials invalid, please enter different credentials.'
        else:
            cursor.execute("INSERT INTO users (firstName, lastName, username, userType, description, age, phone, email, street, town, county, password, salt) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (firstname, lastname, username, user_type, description, age, phone, email, street, town, county, password, the_salt))
            db.commit()
            flash("Registered")

            return redirect("/login", code=302)

    cursor.close()
    db.close()
    return render_template('register.html', error = error)

@app.route('/secure_id', methods = ['GET', 'POST'])
def secure_id():
    job_id = request.form['edit_button']
    session['job_id'] = job_id

    return redirect("/edit_job", code=302)

@app.route('/secure_job_id_applied', methods = ['GET', 'POST'])
def secure_id_applied():
    job_id = request.form['applied_button']
    session['job_id'] = job_id
    return redirect("/view_applied_users", code=302)

@app.route('/edit_job', methods = ['GET', 'POST'])
def edit_job():
    db = pymysql.connect(host='oddjobsfinder.mysql.pythonanywhere-services.com', user='oddjobsfinder', passwd='Rathdrum21', db = 'oddjobsfinder$default')
    cursor = db.cursor()
    user_type = session['user_type']

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
    return render_template('editJob.html', results=results, user_type = user_type)

@app.route('/edit_profile', methods = ['GET', 'POST'])
def edit_profile():
    db = pymysql.connect(host='oddjobsfinder.mysql.pythonanywhere-services.com', user='oddjobsfinder', passwd='Rathdrum21', db = 'oddjobsfinder$default')
    cursor = db.cursor()
    
    if 'username' not in session:
        return redirect("/login", code=302)

    username = session['username']
    user_type = session['user_type']
    user_Id = session['user_id']
    
    job_id = session['job_id']
    sql = "SELECT * FROM users WHERE userId = " + str(user_Id)
    cursor.execute(sql)
    results = cursor.fetchall()
        
    if request.method == 'POST':
        firstname =  request.form["firstname"]
        lastname =  request.form["lastname"]
        username =  request.form["username"]
        description =  request.form["description"]
        age =  request.form["age"]
        phone = request.form["phone"]
        email = request.form["email"]    
        street = request.form["street"]
        town = request.form["town"]
        county = request.form["county"]
        
        cursor.execute("""UPDATE users SET firstname = %s, lastname = %s, username = %s, description = %s, age = %s, phone = %s, email = %s, street = %s, town = %s, county = %s WHERE userId = %s""", 
        (firstname, lastname, username, description, age, phone, email, street, town, county, user_Id))
        db.commit()

        return redirect("/view_profile", code=302)
    
    cursor.close()
    db.close()
    return render_template('editProfile.html', results=results, user_type = user_type)

@app.route('/view_profile', methods = ['GET', 'POST'])
def view_profile():
    db = pymysql.connect(host='oddjobsfinder.mysql.pythonanywhere-services.com', user='oddjobsfinder', passwd='Rathdrum21', db = 'oddjobsfinder$default')
    cursor = db.cursor()

    user_id = session['user_id']
    user_type = session['user_type']

    sql = "SELECT * from users where userId = '" + str(user_id) + "'"
    cursor.execute(sql)
    results = cursor.fetchall()

    if 'username' not in session:
        return redirect("/", code=302)
    
    cursor.close()
    db.close()
    return render_template('viewProfile.html', results = results, user_type = user_type)

@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

app.secret_key = 'super secret key'
if __name__ == '__main__':
   app.run(debug = True)