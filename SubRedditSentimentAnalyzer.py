import os
import json
from transformers import pipeline
import matplotlib.pyplot as plt

# Define directories
input_dir = "data"
output_dir = "results"
os.makedirs(output_dir, exist_ok=True)

# Load processed data
def load_processed_data(filename):
    filepath = os.path.join(input_dir, filename)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)

# Perform sentiment analysis
def perform_sentiment_analysis(data):
    # Load the sentiment analysis model
    sentiment_pipeline = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")

    analyzed_data = []
    for item in data:
        # Analyze the post (title + selftext)
        title = item.get("cleaned_title", "").strip()
        selftext = item.get("cleaned_selftext", "").strip()
        combined_text = f"{title} {selftext}".strip()

        if combined_text:  # Skip empty posts
            try:
                result = sentiment_pipeline(combined_text[:512])  # Limit text length to 512 characters
                item["sentiment"] = result[0]["label"]
            except Exception as e:
                print(f"Error processing post ID {item.get('id', 'unknown')}: {e}")
                item["sentiment"] = "error"

        # Analyze comments
        for comment in item.get("comments", []):
            cleaned_body = comment.get("cleaned_body", "").strip()

            if cleaned_body:  # Skip empty comments
                try:
                    result = sentiment_pipeline(cleaned_body[:512])  # Limit text length to 512 characters
                    comment["sentiment"] = result[0]["label"]
                except Exception as e:
                    print(f"Error processing comment ID {comment.get('id', 'unknown')}: {e}")
                    comment["sentiment"] = "error"

        analyzed_data.append(item)

    return analyzed_data

# Save analyzed data
def save_analyzed_data(data, filename):
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    print(f"Saved sentiment analysis results to {filepath}")

# Map BERT labels to human-readable meanings
BERT_LABELS = {
    "1 star": "Very Negative",
    "2 stars": "Negative",
    "3 stars": "Neutral",
    "4 stars": "Positive",
    "5 stars": "Very Positive"
}

# Sort labels by order of stars
def sort_sentiment_counts(sentiment_counts):
    ordered_labels = ["1 star", "2 stars", "3 stars", "4 stars", "5 stars"]
    sorted_counts = {label: sentiment_counts.get(label, 0) for label in ordered_labels}
    return sorted_counts

# Plot sentiment distribution
def plot_sentiment_distribution_custom(sentiment_counts, successful_texts, version):
    sorted_counts = sort_sentiment_counts(sentiment_counts)
    labels = [BERT_LABELS[label] for label in sorted_counts.keys()]
    counts = list(sorted_counts.values())

    plt.figure(figsize=(45, 20), dpi=300)  # High resolution for A0 poster

    # Customize colors based on version
    if version == "highlight_max":
        max_index = counts.index(max(counts))
        colors = ["FF4500" if i == max_index else "444054" for i in range(len(counts))]
    elif version == "uniform_color":
        colors = ["808F87"] * len(counts)
    else:
        raise ValueError("Invalid version specified. Use 'highlight_max' or 'uniform_color'.")

    plt.bar(labels, counts, color=[f"#{color}" for color in colors])
    plt.ylabel("Number of Texts", fontsize=50, labelpad=20)
    plt.xticks(fontsize=50)
    plt.yticks(fontsize=50)
    plt.subplots_adjust(bottom=0.2)  # Increase bottom margin to avoid overlap

    # Annotate successful analysis count
    plt.figtext(0.99, 0.01, f"Successfully analyzed texts: {successful_texts}",
                horizontalalignment='right', fontsize=16, color='gray')

    # Save plot
    output_path = os.path.join(output_dir, "plots", f"sentiment_distribution_new_{version}.png")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path)
    plt.close()
    print(f"Sentiment distribution plot saved to {output_path}")

# Main function
if __name__ == "__main__":
    # Load subset
    input_filename = "cleaned_politics.json"
    print(f"Loading data from {input_filename}...")
    data = load_processed_data(input_filename)

    print("Performing sentiment analysis...")
    analyzed_data = perform_sentiment_analysis(data)

    print("Saving results...")
    save_analyzed_data(analyzed_data, "sentiment_analysis_results.json")

    print("\nStatistics:")
    sentiment_counts = {}

    # Include both posts and comments in statistics
    for item in analyzed_data:
        # Count sentiment for posts
        sentiment = item.get("sentiment", "unknown")
        sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1

        # Count sentiment for comments
        for comment in item.get("comments", []):
            comment_sentiment = comment.get("sentiment", "unknown")
            sentiment_counts[comment_sentiment] = sentiment_counts.get(comment_sentiment, 0) + 1

    total = sum(sentiment_counts.values())
    errors = sentiment_counts.get("error", 0)
    successful = total - errors

    print(f"  Total texts analyzed (posts + comments): {total}")
    print(f"  Successfully analyzed texts: {successful}")
    print(f"  Errors during analysis: {errors}")

    print("Sentiment distribution:")
    for sentiment, count in sentiment_counts.items():
        if sentiment != "error":  # Exclude "error" from sentiment distribution stats
            print(f"  {sentiment}: {count}")

    # Create plots with customizations
    plot_sentiment_distribution_custom({k: v for k, v in sentiment_counts.items() if k != "error"}, successful, version="highlight_max")
    plot_sentiment_distribution_custom({k: v for k, v in sentiment_counts.items() if k != "error"}, successful, version="uniform_color")
