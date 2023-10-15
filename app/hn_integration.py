# app/hn_integration.py
import requests

def fetch_hackernews_items():
    BASE_URL = 'https://hacker-news.firebaseio.com/v0/'
    TOP_STORIES = 'topstories.json'
    ITEM = 'item/{}.json'
    
    top_stories_ids = requests.get(BASE_URL + TOP_STORIES).json()
    
    # Limit to the top 10 or another reasonable number
    top_10_ids = top_stories_ids[:10]
    
    news_items = []
    for item_id in top_10_ids:
        response = requests.get(BASE_URL + ITEM.format(item_id)).json()
        news_items.append(response)
    
    return news_items
