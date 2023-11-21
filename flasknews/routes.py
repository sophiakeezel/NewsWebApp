from flask import Blueprint, render_template, url_for, session, redirect, request
from flasknews import db, oauth, env
from flasknews.models import User, Post, UserPostAction, Comment
from urllib.parse import urlencode, quote_plus
from flask import jsonify

routes = Blueprint('routes', __name__)

# functon for displaying admin tab when user is an admin
def is_administator():
    is_admin = False
    user_id = session.get('profile', {}).get('user_id')
    if user_id:
        user = User.query.filter_by(auth0_id=user_id).first()
        if user and user.is_admin:
            is_admin = True
    
    return is_admin

#function to get user comments
def all_comments():
    return Comment.query.all()

# ----------------------- Auth0 integration --------------------
# Route for the auth0 callback page
@routes.route("/callback", methods=["GET", "POST"])
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
            try:
                db.session.commit()
            except Exception as e:
                print(f"Error adding user to database: {e}")
                db.session.rollback()
            
        return redirect('/news')
    except Exception as e:
        print(e)
        return redirect('/news')

# Route for the Login page
@routes.route('/login', methods=['GET', 'POST'])
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("routes.callback", _external=True)
    )

# logout route for auth0
@routes.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("routes.home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

#------------------- Admin view --------------------------------

@routes.route('/admin')
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
     
    return render_template('admin.html', news_items=news_items_with_user_actions, is_admin=is_administator(), comments=all_comments())

# logic to delete a post in the admin view
@routes.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    # Verify if the user is an admin
    user_id = session.get('profile').get('user_id')
    user = User.query.filter_by(auth0_id=user_id).first()
    if not user or not user.is_admin:
        return "Access Denied", 403

    # Find the post and its related actions
    post_to_delete = Post.query.get_or_404(post_id)
    actions_to_delete = UserPostAction.query.filter_by(post_id=post_id).all()

    # Delete related actions first
    for action in actions_to_delete:
        db.session.delete(action)

    db.session.delete(post_to_delete)
    db.session.commit()

    # Redirect to the admin page
    return redirect(url_for('routes.admin'))

# edit news posts for admin view
@routes.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)

    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        post.keywords = request.form.get('keywords', '')  
        db.session.commit()
        return redirect(url_for('routes.admin'))

    return render_template('edit_post.html', post=post) # go to edit_post route

#--------------------------- JSON newsfeed route --------------------------

@routes.route('/newsfeed', methods=['GET'])  
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

@routes.route("/")
def home():
    if 'profile' not in session:
        # If the user is not logged in, redirect them to the login page
        return redirect(url_for('routes.login'))
    return redirect(url_for('routes.newsfeed'))  # Redirect to the 'newsfeed' route


# -------------------- News page and functionality --------------------------

@routes.route('/news')
def newsfeed():
    page = request.args.get('page', 1, type=int)
    news_items_pagination = Post.query.order_by(Post.time.desc(), Post.likes.desc(), Post.dislikes).paginate(page=page, per_page=10, error_out=False)
    news_items = news_items_pagination.items

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


    return render_template('newsfeed.html', news_items=news_items, pagination=news_items_pagination, comments=all_comments(), is_admin=is_administator())

# ----------------------- likes/dislikes -------------------
# logic to like a news post
@routes.route('/like/<int:post_id>')
def like(post_id):
    user_id = session.get('profile').get('user_id')
    user_name = session.get('profile').get('name')
    action = UserPostAction.query.filter_by(user_id=user_id, post_id=post_id, user_name=user_name).first()

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
        new_action = UserPostAction(user_id=user_id, post_id=post_id, action='like', user_name=user_name)
        db.session.add(new_action)
        Post.query.get(post_id).likes += 1

    db.session.commit()
    return redirect(url_for('routes.newsfeed'))


# logic to dislike a news post
@routes.route('/dislike/<int:post_id>')
def dislike(post_id):
    user_id = session.get('profile').get('user_id')
    user_name = session.get('profile').get('name')
    action = UserPostAction.query.filter_by(user_id=user_id, post_id=post_id, user_name=user_name).first()

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
        new_action = UserPostAction(user_id=user_id, post_id=post_id, action='dislike', user_name=user_name)
        db.session.add(new_action)
        Post.query.get(post_id).dislikes += 1

    db.session.commit()
    return redirect(url_for('routes.newsfeed'))

#------------------- pages for admin to view user likes/dislikes -------------------------
@routes.route('/post/<int:post_id>/likes_details')
def post_likes_details(post_id):
    user_likes = UserPostAction.query.filter_by(post_id=post_id, action='like').all()
    return render_template('likes_details.html', users=user_likes, post_id=post_id, is_admin=is_administator(), comments=all_comments())

@routes.route('/post/<int:post_id>/dislikes_details')
def post_dislikes_details(post_id):
    user_dislikes = UserPostAction.query.filter_by(post_id=post_id, action='dislike').all()
    return render_template('dislikes_details.html', users=user_dislikes, post_id=post_id, is_admin=is_administator(), comments=all_comments())


#---------------------- comments ----------------------------------------
# logic to post comments in the comment section of the news page
@routes.route('/post_comment', methods=['POST'])
def post_comment():
    if 'profile' not in session:
        # Redirect to login page or handle unauthorized access
        return redirect(url_for('login'))

    user_id = session.get('profile').get('user_id') # get user information
    user_name = session.get('profile').get('name') # get user information
    comment_text = request.form['comment']

    if comment_text:
        # Create a new comment
        new_comment = Comment(user_id=user_id, username=user_name, text=comment_text)
        db.session.add(new_comment)
        db.session.commit()

    return redirect(url_for('routes.newsfeed'))

#--------------------- Profile page ---------------------------
@routes.route('/profile')
def profile():
    user_id = session.get('profile').get('user_id') # get user information
    user_info = session.get('profile', None)
    liked_posts = UserPostAction.query.filter_by(user_id=user_id, action='like').all()

    return render_template('profile.html', user_profile=user_info, liked_posts=liked_posts, is_admin=is_administator(), comments=all_comments())

