import streamlit as st
from src.services.analyzer import DocumentAnalyzer
from src.models.page_analysis import PageAnalysis, KeywordInfo


def init_session_state() -> None:
    """
    Initializes the session state variables for the Streamlit app.
    It sets initial values for analysis results and keywords.
    """
    # -- Initialize session state variables
    if "analysis_results" not in st.session_state:
        st.session_state.analysis_results = []


def page_setup() -> None:
    """
    Sets up the analysis page of the web scraping application.
    """
    # -- Initialize session state
    init_session_state()

    # -- Page title
    st.title("🔍 Search")
    st.markdown(
        "Use esta página para buscar e analisar as palavras-chave nos links coletados."
    )

    # -- Check if links and contents are available
    if not st.session_state.get("links") or not st.session_state.get("contents"):
        st.warning("Você precisa primeiro coletar os links na aba *Crawl Web*.")
        return

    # -- Input fields for keywords
    st.subheader("🧠 Palavras-chave para análise:")
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Palavra-chave 1", key="keyword1", placeholder="Ex: Teste")
    with col2:
        st.text_input("Palavra-chave 2", key="keyword2", placeholder="Ex: Exemplo")

    # -- Analyze button
    if st.button("Analisar Documentos"):
        # -- Clear last analysis results
        st.session_state.analysis_results = []

        # -- Get the input values
        keyword1 = st.session_state.keyword1
        keyword2 = st.session_state.keyword2

        # -- Validate input
        if not keyword1 or not keyword2:
            st.error("Por favor, preencha as duas palavras-chave.")
            return
        elif keyword1.strip().lower() == keyword2.strip().lower():
            st.error("As palavras-chave devem ser diferentes.")
            return

        # -- Prepare the documents for analysis
        documents = list(zip(st.session_state.links, st.session_state.contents))
        keywords = f"{keyword1} {keyword2}"

        # -- Perform analysis
        with st.spinner("Analisando documentos..."):
            results = search_keywords(documents, keywords)

        # -- Store the results in session state
        st.session_state.analysis_results = results

        # -- Exibe os 10 melhores resultados
        st.success("Análise concluída com sucesso!")

    # -- Display the results and save button
    if st.session_state.analysis_results:
        show_results(st.session_state.analysis_results)

        _, col2 = st.columns([4, 1])
        with col2:
            if st.button("Salvar Análise"):
                save_analyses(st.session_state.analysis_results)


def show_results(results: list) -> None:
    """
    Displays the analysis results in a structured format.

    Parameters:
        results - list: A list of dictionaries containing the analysis results
    """
    st.divider()
    st.subheader("📊 Top 10 resultados:")

    # -- Display the results as containers
    for i, res in enumerate(results[:10], 1):
        with st.container():
            # -- The URL
            st.markdown(f"#### {i}. [{res['url']}]({res['url']})")

            # -- The score and similarity
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Score:** {res['score']:.4f}")
            with col2:
                st.markdown(f"**Similaridade:** {res['similarity']:.4f}")

            # -- The frequency of the keywords found
            st.markdown("**Ocorrências:**")
            for kw in res["keywords"]:
                st.markdown(f"- `{kw['word']}` → {len(kw['positions'])} ocorrência(s).")
            st.markdown("---")


def search_keywords(pages: list, keywords: str) -> list:
    """
    Search for keywords in the given pages and return the results.

    Parameters:
        pages - list: A list of PageAnalysis objects
        keywords - str: The keywords to search for

    Returns:
        list: A list of dictionaries containing the analysis results
    """
    # -- Create a DocumentAnalyzer instance
    analyzer = DocumentAnalyzer(pages, keywords)

    # -- Search for keywords in the pages
    results = analyzer.get_document_analyses()

    # -- Check if results are empty
    if not results:
        st.warning("Nenhum resultado foi encontrado para as palavras-chave fornecidas.")
        return None

    return results


def save_analyses(results: list) -> None:
    """
    Save the analysis results to the database.

    Parameters:
        results - list: A list of dictionaries containing the analysis results
    """
    # -- Check if indexer is available
    if "indexer" not in st.session_state:
        st.error("O indexador não está disponível. Volte para a aba *Home*.")
        return

    # -- Check if indexer has connection
    indexer = st.session_state.indexer
    if not indexer.db_connection:
        st.error(
            "Sem conexão com o banco de dados. Verifique se o sistema está devidamente configurado."
        )
        return

    # -- Save the analysis results to the database
    for res in results:
        try:
            analysis = PageAnalysis(
                url=res["url"],
                similarity=res["similarity"],
                score=res["score"],
                keywords=[
                    KeywordInfo(word=kw["word"], positions=kw["positions"])
                    for kw in res["keywords"]
                ],
            )
            indexer.save_analysis(analysis)
        except Exception:
            st.error(f"Erro ao salvar análise da URL: {res['url']}")
            return

    st.success("Todas as análises foram salvas com sucesso no banco de dados! 🎉")


page_setup()
