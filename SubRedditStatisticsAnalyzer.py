import os
import json
import csv
from collections import defaultdict
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import pearsonr
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error


# Function to load from JSON files
def load_subreddit_data(directory):
    posts = []
    for filename in os.listdir(directory):
        if filename.startswith("austria_posts_with_comments_") and filename.endswith(".json"):
            filepath = os.path.join(directory, filename)
            print(f"Loading file: {filepath}")
            with open(filepath, "r", encoding="utf-8") as file:
                data = json.load(file)
                posts.extend(data)
    return posts


# Function to calculate general statistics
def calculate_general_totals(posts):
    total_posts = len(posts)
    total_comments = sum(len(post.get("comments", [])) for post in posts)
    total_upvotes = sum(post.get("upvotes", 0) for post in posts)
    return total_posts, total_comments, total_upvotes




# Function to calculate daily statistics
def calculate_daily_statistics(posts):
    daily_post_counts = defaultdict(int)
    daily_comment_counts = defaultdict(int)
    daily_post_upvote_counts = defaultdict(int)  # Upvotes for posts only
    daily_total_upvote_counts = defaultdict(int)  # Upvotes including comments

    for post in posts:
        date = datetime.utcfromtimestamp(post.get("created_utc", 0)).date()
        daily_post_counts[date] += 1
        daily_comment_counts[date] += len(post.get("comments", []))
        daily_post_upvote_counts[date] += post.get("upvotes", 0)

        # Add upvotes from comments
        for comment in post.get("comments", []):
            daily_total_upvote_counts[date] += comment.get("upvotes", 0)

        # Include post upvotes in the total upvotes count
        daily_total_upvote_counts[date] += post.get("upvotes", 0)

    daily_posts = list(daily_post_counts.values())
    daily_comments = list(daily_comment_counts.values())
    daily_post_upvotes = list(daily_post_upvote_counts.values())
    daily_total_upvotes = list(daily_total_upvote_counts.values())

    avg_posts_per_day = np.mean(daily_posts) if daily_posts else 0
    avg_comments_per_day = np.mean(daily_comments) if daily_comments else 0
    avg_post_upvotes_per_day = np.mean(daily_post_upvotes) if daily_post_upvotes else 0
    avg_total_upvotes_per_day = np.mean(daily_total_upvotes) if daily_total_upvotes else 0

    std_posts_per_day = np.std(daily_posts) if daily_posts else 0
    std_comments_per_day = np.std(daily_comments) if daily_comments else 0
    std_post_upvotes_per_day = np.std(daily_post_upvotes) if daily_post_upvotes else 0
    std_total_upvotes_per_day = np.std(daily_total_upvotes) if daily_total_upvotes else 0

    max_posts_day = max(daily_post_counts, key=daily_post_counts.get, default=None)
    min_posts_day = min(daily_post_counts, key=daily_post_counts.get, default=None)
    max_comments_day = max(daily_comment_counts, key=daily_comment_counts.get, default=None)
    min_comments_day = min(daily_comment_counts, key=daily_comment_counts.get, default=None)
    max_post_upvotes_day = max(daily_post_upvote_counts, key=daily_post_upvote_counts.get, default=None)
    min_post_upvotes_day = min(daily_post_upvote_counts, key=daily_post_upvote_counts.get, default=None)
    max_total_upvotes_day = max(daily_total_upvote_counts, key=daily_total_upvote_counts.get, default=None)
    min_total_upvotes_day = min(daily_total_upvote_counts, key=daily_total_upvote_counts.get, default=None)

    return {
        "daily_post_counts": daily_post_counts,
        "daily_comment_counts": daily_comment_counts,
        "daily_post_upvote_counts": daily_post_upvote_counts,
        "daily_total_upvote_counts": daily_total_upvote_counts,
        "average_posts_per_day": avg_posts_per_day,
        "average_comments_per_day": avg_comments_per_day,
        "average_post_upvotes_per_day": avg_post_upvotes_per_day,
        "average_total_upvotes_per_day": avg_total_upvotes_per_day,
        "std_posts_per_day": std_posts_per_day,
        "std_comments_per_day": std_comments_per_day,
        "std_post_upvotes_per_day": std_post_upvotes_per_day,
        "std_total_upvotes_per_day": std_total_upvotes_per_day,
        "max_posts_day": str(max_posts_day),
        "min_posts_day": str(min_posts_day),
        "max_comments_day": str(max_comments_day),
        "min_comments_day": str(min_comments_day),
        "max_post_upvotes_day": str(max_post_upvotes_day),
        "min_post_upvotes_day": str(min_post_upvotes_day),
        "max_total_upvotes_day": str(max_total_upvotes_day),
        "min_total_upvotes_day": str(min_total_upvotes_day),
    }

