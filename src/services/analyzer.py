"""
This module contains the DocumentAnalyzer class, which is responsible for analyzing documents.
It processes the documents with spaCy, as follows:
- Uses spaCy to vectorize the document and the keywords.
- Execute the following document transformations:
    - Lowercase the document and keywords.
    - Remove stop words and punctuation.
    - Lemmatize the document and keywords.
    - Find the location of the keywords in the document.
- Calculates the score based on:
    - Vector similarity between the document and the keywords.
    - Frequency of the keywords in the document (sum(keyword1_count, keyword2_count)); the more they appear, the better.
    - Location of the keywords in the document (sum(keyword1_index, keyword2_index)); the closer they are to the beginning, the better.
    - Distance between the keywords in the document (keyword1_index - keyword2_index); the closer they are, the better.
- Sorting the documents based on the score, returns the 10 best documents.
"""

import numpy as np
import pt_core_news_md
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from time import time
from src.utils.config import get_logger
from src.models.page_analysis import PageAnalysis, KeywordInfo

# -- Initialize the trained pipeline from spaCy
nlp = pt_core_news_md.load()

# -- Get the logger
logger = get_logger()

# -- Set default score weights
DEFAULT_SCORE_WEIGHTS = {
    "similarity": 0.4,
    "frequency": 0.3,
    "position": 0.2,
    "distance": 0.1,
}


