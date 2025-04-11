"""
This module contains the logic for indexing the crawled data.
It includes functions to connect to the database, insert data, and fetch data.
"""

from src.models.page_analysis import PageAnalysis
from src.utils.config import get_logger

# -- Initialize the logger
logger = get_logger()


def _connect_to_database(db_config: dict) -> object:
    """
    Factory function to connect to the database.
    This function will determine the type of database to connect to and return the appropriate connection object.
    Currently, it supports SQLite and MySQL.

    Parameters:
        db_config - dict: The database configuration dictionary.

    Returns:
        connection - object: The database connection object.
    """
    if db_config["DBTYPE"] == "SQLite":
        from src.utils.sqlite_schema import connect_to_database

        return connect_to_database(db_config)
    elif db_config["DBTYPE"] == "MySQL":
        from src.utils.mysql_schema import connect_to_database

        return connect_to_database(db_config)
    else:
        raise ValueError(
            "Unsupported database type. Supported types are: SQLite, MySQL."
        )


class Indexer:
    """
    Class for indexing crawled data.
    It provides methods to insert and fetch data from the database.

    This class supports the following database connections:
    - SQLite
    - MySQL

    Attributes:
        db_connection - object: The database connection object.
        cursor - object: The database cursor object.
        database_type - str: The type of database (SQLite or MySQL).

    Methods:
        insert_url(url: str): Inserts a URL into the database.
        insert_word(word: str): Inserts a word into the database.
        insert_word_location(idurl: int, idpalavra: int, localizacao: int): Inserts a word location into the database.
        fetch_urls(url: str): Fetches a URL from the database.
        fetch_words(word: str): Fetches a word from the database.
        fetch_word_location(idurl: int, idpalavra: int): Fetches word locations from the database.
    """

    def __init__(self, db_config: dict) -> None:
        """
        Initialize the Indexer class.

        Parameters:
            db_config - dict: The database configuration dictionary.
        """
        self.db_connection = _connect_to_database(db_config)
        self.cursor = self.db_connection.cursor() if self.db_connection else None
        self.database_type = db_config["DBTYPE"]

    def _execute_query(self, query: str, params: tuple = ()) -> bool:
        """
        Execute a query with the appropriate placeholders for the database type.

        Parameters:
            query - str: The SQL query to execute.
            params - tuple: The parameters for the query.

        Returns:
            bool: True if the query was executed successfully, False otherwise.
        """
        # -- If the database type is SQLite, use "?" as the placeholder
        # -- If the database type is MySQL, use "%s" as the placeholder
        if self.database_type == "MySQL":
            query = query.replace("?", "%s")

        try:
            # -- Execute the query with the appropriate placeholders
            self.cursor.execute(query, params)

            # -- Commit the changes to the database
            self.db_connection.commit()
        except Exception as e:
            logger.error(f"Error executing query: {query}")
            logger.debug(f"Parameters: {params}")
            logger.debug(e, exc_info=True)
            return False

        return True

    def insert_url(self, url: str) -> int:
        """
        Insert a URL into the database if it is not already present.

        Parameters:
            url - str: The URL to insert.

        Returns:
            int: The ID of the inserted URL.
        """
        # -- Check if the URL already exists in the database
        existing_url = self.fetch_url(url)
        if existing_url:
            logger.info(f"URL already registered: {url}")
            return existing_url[0][0]

        # -- Prepare the SQL query
        # TODO: Add text_content and vector_map to the table
        query = """
            INSERT INTO urls (url)
            VALUES (?)
        """

        # -- Execute the query with the appropriate placeholders
        if self._execute_query(query, (url,)):
            logger.info(f"URL successfully registered: {url}")
            return self.cursor.lastrowid
        else:
            logger.error(f"Error registering URL: {url}")
            return None

    def insert_word(self, word: str) -> int:
        """
        Insert a word into the database if it is not already present.

        Parameters:
            word - str: The word to insert.

        Returns:
            int: The ID of the inserted word.
        """
        # -- Check if the word already exists in the database
        existing_word = self.fetch_word(word)
        if existing_word:
            logger.info(f"Word already registered: {word}")
            return existing_word[0][0]

        # -- Prepare the SQL query
        query = """
            INSERT INTO palavras (palavra)
            VALUES (?)
        """

        # -- Execute the query with the appropriate placeholders
        if self._execute_query(query, (word,)):
            logger.info(f"Word successfully registered: {word}")
            return self.cursor.lastrowid
        else:
            logger.error(f"Error registering word: {word}")
            return None

    def insert_word_location(self, idurl: int, idpalavra: int, localizacao: int):
        """
        Insert a word location into the database.

        Parameters:
            idurl - int: The ID of the URL.
            idpalavra - int: The ID of the word.
            localizacao - int: The location of the word in the URL.
        """
        # -- Check if the word location already exists in the database
        existing_word_location = self.fetch_word_location(idurl, idpalavra, localizacao)
        if existing_word_location:
            logger.info("Word location already registered")
            return existing_word_location[0][0]

        # -- Prepare the SQL query
        query = """
            INSERT INTO palavra_localizacao (idurl, idpalavra, localizacao)
            VALUES (?, ?, ?)
        """

        # -- Execute the query with the appropriate placeholders
        if self._execute_query(query, (idurl, idpalavra, localizacao)):
            logger.info(
                f"Word location successfully registered: URL {idurl}, Word {idpalavra}, Location {localizacao}"
            )
            return self.cursor.lastrowid
        else:
            logger.error("Error registering word location")
            logger.debug(f"URL: {idurl}, Word: {idpalavra}, Location: {localizacao}")
            return None

    def fetch_url(self, url: str) -> list:
        """
        Fetch URL from the database.

        Parameters:
            url - str: The URL to fetch.

        Returns:
            list: A list of URLs.
        """
        # -- Prepare the SQL query
        query = """
            SELECT * FROM urls WHERE url = ?
        """

        # -- Execute the query with the appropriate placeholders
        self._execute_query(query, (url,))

        # -- Fetch all results
        return self.cursor.fetchall()

    def fetch_word(self, word: str) -> list:
        """
        Fetch word from the database.

        Parameters:
            word - str: The word to fetch.

        Returns:
            list: A list of words.
        """
        # -- Prepare the SQL query
        query = """
            SELECT * FROM palavras WHERE palavra = ?
        """

        # -- Execute the query with the appropriate placeholders
        self._execute_query(query, (word,))

        # -- Fetch all results
        return self.cursor.fetchall()

    def fetch_word_location(self, idurl: int, idpalavra: int, localizacao: int) -> list:
        """
        Fetch word location from the database.

        Parameters:
            idurl - int: The ID of the URL.
            idpalavra - int: The ID of the word.
            localizacao - int: The location of the word in the URL.

        Returns:
            list: A list of word locations.
        """
        # -- Prepare the SQL query
        query = """
            SELECT * FROM palavra_localizacao
            WHERE idurl = ? AND idpalavra = ? AND localizacao = ?
        """

        # -- Execute the query with the appropriate placeholders
        self._execute_query(query, (idurl, idpalavra, localizacao))

        # -- Fetch all results
        return self.cursor.fetchall()

    def save_analysis(self, analysis: PageAnalysis) -> bool:
        """
        Save the full analysis result into the database.

        Parameters:
            analysis - PageAnalysis: The result of the analysis for a given page.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        try:
            # -- Insert URL and get ID
            idurl = self.insert_url(analysis.url)
            if idurl is None:
                logger.warning(f"Could not insert URL: {analysis.url}")
                return False

            for kw in analysis.keywords:
                # -- Insert word and get ID
                idpalavra = self.insert_word(kw.word)
                if idpalavra is None:
                    logger.warning(f"Could not insert keyword: {kw.word}")
                    continue

                # -- Insert word location
                for pos in kw.positions:
                    self.insert_word_location(idurl, idpalavra, pos)

            logger.info(f"Analysis successfully saved for {analysis.url}")
            return True

        except Exception as e:
            logger.error(f"Error saving analysis for {analysis.url}")
            logger.debug(e, exc_info=True)
            return False
