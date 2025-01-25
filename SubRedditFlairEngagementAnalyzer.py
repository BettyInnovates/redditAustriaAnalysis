import os
import pickle
import json
import csv
import matplotlib.pyplot as plt
from collections import defaultdict

# Define result and data directories
RESULTS_DIR = "results"
RESULTS_JSON_DIR = os.path.join(RESULTS_DIR, "json")
RESULTS_PLOTS_DIR = os.path.join(RESULTS_DIR, "plots")
DATA_DIR = "data"
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(RESULTS_JSON_DIR, exist_ok=True)
os.makedirs(RESULTS_PLOTS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# Function to load posts from a pickle file or JSON files
def load_posts(data_directory=DATA_DIR, pickle_file="data/posts.pkl"):
    if os.path.exists(pickle_file):
        print(f"Loading posts from pickle file: {pickle_file}")
        with open(pickle_file, "rb") as file:
            return pickle.load(file)
    else:
        print("Pickle file not found. Loading posts from JSON files.")
        posts = []
        for filename in os.listdir(data_directory):
            if filename.startswith("austria_posts_with_comments_") and filename.endswith(".json"):
                filepath = os.path.join(data_directory, filename)
                print(f"Loading file: {filepath}")
                with open(filepath, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    posts.extend(data)
        with open(pickle_file, "wb") as file:
            pickle.dump(posts, file)
        print(f"Posts saved to pickle file: {pickle_file}")
        return posts

# Function to save analysis results to a JSON file
def save_results_to_file(data, filename):
    filepath = os.path.join(RESULTS_JSON_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    print(f"Results saved to {filepath}")

# Function to save results to a CSV file
def save_results_to_csv(data, filename):
    filepath = os.path.join(RESULTS_DIR, filename)
    with open(filepath, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow(["Flair", "Posts", "Upvotes", "Comments"])
        for flair, metrics in data.items():
            writer.writerow([flair, metrics["posts"], metrics["upvotes"], metrics["comments"]])
    print(f"Results saved to {filepath}")

# Function to calculate percentage of posts and comments with any flair
def calculate_flair_coverage(posts):
    total_posts = len(posts)
    total_comments = sum(len(post.get("comments", [])) for post in posts)

    posts_with_flairs = sum(1 for post in posts if post.get("flair", None))
    comments_with_flairs = sum(
        1 for post in posts for comment in post.get("comments", [])
        if post.get("flair", None)
    )

    print(f"Posts with flairs: {posts_with_flairs} of {total_posts} ({(posts_with_flairs / total_posts) * 100:.2f}%)")
    print(f"Comments with flairs: {comments_with_flairs} of {total_comments} ({(comments_with_flairs / total_comments) * 100:.2f}%)")


# General flair analysis function (with optional comments inclusion)
def analyze_flairs(posts, include_comments=True):
    flair_data = defaultdict(lambda: {"posts": 0, "upvotes": 0, "comments": 0})

    for post in posts:
        flair = post.get("flair", "Unknown")
        flair_data[flair]["posts"] += 1
        flair_data[flair]["upvotes"] += post.get("upvotes", 0)
        flair_data[flair]["comments"] += post.get("num_comments", 0)

        if include_comments:
            for comment in post.get("comments", []):
                flair_data[flair]["upvotes"] += comment.get("upvotes", 0)
                flair_data[flair]["comments"] += 1

    return flair_data

# Flair analysis for specific flairs
def analyze_specific_flairs(posts, flairs_of_interest, include_comments=True):
    flair_data = {flair: {"posts": 0, "upvotes": 0, "comments": 0} for flair in flairs_of_interest}
    others = {"posts": 0, "upvotes": 0, "comments": 0}

    for post in posts:
        flair = post.get("flair", "Unknown")
        if flair in flairs_of_interest:
            flair_data[flair]["posts"] += 1
            flair_data[flair]["upvotes"] += post.get("upvotes", 0)
            flair_data[flair]["comments"] += post.get("num_comments", 0)

            if include_comments:
                for comment in post.get("comments", []):
                    flair_data[flair]["upvotes"] += comment.get("upvotes", 0)
                    flair_data[flair]["comments"] += 1
        else:
            others["posts"] += 1
            others["upvotes"] += post.get("upvotes", 0)
            others["comments"] += post.get("num_comments", 0)

            if include_comments:
                for comment in post.get("comments", []):
                    others["upvotes"] += comment.get("upvotes", 0)
                    others["comments"] += 1

    flair_data["Others"] = others
    return flair_data

# Function to visualize flair data
def visualize_flair_data(flair_data, title, suffix):
    if not flair_data:
        print("No flair data to visualize.")
        return

    flairs = list(flair_data.keys())
    upvotes = [data["upvotes"] for data in flair_data.values()]
    comments = [data["comments"] for data in flair_data.values()]
    posts = [data["posts"] for data in flair_data.values()]

    x = range(len(flairs))

    # Plot Upvotes
    plt.figure(figsize=(10, 6))
    plt.bar(x, upvotes, tick_label=flairs)
    plt.xticks(rotation=90)
    plt.title(f"Upvotes by Flair ({title})")
    plt.ylabel("Upvotes")
    plt.xlabel("Flair")
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_PLOTS_DIR, f"{suffix}_upvotes.png"))
    plt.close()

    # Plot Comments
    plt.figure(figsize=(10, 6))
    plt.bar(x, comments, tick_label=flairs)
    plt.xticks(rotation=90)
    plt.title(f"Comments by Flair ({title})")
    plt.ylabel("Comments")
    plt.xlabel("Flair")
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_PLOTS_DIR, f"{suffix}_comments.png"))
    plt.close()

    # Plot Posts
    plt.figure(figsize=(10, 6))
    plt.bar(x, posts, tick_label=flairs)
    plt.xticks(rotation=90)
    plt.title(f"Posts by Flair ({title})")
    plt.ylabel("Number of Posts")
    plt.xlabel("Flair")
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_PLOTS_DIR, f"{suffix}_posts.png"))
    plt.close()

