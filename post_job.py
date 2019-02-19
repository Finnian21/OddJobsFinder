from flask import Flask, render_template, url_for, escape, request, redirect
import pymysql

db = pymysql.connect(host='localhost', user='root', passwd='', db = 'casualJobs3')
app = Flask(__name__)
cursor = db.cursor()

user_id = "2"

@app.route('/post_job', methods = ['GET', 'POST'])
def post_job():

    sql = "SELECT firstName, lastName FROM users where userId =" + user_id
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
            sql1 = "SELECT phone, email FROM users where userId =" + user_id
            cursor.execute(sql1)
            results2 = cursor.fetchall()
            
            for row in results2:
                phone = row[0]
                email = row[1]

        if checked2 == ['on']:
            street = request.form["street"]
            town = request.form["town"]
            county = request.form["county"] 
 
        else:
            sql2 = "SELECT street, town, county FROM users where userId =" + user_id
            cursor.execute(sql2)
            results3 = cursor.fetchall()
            
            for row in results3:
                street = row[0]
                town = row[1]
                county = row[2]

        cursor.execute("INSERT INTO jobs (title, UserID, description, duration, pay, catagory, resourcesProvided, resourcesRequired, email, phone, street, town, county) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (title, user_id, description, duration, pay, catagory, resources_provided, resources_required, email, phone, street, town, county))
        db.commit()

        cursor.execute("UPDATE users SET JobsPosted = JobsPosted + 1 WHERE userID = %s", (user_id))
        db.commit()

        return redirect("/view_job", code=302)

    return render_template('postJob.html', results=results)

@app.route('/view_job', methods = ['GET', 'POST'])
def view_job():
        rowCount = '9'

        sql2 = "SELECT * FROM jobs INNER JOIN users ON jobs.UserID=users.userId WHERE JobID <=" + rowCount
        cursor.execute(sql2)
        results2 = cursor.fetchall()
        return render_template('viewJob.html', results2 = results2)

if __name__ == '__main__':
   app.run(debug = True)