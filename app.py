from flask import Flask, render_template, request, redirect, url_for,session
from pymongo import MongoClient
from bson import ObjectId
import bcrypt

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
client = MongoClient('mongodb://localhost:27017/')
db = client['quiz_app']
quizzes_collection = db['quizzes']
users_collection = db['users']

def calculate_score(user_answers, quiz_id):
    quiz_id_object = ObjectId(quiz_id)
    quiz = quizzes_collection.find_one({'_id': quiz_id_object})

    correct_answers = [question['correct_option'] for question in quiz['questions']]
    user_score = 0
    i = 0
    for question in quiz["questions"]:
        user_answer_key = question["question"]
        user_answer = user_answers.get(user_answer_key)

        if user_answer and user_answer == correct_answers[i]:
            user_score += 1
        i = i + 1
    return (user_score,i,quiz['title'])
@app.route('/')
def home():
   # Check if the user is authenticated
    if 'username' in session:
        print(session)
        quizzes = list(quizzes_collection.find())
        for obj in quizzes:
            obj['_id'] = str(obj['_id'])
        return render_template('index.html', quizzes=quizzes,role=session['role'])
    else:
        # Redirect to the login page if the user is not authenticated
        return redirect(url_for('login'))

@app.route('/addQuiz', methods=['GET', 'POST'])
def add_quiz():
    print(request.form)
    if request.method == 'POST':
        
        quiz_data = {
            'title': request.form['quiz_title'],
            'questions': []
        }
        print("quiz_data",quiz_data)
        # Extract questions and options dynamically
        question_keys = [key for key in request.form.keys() if key.startswith('question')]
        for key in question_keys:
            question_number = key.replace('question', '')
            options_key = f'options{question_number}'
            correct_option_key = f'correct_option{question_number}'
        
            question_data = {
                'question': request.form[key],
                'options': request.form[options_key].split(','),
                'correct_option': request.form[correct_option_key]
            }

            quiz_data['questions'].append(question_data)
            # print(quiz_data)

        print("quiz_data",quiz_data)

        # Insert quiz into MongoDB
        quiz_id = quizzes_collection.insert_one(quiz_data).inserted_id

        return redirect('/')

    return render_template('create_quiz.html')

@app.route('/quiz/<string:quiz_id>')
def take_quiz(quiz_id):
    quiz_id_object = ObjectId(quiz_id)
    
    # Retrieve quiz from MongoDB
    quiz = quizzes_collection.find_one({'_id': quiz_id_object})
    return render_template('quiz.html', quiz=quiz)

@app.route('/submit_quiz/<string:quiz_id>', methods=['POST'])
def submit_quiz(quiz_id):

    # Handle form submission and calculate the score
    # Retrieve user answers from the form data (request.form)
    # Compare user answers with correct answers in the database
    # Calculate the score and any other relevant information

    # For simplicity, let's assume a function calculate_score() is defined
    # which takes user answers and correct answers and returns the score
    score,number_of_questions,title = calculate_score(request.form, quiz_id)

    result = users_collection.update_one(
        {'_id': ObjectId(session['id']), 'scores.quiz_title': title},
        {'$set': {'scores.$.score': score, 'scores.$.totalQuestions': number_of_questions}},
        upsert=False
    )

    if result.matched_count == 0:
        users_collection.update_one(
        {'_id':ObjectId(session['id'])},
        {'$push': {'scores': {'quiz_title': title, 'score': score,'totalQuestions': number_of_questions}}},
        upsert=True
    )
    
    return render_template('score.html', score=score)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        # Hash the password before storing it
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Check if the username is already taken
        if users_collection.find_one({'username': username}):
            return 'Username already exists. Please choose another username.'

        # Insert the new user into the database with the specified role
        users_collection.insert_one({'username': username, 'password': hashed_password, 'role': role})

        # Redirect to login page after successful registration
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Retrieve user from the database
        user = users_collection.find_one({'username': username})

        # Check if the user exists and the password is correct
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            # Store the user's username in the session
            session['username'] = username
            session['role'] = user['role']
            session['id'] = str(user['_id'])
            return redirect(url_for('home'))
        else:
            return 'Invalid username or password. Please try again.'

    return render_template('login.html')

@app.route('/logout')
def logout():
    # Clear the session to log out the user
    session.clear()

    # Redirect to the login page or another appropriate page
    return redirect(url_for('login'))

@app.route('/chart')
def showchart():
    user = users_collection.find_one({'_id': ObjectId(session['id'])})
    quiz_data = user['scores']
    userScores = []
    quizName = []
    for quiz in quiz_data:
        quizName.append(quiz["quiz_title"])
        percentage = float(quiz["score"])/float(quiz["totalQuestions"])
        percentage = percentage * 100
        userScores.append(percentage)

    
    return render_template('chart.html',userScores = userScores,quizName = quizName)


if __name__ == '__main__':
    app.run(debug=True)



