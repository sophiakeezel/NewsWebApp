from datetime import datetime
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    is_admin = db.Column(db.Boolean, default=False) # user has administrative privelidges
    auth0_id = db.Column(db.String(256), unique=True, nullable=True) 
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f"User('{self.username}, {self.email}')"
    
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    likes = db.Column(db.Integer, default=0) 
    dislikes = db.Column(db.Integer, default=0)  
    by = db.Column(db.String(100), nullable=True)
    descendants = db.Column(db.Integer, default=0)
    kids = db.Column(db.String(500), nullable=True)  # Store as comma-separated string or use a related table
    score = db.Column(db.Integer, default=0)
    type = db.Column(db.String(50), nullable=True)
    url = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"Post('{self.title}, {self.time}')"
    
class UserPostAction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    post = db.relationship('Post', backref='post_actions')  # Add this line
    action = db.Column(db.String(10), nullable=False)  # 'like' or 'dislike'

    def __repr__(self):
        return f"UserPostAction('{self.user_id}', '{self.post_id}', '{self.action}')"
    
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

