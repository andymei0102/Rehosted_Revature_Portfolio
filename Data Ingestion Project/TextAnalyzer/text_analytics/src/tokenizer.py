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
    text = text.lower()

    words = text.split(' ')

    for word in words:
        word = word.strip()

    # pattern for removing punctuation
    pattern = r'[^\w\s]+'

    words = [re.sub(pattern, '', word) for word in words]

    return words




def get_sentences(text):
    """
    Split text into sentences.
    - Handle abbreviations (Dr., Mr., etc.)
    - Handle multiple punctuation (!! or ...)
    Returns: List of sentences
    """
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return sentences

def get_ngrams(words, n):
    """
    Generate n-grams from a list of words.
    Example: get_ngrams(['a', 'b', 'c'], 2) -> [('a', 'b'), ('b', 'c')]
    Returns: List of tuples
    """
    ngrams_list = []
    for i in range(len(words) - n + 1):
        ngrams_list.append(tuple(words[i:i + n]))
    return ngrams_list


def remove_stopwords(words, stopwords=["a", "an", "the", "in", "and", "is", "of", "to", "for"]):
    """
    Remove common stopwords from word list.
    Use a default set if stopwords not provided.
    Returns: Filtered list of words
    """
    return list(filter(lambda x : x not in stopwords, words))


# print(get_sentences("Mr. John Johnson Jr was born in the U.S.A. Is he an engineer? Yes, he is!"))
# print(get_sentences("Mr. John Johnson... Jr. was born in the U.S.A. Is he an engineer? Yes, he is!"))

# print(get_ngrams(['a', 'b', 'c'], 2))

# words = ["a", "an", "the", "in", "and", "is", "of", "to", "for", "example", "example1"]
# print(remove_stopwords(words))

