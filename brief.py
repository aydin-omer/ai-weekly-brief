import requests
import feedparser
import os
import smtplib
from email.mime.text import MIMEText

# ---------- Hacker News ----------
def get_hn_top_stories(limit=10):
    ids_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    ids = requests.get(ids_url, timeout=10).json()[:limit]

    stories = []
    for story_id in ids:
        item_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
        item = requests.get(item_url, timeout=10).json()
        title = item.get("title", "No title")
        link = item.get("url", f"https://news.ycombinator.com/item?id={story_id}")
        stories.append(f"- {title} ({link})")

    return "\n".join(stories) if stories else "No stories found."


# ---------- TechCrunch AI (RSS) ----------
def get_techcrunch_ai(limit=10):
    feed_url = "https://techcrunch.com/category/artificial-intelligence/feed/"
    feed = feedparser.parse(feed_url)

    lines = []
    for entry in feed.entries[:limit]:
        title = entry.get("title", "No title")
        link = entry.get("link", "")
        summary = entry.get("summary", "")
        lines.append(f"- {title}\n  {link}\n  {summary[:200]}")

    return "\n".join(lines) if lines else "No recent posts found."


# ---------- Safe wrapper ----------
def safe_run(func, label):
    try:
        return func()
    except Exception as e:
        return f"Could not fetch {label}: {e}"


# ---------- Gemini summarization ----------
def summarize_with_gemini(raw_content):
    api_key = os.environ["GEMINI_API_KEY"]
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

    prompt = f"""You are an analyst preparing a weekly briefing for a Product Manager.
Below is a raw list of tech and AI news headlines and links from this week.

Write a concise, well-organized weekly brief that:
- Groups related items into short thematic sections
- Highlights what matters most for a Product Manager (business impact, new tools, industry shifts)
- Uses plain, direct language, no fluff
- Keeps the whole brief under 400 words
- Includes the most relevant links inline

Raw content:
{raw_content}
"""

    headers = {
        "x-goog-api-key": api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    return data["candidates"][0]["content"]["parts"][0]["text"]


# ---------- Email ----------
def send_email(subject, body):
    sender = os.environ["MAIL_FROM"]
    password = os.environ["MAIL_PASSWORD"]
    receiver = os.environ["MAIL_TO"]

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.send_message(msg)


def main():
    hn_section = safe_run(get_hn_top_stories, "Hacker News")
    tc_section = safe_run(get_techcrunch_ai, "TechCrunch AI")

    raw_content = f"""HACKER NEWS TOP STORIES:
{hn_section}

TECHCRUNCH AI:
{tc_section}
"""

    try:
        summary = summarize_with_gemini(raw_content)
    except Exception as e:
        summary = f"Could not generate AI summary: {e}\n\nRaw content:\n{raw_content}"

    body = f"""AI & Tech Weekly Brief

{summary}

---
Generated automatically from Hacker News and TechCrunch AI.
"""

    send_email("AI & Tech Weekly Brief", body)


if __name__ == "__main__":
    main()
