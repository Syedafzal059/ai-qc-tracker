# server.py
import requests
from xml.etree import ElementTree as ET
from mcp.server.fastmcp import FastMCP
from mcp.types import Tool
from dotenv import load_dotenv
import os
from openai import OpenAI


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

mcp = FastMCP("AI_QC Tracker")
print("🔌 [MCP] FastMCP server started.", flush = True)



@mcp.tool()
def summarize_text(text: str) -> str:
    """Summarizes the input text using OpenAI GPT"""
    if not text.strip():
        return "No text provided."

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant who simplifies complex text."},
                {"role": "user", "content": f"Summarize and simplify this:\n{text}"}
            ],
            temperature=0.7,
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"





@mcp.tool()
def get_latest_arxiv_updates(topic: str) -> list[str]:
    """
    Fetches the latest arXiv papers based on a topic.
    Returns list of paper titles with URLs.
    """

    try:
        url = f"http://export.arxiv.org/api/query?search_query=all:{topic}&sortBy=submittedDate&sortOrder=descending&max_results=5"
        response = requests.get(url)
        if response.status_code != 200:
            return [f"Failed to fetch papers. Status code: {response.status_code}"]

        root = ET.fromstring(response.text)
        ns = {"arxiv": "http://www.w3.org/2005/Atom"}

        papers = []
        for entry in root.findall("arxiv:entry", ns):
            title = entry.find("arxiv:title", ns).text.strip().replace("\n", " ")
            link = entry.find("arxiv:id", ns).text
            papers.append(f"{title} → {link}")
        
        if not papers:
            return ["No papers found."]
        return papers

    except Exception as e:
        return [f"Error: {str(e)}"]



if __name__ == "__main__":
    print("✅ MCP server script is running...", flush=True)

    try:
        mcp.run()
    except Exception as e:
        print(f"❌ MCP server failed: {e}", flush=True)