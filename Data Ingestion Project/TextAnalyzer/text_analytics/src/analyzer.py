from collections import Counter, defaultdict, namedtuple
from models import WordFrequency, NGram, DocumentStats, AnalysisResult
from tokenizer import tokenize, get_sentences, get_ngrams, remove_stopwords
from metrics import calculate_readability

from copy import deepcopy
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
        words = deepcopy(self.words)
        if exclude_stopwords:
            words = remove_stopwords(words)

        cnt = Counter(words)

        return cnt.most_common(top_n)
    
    def get_bigrams(self, top_n=10):
        """
        Get top N bigrams (2-word phrases).
        Returns: List of NGram namedtuples
        """
        ngrams = get_ngrams(self.words, 2)

        return ngrams[:top_n]
    
    def get_trigrams(self, top_n=10):
        """
        Get top N trigrams (3-word phrases).
        Returns: List of NGram namedtuples
        """
        ngrams = get_ngrams(self.words, 3)

        return ngrams[:top_n]
    
    def get_document_stats(self):
        """
        Calculate overall document statistics.
        Returns: DocumentStats namedtuple
        """
        cnt = Counter(self.words)

        word_count = len(self.words)
        unique_words = len(cnt)
        sentence_count = len(self.sentences)
        
        total = 0
        for word in self.words:
            total += len(word)

        average_word_length = round(total / len(self.words),2)

        total = 0
        for sentence in self.sentences:
            total += len(sentence)

        average_sentence_length = round((total / len(self.sentences) ),2)

        return DocumentStats(word_count, unique_words,sentence_count,average_word_length,average_sentence_length)
        
    
    def get_word_length_distribution(self):
        """
        Group words by length.
        Returns: defaultdict mapasspping length -> list of words
        """
        d = {}
        cnt = Counter(self.words)
        
        unique_words = list(cnt.keys())

        for word in unique_words:
            word_length = len(word)

            if d.get(word_length,None) == None:
                d[word_length] = [word]
            else:
                d[word_length].append(word)
        return d
    
    def analyze(self):
        """
        Run complete analysis.
        Returns: AnalysisResult namedtuple
        """
        """
            AnalysisResult = namedtuple('AnalysisResult', [
        'document_stats',
        'top_words',
        'top_bigrams',
        'top_trigrams',
        'readability_score'
    ])
        """
        document_stats = self.get_document_stats()
        top_words = self.get_word_frequencies()
        top_bigrams = self.get_bigrams()
        top_trigrams = self.get_trigrams()
        readability = calculate_readability(self)

        return AnalysisResult(document_stats, top_words, top_bigrams, top_trigrams, readability)



if __name__ == "__main__":
    text = "my my name is joe. I am a yes."
    with open("test_text.txt","r") as f:
        text = f.read()
    t = TextAnalyzer(text)
    print(t.analyze())