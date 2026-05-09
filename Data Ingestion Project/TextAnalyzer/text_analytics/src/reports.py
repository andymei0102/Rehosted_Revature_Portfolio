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

    statistics = analysis_result.document_stats

    lines = []

    lines.append("=" * 50)
    lines.append("*** Text Analysis Report ***")
    lines.append("=" * 50)

    lines.append("\n--- 1. Document Overview ---")
    lines.append(f"Word Count:          {statistics.word_count}")
    lines.append(f"Unique Words:        {statistics.unique_words}")
    lines.append(f"Sentence Count:      {statistics.sentence_count}")
    lines.append(f"Avg Word Length:     {statistics.avg_word_length}")
    lines.append(f"Avg Sentence Length: {statistics.avg_sentence_length}")

    lines.append("\n--- 2. Top Words ---")
    for word, count in analysis_result.top_words:
        lines.append(f"Word: {word} --> Count: {count}")

    lines.append("\n--- 3. Top Phrases ---")
    lines.append("Bigrams:")
    for tokens in analysis_result.top_bigrams:
        lines.append(f"  {' '.join(tokens)}")
    lines.append("Trigrams:")
    for tokens in analysis_result.top_trigrams:
        lines.append(f"  {' '.join(tokens)}")

    lines.append("\n--- 4. Readability Assessment ---")
    lines.append(f"  {analysis_result.readability_score}")

    lines.append("\n" + "=" * 50)

    report = "\n".join(lines)

    with open(output_path, "w") as f:
        f.write(report)

    return report

    

def generate_word_cloud_data(word_frequencies):
    """
    Prepare data for word cloud visualization.
    Returns: OrderedDict of word -> weight (ordered by frequency)
    """
    total = 0
    for word, count in word_frequencies:
        total += count
    result = OrderedDict()
    for word, count in word_frequencies:
        result[word] = round(count / total, 4)
    return result

def generate_frequency_table(word_frequencies):
    """
    Generate a formatted frequency table.
    Uses OrderedDict to maintain ranking order.
    """
    total = 0
    for word, count in word_frequencies:
        total += count
    table = OrderedDict()
    for rank, (word, count) in enumerate(word_frequencies, start = 1):
        table[word] = {
            "rank": rank,
            "count": count,
            "percentage": round(count / total * 100, 2)
            }
    return table