# Function to visualize flair data as a pie chart
def visualize_flairs_as_pie(flair_data, flairs_of_interest, flair_colors, title, metric, output_filename):
    # Prepare data for the pie chart
    labels = [flair for flair in flairs_of_interest if flair in flair_data]
    values = [flair_data[flair][metric] for flair in labels]
    colors = [flair_colors.get(flair, "#AFD0BF") for flair in labels]  # Default color for unspecified flairs

    # Create pie chart
    plt.figure(figsize=(10, 10))
    plt.pie(
        values,
        labels=labels,
        autopct="%1.1f%%",
        startangle=140,
        colors=colors,
        textprops={'fontsize': 12, 'fontweight': 'bold'}
    )

    # Add title and save
    plt.title(f"{title}: {metric.capitalize()}", fontsize=14, pad=20, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_PLOTS_DIR, output_filename), dpi=300)
    plt.close()
    print(f"Saved pie chart as {output_filename}.")

# Function to visualize flair data as a stacked bar chart with legend
def visualize_flairs_as_stacked_bar_with_legend(flair_data, metric, flair_colors, output_filename):
    # Extract labels and values
    labels = list(flair_data.keys())
    values = [data[metric] for data in flair_data.values()]

    # Calculate total for normalization
    total = sum(values)
    normalized_values = [v / total for v in values]

    # Set up plot size
    fig, ax = plt.subplots(figsize=(45, 5))  # Wide and short plot for poster

    # Draw the stacked bar
    left_offset = 0
    for i, value in enumerate(normalized_values):
        ax.barh(0, value, left=left_offset, color=flair_colors.get(labels[i], "#AFD0BF"), edgecolor="black")
        # Add percentage label inside the bar
        ax.text(
            left_offset + value / 2, 0, f"{value * 100:.1f}%", ha='center', va='center',
            fontsize=48, color="white" if value > 0.05 else "black", weight='bold'
        )
        left_offset += value

    # Remove axes
    ax.axis('off')

    # Add legend
    ax.legend(labels, loc='upper center', bbox_to_anchor=(0.5, -0.3), fontsize=48, ncol=len(labels), frameon=False)

    # Transparent background
    fig.patch.set_alpha(0.0)
    ax.set_facecolor('none')

    # Save the chart
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_PLOTS_DIR, output_filename), dpi=300, transparent=True)
    plt.close()
    print(f"Saved stacked bar chart with legend as {output_filename}.")

