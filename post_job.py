from flask import Flask, render_template
import pymysql

db = pymysql.connect(host='localhost', user='root', passwd='', db = 'casualJobs3')
app = Flask(__name__)

@app.route('/post_job')
def post_job():
    user_id = "3"
    cursor = db.cursor()
    sql = "SELECT firstName, lastName FROM users where userId =" + user_id
    cursor.execute(sql)
    results = cursor.fetchall()
    return render_template('postJob.html', results=results)

if __name__ == '__main__':
   app.run(debug = True)