# Function to get the time range of posts and comments
def get_time_range(posts):
    earliest_timestamp = float("inf")
    latest_timestamp = float("-inf")

    for post in posts:
        # Check post timestamp
        created_utc = post.get("created_utc", 0)
        earliest_timestamp = min(earliest_timestamp, created_utc)
        latest_timestamp = max(latest_timestamp, created_utc)

        # Check comments timestamps
        for comment in post.get("comments", []):
            comment_created_utc = comment.get("created_utc", 0)
            earliest_timestamp = min(earliest_timestamp, comment_created_utc)
            latest_timestamp = max(latest_timestamp, comment_created_utc)

    # Convert timestamps to datetime
    earliest_date = datetime.utcfromtimestamp(earliest_timestamp).strftime('%Y-%m-%d %H:%M:%S')
    latest_date = datetime.utcfromtimestamp(latest_timestamp).strftime('%Y-%m-%d %H:%M:%S')

    return {
        "earliest_date": earliest_date,
        "latest_date": latest_date
    }

# Function to calculate comment and upvote statistics with ratios
def calculate_comment_upvote_statistics(posts):

    relation = []
    upvote_counts = []
    comment_counts = []
    ratios = []

    for post in posts:
        upvotes = post.get("upvotes", 0)
        num_comments = len(post.get("comments", []))
        ratio = num_comments / upvotes if upvotes > 0 else None  # Avoid division by zero

        # Append to the lists for statistics
        upvote_counts.append(upvotes)
        comment_counts.append(num_comments)
        if ratio is not None:
            ratios.append(ratio)

        # Add individual post statistics
        relation.append({
            "upvotes": upvotes,
            "num_comments": num_comments,
            "comments_per_upvote": ratio
        })

    # Calculate mean and standard deviation
    mean_upvotes = np.mean(upvote_counts) if upvote_counts else 0
    std_upvotes = np.std(upvote_counts) if upvote_counts else 0
    mean_comments = np.mean(comment_counts) if comment_counts else 0
    std_comments = np.std(comment_counts) if comment_counts else 0
    mean_ratio = np.mean(ratios) if ratios else None
    std_ratio = np.std(ratios) if ratios else None

    return {
        "per_post_statistics": relation,
        "mean_upvotes": mean_upvotes,
        "std_upvotes": std_upvotes,
        "mean_comments": mean_comments,
        "std_comments": std_comments,
        "mean_comments_per_upvote": mean_ratio,
        "std_comments_per_upvote": std_ratio
    }

# ********************************************************************************
# CORRELATION
# ********************************************************************************
def calculate_correlation(x, y):
    if not x or not y or len(x) != len(y):
        return {"correlation": None, "p_value": None}

    correlation, p_value = pearsonr(x, y)
    return {"correlation": correlation, "p_value": p_value}

def calculate_daily_posts_comments_correlation(daily_post_counts, daily_comment_counts):
    x = list(daily_post_counts.values())
    y = list(daily_comment_counts.values())
    return calculate_correlation(x, y)

def calculate_post_upvotes_comments_correlation(posts):
    upvotes = [post.get("upvotes", 0) for post in posts]
    num_comments = [len(post.get("comments", [])) for post in posts]
    return calculate_correlation(upvotes, num_comments)

# ********************************************************************************
# LINEAR REGRESSION
# ********************************************************************************
def perform_linear_regression(x, y):
    if not x or not y or len(x) != len(y):
        return {"slope": None, "intercept": None, "mae": None, "r_squared": None}

    # Reshape for sklearn
    x = np.array(x).reshape(-1, 1)
    y = np.array(y)

    # Perform linear regression
    model = LinearRegression()
    model.fit(x, y)

    # Predictions and metrics
    predictions = model.predict(x)
    mae = mean_absolute_error(y, predictions)
    r_squared = model.score(x, y)

    return {
        "slope": model.coef_[0],
        "intercept": model.intercept_,
        "mae": mae,
        "r_squared": r_squared
    }

