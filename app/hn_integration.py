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
        keywords = extract_keywords(response)  # Function to extract keywords
        
        # Add the response with the keywords
        news_item = response
        news_item['keywords'] = keywords  # Add keywords to the news item
        news_items.append(news_item)  # Add the enriched news item to the list
    
    return news_items

def extract_keywords(response):
    # Logic to extract keywords from the response
    return ','.join(response['title'].split())  
