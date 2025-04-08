"""
MySQL schema for the web scraping project.
This module defines the schema for the MySQL database used in the web scraping project.
It includes functions to create the necessary tables and establish a connection to the database.

The schema includes the following tables:
1. urls: Stores the URLs scraped from the web.
2. palavras: Stores the words found in the scraped content.
3. palavra_localizacao: Stores the location of words in the URLs.
"""

import pymysql
from src.utils.config import get_logger

# -- Initialize the logger
logger = get_logger()

def connect_to_database(db_config: dict) -> pymysql.connections.Connection:
    """
    Connect to MySQL database.

    Parameters:
        db_config - dict: The database configuration dictionary.
            It should contain the following keys:
            - DBPATH: The path to the MySQL database file.
            - HOST: The host of the MySQL server.
            - USER: The username for the MySQL server.
            - PASSWORD: The password for the MySQL server.
            - DBNAME: The name of the MySQL database.
            - DBTYPE: The type of database (MySQL).
    Returns:
        connection - pymysql.connections.Connection: The database connection object.
    """
    # -- Connect to the MySQL database
    connection = pymysql.connect(
        host=db_config["HOST"],
        user=db_config["USER"],
        password=db_config["PASSWORD"],
        db=db_config["DBNAME"],
        autocommit=True,
        use_unicode=True,
        charset="utf8mb4",
    )

    # -- Check if database was created
    if connection is None:
        logger.error("Failed to create or connect to the database.")
        return None

    # -- Check if the database is empty
    cursor = connection.cursor()
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()
    if not tables:
        # -- Create the tables if the database is empty
        if db_config["DBPATH"]:
            load_sql_file(connection, db_config["DBPATH"])
        else:
            create_tables(connection)

    return connection


def load_sql_file(
    connection: pymysql.connections.Connection, sql_file_path: str
) -> None:
    """
    Load and execute a SQL file into the database.

    Parameters:
        connection - pymysql.connections.Connection: The database connection object.
        sql_file_path - str: The path to the SQL file to load.
    """
    # -- Read the SQL file
    with open(sql_file_path, "r", encoding="utf-8") as sql_file:
        sql_commands = sql_file.read()

    # Split the SQL file into individual commands
    commands = sql_commands.split(";")

    with connection.cursor() as cursor:
        for command in commands:
            command = command.strip()
            if command:  # Skip empty commands
                try:
                    cursor.execute(command)
                except Exception as e:
                    logger.error(f"Error executing command on loading data from SQL file: {command}")
                    logger.debug(e, exc_info=True)

    connection.commit()


def create_url_table(cursor: pymysql.cursors.Cursor) -> None:
    """
    Create the URL table in the database.

    Parameters:
        cursor - pymysql.cursors.Cursor: The database cursor object.
    """
    # -- Create the URL table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            idurl INT AUTO_INCREMENT PRIMARY KEY,
            url VARCHAR(1000) NOT NULL
        );
    """)

    # -- Create the index for the URL column
    cursor.execute("""
        CREATE INDEX idx_urls_url ON urls (url);
    """)


def create_word_table(cursor: pymysql.cursors.Cursor) -> None:
    """
    Create the word table in the database.

    Parameters:
        cursor - pymysql.cursors.Cursor: The database cursor object.
    """
    # -- Create the word table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS palavras (
            idpalavra INT AUTO_INCREMENT PRIMARY KEY,
            palavra VARCHAR(200) NOT NULL
        );
    """)

    # -- Create the index for the word column
    cursor.execute("""
        CREATE INDEX idx_palavras_palavra ON palavras (palavra);
    """)


def create_word_location_table(cursor: pymysql.cursors.Cursor) -> None:
    """
    Create the word location table in the database.

    Parameters:
        cursor - pymysql.cursors.Cursor: The database cursor object.
    """
    # -- Create the word location table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS palavra_localizacao (
            idpalavra_localizacao INT AUTO_INCREMENT PRIMARY KEY,
            idurl INT NOT NULL,
            idpalavra INT NOT NULL,
            localizacao INT NOT NULL,
            FOREIGN KEY (idurl) REFERENCES urls (idurl),
            FOREIGN KEY (idpalavra) REFERENCES palavras (idpalavra)
        );
    """)

    # -- Create the index for the word location table
    cursor.execute("""
        CREATE INDEX idx_palavra_localizacao_idpalavra ON palavra_localizacao (idpalavra);
    """)


def create_tables(db_connection: pymysql.connections.Connection) -> None:
    """
    Create the necessary tables in the database.

    Parameters:
        db_connection - pymysql.connections.Connection: The database connection object.
    """
    with db_connection.cursor() as cursor:
        create_url_table(cursor)
        create_word_table(cursor)
        create_word_location_table(cursor)

    db_connection.commit()

def close_database_connection(connection: pymysql.connections.Connection) -> None:
    """
    Close the database connection.

    Parameters:
        connection - pymysql.connections.Connection: The database connection object.
    """
    if connection:
        connection.close()
