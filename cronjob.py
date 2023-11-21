# cronjob.py
from flasknews.hn_integration import fetch_hackernews_items
from flasknews import create_app, db
from flasknews.models import Post, User
from flasknews import db
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
            post = Post(
                title=news_item['title'], 
                time=news_time, 
                keywords=news_item.get('keywords', ''),  # Save keywords
                content=news_item.get('url', ''),
                by=news_item.get('by', ''),
                descendants=news_item.get('descendants', 0),
                kids=','.join(map(str, news_item.get('kids', []))),
                score=news_item.get('score', 0),
                type=news_item.get('type', ''),
                url=news_item.get('url', '')
            )
            db.session.add(post)

    db.session.commit()

if __name__ == "__main__":
    app = create_app('default') 
    with app.app_context():
        store_news_in_db()

