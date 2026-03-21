import ipaddress
from socket import socket
from urllib.parse import urlparse

from crewai.tools import BaseTool, field_validator
from crewai_tools import ScrapeWebsiteTool, TavilySearchTool, FirecrawlSearchTool
from pydantic import BaseModel, Field, HttpUrl
from typing import Type


class ScraperInput(BaseModel):
    search_query: str = Field(..., description="The specific thing to look for on the website.")
    website_url: str = Field(..., description="The URL of the website to scrape.")


class ResilientSearchTool(BaseTool):
    name: str = "Resilient Search"
    description: str = "Search the internet for news and trends. Automatically fails over to backup if limits are hit."

    @field_validator('website_url')
    @classmethod
    def validate_website_url(cls, v: HttpUrl) -> HttpUrl:
        url_str = str(v)
        parsed = urlparse(url_str)
        hostname = parsed.hostname

        if not hostname:
            raise ValueError("Invalid hostname in URL.")

        try:
            # 2. Resolve Host to IP to prevent DNS Rebinding/SSRF
            ip_address = socket.gethostbyname(hostname)
            ip = ipaddress.ip_address(ip_address)

            # 3. Block Private, Loopback, Link-Local, and Cloud Metadata ranges
            if any([
                ip.is_private,      # RFC1918 (10.x, 172.16.x, 192.168.x)
                ip.is_loopback,     # 127.0.0.1
                ip.is_link_local,   # 169.254.x.x (AWS/GCP Metadata)
                ip.is_multicast,
                ip.is_unspecified
            ]):
                raise ValueError(f"Access to private or local IP {ip_address} is forbidden.")

        except socket.gaierror:
            raise ValueError(f"Could not resolve hostname: {hostname}")

        return v
    
    # Track usage for your React/Angular dashboard

    def _run(self, search_query: str) -> str:
        # Try Tavily First (Main Tool)
        try:
            print(f"Attempting to use Tavily for query: {search_query}")
            tavily = TavilySearchTool()
            results = tavily._run(query=search_query)
            return f"[Source: Tavily] {results}"
        except Exception as e:
            print(f"Error occurred with Tavily: {str(e)}")
            # Fallback to Firecrawl (Fallback Tool)
            try:
                # Firecrawl's search feature is a great fallback for Serper
                firecrawl = FirecrawlSearchTool() 
                results = firecrawl._run(search_query=search_query)
                return f"[Source: Firecrawl] {results}"
            except Exception as e:
                print(f"Error occurred with Firecrawl: {str(e)}")
                return f"All tools failed: {str(e)}"

class VisualScraperTool(BaseTool):
    name: str = "website_scraper"
    description: str = "Search and read content from a specific URL."
    args_schema: Type[BaseModel] = ScraperInput

    def _run(self, search_query: str, website_url: str) -> str:
        # --- Visual Console Header ---
        print(f"\n{'='*30}")
        print(f"🌐 [SCRAPER] Target: {website_url}")
        print(f"🧐 [QUERY]: {search_query}")
        print(f"{'='*30}")

        try:
            # Initialize the internal tool
            # Note: We pass the website here so it focuses on that URL
            inner_tool = ScrapeWebsiteTool(website_url=website_url)
            
            # Execute the search
            result = inner_tool._run(search_query=search_query)

            # --- Visual Console Result ---
            result_str = str(result) if result else ""
            print(f"✅ [SUCCESS] Found data ({len(result_str)} chars)")
            print(f"📄 [PREVIEW]: {result_str[:200]}...")
            print(f"{'='*60}\n")
            
            return result
        except Exception as e:
            print(f"❌ [ERROR]: {str(e)}")
            return f"Failed to scrape {website_url}: {str(e)}"