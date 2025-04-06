"""
This module contains the WebCrawler class for crawling web pages and extracting links.
It uses the requests library to fetch web pages and BeautifulSoup to parse HTML content.
"""
# SEARCH: Consider using selenium for dynamic content

import requests
from collections import deque
from bs4 import BeautifulSoup

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
        self.visited_links = set()
        self.page_contents = set()

    def check_main_page(self):
        """
        Check if the main page is reachable.
        
        Returns:
            bool: Boolean value for requesting the page
        """
        try:
            # -- Try to fetch the main page
            response = requests.get(self.main_url)
            response.raise_for_status() # Raise an error for bad responses
            return True
        except requests.RequestException as e:
            print(f"Error fetching main page{self.main_url}")
            print(e)
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
            response.raise_for_status() # Raise an error for bad responses
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return ""

    def extract_links(self, html) -> set:
        """
        Extract all links from a HTML content.
        
        Parameters:
            html - str: The HTML content of the page
            
        Returns:
            set: A set of links found in the HTML content
        """
        # -- Parse the HTML content
        soup = BeautifulSoup(html, 'lxml')

        # -- Find all links in the HTML content
        links = set()
        for link in soup.find_all('a', href=True):
            # -- Remove the fragment identifier from the link
            link = link['href'].split('#')[0]
            
            # -- Check if the link is valid
            if link.startswith('http') and link not in self.visited_links:
                # -- Add the link to the list
                links.add(link)
                
        return links
    
    def fetch_links(self, url: str, depth: int) -> list:
        """
        Fetch links from the main page and its subpages up to the specified depth using Breadth-First Search (BFS).
        
        Parameters:
            url - str: The URL to fetch links from
            depth - int: The depth of the links to fetch

        Returns:
            list: A list of links found in the page and its subpages
        """
        # -- Initialize a queue for BFS
        queue = deque([(url, 0)])  # current_url, current_depth
        all_links = []
        
        while queue:
            current_url, current_depth = queue.popleft()
            
            # -- Skip if the URL has already been visited
            if current_url in self.visited_links:
                continue
            
            # -- Mark the URL as visited
            self.visited_links.add(current_url)

            # -- Fetch the page content
            html = self.fetch_page(current_url)
            self.page_contents.add(html)
            
            # -- Add the current URL to the list of all links
            all_links.append(current_url)
            
            # -- Stop if the maximum depth is reached or the page content is empty
            if current_depth >= depth or not html:
                continue
            
            # -- Extract links from the page and add them to the queue
            links = self.extract_links(html)
            for link in links:
                queue.append((link, current_depth + 1))
        
        return all_links