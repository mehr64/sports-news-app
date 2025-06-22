from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

BBC_URL = "https://www.bbc.com/sport"

def get_article_links():
    """Scrape article titles and links from BBC Sport homepage."""
    response = requests.get(BBC_URL)
    soup = BeautifulSoup(response.content, "html.parser")
    
    articles = []
    for tag in soup.find_all("a", href=True):
        title = tag.get_text(strip=True)
        href = tag['href']
        
        if title and "/sport/" in href and "live" not in href.lower():
            full_url = "https://www.bbc.com" + href if href.startswith("/") else href
            articles.append({"title": title, "url": full_url})
        
        if len(articles) >= 5:
            break

    return articles

@app.route("/")
def index():
    articles = get_article_links()
    return render_template("index.html", articles=articles)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
