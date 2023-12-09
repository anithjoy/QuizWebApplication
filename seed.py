from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['quiz_app']
quizzes_collection = db['quizzes']

# Sample seed data
sample_quizzes = [
    {
        'title': 'General Knowledge',
        'questions': [
            {'question': 'What is the capital of France?', 'options': ['Berlin', 'Madrid', 'Paris'], 'correct_option': 'Paris'},
            {'question': 'Which planet is known as the Red Planet?', 'options': ['Venus', 'Mars', 'Jupiter'], 'correct_option': 'Mars'},
        ]
    },
    {
        'title': 'Python Programming',
        'questions': [
            {'question': 'What is the purpose of the "elif" keyword in Python?', 'options': ['Else If', 'End Loop If', 'Exclusive If'], 'correct_option': 'Else If'},
            {'question': 'Which of the following is a mutable data type in Python?', 'options': ['Tuple', 'List', 'String'], 'correct_option': 'List'},
        ]
    },
    # Add more sample quizzes
]

# Insert sample quizzes into MongoDB
for quiz in sample_quizzes:
    quizzes_collection.insert_one(quiz)

print("Sample quizzes and questions inserted successfully.")
