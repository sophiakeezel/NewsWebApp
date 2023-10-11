from flask import Flask, render_template, url_for
from os import environ
from flask import session
app = Flask(__name__)

app.secret_key = environ.get('SECRET_KEY')  # or set it to a strong random value

# dummy data for testing
news_data = [
    {"title": "News 1", "time": "2023-10-05", "likes": 10, "dislikes": 2, "content": "news1"},
    {"title": "News 2", "time": "2023-10-04", "likes": 8, "dislikes": 1, "content": "news2"},
    {"title": "News 3", "time": "2023-10-04", "likes": 11, "dislikes": 3, "content": "news3"},
    {"title": "News 4", "time": "2023-10-04", "likes": 3, "dislikes": 1, "content": "news4"},
    {"title": "News 5", "time": "2023-10-04", "likes": 6, "dislikes": 2, "content": "news5"},
    {"title": "News 6", "time": "2023-10-04", "likes": 9, "dislikes": 0, "content": "news6"}    
]

user_profile = {"username": "john_doe", "email": "john@example.com"}  # Dummy user profile data

# Route for the Sign Up page
@app.route('/signup')
def signup():
    return render_template('signup.html')  # Render the HTML template for Sign Up

# Route for the Login page
@app.route('/login')
def login():
    return render_template('login.html', news_data=news_data)

# Route for the News Feed page
@app.route('/')
@app.route('/newsfeed')
def newsfeed():
    return render_template('newsfeed.html', news_data=news_data)

# Route for the Profile page
@app.route('/profile')
def profile():
    return render_template('profile.html', user_profile=user_profile)

# Route for the Admin page
@app.route('/admin')
def admin():
    return render_template('admin.html')

if __name__ == '__main__':
    app.run(debug=True)

