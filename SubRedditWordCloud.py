import os
import json
import csv
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import random
from collections import Counter

# Function to load cleaned posts
def load_cleaned_posts(filename):
    """Loads cleaned posts from a specified JSON file."""
    data_directory = "data"
    filepath = os.path.join(data_directory, filename)
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        print("Please run 'SubRedditTextCleaner.py' to generate the cleaned data.")
        return []

    with open(filepath, "r", encoding="utf-8") as file:
        data = json.load(file)
        print(f"Loaded {len(data)} posts from {filename}.")
        return data

# Generate word cloud
def generate_wordcloud_transparent(texts, output_filename, mask_path=None, palette=None):
    """Generates a word cloud from the provided texts."""
    combined_text = " ".join(texts)
    print(f"Combined text length: {len(combined_text)} characters.")

    # Load the mask image if provided
    mask = None
    if mask_path and os.path.exists(mask_path):
        print(f"Using mask: {mask_path}")
        mask = np.array(Image.open(mask_path))
    else:
        print("No valid mask provided. Using a square shape for the word cloud.")

    # Ensure palette is non-empty
    if not palette:
        palette = ["#FF4500", "#444054", "#808F87", "#AFD0BF"]  # Default palette

    # Custom color function
    def custom_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
        return random.choice(palette)

    # Generate the word cloud
    print("Generating the word cloud...")
    wordcloud = WordCloud(
        width=7000,  # Large size for A0 poster
        height=3823,
        background_color=None,
        mode="RGBA",
        max_words=200,
        mask=mask,
        contour_width=0,
        color_func=custom_color_func,
        scale=3
    ).generate(combined_text)

    # Save the word cloud
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    plt.figure(figsize=(20, 10))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.savefig(output_filename, dpi=300, transparent=True)
    plt.close()
    print(f"Word cloud saved as {output_filename}.")

# Count word frequencies
def count_word_frequencies(texts):
    words = " ".join(texts).split()
    return Counter(words)

# Save word frequencies as CSV
def save_word_frequencies_to_csv(word_frequencies, output_filename):
    with open(output_filename, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Word", "Frequency"])
        writer.writerows(word_frequencies.most_common())

# Plot horizontal bar chart for word frequencies
def plot_word_frequencies(word_frequencies, output_filename, top_n=20):
    # Get top N words
    most_common = word_frequencies.most_common(top_n)
    words, frequencies = zip(*most_common)

    # Plot settings
    plt.figure(figsize=(11.69, 8.27))  # A4 landscape size in inches
    plt.barh(words, frequencies, color="#808F87")
    plt.xlabel("Frequency")
    plt.ylabel("Words")
    plt.title("Top Words by Frequency")
    plt.gca().invert_yaxis()  # Highest frequencies on top
    plt.tight_layout()

    # Save the plot
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    plt.savefig(output_filename, dpi=300)
    plt.close()

# Main function
if __name__ == "__main__":
    # Define the input file (politics with stopwords removed)
    input_filename = "cleaned_politics_no_stopwords.json"  # Adjust as needed
    mask_filename = "WordCloudMask.png"  # Name of the mask file
    output_dir = os.path.join("results", "plots")
    mask_path = os.path.join(os.getcwd(), mask_filename)  # Full path to the mask
    output_filename_transparent = os.path.join(output_dir, "wordcloud_AT_politics.png")
    output_csv = os.path.join("results", "word_frequencies.csv")
    output_plot = os.path.join(output_dir, "word_frequencies_bar_chart.png")

    # Load the dataset
    print(f"Loading cleaned posts from {input_filename}...")
    posts = load_cleaned_posts(input_filename)

    if not posts:
        print("No posts loaded. Exiting.")
        exit()

    # Combine texts from titles, selftexts, and comments
    print("Combining texts from titles, selftexts, and comments...")
    texts = []
    for post in posts:
        # Combine title and selftext
        if post.get("title"):
            texts.append(post["title"])
        if post.get("selftext"):
            texts.append(post["selftext"])
        # Combine comments
        if post.get("comments"):
            for comment in post["comments"]:
                if "cleaned_body" in comment:
                    texts.append(comment["cleaned_body"])

    print(f"Total combined texts: {len(texts)}")

    # Generate the word cloud
    print("Generating word cloud...")
    #generate_wordcloud_transparent(texts, output_filename_transparent, mask_path)

    print(f"Word cloud saved as {output_filename_transparent}.")

    # Count word frequencies
    print("Counting word frequencies...")
    word_frequencies = count_word_frequencies(texts)

    # Save word frequencies as CSV
    print(f"Saving word frequencies to {output_csv}...")
    save_word_frequencies_to_csv(word_frequencies, output_csv)

    # Plot word frequencies
    print(f"Plotting word frequencies to {output_plot}...")
    plot_word_frequencies(word_frequencies, output_plot)

    print("Word frequency analysis complete.")
