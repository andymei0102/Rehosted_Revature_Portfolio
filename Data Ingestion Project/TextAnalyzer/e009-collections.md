# Collaborative Project: Text Analytics Tool

## Overview

This is a **collaborative project** designed to synthesize the week's learning. You will work in pairs to build a text analytics tool using the collections module.

**Mode:** Collaborative (Pair Programming)
**Estimated Time:** 3-4 hours
**Prerequisites:** Content c067-c070 (Collections Module, Counter, namedtuple, OrderedDict)

---

## Collaboration Format

### Pair Programming Roles

**Driver:** Writes the code, controls the keyboard.
**Navigator:** Reviews code, thinks ahead, catches errors.

**Rotation Schedule:**

- Rotate every 30 minutes
- Both partners should drive for roughly equal time
- Document who drove which component

---

## Learning Objectives

By completing this exercise, you will be able to:

- Apply Counter for frequency analysis
- Use namedtuple for structured data
- Implement defaultdict for grouping operations
- Work collaboratively on a shared codebase

---

## The Project

Build a **Text Analytics Tool** that can analyze documents and extract insights. The tool should work with any text file and provide:

- Word frequency analysis
- N-gram analysis
- Readability metrics
- Keyword extraction

---

## Project Structure

```
text_analytics/
    README.md
    src/
        text_analytics/
            __init__.py
            analyzer.py      # Main analyzer class
            tokenizer.py     # Text tokenization
            metrics.py       # Readability metrics
            models.py        # Data structures (namedtuple)
            reports.py       # Report generation
    tests/
        test_analyzer.py
        test_tokenizer.py
    samples/
        sample_article.txt
    output/
        (generated reports)
```

---

## Core Tasks

### Part 1: Data Models (Driver A, 30 min)

In `models.py`, create namedtuples for structured data:

```python
from collections import namedtuple

# Define these namedtuples:

WordFrequency = namedtuple('WordFrequency', ['word', 'count', 'percentage'])
# Represents a word and its frequency

NGram = namedtuple('NGram', ['tokens', 'count'])
# Represents an n-gram (tuple of words) and its count

DocumentStats = namedtuple('DocumentStats', [
    'word_count',
    'unique_words',
    'sentence_count',
    'avg_word_length',
    'avg_sentence_length'
])
# Overall document statistics

AnalysisResult = namedtuple('AnalysisResult', [
    'document_stats',
    'top_words',
    'top_bigrams',
    'top_trigrams',
    'readability_score'
])
# Complete analysis result
```

### Part 2: Tokenizer (Driver B, 30 min)

In `tokenizer.py`, implement text processing:

```python
import re
from collections import Counter

def tokenize(text):
    """
    Split text into words.
    - Convert to lowercase
    - Remove punctuation
    - Remove extra whitespace
    Returns: List of words
    """
    pass

def get_sentences(text):
    """
    Split text into sentences.
    - Handle abbreviations (Dr., Mr., etc.)
    - Handle multiple punctuation (!! or ...)
    Returns: List of sentences
    """
    pass

def get_ngrams(words, n):
    """
    Generate n-grams from a list of words.
    Example: get_ngrams(['a', 'b', 'c'], 2) -> [('a', 'b'), ('b', 'c')]
    Returns: List of tuples
    """
    pass

def remove_stopwords(words, stopwords=None):
    """
    Remove common stopwords from word list.
    Use a default set if stopwords not provided.
    Returns: Filtered list of words
    """
    pass
```

### Part 3: Frequency Analysis (Driver A, 45 min)

In `analyzer.py`, implement analysis using Counter:

```python
from collections import Counter, defaultdict
from .models import WordFrequency, NGram, DocumentStats, AnalysisResult
from .tokenizer import tokenize, get_sentences, get_ngrams, remove_stopwords

class TextAnalyzer:
    """Analyzes text documents for various metrics."""
    
    def __init__(self, text):
        self.text = text
        self.words = tokenize(text)
        self.sentences = get_sentences(text)
        self.word_counter = Counter(self.words)
    
    def get_word_frequencies(self, top_n=20, exclude_stopwords=True):
        """
        Get top N word frequencies.
        Returns: List of WordFrequency namedtuples
        """
        pass
    
    def get_bigrams(self, top_n=10):
        """
        Get top N bigrams (2-word phrases).
        Returns: List of NGram namedtuples
        """
        pass
    
    def get_trigrams(self, top_n=10):
        """
        Get top N trigrams (3-word phrases).
        Returns: List of NGram namedtuples
        """
        pass
    
    def get_document_stats(self):
        """
        Calculate overall document statistics.
        Returns: DocumentStats namedtuple
        """
        pass
    
    def get_word_length_distribution(self):
        """
        Group words by length.
        Returns: defaultdict mapping length -> list of words
        """
        pass
    
    def analyze(self):
        """
        Run complete analysis.
        Returns: AnalysisResult namedtuple
        """
        pass
```

