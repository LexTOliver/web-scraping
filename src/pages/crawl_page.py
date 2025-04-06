"""
This page contains the code for the Search page of the web scraping application.
It provides an overview of the app and allows users to input a URL, search depth for crawling,
"""

import streamlit as st
from urllib.parse import urlparse
from src.crawler import WebCrawler


def page_setup() -> None:
    """
    Sets up the search page of the web scraping application.
    It includes the title and input fields for the URL and search depth.
    """
    # -- Page title
    st.title("🔍 Search")

    # -- Input fields
    st.subheader("Insira os parâmetros para buscar:")
    st.text_input(
        "Digite uma URL para scraping:",
        key="url",
        help="Digite o endereço com o protocolo (http:// ou https://)",
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
        st.divider()

        # -- Get the input values
        url = st.session_state.url
        depth = int(st.session_state.depth.split(" ")[0])

        # -- Search for the URL
        search_url(url, depth)


def search_url(url: str, depth: int) -> None:
    """
    Search for a URL and its subpages.

    Parameters:
        url - str: The URL to search
        depth - int: The depth of the search (0 to 2)
    """
    # -- Validate inputs
    if not url:
        st.error("Por favor, preencha o campo da URL.")
        return

    # -- Validate URL
    parsed_url = urlparse(url)
    if not parsed_url.scheme or not parsed_url.netloc:
        st.error("URL inválida.")
        return

    # -- Initialize the web crawler
    crawler = WebCrawler(url)
    if crawler.check_main_page():
        # -- Fetch links from the main page and its subpages
        with st.spinner("Buscando links..."):
            links = crawler.fetch_links(url, depth)

        # -- Check if any links were found
        if not links:
            st.warning("Nenhum link encontrado.")
            return

        # -- Display the links found
        st.success(f"Links encontrados: {len(links)}")

        # -- Display the links in a table
        st.table(
            [{"Link": link} for link in links[:10]]
        )  # Display only the first 10 links without index
    else:
        st.error("Erro ao acessar a página principal.")


# -- Run the page setup function
page_setup()
