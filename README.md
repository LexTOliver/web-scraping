# ScrapeSearch

This project is designed to work as a Search Engine for a specific website. It allows users to input a URL and two keywords (**in portuguese**), and then it scrapes the webpage for links in a certain depth. The application evaluates the links based on the presence of the keywords and other criteria, providing a score for each document. The links with the highest scores are returned to the user.

## Search Score Criteria
The application evaluates documents based on the following criteria:
- **Vector Similarity** (TODO): The similarity score between the document and the keywords.
- **Keyword Presence**: The number of times the keywords appear in the documents.
- **Keyword Location**: The position of the keywords (the minimum sum of the two words) in the documents.
- **Keyword Distance**: The distance between the two keywords in the documents.

## Features

- **Web scraping**: Fetches content from a specified URL and extracts links, going a user-defined depth.
- **Indexing**: Stores the scraped data in a SQLite database, allowing for efficient retrieval and analysis.
- **Document analysis**: Evaluates documents based on user-defined keywords and criteria. The application calculates scores for each document and identifies the best ones.

## Project Structure

```
web-scraping-project
├── data
│   └── database.db           # SQLite database for storing documents and metadata
├── src
|   ├── pages
│   │   ├── analyze_page.py   # Streamlit page for document analysis
│   │   └── crawl_page.py     # Streamlit page for web crawling
|   ├── utils
│   |   ├── config.py         # Configuration settings for the application
│   |   ├── mysql_schema.py   # MySQL schema functions for creating and managing the database
│   |   └── sqlite_schema.py  # SQLite schema functions for creating and managing the database
│   ├── analyzer.py           # Contains the DocumentAnalyzer class for evaluating documents
│   ├── crawler.py            # Contains the WebCrawler class for fetching content and links
│   └── indexer.py            # Contains the Indexer class for storing and retrieving documents
├── .gitignore                # Files and directories to be ignored by Git
├── .python-version           # Python version for the project
├── app.py                    # Streamlit application entry point
├── example_config.yaml      # Example configuration file for the application
├── LICENSE                   # License file for the project
├── main.py                   # Entry point of the application
├── pyproject.toml            # Project metadata and dependencies
├── README.md                 # Project documentation
├── requirements.txt          # Project dependencies
└── uv.lock                   # UV environment lock file
```

## Setup Instructions
Clone the repository, create a virtual environment, install the required dependencies and set environment variables with application settings.

### Virtual Environment
1. With pip:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
    pip install -r requirements.txt
    ```
2. With UV:
    ```bash
    uv venv
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
    uv sync

    spacy download pt_core_news_md  # Download the Portuguese trained pipeline for spaCy
    ```

    Obs.: The spacy pipeline model is not included in the installation process through UV, so it needs to be downloaded separately.

### Environment Variables
The application sets up environment variables in a YAML file (e.g. [`example_config.yaml`](./example_config.yaml)). 

By default, the application uses the example settings (with SQLite and some default settings) for running without any additional setup. However, it is recommended to create a custom configuration file for your specific needs, including database connection settings for MySQL.

You must:
- Create a `config.yaml` file in the root directory.
- Change the reference from `example_config.yaml` to `config.yaml` in the necessary files (`main.py`, `app.py`, `src/utils/config.py`). 

## Usage
You can run the application via command line or through a Streamlit interface.

1. From the command line:

    Run the following command in your terminal:
    ```
    python src/main.py
    ```

    Follow the prompts to enter a URL, depth for search (up to 2) and two keywords. The application will scrape the specified webpage, retrieve links, and analyze the documents based on the criteria.

2. Through Streamlit interface:

    The instructions will appear on the Streamlit interface. You can run the application using:
    ```bash
    streamlit run app.py
    ```

## Example

- Input:
    ```
    Enter a URL: https://example.com
    Enter the depth for search (up to 2): 2
    Enter the first keyword: Python
    Enter the second keyword: Programação
    ```

- Output:
    ```
    The links with the highest scores are:
    - https://example.com/document1
    - https://example.com/document2
    - https://example.com/document3
    ...
    ```

## Main Dependencies
- BeautifulSoup4, for web scraping
- spaCy, for natural language processing
- SQLite3 and PyMySQL, for database management
- Streamlit, for the web interface
- requests, for making HTTP requests
- PyYAML, for configuration file handling

Make sure to check the `requirements.txt` file or `pyproject.toml` for the specific versions of the libraries used in this project.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.