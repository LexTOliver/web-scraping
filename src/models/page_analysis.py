"""
This module defines the PageAnalysis and KeywordInfo classes for analyzing web pages.
"""

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class KeywordInfo:
    """
    Keyword information for a web page.

    Attributes:
        word - str: The keyword.
        positions - List[int]: The positions of the keyword in the text.
        count - int: The number of occurrences of the keyword.
    """

    word: str
    positions: List[int] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.positions)

    def __repr__(self) -> str:
        return f"KeywordInfo(word={self.word}, positions={self.positions}, count={self.count})"


# TODO: Add content attribute to PageAnalysis class (?)
@dataclass
class PageAnalysis:
    """
    Page analysis information.

    Attributes:
        url - str: The URL of the web page.
        similarity - float: The similarity score of the page.
        keywords - List[KeywordInfo]: A list of keyword information.
        score - float: The score of the page analysis.
        frequency - int: The frequency of keywords in the page analysis.

    Methods:
        to_dict: Converts the PageAnalysis object to a dictionary.
    """

    url: str
    similarity: float
    keywords: List[KeywordInfo]
    score: float = 0.0

    @property
    def frequency(self) -> int:
        """
        Calculate the frequency of keywords in the page analysis.

        Returns:
            int: The frequency of keywords.
        """
        return sum(kw.count for kw in self.keywords)

    def to_dict(self) -> Dict:
        return {
            "url": self.url,
            "score": self.score,
            "similarity": self.similarity,
            "frequency": self.frequency,
            "keywords": [
                {"word": kw.word, "positions": kw.positions, "count": kw.count}
                for kw in self.keywords
            ],
        }
