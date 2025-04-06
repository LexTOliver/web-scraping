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
    st.subheader("Insira os parâmetros para scraping:")
    st.text_input(
        "Digite uma URL para scraping:",
        key="url",
    )
    st.slider("Selecione uma profundidade de busca:", 0, 2, 1, key="depth")

    # -- Search button
    if st.button("Buscar"):
        # -- Get the input values
        url = st.session_state.url
        depth = st.session_state.depth

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
