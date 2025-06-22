from flask import Flask, render_template
from transformers import pipeline
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Use a lightweight summarization model
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

BBC_URL = "https://www.bbc.com/sport"

def get_article_links():
    """Scrape titles and links from BBC Sport homepage."""
    response = requests.get(BBC_URL)
    soup = BeautifulSoup(response.content, "html.parser")
    articles = []
    for tag in soup.find_all("a", href=True):
        title = tag.get_text(strip=True)
        href = tag['href']
        if title and "/sport/" in href and "live" not in href.lower():
            full_url = "https://www.bbc.com" + href if href.startswith("/") else href
            articles.append({"title": title, "url": full_url})
        if len(articles) >= 2:  # Limit for performance
            break
    return articles

def fetch_article_text(url):
    """Extract text from article."""
    try:
        res = requests.get(url)
        soup = BeautifulSoup(res.content, "html.parser")
        paragraphs = soup.find_all("p")
        return " ".join(p.get_text() for p in paragraphs).strip()
    except Exception:
        return ""

def summarize_article(text):
    """Summarize article using transformer."""
    if not text:
        return "Could not fetch content."
    text = text[:600]  # Trim for low memory use
    try:
        result = summarizer(text, max_length=40, min_length=20, do_sample=False)
        return result[0]['summary_text']
    except Exception:
        return "Failed to summarize."

@app.route("/")
def index():
    """Render homepage with summaries."""
    articles = get_article_links()
    for article in articles:
        full_text = fetch_article_text(article["url"])
        article["summary"] = summarize_article(full_text)
    return render_template("index.html", articles=articles)
