import streamlit as st
from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool
import requests
import os
from dotenv import load_dotenv

# ---- Load Environment Variables ----
load_dotenv()
BRIGHT_API_KEY = os.getenv("BRIGHTDATA_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ---- Bright Data Tool ----
@tool("BrightData Scraper")
def scrape_with_brightdata(url: str) -> str:
    """Scrape the HTML content of a given website URL using Bright Data API."""
    BRIGHT_API_URL = "https://api.brightdata.com/scraper"

    payload = {"url": url, "render": True}
    headers = {"Authorization": f"Bearer {BRIGHT_API_KEY}"}

    response = requests.post(BRIGHT_API_URL, json=payload, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        return f"Error scraping {url}: {response.text}"

# ---- LLM (Groq with LLaMA3) ----
llm = LLM(
    model="groq/deepseek-r1-distill-llama-70b",  # ✅ specify provider + model
    api_key=GROQ_API_KEY
)

# ---- SEO Analysis Agent ----
seo_agent = Agent(
    role="SEO Analyst",
    goal="Analyze websites and generate detailed SEO reports",
    backstory="You are an expert SEO Analyst who helps businesses optimize websites for search engines.",
    tools=[scrape_with_brightdata],
    llm=llm,
    verbose=True
)

# ---- SEO Prompt ----
seo_prompt = """
You are an expert SEO Analyst. Analyze the provided website content and generate a structured SEO analysis report.  

Steps:
1. Basic Info: Extract title, meta description, headers (H1, H2).
2. Content Quality: Check word count, keyword usage, readability.
3. On-Page SEO: Inspect title tags, alt text, internal linking, URLs.
4. Technical SEO: Page speed signals, mobile-friendly, sitemap, robots.txt.
5. Backlinks: Identify if any reference/backlink data is visible.
6. Competitors: Suggest a brief benchmark approach.
7. Recommendations: Provide clear action items.

Output:
- Summary of findings
- SEO scores (On-page, Technical, Content) out of 10
- Final Recommendations (bullet points)
"""

# ---- Streamlit App ----
st.title("🔎 SEO Analysis with CrewAI + Bright Data + Groq LLaMA3")

url_input = st.text_input("Enter a website URL:", placeholder="https://example.com")

if st.button("Run SEO Analysis"):
    if url_input:
        with st.spinner("Analyzing website..."):
            try:
                # Create a task dynamically with user input
                seo_task = Task(
                    description=f"Scrape {url_input} using Bright Data and analyze SEO. Follow these steps:\n{seo_prompt}",
                    agent=seo_agent,
                    expected_output="A structured SEO analysis report with summary, scores, and recommendations."
                )

                crew = Crew(
                    agents=[seo_agent],
                    tasks=[seo_task],
                    verbose=True
                )

                result = crew.kickoff()
                st.subheader("📊 SEO Analysis Report")
                st.write(result)

            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Please enter a URL.")
