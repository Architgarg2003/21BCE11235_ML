import threading
import time
import requests
from bs4 import BeautifulSoup
from models import Document, get_db
from search_engine import load_and_index_document

def scrape_news_articles():
    # Example news sources (you can add more)
    news_sources = [
        "https://www.bbc.com/news",
        "https://www.cnn.com",
        "https://www.reuters.com"
    ]

    while True:
        db = next(get_db())
        for source in news_sources:
            try:
                response = requests.get(source)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract article titles and content (this is a simplified example)
                articles = soup.find_all('article')
                for article in articles:
                    title = article.find('h2').text if article.find('h2') else "No title"
                    content = article.find('p').text if article.find('p') else "No content"
                    
                    # Save to database
                    document = Document(filename=f"{title}.txt", content=f"{title}\n\n{content}")
                    db.add(document)
                
                db.commit()
                
                # Index the new documents
                load_and_index_document(f"{title}.txt")
                
            except Exception as e:
                print(f"Error scraping {source}: {str(e)}")
        
        # Wait for an hour before the next scraping cycle
        time.sleep(3600)

def start_background_scraper():
    scraper_thread = threading.Thread(target=scrape_news_articles)
    scraper_thread.daemon = True
    scraper_thread.start()