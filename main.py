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
from time import time
from urllib.parse import urlparse
from src.models.page_analysis import PageAnalysis, KeywordInfo
from src.services.analyzer import DocumentAnalyzer
from src.services.crawler import WebCrawler
from src.services.indexer import Indexer
from src.utils.config import load_config

# TODO: Add argparse for command line arguments
def get_user_inputs() -> tuple:
    """
    Get user inputs for URL, search depth, and keywords.

    Returns:
        tuple: A tuple containing the URL, search depth, and keywords
    """
    url = input("Digite a URL para scraping: ")
    search_depth = input("Digite a profundidade de busca (0 a 2): ")
    keyword1 = input("Digite a primeira palavra-chave: ")
    keyword2 = input("Digite a segunda palavra-chave: ")
    
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


def crawl(url: str, depth: int) -> tuple:
    """
    Crawl the specified URL and return the list of links found.

    Parameters:
        url - str: The URL to scrape
        depth - int: The depth of the search (0 to 2)

    Returns:
        tuple: A tuple containing a list of links and their contents
    """
    # -- Create a WebCrawler instance
    crawler = WebCrawler(url)

    # -- Check if the URL is reachable
    if not crawler.check_main_page():
        return [], []

    # -- Set the time
    start_time = time()

    # -- Fetch the links from the main page based on the requested depth
    links, contents = crawler.fetch_links(crawler.main_url, depth)

    # -- Print the time taken
    elapsed_time = time() - start_time
    print(f"Tempo de execução: {elapsed_time:.2f} segundos")

    return links, contents


def print_links(links: list, contents: list) -> None:
    """
    Print the links found in the specified URL.

    Parameters:
        links - list: A list of links found in the specified URL
    """
    # -- Print the links found
    print(f"Quantidade de links encontrados: {len(links)}")
    print("Links encontrados:")
    for count, (link, content) in enumerate(zip(links, contents), start=1):
        if count > 10:
            print("...")
            break
        print(f"{count}. {link}\n{content[:100]}...\n")


def indexing_links(links: list, db_config: dict) -> bool:
    """
    Index the links found in the specified URL.

    Parameters:
        links - list: A list of links found in the specified URL
        db_config - dict: The database configuration dictionary

    Returns:
        bool: True if indexing was successful, False otherwise
    """
    # -- Create an Indexer instance
    indexer = Indexer(db_config)

    # -- Check if the database connection is valid
    if not indexer.db_connection:
        print("Erro ao conectar ao banco de dados.")
        return False

    for link in links:
        # -- Insert the URL into the database
        url_id = indexer.insert_url(link)
        if not url_id:
            print(f"Erro ao cadastrar o link: {link}")

    return True


def search_keywords(pages: list, keywords: str) -> dict:
    """
    Search for keywords in the pages and return a dictionary with the results.

    Parameters:
        pages - list: List of pages (tuples of URL and content) to search in
        keywords - str: Comma-separated string of keywords to search for (e.g., "keyword1, keyword2")
    
    Returns:
        dict: Dictionary with the results of the keyword search
    """
    # -- Create a DocumentAnalyzer instance
    analyzer = DocumentAnalyzer(pages, keywords)

    # -- Search for keywords in the pages
    results = analyzer.get_document_analyses()

    return results


def print_search_results(results: list) -> None:
    """
    Print the search results.

    Parameters:
        results - list: List of analysis dictionaries.
    """
    # -- Print the search results
    print("Resultados da análise:")
    # -- Print the first 10 results
    for result in results[:10]:
        print("URL:", result['url'])
        print("Similaridade:", f"{result['similarity']:.2f}")
        print("Pontuação:", f"{result['score']:.2f}")
        print("Palavras-chave:")
        for kw in result["keywords"]:
            print(f"  - {kw['word']} (ocorrências: {len(kw['positions'])})")
        print()
    

def save_analyses(results: list, db_config: dict) -> None:
    """
    Save the document analysis results into the database.

    Parameters:
        results - list: List of analysis dictionaries.
        db_config - dict: Database configuration.
    """
    # -- Create an Indexer instance
    indexer = Indexer(db_config)

     # -- Check if the database connection is valid
    if not indexer.db_connection:
        print("Erro ao conectar ao banco de dados.")
        return False

    # -- Save each analysis result into the database
    for result in results:

        # -- Create a PageAnalysis instance
        analysis = PageAnalysis(
            url=result["url"],
            similarity=result["similarity"],
            score=result["score"],
            keywords=[
                KeywordInfo(word=kw["word"], positions=kw["positions"])
                for kw in result["keywords"]
            ]
        )

        # -- Save the analysis to the database
        if not indexer.save_analysis(analysis):
            print(f"Erro ao indexar resultados da análise para a URL: {result['url']}")

def main():
    """
    Main function to run the web scraping and document analysis application.
    """
    # INITIALIZATION
    # ----------------------------------------------------------------------
    print("BEM-VINDO AO SCRAPESEARCH!")

    # -- Load the configuration file
    config = load_config("example_config.yaml")

    # INPUTS
    # ----------------------------------------------------------------------
    # -- Get user input for URL and keywords
    url, search_depth, keyword1, keyword2 = get_user_inputs()

    # -- Validate the inputs
    if not validate_inputs(url, search_depth, keyword1, keyword2):
        sys.exit()

    # CRAWLING
    # ----------------------------------------------------------------------
    print("\n-----------------------------------------------------")
    print(f"BUSCANDO LINKS NA URL: {url}")
    # -- Crawl the specified URL
    links, contents = crawl(url, int(search_depth))

    # -- Check if any links were found
    if not links:
        print("Nenhum link encontrado.")
        sys.exit()

    # -- Print the links found
    print_links(links, contents)

    # INDEXING
    # ----------------------------------------------------------------------
    print("\n-----------------------------------------------------")
    print("INDEXANDO LINKS ENCONTRADOS...")
    # -- Index the links found
    if indexing_links(links, config["DATABASE"]):
        print("Indexação concluída com sucesso.")
    else:
        sys.exit()

    # ANALYSIS
    # ----------------------------------------------------------------------
    print("\n-----------------------------------------------------")
    print("ANALISANDO DOCUMENTOS...")

    # -- Prepare the documents for analysis
    pages = list(zip(links, contents))
    keywords = f"{keyword1}, {keyword2}"

    # -- Search for keywords in the pages
    results = search_keywords(pages, keywords)
    
    if not results:
        print("Nenhum resultado encontrado.")
        sys.exit()
    else:
        print_search_results(results)

    # INDEXING RESULTS
    # ----------------------------------------------------------------------
    print("\n-----------------------------------------------------")
    print("INDEXANDO RESULTADOS DA ANÁLISE...")
    # -- Save the analysis results into the database
    save_analyses(results, config["DATABASE"])
    print("Indexação dos resultados da análise concluída com sucesso.")

    # TODO:
    # -- Create a DocumentAnalyzer instance and evaluate the documents
    # analyzer = DocumentAnalyzer()
    # results = analyzer.evaluate_documents(links, keyword1, keyword2)

    # if results:
    #     best_link = max(results, key=lambda x: x['score'])
    #     print(f"O link mais bem avaliado é: {best_link['url']} com uma pontuação de {best_link['score']}.")
    # else:
    #     print("Nenhum resultado de análise disponível.")


if __name__ == "__main__":
    main()