### Part 4: Readability Metrics (Driver B, 30 min)

In `metrics.py`, calculate readability:

```python
def flesch_reading_ease(word_count, sentence_count, syllable_count):
    """
    Calculate Flesch Reading Ease score.
    Formula: 206.835 - 1.015 * (words/sentences) - 84.6 * (syllables/words)
    
    Score interpretation:
    - 90-100: Very easy (5th grade)
    - 60-70: Standard (8th-9th grade)
    - 30-50: Difficult (college)
    - 0-30: Very difficult (college graduate)
    """
    pass

def count_syllables(word):
    """
    Count syllables in a word.
    Simple heuristic: count vowel groups.
    """
    pass

def calculate_readability(analyzer):
    """
    Calculate readability metrics for an analyzed document.
    Returns: Dict with various readability scores
    """
    pass
```

### Part 5: Report Generation (Driver A, 30 min)

In `reports.py`, create formatted output:

```python
from collections import OrderedDict

def generate_text_report(analysis_result, output_path):
    """
    Generate a formatted text report.
    
    Sections:
    1. Document Overview
    2. Top Words
    3. Top Phrases (bigrams/trigrams)
    4. Readability Assessment
    """
    pass

def generate_word_cloud_data(word_frequencies):
    """
    Prepare data for word cloud visualization.
    Returns: OrderedDict of word -> weight (ordered by frequency)
    """
    pass

def generate_frequency_table(word_frequencies):
    """
    Generate a formatted frequency table.
    Uses OrderedDict to maintain ranking order.
    """
    pass
```

### Part 6: Integration and Testing (Both Partners, 45 min)

1. Create `__main__.py` to run analysis from command line:

```python
def main():
    """Main entry point for the text analyzer."""
    # Parse command line arguments
    # Load text file
    # Run analysis
    # Generate reports
    pass
```

1. Write tests in `test_analyzer.py`:

```python
import pytest
from text_analytics.analyzer import TextAnalyzer
from text_analytics.tokenizer import tokenize, get_ngrams

def test_tokenize_basic():
    """Test basic tokenization."""
    pass

def test_word_frequency_ranking():
    """Test that words are ranked correctly by frequency."""
    pass

def test_ngram_generation():
    """Test n-gram generation."""
    pass

# Add at least 5 more tests
```

---

## Sample Input

Create `samples/sample_article.txt` with any article (~500 words).

---

## Expected Output

```
=== Text Analysis Report ===
Generated: 2024-01-18

Document Statistics:
- Word Count: 523
- Unique Words: 287
- Sentence Count: 32
- Average Word Length: 4.8 characters
- Average Sentence Length: 16.3 words

Top 10 Words (excluding stopwords):
1. data (15) - 2.87%
2. analysis (12) - 2.29%
3. python (10) - 1.91%
...

Top 5 Bigrams:
1. "machine learning" (5)
2. "data analysis" (4)
...

Readability:
- Flesch Reading Ease: 58.2 (Standard - 8th-9th grade)
```

---

## Definition of Done

- [ ] All namedtuples are defined correctly
- [ ] Tokenizer handles edge cases (punctuation, whitespace)
- [ ] Counter-based frequency analysis works
- [ ] Readability metrics are calculated
- [ ] Report generation produces clean output
- [ ] At least 8 tests pass
- [ ] Both partners contributed code (documented)

---

## Collaboration Log

Track your pair programming:

| Time | Driver | Navigator | Component |
|------|--------|-----------|-----------|
| 0:00-0:30 | Partner A | Partner B | models.py |
| 0:30-1:00 | Partner B | Partner A | tokenizer.py |
| ... | ... | ... | ... |

---

## Submission

1. Ensure all code is committed
2. Include collaboration log in README.md
3. Run all tests and verify they pass
4. Analyze the sample text and include output
5. Be prepared to explain your partner's code