if __name__ == "__main__":

    # Load posts
    posts = load_posts(DATA_DIR)

    # Calculate coverage of posts and comments with any flair
    calculate_flair_coverage(posts)

    # Analyze all flairs (with comments)
    print(f"\nAnalyzing all flairs (including comments)")
    all_flairs_with_comments = analyze_flairs(posts, include_comments=True)
    save_results_to_file(all_flairs_with_comments, "all_flairs_with_comments.json")
    save_results_to_csv(all_flairs_with_comments, "all_flairs_with_comments.csv")
    visualize_flair_data(all_flairs_with_comments, "All Flairs (Including Comments)", "all_flairs_with_comments")

    # Analyze all flairs (without comments)
    print(f"Analyzing all flairs (only posts, without comments)")
    all_flairs_without_comments = analyze_flairs(posts, include_comments=False)
    save_results_to_file(all_flairs_without_comments, "all_flairs_without_comments.json")
    save_results_to_csv(all_flairs_without_comments, "all_flairs_without_comments.csv")
    visualize_flair_data(all_flairs_without_comments, "All Flairs (Excluding Comments)", "all_flairs_without_comments")
    print("Visualization \"Engagement all Flairs\" complete. All plots saved in the 'results/plots' directory.")


    # Define flairs of interest
    # --------------------------
    # The selected flairs of interest were chosen based on the r/Austria subreddit.
    # Feel free to modify the 'flairs_of_interest' list to match your subreddit.
    # Define the flairs of interest and their colors
    flairs_of_interest = ["Memes & Humor", "Politik | Politics", "Frage | Question", "Nachrichten | News"]
    flair_colors = {
        "Memes & Humor": "#444054",
        "Politik | Politics": "#FF4500",
        "Frage | Question": "#FFD700",
        "Nachrichten | News": "#808F87"
    }


    # Print note for flairs_of_interest
    print(f"\nAnalyzing focused on flairs of interest ...")
    print("Note: The selected flairs of interest were chosen based on the r/Austria subreddit.")
    print(f"Flairs of Interest: {flairs_of_interest}")
    print("Feel free to modify the 'flairs_of_interest' list to match your subreddit.")

    print("Feel free to modify the 'flairs_of_interest' list to match your subreddit.")

    # Analyze specific flairs (with comments)
    specific_flair_data_with_comments = analyze_specific_flairs(posts, flairs_of_interest, include_comments=True)
    save_results_to_file(specific_flair_data_with_comments, "specific_flair_analysis_with_comments.json")
    save_results_to_csv(specific_flair_data_with_comments, "specific_flair_analysis_with_comments.csv")
    specific_flair_data_with_comments = analyze_specific_flairs(posts, flairs_of_interest, include_comments=True)
    save_results_to_file(specific_flair_data_with_comments, "specific_flair_analysis_with_comments.json")
    save_results_to_csv(specific_flair_data_with_comments, "specific_flair_analysis_with_comments.csv")
    visualize_flairs_as_pie(
        specific_flair_data_with_comments,
        flairs_of_interest,
        flair_colors,
        "Specific Flairs (Including Comments)",
        "posts",
        "specific_flairs_with_comments_pie_plots.png"
    )
    visualize_flairs_as_pie(
        specific_flair_data_with_comments,
        flairs_of_interest,
        flair_colors,
        "Specific Flairs (Including Comments)",
        "comments",
        "specific_flairs_with_comments_pie_comments.png"
    )
    visualize_flairs_as_pie(
        specific_flair_data_with_comments,
        flairs_of_interest,
        flair_colors,
        "Specific Flairs (Including Comments)",
        "upvotes",
        "specific_flairs_with_comments_pie_upvotes.png"
    )
    # Plots for Poster
    visualize_flairs_as_stacked_bar_with_legend(
        specific_flair_data_with_comments,
        "posts",
        flair_colors,
        "specific_flairs_with_comments_stacked_bar_plots.png"
    )
    visualize_flairs_as_stacked_bar_with_legend(
        specific_flair_data_with_comments,
        "comments",
        flair_colors,
        "specific_flairs_with_comments_stacked_bar_comments.png"
    )



    # Analyze specific flairs (without comments)
    specific_flair_data_without_comments = analyze_specific_flairs(posts, flairs_of_interest, include_comments=False)
    save_results_to_file(specific_flair_data_without_comments, "specific_flair_analysis_without_comments.json")
    save_results_to_csv(specific_flair_data_without_comments, "specific_flair_analysis_without_comments.csv")
    visualize_flairs_as_pie(
        specific_flair_data_without_comments,
        flairs_of_interest,
        flair_colors,
        "Specific Flairs (Only Posts)",
        "posts",
        "specific_flairs_only_posts_pie_posts.png"
    )
    visualize_flairs_as_pie(
        specific_flair_data_without_comments,
        flairs_of_interest,
        flair_colors,
        "Specific Flairs (Only Posts)",
        "comments",
        "specific_flairs_only_posts_pie_comments.png"
    )
    visualize_flairs_as_pie(
        specific_flair_data_without_comments,
        flairs_of_interest,
        flair_colors,
        "Specific Flairs (Only Posts)",
        "upvotes",
        "specific_flairs_only_posts_pie_upvotes.png"
    )
    print("Analysis and visualization complete.")


