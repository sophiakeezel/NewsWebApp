from flask import render_template, url_for, session, redirect, request
from app import app, db, oauth, env
from app.models import User, Post, UserPostAction, Comment
from urllib.parse import urlencode, quote_plus
from flask import jsonify

# ----------------------- Auth0 integration --------------------
# Route for the auth0 callback page
@app.route("/callback", methods=["GET", "POST"])
def callback():
    try:
        # Exchange the authorization code for an access token
        token = oauth.auth0.authorize_access_token()
        # Get the user's profile information
        userinfo_endpoint = f"https://{env.get('AUTH0_DOMAIN')}/userinfo"
        resp = oauth.auth0.get(userinfo_endpoint)
        userinfo = resp.json()

        # Store the user information in flask session
        session["jwt_payload"] = userinfo
        session["profile"] = {
            "user_id": userinfo["sub"],
            "name": userinfo["name"],
            "picture": userinfo["picture"],
            "email": userinfo.get("email")
        }

        # Get or create user in the database
        user = User.query.filter_by(auth0_id=userinfo["sub"]).first()
        if not user:
            # Create a new user object
            new_user = User(
                auth0_id=userinfo["sub"],
                username=userinfo["name"],  
                email=userinfo["email"]
            )
            db.session.add(new_user)
            db.session.commit()
        return redirect('/news')
    except Exception as e:
        print(e)
        return redirect('/news')

# Route for the Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

# logout route for auth0
@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

#------------------- Admin view --------------------------------

@app.route('/admin')
def admin():
    user_id = session.get('profile').get('user_id')
    user = User.query.filter_by(auth0_id=user_id).first()
    if not user or not user.is_admin:  
        return "Access Denied", 403
    
    # Fetch all news items that have been liked or disliked
    news_items = Post.query.join(UserPostAction, Post.id == UserPostAction.post_id).group_by(Post.id).all()

    # Prepare a dictionary to store user actions for each news item
    news_items_with_user_actions = {}
    for item in news_items:
        actions = db.session.query(User.username, UserPostAction.action).join(UserPostAction, User.id == UserPostAction.user_id).filter(UserPostAction.post_id == item.id).all()
        news_items_with_user_actions[item.id] = {
            'post': item,
            'actions': actions
        }
     
    return render_template('admin.html', news_items=news_items_with_user_actions)

#--------------------------- JSON newsfeed route --------------------------

@app.route('/newsfeed', methods=['GET'])  
def api_newsfeed():
    # Fetch news items from the database and sort them by time and likes/dislikes
    news_items = Post.query.order_by(Post.time.desc(), Post.likes.desc(), Post.dislikes).limit(10).all()
    
    # Convert the news items to a JSON response
    data = {
        "news_items": [{
            'by': item.by,
            'descendants': item.descendants,
            'id': item.id,
            'kids': list(map(int, item.kids.split(','))) if item.kids else [],
            'score': item.score,
            'text': item.content,
            'time': int(item.time.timestamp()),
            'title': item.title,
            'type': item.type,
            'url': item.url
        } for item in news_items]
    }
    
    return jsonify(data)

#--------------------- Home page----------------------------

@app.route("/")
def home():
    if 'profile' not in session:
        # If the user is not logged in, redirect them to the login page
        return redirect(url_for('login'))
    return redirect(url_for('newsfeed'))  # Redirect to the 'newsfeed' route


# -------------------- News page and functionality --------------------------

@app.route('/news')
def newsfeed():
    comments = (Comment.query
                .join(User, User.id == Comment.user_id)
                .add_columns(User.email, User.username, Comment.text, Comment.timestamp)
                .order_by(Comment.timestamp.desc())
                .limit(10)
                .all())
    user_id = session.get('profile', {}).get('user_id')
    # Fetch news items from the database and sort them by time and likes/dislikes
    news_items = (
        Post.query.order_by(Post.time.desc(), Post.likes.desc(), Post.dislikes)
        .paginate(page=1, per_page=10, error_out=False)
        .items
    )

    # Fetch user's actions on these posts
    user_actions = UserPostAction.query.filter_by(user_id=user_id).all()
    user_actions_map = {action.post_id: action.action for action in user_actions}

    # Add user-specific like/dislike information to each news item
    for item in news_items:
        item.user_action = user_actions_map.get(item.id, None)

    # display admin tab when user is an admin
    is_admin = False
    user_id = session.get('profile', {}).get('user_id')
    if user_id:
        user = User.query.filter_by(auth0_id=user_id).first()
        if user and user.is_admin:
            is_admin = True

    return render_template('newsfeed.html', news_items=news_items, comments=comments, is_admin=is_admin)

