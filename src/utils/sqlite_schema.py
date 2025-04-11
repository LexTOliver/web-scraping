"""
SQLite database schema for web scraping project.
This module defines the schema for the SQLite database used in the web scraping project.
It includes functions to create the necessary tables and establish a connection to the database.

The schema includes the following tables:
1. urls: Stores the URLs scraped from the web.
2. palavras: Stores the words found in the scraped content.
3. palavra_localizacao: Stores the location of words in the URLs.
"""

import sqlite3
from src.utils.config import get_logger

# -- Initialize the logger
logger = get_logger()


def connect_to_database(db_config: dict) -> sqlite3.Connection:
    """
    Connect to SQLite database.
    If the database does not exist, it will be created.

    Parameters:
        db_config - dict: The database configuration dictionary.
            It should contain the following keys:
            - DBPATH: The path to the SQLite database file.

    Returns:
        connection - sqlite3.Connection: The database connection object.
    """
    # -- Connect to the SQLite database
    try:
        # -- If the database does not exist, it will be created
        connection = sqlite3.connect(db_config["DBPATH"])

        # -- Check if database was created
        if connection is None:
            logger.error("Failed to create or connect to the database.")
            return None

        # -- Set the connection to use foreign keys
        connection.execute("PRAGMA foreign_keys = ON;")
        connection.commit()

        # -- Check if the database is empty
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        cursor.close()

        # -- Create the tables if the database is empty
        if not tables:
            create_tables(connection)

    except sqlite3.DatabaseError as e:
        logger.error("Error connecting to the database.")
        logger.debug(e, exc_info=True)
        return None

    return connection


def create_url_table(cursor: sqlite3.Cursor) -> None:
    """
    Create the URL table in the database.

    Parameters:
        cursor - sqlite3.Cursor: The database cursor object.
    """
    # -- Create the URL table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            idurl INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL
        );
    """)

    # -- Create an index on the URL column
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_urls_url ON urls (url);
    """)


def create_word_table(cursor: sqlite3.Cursor) -> None:
    """
    Create the word table in the database.

    Parameters:
        cursor - sqlite3.Cursor: The database cursor object.
    """
    # -- Create the word table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS palavras (
            idpalavra INTEGER PRIMARY KEY AUTOINCREMENT,
            palavra VARCHAR(200) NOT NULL
        );
        
    """)

    # -- Create an index on the word column
    cursor.execute("""
        CREATE INDEX idx_palavras_palavra ON palavras (palavra);
    """)


def create_word_location_table(cursor: sqlite3.Cursor) -> None:
    """
    Create the word location table in the database.

    Parameters:
        cursor - sqlite3.Cursor: The database cursor object.
    """
    # -- Create the word location table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS palavra_localizacao (
            idpalavra_localizacao INTEGER PRIMARY KEY AUTOINCREMENT,
            idurl INTEGER NOT NULL,
            idpalavra INTEGER NOT NULL,
            localizacao INTEGER NOT NULL,
            FOREIGN KEY (idurl) REFERENCES urls (idurl),
            FOREIGN KEY (idpalavra) REFERENCES palavras (idpalavra)
        );
        
    """)

    # -- Create an index on the idpalavra column
    cursor.execute("""
        CREATE INDEX idx_palavra_localizacao_idpalavra ON palavra_localizacao (idpalavra);
    """)


def create_tables(db_connection: sqlite3.Connection) -> None:
    """
    Create the necessary tables in the database.

    Parameters:
        connection - sqlite3.Connection: The database connection object.
    """
    try:
        # -- Create a cursor object
        cursor = db_connection.cursor()

        # -- Create the tables
        create_url_table(cursor)
        create_word_table(cursor)
        create_word_location_table(cursor)

        # -- Commit the changes
        db_connection.commit()

    except sqlite3.OperationalError as e:
        logger.error("Operational error connecting to the database:")
        logger.debug(e, exc_info=True)

    # -- Close the cursor
    cursor.close()


def close_database(connection: sqlite3.Connection) -> None:
    """
    Close the database connection.

    Parameters:
        connection - sqlite3.Connection: The database connection object.
    """
    # -- Close the database connection
    if connection:
        connection.close()
