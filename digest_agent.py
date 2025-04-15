import asyncio
import sys
from crewai import Agent, Task, Crew
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import os

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Define MCP server execution details
# server_params = StdioServerParameters(
#     command=sys.executable,  # safer than hardcoded "python"
#     args=["-u", "server.py"],  # -u = unbuffered output for proper MCP communication
#     env=None,
#     stderr_file="mcp_stderr.log",  # log stderr for debugging
#     stdout_file="mcp_stdout.log"   # log stdout too
# )

server_params = StdioServerParameters(
    command=sys.executable,
    args=["-u", "dummy_server.py"],
    stderr_file="mcp_stderr.log",
    stdout_file="mcp_stdout.log"
)

# Define the CrewAI agent
research_agent = Agent(
    role="Research Analyst",
    goal="Track recent developments in AI and quantum computing",
    backstory="You are a research assistant who fetches recent papers and summarizes them for a newsletter.",
    verbose=True
)

# Define the summarization task using MCP tools
def generate_digest_task(topic: str, session: ClientSession) -> Task:
    def run(_):
        print("📦 [TASK] Starting digest task...")
        print(f"📚 [TOPIC] Working on: {topic}")
        
        try:
            print("📡 [FETCH] Calling tool: get_latest_arxiv_updates")
            papers = asyncio.run(session.call_tool("get_latest_arxiv_updates", {"topic": topic}))
            print(f"📑 [FETCH] Papers fetched: {len(papers)}")
        except Exception as e:
            print(f"❌ [ERROR] Failed to fetch papers: {e}")
            return "❌ Error fetching papers."

        summaries = []
        print("🌀 [SUMMARY] Summarizing each paper...")

        for idx, paper in enumerate(papers, start=1):
            print(f"\n🔢 [{idx}] Paper: {paper}")
            try:
                summary = asyncio.run(session.call_tool("summarize_text", {"text": paper}))
                print(f"✅ [SUMMARY {idx}] Done.")
                summaries.append(f"### {paper}\n{summary}\n")
            except Exception as e:
                print(f"⚠️ [SUMMARY {idx}] Failed: {e}")
                summaries.append(f"### {paper}\n⚠️ Failed to summarize.\n")

        print("📚 [SUMMARY] All papers processed.")
        return "\n".join(summaries)

    return Task(
        description=f"Summarize recent {topic} research from arXiv.",
        agent=research_agent,
        output_file=f"{topic}_digest.md",
        func=run
    )

# Main async logic
async def main():
    print("🔌 [START] Connecting to MCP server...")
    async with stdio_client(server_params) as (read, write):
        print("✅ [STDIO] Transport channel ready.")

        async with ClientSession(read, write) as session:
            print("🔄 [MCP] Initializing session...")

            try:
                await asyncio.wait_for(session.initialize(), timeout=15)
                print("✅ [MCP] Session initialized!")
            except asyncio.TimeoutError:
                print("⏳ [TIMEOUT] MCP session did not respond in time.")
                return
            except Exception as e:
                print(f"❌ [ERROR] MCP session init failed: {e}")
                return

            task = generate_digest_task("quantum computing", session)
            print("🧠 [CREW] Task and agent created. Starting CrewAI...")

            result = Crew(
                agents=[research_agent],
                tasks=[task]
            ).run()

            print("\n✅ [DONE] Digest complete. Saved to markdown file.")
            print("📄 [PREVIEW]")
            print(result[:1000])  # First 1000 characters of summary

if __name__ == "__main__":
    asyncio.run(main())
