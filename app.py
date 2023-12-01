import flask
from flask import Flask, render_template, request, url_for, redirect, flash, session
from flask_session import Session
import mysql.connector

connect = mysql.connector.connect(host="localhost",
                                  user="greg",
                                  password="Password123#@!",
                                  database='myexampledb')
cursor = connect.cursor()

app = Flask(__name__)
app.secret_key = 'super secret key'

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)


@app.route('/', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['Email']
        password = request.form['Password']
        cursor.execute('SELECT PersonID, Email, Password FROM login where Email=%s AND Password=%s', (email, password))
        record = cursor.fetchone()  # zwracany jak krotka (tuple)
        if record:
            PersonID = record[0]
            session['id'] = PersonID
            return redirect(url_for('content', PersonID=PersonID))
        else:
            flash('Incorrect password or no user')
            return render_template('login.html')
    return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form.get('Email')
        password = request.form.get('Password')
        password2 = request.form.get('Password2')
        cursor.execute("SELECT Email From login where Email='{}'".format(email))
        check_email = cursor.fetchone()
        if check_email:
            flash('User is already register')
        else:
            if password != password2:
                flash('Incorrect retype password')
                return render_template('register.html')
            else:
                cursor.execute("INSERT INTO login (Email, Password) VALUES ('{}', '{}')".format(email, password))
                connect.commit()
                flash('Success, congratulation!')
                return render_template('login.html')
    return render_template('register.html')


@app.route('/user/<int:PersonID>')
def content(PersonID):
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_{} 
    (Task_ID int NOT NULL AUTO_INCREMENT, 
    Title varchar(255), 
    Task varchar(255),
    PRIMARY KEY (Task_ID))'''.format(PersonID))
    connect.commit()

    return redirect(url_for('task', PersonID=PersonID))


@app.route('/user/<int:PersonID>/task')
def task(PersonID):
    if 'id' in session:
        pid = int(session['id'])
        if pid == PersonID:
            cursor.execute("SELECT * FROM user_{}".format(PersonID))
            post_record = cursor.fetchall()
            return render_template('content.html', post_record=post_record, PersonID=PersonID)
        else:
            flash('No permissions to view other users!')
            return render_template('none.html')
    else:
        return flask.redirect('/')


@app.route('/user/<int:PersonID>/task/delete/<string:Task_ID>', methods=['POST', 'GET'])
def delete(PersonID, Task_ID):
    cursor.execute("DELETE from user_{} WHERE Task_ID={}".format(PersonID, Task_ID))
    connect.commit()
    return redirect(url_for('content', PersonID=PersonID))


@app.route('/user/<int:PersonID>/task/update/<int:Task_ID>/<string:Title>/<string:Task>', methods=['POST', 'GET'])
def update(PersonID, Task_ID, Title, Task):
    if request.method == 'POST':
        newTitle = request.form.get('Title')
        newTask = request.form.get('Task')
        cursor.execute(
            "UPDATE user_{} SET Title='{}', Task='{}' WHERE Title='{}' AND Task='{}' AND Task_ID='{}'".format(PersonID,
                                                                                                              newTitle,
                                                                                                              newTask,
                                                                                                              Title,
                                                                                                              Task,
                                                                                                              Task_ID))
        return redirect(url_for('content', PersonID=PersonID))
    return render_template('update.html', PersonID=PersonID, Task_ID=Task_ID, Title=Title, Task=Task)


@app.route('/user/<int:PersonID>/task/add', methods=['POST', 'GET'])
def add(PersonID):
    if 'id' in session:
        pid = int(session['id'])
        if pid == PersonID:
            if request.method == 'POST':
                addTitle = request.form.get('addTitle')
                addTask = request.form.get('addTask')
                cursor.execute("INSERT INTO user_{} (Title, Task) VALUES ('{}', '{}')".format(PersonID,
                                                                                              addTitle,
                                                                                              addTask))
                connect.commit()
                return redirect(url_for('content', PersonID=PersonID))

            return render_template('add.html', PersonID=PersonID)





@app.route("/logout")
def logout():
    session['id'] = None
    return redirect("/")



if __name__ == '__main__':
    app.run(debug=True)
