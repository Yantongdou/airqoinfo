from flask import Flask, render_template, request, session, redirect, url_for, make_response
import pandas as pd
import pymysql
import datetime
import uuid
import os

login_time = 0
logout_time = 0

db = pymysql.connect(
    host='airqoweb.cugf7jeo6plr.us-west-1.rds.amazonaws.com',
    port=3306,
    user='admin',
    password='airqoweb',
    db='airqoweb',
)
cursor = db.cursor()
firm_info = pd.read_sql('select * from firm_data', con=db)
username_list = list(firm_info['firm_id'])
password_list = list(firm_info['password'])

app = Flask(__name__)

@app.route("/", methods=["POST", "GET"])
def Web():
    if 'username' in request.cookies:
        global log_info
        log_info = list(pd.read_sql('select * from record_2', con=db)['log_index'])
        if request.cookies.get('log_id') not in log_info:
            sql = "insert into record_2 values('%s','%s','%s','%s')" % (request.cookies.get('log_id'), request.cookies.get('username'), request.cookies.get('login_time'), request.cookies.get('logout_time'))
            cursor.execute(sql)
            db.commit()
        return render_template('index.html')
    return redirect("login")


@app.route('/login', methods=["POST", "GET"])
def login():
    username = request.form.get('USERNAME')
    if username in username_list:
        id = uuid.uuid1().hex
        login_time = datetime.datetime.now()
        logout_time = login_time + datetime.timedelta(seconds=3600)
        resp = make_response(redirect(url_for("Web")))
        resp.set_cookie('username', username, max_age=3600)
        resp.set_cookie('log_id', id, max_age=3600)
        resp.set_cookie('login_time', str(login_time), max_age=3600)
        resp.set_cookie('logout_time', str(logout_time), max_age=3600)
        return resp
    return render_template('login.html')

@app.route('/logout', methods=["POST", "GET"])
def logout():
    logout_time = datetime.datetime.now()
    sql = "UPDATE record_2 SET logout = '%s' WHERE log_index = '%s'" % (logout_time, request.cookies.get('log_id'))
    cursor.execute(sql)
    db.commit()
    resp = make_response(redirect(url_for("login")))
    resp.delete_cookie('username')
    resp.delete_cookie('log_id')
    resp.delete_cookie('login_time')
    resp.delete_cookie('logout_time')
    return resp

app.secret_key = os.urandom(24)


if __name__ == '__main__':
    app.run(debug=True, processes=True)
    db.close()
