# agents/research_agent.py

import requests
from bs4 import BeautifulSoup
import re
from backend.summarizer import summarize_text

def search_web(query: str, max_results: int = 3) -> list:
    """
    Performs a web search using DuckDuckGo HTML (safe & public) and scrapes the top results.
    """
    results = []
    try:
        url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        for a in soup.select("a.result__a", limit=max_results):
            link = a["href"]
            results.append(link)
    except Exception as e:
        results.append(f"❌ Web search error: {e}")

    return results

def fetch_and_summarize(url: str) -> str:
    """
    Fetches article text from a URL and summarizes it.
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        text = ' '.join([p.text for p in soup.find_all('p')])
        cleaned = re.sub(r"\s+", " ", text.strip())

        if len(cleaned) > 200:
            return summarize_text(cleaned)
        else:
            return cleaned or "⚠️ No article text found."
    except Exception as e:
        return f"❌ Error fetching content: {e}"

def deep_research_answer(prompt: str) -> str:
    """
    High-level wrapper: search + fetch + summarize + return sources.
    """
    links = search_web(prompt)
    if not links:
        return "⚠️ No results found."

    summaries = [fetch_and_summarize(link) for link in links]

    combined = "\n\n---\n\n".join(summaries)
    citations = "\n".join([f"🔗 {link}" for link in links])

    return f"**Summary of Findings:**\n\n{combined}\n\n**Sources:**\n{citations}"
