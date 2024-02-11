import asyncio

from flask import Flask
from flask import render_template
import sqlite3
import random
from flask import redirect, url_for

from keras.models import load_model  # TensorFlow is required for Keras to work
import cv2  # Install opencv-python
import numpy as np
import time

from flask import request

app = Flask(__name__)
username = None

connection = sqlite3.connect('signlang_user.db', check_same_thread=False)
cursor = connection.cursor()

async def camera(correct_answer):
    time.sleep(1.5)

    # Disable scientific notation for clarity
    np.set_printoptions(suppress=True)

    # Load the model
    model = load_model("keras_model.h5", compile=False)

    # Load the labels
    class_names = open("labels.txt", "r", encoding="utf-8").readlines()

    # CAMERA can be 0 or 1 based on default camera of your computer
    camera = cv2.VideoCapture(0)

    while True:
        # Grab the webcamera's image.
        ret, image = camera.read()

        # Resize the raw image into (224-height,224-width) pixels
        image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)

        # Show the image in a window
        # cv2.imshow("Webcam Image", image)

        # Make the image a numpy array and reshape it to the models input shape.
        image = np.asarray(image, dtype=np.float32).reshape(1, 224, 224, 3)

        # Normalize the image array
        image = (image / 127.5) - 1

        # Predicts the model
        prediction = model.predict(image)
        index = np.argmax(prediction)
        class_name = class_names[index]
        confidence_score = prediction[0][index]

        # Print prediction and confidence score
        print("Class:", class_name[2:], end="")
        print("Correct answer:", correct_answer, correct_answer.split() == class_name[2:].split())
        print("Confidence Score:", str(np.round(confidence_score * 100))[:-2], "%")

        # 27 is the ASCII for the esc key on your keyboard.
        if class_name[2:].split() == correct_answer.split():
            break

        time.sleep(1.5)

    camera.release()
    cv2.destroyAllWindows()


@app.route('/')
def main_page():
    return render_template('main_page.html')


@app.route('/home/<username>')
def home(username):
    lesson_num = cursor.execute('SELECT next_lesson_num FROM users_information WHERE nickname=?', (username,)).fetchall()[0][0]
    if lesson_num != '':
        return render_template('homepage.html', lesson_num=lesson_num, username=username)


@app.route('/lesson/<lesson_num>/<task_num>/<username>', methods=["GET", "POST"])
async def lesson(lesson_num, task_num, username):
    try:
        cursor.execute('SELECT * FROM tasks WHERE complexity = ? AND id = ?', (int(lesson_num), int(task_num)))
        lesson = cursor.fetchall()[0]
        counter = 0
        correct_answer = lesson[3]
        if lesson[2] == 'camera':
            task = asyncio.create_task(camera(correct_answer))
            await task
            return render_template('lesson_video.html', lesson_num=lesson_num, task_num=int(task_num),
                                   username=username)
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


@app.route('/lesson/<lesson_num>/<task_num>/checking_camera/<username>')
def checking_camera(lesson_num, task_num, username):
    return render_template('checking_camera.html', lesson_num=lesson_num, task_num=int(task_num),
                                           username=username)


@app.route('/user/<username>')
def profil(username):
    try:
        password = cursor.execute(
            f'''SELECT Password FROM users_information WHERE nickname == "{username}"''').fetchall()
        lesson_num = cursor.execute(
            f'''SELECT next_lesson_num FROM users_information WHERE nickname == "{username}"''').fetchall()[0][0]

        return render_template('profil.html', username=username, password=password[0][0], lesson_num=int(lesson_num - 1))
    except BaseException:
        return 'Пользователь не найден'


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

        return redirect(url_for('main_page', main="main"))


@app.route('/enter', methods=['POST', 'GET'])
@app.route('/enter/<ok>', methods=['POST', 'GET'])
def log_in(ok='True'):
    if request.method == 'GET' and ok == 'True':
        return render_template('log_in.html', main='main')
    elif request.method == 'GET' and ok == 'False':
        return render_template('log_in.html', main='mistake')
    elif request.method == 'POST':
        print('asdfghjkl;')
        username = request.form.get('username')
        password = request.form.get('password')

        password_right = cursor.execute(f'''SELECT Password FROM users_information WHERE nickname == "{username}"''').fetchall()
        try:
            print('sagsgfahdfahdfafafa')
            if password_right[0][0] == password:
                print('AAAAAAAAAAAAA')
                return render_template('homepage.html', username=username)
            else:
                return render_template('log_in.html', main='mistake')
        except BaseException:
            return render_template('log_in.html', main='mistake')



if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
