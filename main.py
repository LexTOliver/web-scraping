"""
This script runs the application for web scraping and document analysis via the command line.
It prompts the user for a URL, search depth, and keywords, then retrieves links from the specified URL.

Example usage:
    Digite a URL para scraping: https://example.com
    Digite a profundidade de busca (0 a 2): 1
    Digite a primeira palavra-chave: example
    Digite a segunda palavra-chave: test
"""

import sys
from urllib.parse import urlparse
from src.crawler import WebCrawler
# from src.analyzer import DocumentAnalyzer


def get_user_inputs() -> tuple:
    """
    Get user inputs for URL, search depth, and keywords.

    Returns:
        tuple: A tuple containing the URL, search depth, and keywords
    """
    url = input("Digite a URL para scraping: ")
    search_depth = input("Digite a profundidade de busca (0 a 2): ")
    # keyword1 = input("Digite a primeira palavra-chave: ")
    # keyword2 = input("Digite a segunda palavra-chave: ")
    keyword1 = "example"
    keyword2 = "test"

    return url, search_depth, keyword1, keyword2


def validate_inputs(url: str, depth: str, keyword1: str, keyword2: str) -> bool:
    """
    Validate the user inputs.

    Parameters:
        url - str: The URL to scrape
        depth - int: The depth of the search (0 to 2), being:
            0 - only the main page
            1 - the main page and its subpages
            2 - the main page, its subpages, and their subpages
        keyword1 - str: The first keyword to search for
        keyword2 - str: The second keyword to search for

    Returns:
        bool: True if inputs are valid, False otherwise
    """
    try:
        # -- Validate URL
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            print("URL inválida.")
            return False

        # -- Validate depth
        if not depth.isdigit():
            print("Profundidade deve ser um número inteiro.")
            return False
        if int(depth) < 0 or int(depth) > 2:
            print("Profundidade deve estar entre 0 e 2.")
            return False

        # -- Validate keywords
        k1 = keyword1.strip()
        k2 = keyword2.strip()
        if k1 == "" or k2 == "":
            print("Palavras-chave não podem ser vazias.")
            return False
        elif k1 == k2:
            print("Palavras-chave não podem ser iguais.")
            return False
        elif len(k1.split(" ")) > 1 or len(k2.split(" ")) > 1:
            print("Palavras-chave não podem conter espaços.")
            return False
    except Exception as e:
        print("Erro na validação de entradas:")
        print(e)
        return False

    return True


def crawl(url: str, depth: int) -> list:
    """
    Crawl the specified URL and return the list of links found.

    Parameters:
        url - str: The URL to scrape
        depth - int: The depth of the search (0 to 2)

    Returns:
        list: A list of links found in the specified URL
    """
    # -- Create a WebCrawler instance
    crawler = WebCrawler(url)

    # -- Check if the URL is reachable
    if not crawler.check_main_page():
        return []

    # -- Fetch the links from the main page based on the requested depth
    links = crawler.fetch_links(crawler.main_url, depth)
    return links


def print_links(links: list):
    """
    Print the links found in the specified URL.

    Parameters:
        links - list: A list of links found in the specified URL
    """
    # -- Print the links found
    print(f"Quantidade de links encontrados: {len(links)}")
    print("Links encontrados:")
    for count, link in enumerate(links, start=1):
        if count > 10:
            break
        print(f"{count}. {link}")


def main():
    # -- Get user input for URL and keywords
    url, search_depth, keyword1, keyword2 = get_user_inputs()
    
    # -- Validate the inputs
    if not validate_inputs(url, search_depth, keyword1, keyword2):
        sys.exit()

    # -- Crawl the specified URL
    links = crawl(url, int(search_depth))

    # -- Check if any links were found
    if not links:
        print("Nenhum link encontrado.")
        sys.exit()

    # -- Print the links found
    print_links(links)

    # TODO:
    # -- Create a DocumentAnalyzer instance and evaluate the documents
    # analyzer = DocumentAnalyzer()
    # best_link = analyzer.evaluate_documents(links, keyword1, keyword2)

    # if best_link:
    # print(f"O link mais bem avaliado é: {best_link}")
    # else:
    # print("Nenhum link encontrado ou avaliado.")


if __name__ == "__main__":
    main()
