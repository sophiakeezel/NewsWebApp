from datetime import datetime
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.username}, {self.email}, {self.image_file}')"
    

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