# edit news posts for admin view
@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)

    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        post.keywords = request.form.get('keywords', '')  
        db.session.commit()
        return redirect(url_for('admin'))

    return render_template('edit_post.html', post=post) # go to edit_post route


# ----------------------- Post comments/likes/dislikes -------------------
# logic to like a news post
@app.route('/like/<int:post_id>')
def like(post_id):
    user_id = session.get('profile').get('user_id')
    action = UserPostAction.query.filter_by(user_id=user_id, post_id=post_id).first()

    if action:
        if action.action == 'like':
            # User already liked, so undo the like
            db.session.delete(action)
            Post.query.get(post_id).likes -= 1
        else:
            # User had disliked, now likes
            action.action = 'like'
            Post.query.get(post_id).likes += 1
            Post.query.get(post_id).dislikes -= 1
    else:
        # New like
        new_action = UserPostAction(user_id=user_id, post_id=post_id, action='like')
        db.session.add(new_action)
        Post.query.get(post_id).likes += 1

    db.session.commit()
    return redirect(url_for('newsfeed'))


# logic to dislike a news post
@app.route('/dislike/<int:post_id>')
def dislike(post_id):
    user_id = session.get('profile').get('user_id')
    action = UserPostAction.query.filter_by(user_id=user_id, post_id=post_id).first()

    if action:
        if action.action == 'dislike':
            # User already liked, so undo the like
            db.session.delete(action)
            Post.query.get(post_id).dislikes -= 1
        else:
            # User had disliked, now likes
            action.action = 'dislike'
            Post.query.get(post_id).dislikes += 1
            Post.query.get(post_id).likes -= 1
    else:
        # New like
        new_action = UserPostAction(user_id=user_id, post_id=post_id, action='dislike')
        db.session.add(new_action)
        Post.query.get(post_id).dislikes += 1

    db.session.commit()
    return redirect(url_for('newsfeed'))

@app.route('/post/<int:post_id>/likes')
def post_likes(post_id):
    user_likes = db.session.query(User.username).join(UserPostAction, User.id == UserPostAction.user_id).filter(UserPostAction.post_id == post_id, UserPostAction.action == 'like').all()
    return jsonify([user.username for user in user_likes])

@app.route('/post/<int:post_id>/dislikes')
def post_dislikes(post_id):
    user_dislikes = db.session.query(User.username).join(UserPostAction, User.id == UserPostAction.user_id).filter(UserPostAction.post_id == post_id, UserPostAction.action == 'dislike').all()
    return jsonify([user.username for user in user_dislikes])

# logic to post comments in the comment section of the news page
@app.route('/post_comment', methods=['POST'])
def post_comment():
    if 'profile' not in session:
        # Redirect to login page or handle unauthorized access
        return redirect(url_for('login'))

    user_id = session['profile']['user_id']
    comment_text = request.form['comment']

    if comment_text:
        # Create a new comment
        new_comment = Comment(user_id=user_id, text=comment_text)
        db.session.add(new_comment)
        db.session.commit()

    return redirect(url_for('newsfeed'))

# logic to delete a post in the admin view
@app.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    # Verify if the user is an admin
    user_id = session.get('profile').get('user_id')
    user = User.query.filter_by(auth0_id=user_id).first()
    if not user or not user.is_admin:
        return "Access Denied", 403

    # Find the post and delete it
    post_to_delete = Post.query.get_or_404(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()

    # Redirect to the admin page
    return redirect(url_for('admin'))

#--------------------- Profile page ---------------------------
@app.route('/profile')
def profile():
    user_id = session.get('profile').get('user_id') # get user information
    user_info = session.get('profile', None)
    liked_posts = UserPostAction.query.filter_by(user_id=user_id, action='like').all()

    # display admin tab if the user is an admin
    is_admin = False
    user_id = session.get('profile', {}).get('user_id')
    if user_id:
        user = User.query.filter_by(auth0_id=user_id).first()
        if user and user.is_admin:
            is_admin = True
    return render_template('profile.html', user_profile=user_info, liked_posts=liked_posts, is_admin=is_admin)

