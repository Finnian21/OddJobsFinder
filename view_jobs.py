from flask import Flask, render_template, url_for, escape, request
import pymysql

db = pymysql.connect(host='localhost', user='root', passwd='', db = 'casualJobs3')
app = Flask(__name__)
cursor = db.cursor()

@app.route('/view_job')
def post_job():
    
    sql = "SELECT * FROM jobs"
    cursor.execute(sql)
    results = cursor.fetchall()

    print(results)

    return render_template('viewJob.html')

if __name__ == '__main__':
   app.run(debug = True)