from pathlib import Path
from typing import Annotated
from langchain_core.tools import tool
from firecrawl import FirecrawlApp, ScrapeOptions
from pydantic import BaseModel

app = FirecrawlApp()

PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"


class SearchResult(BaseModel):
    title: str
    url: str
    markdown: str
    links: list[str]


@tool
def search_web(
    query: Annotated[str, "The query to search the web"],
) -> list[SearchResult]:
    """
    A tool to search the web for job posting for a specific company.
    """
    search_result = app.search(
        query, limit=5, scrape_options=ScrapeOptions(formats=["markdown", "links"])
    )
    return [SearchResult(**i) for i in search_result.data]


@tool
def scrape_job_postings_links(
    company: Annotated[str, "The company name"],
    links: Annotated[list[str], "The job posting links to scrape"],
) -> tuple[str, list[str]]:
    """
    A tool to scrape the links of job postings in batch and return the content.
    """
    scrape = app.batch_scrape_urls(links, formats=["markdown"])
    data = ""
    for i, page in enumerate(scrape.data):
        job_posting = f"THIS IS THE ROLE:\n{page.markdown}\nEND OF ROLE\n\n"
        data += job_posting
        file_name = links[i].split("/")[-1]
        path = DATA_DIR / company
        path.mkdir(exist_ok=True)
        with open(path / f"{file_name}.txt", "w") as f:
            f.write(page.markdown)  # type: ignore
    return data, links


agent_tools = [search_web, scrape_job_postings_links]
