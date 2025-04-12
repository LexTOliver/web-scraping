"""
This page contains the code for the Search page of the web scraping application.
It provides an overview of the app and allows users to input a URL, search depth for crawling,
"""

import streamlit as st
from time import time
from urllib.parse import urlparse
from src.services.crawler import WebCrawler


def init_session_state() -> None:
    """
    Initializes the session state variables for the Streamlit app.
    It sets initial values for crawler results.
    """
    # -- Initialize session state variables
    if "links" not in st.session_state:
        st.session_state.links = []
    if "contents" not in st.session_state:
        st.session_state.contents = []


def page_setup() -> None:
    """
    Sets up the search page of the web scraping application.
    It includes the title and input fields for the URL and search depth.
    """
    # -- Initialize session state
    init_session_state()

    # -- Page title
    st.title("🕸️ Crawl Web")
    st.markdown("Use esta página para buscar links e conteúdos de um site.")

    # -- Input fields
    st.subheader("🔗 Parâmetros da busca:")
    st.text_input(
        "Digite uma URL para scraping:",
        key="url",
        help="Inclua o protocolo (http:// ou https://)",
        placeholder="https://example.com",
    )
    st.radio(
        "Selecione a profundidade de busca:",
        (
            "0 - Apenas a página principal",
            "1 - Página principal e subpáginas",
            "2 - Página principal, subpáginas em dois níveis",
        ),
        key="depth",
        horizontal=True,
    )

    # -- Search button
    if st.button("Buscar"):
        # -- Clear last search results
        st.session_state.links = []
        st.session_state.contents = []

        # -- Get the input values
        url = st.session_state.url
        depth = int(st.session_state.depth.split(" ")[0])

        # -- Search for the URL
        results = crawl_url(url, depth)

        # -- Store the results in session state
        st.session_state.links, st.session_state.contents = results

    # -- Display the results
    if st.session_state.links:
        show_links(st.session_state.links)


def show_links(links: list) -> None:
    """
    Displays the links found during the search.

    Parameters:
        links - list: A list of links found during the search
    """
    st.divider()
    st.subheader("Links encontrados:")
    st.caption(f"{len(links)} links encontrados. Exibindo os 10 primeiros.")

    if links:
        # -- Display the links in a table
        st.table(
            [{"Link": link} for link in links[:10]]
        )  # Display only the first 10 links without index
    else:
        st.warning("Nenhum link encontrado.")


def crawl_url(url: str, depth: int) -> list:
    """
    Search for a URL and its subpages in a defined depth.

    Parameters:
        url - str: The URL to search
        depth - int: The depth of the search (0 to 2)

    Returns:
        list: A list of links found on the URL
    """
    # -- Validate inputs
    if not url:
        st.error("Por favor, insira uma URL.")
        return None

    # -- Validate URL
    parsed_url = urlparse(url)
    if not parsed_url.scheme or not parsed_url.netloc:
        st.error("URL inválida. Use http:// ou https://")
        return None

    # -- Initialize the web crawler and check the main page
    crawler = WebCrawler(url)
    if not crawler.check_main_page():
        st.error("Erro ao acessar a página principal.")
        return None

    # -- Start search timer
    start_time = time()

    # -- Fetch links from the main page and its subpages
    with st.spinner("Buscando links..."):
        links, contents = crawler.fetch_links(url, depth)

    # -- Check if any links were found
    if not links:
        st.warning("Nenhum link encontrado.")
        return None

    # -- Stop search timer
    st.success(f"Busca concluída com sucesso em {time() - start_time:.2f} segundos.")
    return links, contents


# -- Run the page setup function
page_setup()