class DocumentAnalyzer:
    """
    Class to analyze documents and calculate scores based on keywords and other criteria.

    Attributes:
    """

    def __init__(self, pages: list, keywords: str) -> None:
        """
        Initialize the DocumentAnalyzer with keywords and pages.

        Parameters:
            pages - list: List of pages to analyze.
        """
        self.documents = self._generate_documents(pages)
        self.keywords = self._process_keywords(keywords)

    def _generate_documents(self, pages: list) -> list:
        """
        Generate documents from the given pages.
        This method processes the content of each page using spaCy.
        It extracts relevant information such as lemmatized words and vectors.
        It also handles the removal of stop words and punctuation.

        Parameters:
            pages - list: List of pages to process.

        Returns:
            documents - list: List of processed documents.
        """
        documents = []
        for page in pages:
            # -- Get the URL and content from the page
            url, content = page
        
            # -- Process the content with spaCy
            content = content.lower()  # Lowercase the content
            doc = nlp(content)  # Process the content with spaCy
            word_list = [
                token.lemma_
                for token in doc
                if not token.is_stop and not token.is_punct
            ]
            
            documents.append({
                "url": url,  # Source URL
                "content": content,  # Original content
                "doc": doc,  # Processed document with spaCy object
                "words": word_list,  # Bag of lemmatized words
            })

        logger.info("Documents were generated based on the pages.")
        return documents

    def _process_keywords(self, keywords: str) -> list:
        """
        Process the keywords using spaCy.
        This method lemmatizes the keywords and removes stop words and punctuation.

        Parameters:
            keywords - str: Keywords to process.

        Returns:
            processed_keywords - list: List of processed keywords.
        """
        # -- Lowercase the keywords
        keywords = keywords.lower()

        # -- Process the keywords with spaCy
        words = nlp(keywords)

        # -- Get the lemmatized words and tokens removing stop words and punctuation
        processed_keywords = [
            {
                "word": token.lemma_,
                "token": token,
            }
            for token in words
            if not token.is_stop and not token.is_punct
        ]
        logger.info(f"Keywords processed: {processed_keywords}")
        return processed_keywords

    def _validate_score_weights(self, score_weights: dict) -> bool:
        """
        Validate the score weights.
        This method checks if the score weights are valid and sum to 1.

        Parameters:
            score_weights - dict: Weights for the scoring criteria.
                - similarity
                - position
                - distance
                - frequency

        Returns:
            bool: True if the score weights are valid, False otherwise.
        """
        if not all(key in score_weights for key in DEFAULT_SCORE_WEIGHTS.keys()):
            logger.error("Invalid score weights provided.")
            return False
        if not all(0 <= weight <= 1 for weight in score_weights.values()):
            logger.error("Score weights must be between 0 and 1.")
            return False
        if not np.isclose(sum(score_weights.values()), 1):
            logger.error("Score weights must sum to 1.")
            return False
        return True

    def analyze_documents(self) -> list:
        """
        Analyze all documents for similarity and keyword location.
        This method calculates the similarity between the keywords and the documents.
        It also finds the locations of the keywords in the documents.

        Returns:
            analyses - list: List of PageAnalysis objects containing:
                - url
                - similarity
                - keywords (list of KeywordInfo objects)
        """
        analyses = []

        # -- Iterate over each document
        # -- and calculate the similarity and keyword locations
        for doc in self.documents:
            keyword_locations = defaultdict(list)
            similarities = []

            # -- Iterate over each keyword
            for kw in self.keywords:
                kw_word = kw["word"]
                token = kw["token"]

                # -- Calculate the similarity between the keyword and the document
                similarity = token.similarity(doc["doc"])
                similarities.append(similarity)

                # -- Find the locations of the keywords in the document
                for idx, word in enumerate(doc["words"]):
                    if word == kw_word:
                        keyword_locations[kw_word].append(idx)

            # -- Set keywords info
            keywords_info = [
                KeywordInfo(word=w, positions=positions)
                for w, positions in keyword_locations.items()
            ]
            
            # -- Append the analysis to the results
            # -- Calculate the average similarity from the keywords in the document
            analyses.append(
                PageAnalysis(
                    url=doc["url"],
                    similarity=float(np.mean(similarities)),
                    keywords=keywords_info,
                )
            )

        return analyses

    def calculate_scores(self, score_weights: dict = DEFAULT_SCORE_WEIGHTS) -> list:
        """
        Calculate the score for each document based on:
        - Vector similarity (average of keywords)
        - Frequency of keywords
        - Position of keywords (the earlier, the better)
        - Distance between keywords (the closer, the better)
        This method evaluates the documents and calculates a score for each document.

        Parameters:
            score_weights - dict: Weights for the scoring criteria.
                - similarity
                - frequency
                - position
                - distance
                Default weights are set in DEFAULT_SCORE_WEIGHTS.

        Returns:
            scored_docs - list: List of PageAnalysis objects with calculated scores.
        """
        # -- Check if the score weights are valid
        # -- If the score weights are not the default, validate them
        if score_weights != DEFAULT_SCORE_WEIGHTS:
            if not self._validate_score_weights(score_weights):
                logger.error("Invalid score weights provided. Using default weights.")
                score_weights = DEFAULT_SCORE_WEIGHTS

        # -- Evaluate the documents for similarity and keyword locations
        analyzed_docs = self.analyze_documents()

        # -- Calculate the score for each document
        scored_docs = []
        for analysis in analyzed_docs:
            all_positions = []
            first_occurrences = []

            # -- Get the first occurrences and all positions of the keywords
            for kw in analysis.keywords:
                if kw.positions:
                    first_occurrences.append(min(kw.positions))
                    all_positions.extend(kw.positions)

            # -- If there are no keywords in the document, set the score to 0
            if not first_occurrences:
                analysis.score = 0
            else:
                # -- Base values for scoring
                # -- Similarity: average similarity of the keywords in the document
                # -- Frequency: sum of keyword frequencies
                # -- Position: 1 / (1 + sum(first_occurrences))
                # -- Distance: 1 / (1 + max(first_occurrences) - min(first_occurrences))
                position_score = 1 / (1 + sum(first_occurrences))
                distance_score = (
                    1 / (1 + max(first_occurrences) - min(first_occurrences))
                    if len(first_occurrences) > 1
                    else 0
                )

                # -- Final score calculation
                # -- The weights are multiplied by the respective scores
                # -- and summed to get the final score
                analysis.score = (
                    score_weights["similarity"] * analysis.similarity
                    + score_weights["frequency"] * analysis.frequency
                    + score_weights["position"] * position_score
                    + score_weights["distance"] * distance_score
                )

            # -- Append the analysis to the scored_docs
            scored_docs.append(analysis)

        # -- Sort the documents by score in descending order
        scored_docs.sort(key=lambda x: x.score, reverse=True)
        return [a.to_dict() for a in scored_docs]
    

    def get_document_analyses(self) -> list:
        """
        Get the document analyses.

        Returns:
            list: List of document analyses.
        """
        # -- Calculate the scores for the documents
        return self.calculate_scores()