def perform_daily_posts_comments_regression(daily_post_counts, daily_comment_counts):
    x = list(daily_post_counts.values())
    y = list(daily_comment_counts.values())
    return perform_linear_regression(x, y)

def perform_post_upvotes_comments_regression(posts):
    upvotes = [post.get("upvotes", 0) for post in posts]
    num_comments = [len(post.get("comments", [])) for post in posts]
    return perform_linear_regression(upvotes, num_comments)

# ********************************************************************************
# SAVING RESULTS
# ********************************************************************************
# Function to save results to a CSV file
def save_to_csv(data, filename, directory="results"):
    # Ensure directory exists
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, filename)

    # Write data to CSV
    if data:
        keys = data[0].keys()  # Use keys of the first dict as headers
        with open(filepath, "w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=keys, delimiter=";")  # Use ";" as delimiter
            writer.writeheader()
            writer.writerows(data)
        print(f"Data saved to {filepath}")
    else:
        print(f"No data to save for {filename}")

# ********************************************************************************
# VISUALIZATION
# ********************************************************************************
def visualize_daily_stats(daily_post_counts, daily_comment_counts):
    # Sort the data by date
    dates = sorted(daily_post_counts.keys())
    post_counts = [daily_post_counts[date] for date in dates]
    comment_counts = [daily_comment_counts[date] for date in dates]

    # Create the overlay bar chart
    fig, ax1 = plt.subplots(figsize=(45, 20))

    # Posts as bars
    ax1.bar(dates, post_counts, label="Posts", color="#808F87", alpha=1.0)
    ax1.set_ylabel("Posts", color="#808F87", fontsize=80, labelpad=70)  # More space for axis label
    ax1.tick_params(axis="y", labelcolor="#808F87", labelsize=60, length=15, width=3)  # Larger ticks on the y-axis
    ax1.axhline(0, color='black', linewidth=1.5)  # Clear horizontal line on the y-axis

    # Comments as bars (on the second y-axis)
    ax2 = ax1.twinx()
    ax2.bar(dates, comment_counts, label="Comments", color="#444054", alpha=1.0, width=0.4, align="edge")
    ax2.set_ylabel("Comments", color="#444054", fontsize=80, labelpad=70)  # More space for axis label
    ax2.tick_params(axis="y", labelcolor="#444054", labelsize=60, length=15, width=3)  # Larger ticks on the y-axis
    ax2.axhline(0, color='black', linewidth=1.5)  # Clear horizontal line on the y-axis

    # Adjust the x-axis (display only 3 ticks: start, middle, and end)
    ax1.set_xticks([dates[0], dates[len(dates)//2], dates[-1]])
    ax1.set_xticklabels([dates[0], dates[len(dates)//2], dates[-1]], fontsize=60)
    ax1.tick_params(axis="x", pad=30, length=15, width=3)  # Larger ticks on the x-axis
    ax1.axhline(0, xmin=0, xmax=1, color='black', linewidth=1.5)  # Clear horizontal line on the x-axis

    # Title and layout
    fig.tight_layout()

    # Output directory for the chart within the results folder
    output_dir = os.path.join("results", "daily_overlay_charts")
    os.makedirs(output_dir, exist_ok=True)

    # Save the chart with high resolution
    output_filename = os.path.join(output_dir, "daily_posts_comments_overlay.png")
    plt.savefig(output_filename, dpi=300)
    plt.close()
    print(f"Saved overlay bar chart as {output_filename}.")


def visualize_correlation_with_regression(x, y, x_label, y_label, title, correlation, p_value, output_filename):
    # Ensure the output directory exists
    output_dir = os.path.dirname(output_filename)
    os.makedirs(output_dir, exist_ok=True)

    # Convert to numpy arrays for processing
    x = np.array(x)
    y = np.array(y)

    # Perform linear regression
    slope, intercept = np.polyfit(x, y, 1)
    regression_line = slope * x + intercept

    # Create scatter plot with regression line
    plt.figure(figsize=(10, 6))
    plt.scatter(x, y, label="Data Points", color="blue", alpha=0.6)
    plt.plot(x, regression_line, color="red", label=f"y = {slope:.2f}x + {intercept:.2f}")

    # Add labels, title, and legend
    plt.xlabel(x_label, fontsize=14)
    plt.ylabel(y_label, fontsize=14)
    plt.title(title, fontsize=16)
    plt.title(f"{title}\nR = {correlation:.2f}, p = {p_value:.5f}", fontsize=16)
    plt.legend()

    # Save the plot
    plt.tight_layout()
    plt.savefig(output_filename, dpi=300)
    plt.close()
    print(f"Saved correlation plot as {output_filename}.")

# ********************************************************************************
# Main workflow
# ********************************************************************************
if __name__ == "__main__":
    # Load posts
    posts = load_subreddit_data("data")

    # Calculate daily statistics
    daily_stats = calculate_daily_statistics(posts)

    # Save daily statistics to CSV
    daily_stats_csv = [
        {"date": str(date), "posts": daily_stats["daily_post_counts"][date],
         "comments": daily_stats["daily_comment_counts"][date],
         "post_upvotes": daily_stats["daily_post_upvote_counts"][date],
         "total_upvotes": daily_stats["daily_total_upvote_counts"][date]}
        for date in daily_stats["daily_post_counts"]
    ]
    save_to_csv(daily_stats_csv, "daily_statistics.csv")

    # Calculate correlations
    daily_correlation = calculate_daily_posts_comments_correlation(
        daily_stats["daily_post_counts"], daily_stats["daily_comment_counts"]
    )
    post_correlation = calculate_post_upvotes_comments_correlation(posts)

    # Save correlation results
    correlations_csv = [
        {"type": "Daily Posts vs Comments", "correlation": daily_correlation["correlation"],
         "p_value": daily_correlation["p_value"]},
        {"type": "Post Upvotes vs Comments", "correlation": post_correlation["correlation"],
         "p_value": post_correlation["p_value"]}
    ]
    save_to_csv(correlations_csv, "correlations.csv")

    # Perform regressions
    daily_regression = perform_daily_posts_comments_regression(
        daily_stats["daily_post_counts"], daily_stats["daily_comment_counts"]
    )
    post_regression = perform_post_upvotes_comments_regression(posts)

    # Save regression results
    regressions_csv = [
        {"type": "Daily Posts vs Comments", "slope": daily_regression["slope"],
         "intercept": daily_regression["intercept"], "mae": daily_regression["mae"],
         "r_squared": daily_regression["r_squared"]},
        {"type": "Post Upvotes vs Comments", "slope": post_regression["slope"],
         "intercept": post_regression["intercept"], "mae": post_regression["mae"],
         "r_squared": post_regression["r_squared"]}
    ]
    save_to_csv(regressions_csv, "regressions.csv")

    daily_post_counts = {"2023-01-01": 10, "2023-01-02": 15, "2023-01-03": 20}
    daily_comment_counts = {"2023-01-01": 50, "2023-01-02": 75, "2023-01-03": 100}

    # Visualize daily statistics
    visualize_daily_stats(daily_stats["daily_post_counts"], daily_stats["daily_comment_counts"])

    # Visualize correlation between daily posts and comments
    visualize_correlation_with_regression(
        list(daily_stats["daily_post_counts"].values()),
        list(daily_stats["daily_comment_counts"].values()),
        x_label="Daily Posts",
        y_label="Daily Comments",
        title="Correlation: Daily Posts vs Comments",
        correlation=daily_correlation["correlation"],  # Use precomputed correlation
        p_value=daily_correlation["p_value"],  # Use precomputed p-value
        output_filename=os.path.join("results", "plots", "daily_posts_vs_comments.png")
    )

    # Visualize correlation between post upvotes and comments
    post_upvotes = [post.get("upvotes", 0) for post in posts]
    post_comments = [len(post.get("comments", [])) for post in posts]
    visualize_correlation_with_regression(
        post_upvotes,
        post_comments,
        x_label="Post Upvotes",
        y_label="Post Comments",
        title="Correlation: Post Upvotes vs Comments",
        correlation=post_correlation["correlation"],  # Use precomputed correlation
        p_value=post_correlation["p_value"],  # Use precomputed p-value
        output_filename=os.path.join("results", "plots", "post_upvotes_vs_comments.png")
    )


    print("Processing complete.")
