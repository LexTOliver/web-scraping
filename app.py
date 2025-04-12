"""
This file contains the main code for the Streamlit app.
"""

import streamlit as st

# from src.crawler import WebCrawler
from src.services.indexer import Indexer
from src.utils.config import load_config


def init_session_state():
    """
    This function initializes the session state variables for the Streamlit app.
    It sets default values for URL, depth, and search results.
    """
    # -- Load configurations
    config = load_config("example_config.yaml")

    # -- Initialize session state variables
    if "indexer" not in st.session_state:
        st.session_state.indexer = Indexer(config["DATABASE"])

    if "config" not in st.session_state:
        st.session_state.config = config


def home_page():
    """
    Setup the home page of the Streamlit app with guidance.
    """
    # -- Initialize session state
    init_session_state()

    # -- Page title and description
    st.title("🔍 ScrapeSearch")
    st.markdown("### Busque, explore e analise conteúdo da web de forma automatizada.")

    st.write("""
    Bem-vindo ao **ScrapeSearch**, uma buscador com _web scraping_ para análise inteligente de documentos.
    
    Esta ferramenta permite:
    - 📥 Coletar conteúdo de sites em diferentes níveis de profundidade.
    - 🧠 Analisar os textos extraídos com base em palavras-chave.
    - 📊 Classificar e armazenar os resultados automaticamente.
             
    O critério baseado nas palavras-chave é feito com base num cálculo ponderado de:
    - Similaridade entre os textos e as palavras-chave.
    - Frequência de palavras-chave nos textos.
    - Posicionamento das palavras-chave nos textos (título, parágrafo, etc.).
    - Distância entre as palavras-chave.
    """)

    st.divider()

    st.markdown("## 🛠️ Como usar:")

    with st.expander("Passo a passo para realizar uma busca", expanded=True):
        st.markdown("""
        1. Acesse a aba **Crawl Web** 🕸️
            - Insira uma URL e escolha a profundidade de busca (0 a 2).
            - Clique em **Buscar** para iniciar o scraping.

        2. Após a coleta, vá para **Search** 🔍
            - Insira até duas palavras-chave para análise.
            - Clique em **Analisar Documentos**.
            - Veja os 10 resultados mais relevantes, ordenados por similaridade e contexto.

        3. Todas as informações serão armazenadas no banco para consultas futuras.
        """)

    st.divider()
    st.caption("🧑‍💻 Desenvolvido com Streamlit, spaCy e muito carinho.")


# Setting the pages
pages = [
    st.Page(home_page, title="Home", icon="🏠"),
    st.Page("src/pages/crawl_page.py", title="Crawl Web", icon="🕸️"),
    st.Page("src/pages/analyze_page.py", title="Search", icon="🔍"),
]

# Running the app
pg = st.navigation({"ScrapeSearch": pages})
st.set_page_config(page_title="ScrapeSearch", page_icon="🔍", layout="wide")
pg.run()
