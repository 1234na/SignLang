from flask import Flask
from flask import render_template
import sqlite3

# from flask import request
# from camera import SignLang

app = Flask(__name__)
username = None

connection = sqlite3.connect('signlang_user.db', check_same_thread=False)
cursor = connection.cursor()

@app.route('/')
def home():
    return 'HOMEPAGE'

@app.route('/lesson/<lesson_num>')
def lesson(lesson_num):
    cursor.execute('SELECT * FROM tasks WHERE id = ?', (int(lesson_num),))
    lesson = cursor.fetchall()[0]
    return render_template('lesson.html', lesson_num=lesson_num, task_image=lesson[2], correct_answer=lesson[3])

@app.route('/user/<username>')
def profil(username):
    return render_template('profil.html', username=username)

@app.route('/my_lessons/<user_id>')
def lessons(user_id):
    pass


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
