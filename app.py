from flask import Flask, render_template
from transformers import pipeline
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Load Hugging Face summarization pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# BBC Sport URL to scrape
BBC_URL = "https://www.bbc.com/sport"

def get_article_links():
    """Scrape article titles and links from BBC Sport homepage."""
    response = requests.get(BBC_URL)
    soup = BeautifulSoup(response.content, "html.parser")
    
    articles = []
    for tag in soup.find_all("a", href=True):
        title = tag.get_text(strip=True)
        href = tag['href']
        
        # Basic filtering for real articles (ignore empty, images, etc.)
        if title and "/sport/" in href and "live" not in href.lower():
            full_url = "https://www.bbc.com" + href if href.startswith("/") else href
            articles.append({"title": title, "url": full_url})
        
        if len(articles) >= 5:
            break  # Limit to 5 articles

    return articles

def fetch_article_text(url):
    """Extract visible article text from the URL."""
    try:
        res = requests.get(url)
        soup = BeautifulSoup(res.content, "html.parser")
        paragraphs = soup.find_all("p")
        text = " ".join(p.get_text() for p in paragraphs)
        return text.strip()
    except Exception:
        return ""

def summarize_article(text):
    """Summarize article text using Hugging Face model."""
    if not text:
        return "Could not fetch content."
    
    # Truncate to max token-friendly length
    text = text[:1000]

    try:
        result = summarizer(text, max_length=120, min_length=30, do_sample=False)
        return result[0]['summary_text']
    except Exception:
        return "Failed to summarize."

@app.route("/")
def index():
    """Main route to display summarized articles."""
    articles = get_article_links()
    
    for article in articles:
        full_text = fetch_article_text(article["url"])
        summary = summarize_article(full_text)
        article["summary"] = summary
    
    return render_template("index.html", articles=articles)

if __name__ == "__main__":
    app.run(debug=True)
