from flask import render_template, url_for, flash, redirect
from app import app
from app import db
from app.forms import RegistrationForm, LoginForm
from app.models import User, Post
from flask import jsonify

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
def newsfeed():
    # Fetch news items from the database and sort them by time and likes/dislikes
    news_items = (
        Post.query.order_by(Post.time.desc(), Post.likes.desc(), Post.dislikes)
        .paginate(page=1, per_page=10, error_out=False)
        .items
    )
    return render_template('newsfeed.html', news_items=news_items)

# Route for the Profile page
@app.route('/profile')
def profile():
    return render_template('profile.html', user_profile=user_profile)

# Route for the Admin page
@app.route('/admin')
def admin():
    return render_template('admin.html')

# route for newsfeed in JSON format
@app.route('/newsfeed', methods=['GET'])  # Note the typo in the route, I kept it as is.
def api_newsfeed():
    # Fetch news items from the database and sort them by time and likes/dislikes
    news_items = Post.query.order_by(Post.time.desc(), Post.likes.desc(), Post.dislikes).limit(10).all()
    
    # Convert the news items to a JSON response
    data = [{
        'id': item.id,
        'title': item.title,
        'time': item.time.strftime('%Y-%m-%d %H:%M:%S'),
        'content': item.content,
        'likes': item.likes,
        'dislikes': item.dislikes
    } for item in news_items]
    
    return jsonify(data)

# logic to like a news post
@app.route('/like/<int:post_id>')
def like(post_id):
    post = Post.query.get_or_404(post_id)
    post.likes += 1
    db.session.commit()
    return redirect(url_for('newsfeed'))

# logic to dislike a news post
@app.route('/dislike/<int:post_id>')
def dislike(post_id):
    post = Post.query.get_or_404(post_id)
    post.dislikes += 1
    db.session.commit()
    return redirect(url_for('newsfeed'))
