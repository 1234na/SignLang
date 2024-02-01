from flask import Flask
from flask import render_template
import sqlite3
import random
from flask import redirect, url_for

from flask import request
# from camera import SignLang

app = Flask(__name__)
username = None

connection = sqlite3.connect('signlang_user.db', check_same_thread=False)
cursor = connection.cursor()


@app.route('/')
def home():
    return 'HOMEPAGE'


@app.route('/lesson/<lesson_num>/<task_num>/<username>', methods=["GET", "POST"])
def lesson(lesson_num, task_num, username):
    try:
        cursor.execute('SELECT * FROM tasks WHERE complexity = ? AND id = ?', (int(lesson_num), int(task_num)))
        lesson = cursor.fetchall()[0]
        counter = 0
        correct_answer = lesson[3]
        if lesson[2] == 'camera':
            if request.method == 'GET':
                return render_template('lesson_video.html', lesson_num=lesson_num, task_num=int(task_num),
                                       username=username)

            if request.method == 'POST':
                return 'AAAAAAAAAAAAAAAAAAAAA'

        else:
            buttons = list(lesson[3:])
            random.shuffle(buttons)

            if request.method == 'GET':
                return render_template('lesson.html', lesson_num=lesson_num, task_image='images/gestures/' + lesson[2],
                                       button_1=buttons[0],
                                       button_2=buttons[1], button_3=buttons[2], button_4=buttons[3],
                                       task_num=int(task_num), username=username)

            if request.method == 'POST':
                answer = request.form.get("answer")
                if answer == correct_answer:
                    n = buttons.index(correct_answer) + 1
                    counter += 1
                    return render_template('checking_answer_right.html', lesson_num=lesson_num, task_num=int(task_num),
                                           username=username)

                else:
                    n = buttons.index(answer)
                    return render_template('checking_answer_false.html', lesson_num=lesson_num, task_num=int(task_num),
                                           username=username)
    except BaseException:
        if (int(lesson_num) + 1,) in cursor.execute('SELECT complexity FROM tasks').fetchall():
            cursor.execute('UPDATE users_information SET next_lesson_num=? WHERE nickname=?', (int(lesson_num) + 1, username))
            connection.commit()
            return redirect(url_for('lesson', lesson_num=int(lesson_num) + 1, task_num=1, username=username))
        else:
            return 'Урок не найден'



@app.route('/user/<username>')
def profil(username):
    try:
        password = cursor.execute(
            f'''SELECT Password FROM users_information WHERE nickname == "{username}"''').fetchall()
        return render_template('profil.html', username=username, password=password[0][0])
    except BaseException:
        return 'Пользователь не найден'


@app.route('/my_lessons/<user_id>')
def lessons(user_id):
    pass


@app.route('/reg', methods=['POST', 'GET'])
def registration():
    if request.method == 'GET':
        return render_template('registration.html')
    elif request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')

        cursor.execute('''INSERT INTO users_information VALUES (?, ?, ?, ?, 1)''', (name, username, email, password))

        connection.commit()
        connection.close()

        return render_template('log_in.html', main='main')


@app.route('/enter', methods=['POST', 'GET'])
@app.route('/enter/<ok>', methods=['POST', 'GET'])
def log_in(ok='True'):
    if request.method == 'GET' and ok == 'True':
        return render_template('log_in.html', main='main')
    elif request.method == 'GET' and ok == 'False':
        return render_template('log_in.html', main='mistake')
    elif request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        password_right = cursor.execute(f'''SELECT Password FROM users_information WHERE nickname == "{username}"''').fetchall()
        try:
            if password_right[0][0] == password:
                return render_template('homepage.html', username=username)
            else:
                return render_template('log_in.html', main='mistake')
        except BaseException:
            return render_template('log_in.html', main='mistake')



if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
