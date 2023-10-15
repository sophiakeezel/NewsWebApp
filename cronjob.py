# cronjob.py
from app.hn_integration import fetch_hackernews_items
from app.models import Post
from app.models import User
from app import db
from datetime import datetime

def store_news_in_db():
    # Get the system user
    system_user = User.query.filter_by(email="system@yourdomain.com").first()

    news_items = fetch_hackernews_items()
    
    for news_item in news_items:
        # Convert the Unix time to datetime object
        news_time = datetime.fromtimestamp(news_item['time'])

        # Check if the news item is already in the DB
        exists = Post.query.filter_by(title=news_item['title']).first()
        if not exists:
            post = Post(title=news_item['title'], time=news_time, content=news_item.get('url', ''))
            db.session.add(post)

    db.session.commit()

if __name__ == "__main__":
    store_news_in_db()
