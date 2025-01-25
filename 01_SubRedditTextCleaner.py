import os
import json
import re
from collections import defaultdict
from spacy.lang.de.stop_words import STOP_WORDS as GERMAN_STOPWORDS
from spacy.lang.en.stop_words import STOP_WORDS as ENGLISH_STOPWORDS

# Function to load data
def load_data(directory):
    all_posts = []
    for filename in os.listdir(directory):
        if filename.startswith("austria_posts_with_comments_") and filename.endswith(".json"):
            with open(os.path.join(directory, filename), "r", encoding="utf-8") as file:
                data = json.load(file)
                all_posts.extend(data)
    return all_posts

# Load stopwords for German and English with custom additions
def get_multilingual_stopwords():
    # Add any custom stopwords here
    custom_stopwords = {
        "halt", "mal", "einfach", "genau", "nix", "ned", "mehr", "schon", "immer", "gut", "geht", "wäre", "hab", "die", "paar", "eher",  # German filler words
        "dont", "cant", "im", "youre", "the", "and", "you", "that", "for", "are", "not", "but", "this", "have", "like", "one", "would"  # Common English words
    }
    return GERMAN_STOPWORDS.union(ENGLISH_STOPWORDS).union(custom_stopwords)


# Function to preprocess text
def preprocess_text(text, custom_stopwords=None):

    if custom_stopwords is None:
        custom_stopwords = set()

    # Combine custom stopwords with German and English stopwords
    stopwords = GERMAN_STOPWORDS.union(ENGLISH_STOPWORDS).union(custom_stopwords)

    # Remove URLs and non-alphabetic characters
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^a-zA-ZäöüÄÖÜß\s]', '', text)

    # Convert text to lowercase
    text = text.lower()

    # Tokenize and remove stopwords
    tokens = [word for word in text.split() if word not in stopwords and len(word) > 2]
    return " ".join(tokens)

# Clean and filter data
def clean_and_filter_data(posts, remove_stopwords=False, custom_stopwords=None, show_statistics=True):

    cleaned_posts = []
    empty_posts_count = 0
    empty_comments_count = 0

    for post in posts:
        # Check if the post is empty
        if not post.get("title", "").strip() and not post.get("selftext", "").strip():
            empty_posts_count += 1
            continue  # Skip empty posts

        # Clean comments
        comments = []
        for comment in post.get("comments", []):
            cleaned_body = preprocess_text(comment.get("body", ""), custom_stopwords) if remove_stopwords else preprocess_text(comment.get("body", ""))
            if not cleaned_body.strip():
                empty_comments_count += 1
                continue  # Skip empty comments
            comments.append({**comment, "cleaned_body": cleaned_body})

        # Clean post title and selftext
        cleaned_title = preprocess_text(post.get("title", ""), custom_stopwords) if remove_stopwords else preprocess_text(post.get("title", ""))
        cleaned_selftext = preprocess_text(post.get("selftext", ""), custom_stopwords) if remove_stopwords else preprocess_text(post.get("selftext", ""))

        cleaned_posts.append({
            **post,
            "cleaned_title": cleaned_title,
            "cleaned_selftext": cleaned_selftext,
            "comments": comments
        })

    # Display statistics only if show_statistics is True
    if show_statistics:
        print(f"Empty posts removed: {empty_posts_count}")
        print(f"Empty comments removed: {empty_comments_count}")

    return cleaned_posts

# Save cleaned data
def save_cleaned_data(posts, filename):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(posts, file, ensure_ascii=False, indent=4)

# Analyze and print statistics
def analyze_data(posts):
    total_posts = len(posts)
    total_comments = sum(len(post.get("comments", [])) for post in posts)

    flairs = defaultdict(int)
    for post in posts:
        if post.get("flair"):
            flairs[post["flair"]] += 1

    print(f"Total posts: {total_posts}")
    print(f"Total comments: {total_comments}")
    print(f"Flairs found: {len(flairs)}")
    print("Top flairs:")
    for flair, count in sorted(flairs.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {flair}: {count} posts")

# Main function
if __name__ == "__main__":
    # Directory containing the JSON files
    data_directory = "data"

    # Generate multilingual stopwords
    stopwords = get_multilingual_stopwords()
    print(stopwords)

    # Output filenames
    cleaned_all_filename = os.path.join(data_directory, "cleaned_all.json")
    cleaned_all_no_stopwords_filename = os.path.join(data_directory, "cleaned_all_no_stopwords.json")

    input_flair_name = "Politik | Politics"
    output_flair_name = "politics"

    # Load data
    print("Loading data...")
    posts = load_data(data_directory)

    # Clean and save all posts
    print("\nCleaning all posts (including comments)...")
    cleaned_all_posts = clean_and_filter_data(posts, remove_stopwords=False, custom_stopwords=stopwords, show_statistics=True)
    save_cleaned_data(cleaned_all_posts, cleaned_all_filename)
    print(f"Cleaned all posts saved to {cleaned_all_filename}.")

    cleaned_all_no_stopwords_posts = clean_and_filter_data(posts, remove_stopwords=True, custom_stopwords=stopwords, show_statistics=False)
    save_cleaned_data(cleaned_all_no_stopwords_posts, cleaned_all_no_stopwords_filename)
    print(f"Cleaned all posts without stopwords saved to {cleaned_all_no_stopwords_filename}.")

    # Filter posts with specific flair
    flair_posts = [post for post in cleaned_all_posts if post.get("flair") == input_flair_name]
    flair_no_stopwords_posts = [post for post in cleaned_all_no_stopwords_posts if post.get("flair") == input_flair_name]

    # Save filtered flair-specific posts
    save_cleaned_data(flair_posts, os.path.join(data_directory, f"cleaned_{output_flair_name}.json"))
    save_cleaned_data(flair_no_stopwords_posts, os.path.join(data_directory, f"cleaned_{output_flair_name}_no_stopwords.json"))

    # Analyze all posts and specific flair
    print("\nStatistics for all posts:")
    analyze_data(cleaned_all_posts)

    print(f"\nStatistics for flair '{input_flair_name}':")
    analyze_data(flair_posts)
