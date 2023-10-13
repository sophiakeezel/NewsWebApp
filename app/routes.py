from flask import render_template, url_for, flash, redirect
from app import app
from app.forms import RegistrationForm, LoginForm
from app.models import User, Post

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
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('newsfeed'))
    return render_template('signup.html', title='Register', form=form)  

# Route for the Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('newsfeed'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

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


