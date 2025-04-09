"""
This module contains the WebCrawler class for crawling web pages and extracting links.
It uses the requests library to fetch web pages and BeautifulSoup to parse HTML content.
"""
# SEARCH: Consider using selenium for dynamic content

import requests
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse

from src.utils.config import get_logger

# -- Initialize the logger
logger = get_logger()

class WebCrawler:
    """
    Class for crawling into the web pages.

    Attributes:
        main_url - str: The main URL to start scraping from.
        visited_links - set: A set to keep track of visited links.
        page_contents - set: A set to keep track of page contents.

    Methods:
        check_main_page: Check if the main page is reachable.
        fetch_page: Fetch the content of a page.
        extract_links: Extract all links from the HTML content.
        fetch_links: Fetch links from the main page and its subpages up to a specified depth.
    """

    def __init__(self, url: str) -> None:
        self.main_url = url
        self.visited_links = {}

    def check_main_page(self):
        """
        Check if the main page is reachable.

        Returns:
            bool: Boolean value for requesting the page
        """
        try:
            # -- Try to fetch the main page
            response = requests.get(self.main_url)
            response.raise_for_status()  # Raise an error for bad responses
            return True
        except requests.RequestException as e:
            logger.error(f"Error fetching main page {self.main_url}")
            logger.debug(e)
            return False

    def fetch_page(self, url: str) -> str:
        """
        Extract the content of the page.

        Parameters:
            url - str: The URL for extracting the content

        Returns:
            str: The text content of the page found in the URL
        """
        try:
            # -- Try to fetch the page and return the content
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses
            soup = BeautifulSoup(response.text, "lxml")
            return soup.get_text(separator=" ", strip=True)
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}")
            logger.debug(e)
            return ""

    def fetch_multiple_pages(self, urls: list[str]) -> dict:
        """
        Fetch multiple pages in parallel using ThreadPoolExecutor.

        Parameters:
            urls - list: List of URLs to fetch.

        Returns:
            dict: A dictionary mapping URL to HTML content.
        """
        results = {}
        # -- Use ThreadPoolExecutor to fetch pages in parallel
        with ThreadPoolExecutor(max_workers=10) as executor:
            # -- Submit tasks to the executor
            future_to_url = {executor.submit(self.fetch_page, url): url for url in urls}

            # -- Wait for the tasks to complete and collect results
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    results[url] = future.result()
                except Exception as e:
                    logger.error(f"Error fetching {url}")
                    logger.debug(e)
                    results[url] = ""
        return results

    def extract_links(self, html) -> set:
        """
        Extract all links from a HTML content.

        Parameters:
            html - str: The HTML content of the page

        Returns:
            set: A set of links found in the HTML content
        """
        # -- Parse the HTML content
        soup = BeautifulSoup(html, "lxml")

        # -- Find all links in the HTML content
        links = set()
        for link in soup.find_all("a", href=True):
            # Parse the URL
            parsed_url = urlparse(link["href"])

            # Remove the fragment
            link = urlunparse(parsed_url._replace(fragment=""))

            # -- Check if the link is valid
            if (
                link.startswith("http")
                and link not in self.visited_links.keys()
                and not link.lower().endswith(
                    (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg", ".webp")
                )
            ):
                # -- Add the link to the list
                links.add(link)

        return links

    def fetch_links(self, url: str, depth: int) -> tuple:
        """
        Fetch links from the main page and its subpages up to the specified depth using Breadth-First Search (BFS).

        Parameters:
            url - str: The URL to fetch links from
            depth - int: The depth of the links to fetch

        Returns:
            tuple: A tuple containing two lists:
                - all_links: A list of all links found
                - all_contents: A list of the contents of the pages found
        """
        # -- Initialize a queue for BFS
        queue = deque([(url, 0)])  # current_url, current_depth
        
        while queue:
            batch = []
            next_queue = deque()

            # Collect a batch of URLs at the same depth
            while queue:
                current_url, current_depth = queue.popleft()
                if current_url not in self.visited_links.keys():
                    self.visited_links[current_url] = ""
                    batch.append((current_url, current_depth))

            # Fetch pages in parallel
            urls_to_fetch = [url for url, _ in batch]
            html_map = self.fetch_multiple_pages(urls_to_fetch)

            # Process the fetched pages
            for (url, depth_level), html in zip(
                batch, [html_map.get(u, "") for u in urls_to_fetch]
            ):
                self.visited_links[url] = html

                if depth_level < depth and html:
                    links = self.extract_links(html)
                    for link in links:
                        if link not in self.visited_links.keys():
                            next_queue.append((link, depth_level + 1))

            queue = next_queue

        return self.visited_links.keys(), self.visited_links.values()
