# import TextAnalyzer

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
    score = 206.835 - 1.015 * (word_count / sentence_count) - 84.6 * (syllable_count / word_count)
    
    if score >= 90:
        return f"{score}: Very easy (5th grade)"
    elif score >= 60:
        return f"{score}: Standard (8th-9th grade)"
    elif score >= 30:
        return f"{score}: Difficult (college)"
    else:
        return "Very difficult (college graduate)"


def count_syllables(word):
    """
    Count syllables in a word.
    Simple heuristic: count vowel groups.
    """
    vowels = {'a', 'e', 'i', 'o', 'u'}
    count = 0
    for character in word:
        if character in vowels:
            count += 1
    if word[:-1] == 'e':
        count -= 1
    return count


def calculate_readability(analyzer):
    """
    Calculate readability metrics for an analyzed document.
    Returns: Dict with various readability scores
    """
    num_syllables = 0
    for word in analyzer.words:
        num_syllables += count_syllables(word)
    return flesch_reading_ease(len(analyzer.words), len(analyzer.sentences), num_syllables)


# if __name__ == "__main__":
#     print(flesch_reading_ease(100, 20, 34))
#     text = ""
#     with open("test_text.txt","r") as f:
#        text = f.read()
#     t = TextAnalyzer(text)
#     print(calculate_readability(t))