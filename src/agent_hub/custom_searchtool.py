import os
import socket
from typing import Type, Dict
from urllib.parse import urlparse
from pydantic import BaseModel, Field, PrivateAttr
from crewai.tools import BaseTool
from crewai_tools import TavilySearchTool, FirecrawlSearchTool, ScrapeWebsiteTool

# --- 1. SCHEMAS ---

class SearchInput(BaseModel):
    query: str = Field(..., description="The query to search the internet for.")

class ScraperInput(BaseModel):
    website_url: str = Field(..., description="The URL of the website to scrape.")

# --- 2. RESILIENT SEARCH TOOL (Tavily -> Firecrawl) ---

class ResilientSearchTool(BaseTool):
    name: str = "google_search"
    description: str = "Search the internet for news and trends. Fails over to backup if limits hit."
    args_schema: Type[BaseModel] = SearchInput
    _usage_stats: Dict[str, int] = PrivateAttr(default={"tavily": 0, "firecrawl": 0})

    def _run(self, query: str) -> str:
        print(f"\n{'*'*20} 🔍 SEARCH START {'*'*20}")
        print(f"Query: {query}")
        
        try:
            # Primary: Tavily
            tavily = TavilySearchTool()
            results = tavily._run(query=query)
            self._usage_stats["tavily"] += 1
            print(f"✅ [Tavily] Success")
            return f"[Source: Tavily] {results}"
        except Exception as e:
            print(f"⚠️ [Tavily] Failed: {e}. Trying Firecrawl...")
            try:
                # Fallback: Firecrawl Search
                firecrawl = FirecrawlSearchTool()
                results = firecrawl._run(query=query)
                self._usage_stats["firecrawl"] += 1
                return f"[Source: Firecrawl] {results}"
            except Exception as final_e:
                return f"❌ All search tools failed: {str(final_e)}"
        finally:
            print(f"{'*'*20} 🔍 SEARCH END {'*'*20}\n")

# --- 3. SECURE SCRAPER TOOL (SSRF Protected) ---

class SecureScraperTool(BaseTool):
    name: str = "website_scraper"
    description: str = "Scrape content from a specific PUBLIC website URL."
    args_schema: Type[BaseModel] = ScraperInput

    def _is_safe(self, url: str) -> bool:
        """Blocks private IPs, Loopback, and Cloud Metadata (SSRF Protection)"""
        try:
            hostname = urlparse(url).hostname
            if not hostname: return False
            ip = socket.gethostbyname(hostname)
            # Block: 127.x, 10.x, 192.168.x, 172.x, 169.254.x
            forbidden = ("127.", "10.", "192.168.", "172.", "169.254.")
            return not any(ip.startswith(prefix) for prefix in forbidden)
        except:
            return False

    def _run(self, website_url: str) -> str:
        print(f"\n{'='*20} 🌐 SCRAPER START {'='*20}")
        print(f"URL: {website_url}")

        if not self._is_safe(website_url):
            print("❌ [SECURITY] Blocked Private/Local URL")
            return "Error: Access to private or local network addresses is forbidden."

        try:
            # Simple Scrape (No OpenAI embeddings needed)
            scraper = ScrapeWebsiteTool(website_url=website_url)
            content = scraper._run()
            print(f"✅ [Scraper] Success ({len(content)} chars)")
            return content
        except Exception as e:
            print(f"❌ [Scraper] Failed: {e}")
            return f"Scraping error: {str(e)}"
        finally:
            print(f"{'='*20} 🌐 SCRAPER END {'='*20}\n")

