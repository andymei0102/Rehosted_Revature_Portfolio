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
