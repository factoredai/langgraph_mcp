from typing import Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
from firecrawl import FirecrawlApp, ScrapeOptions
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("mcp")
app = FirecrawlApp()


class SearchResult(BaseModel):
    title: str
    url: str
    markdown: str
    links: list[str]


@mcp.tool()
def mcp_search_web(
    query: Annotated[str, Field(description="The query to search the web")],
) -> list[SearchResult]:
    """
    A tool to search the web for job posting for a specific company.
    """
    search_result = app.search(
        query, limit=5, scrape_options=ScrapeOptions(formats=["markdown", "links"])
    )
    return [SearchResult(**i) for i in search_result.data]


@mcp.tool()
def mcp_scrape_job_postings_links(
    links: Annotated[list[str], Field(description="The job posting links to scrape")],
) -> tuple[str, list[str]]:
    """
    A tool to scrape the links of job postings in batch and return the content.
    """
    scrape = app.batch_scrape_urls(links, formats=["markdown"])
    data = ""
    for page in scrape.data:
        job_posting = f"THIS IS THE ROLE:\n{page.markdown}\nEND OF ROLE\n\n"
        data += job_posting
    return data, links


if __name__ == "__main__":
    mcp.run()
