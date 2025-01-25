import praw
from datetime import datetime, timedelta
import os
import json
import time

# To use this script, you need to set up the Reddit API:
# 1. Create a Reddit account if you don’t already have one.
# 2. Go to https://www.reddit.com/prefs/apps and log in.
# 3. Click on "Create App" or "Create Another App."
# 4. Fill in the fields:
#    - Name: Give your project a name (e.g., "MyResearchApp").
#    - App type: Select "script."
#    - Redirect URI: Enter "http://localhost:8080."
#    - Save the app.
# 5. Copy the "client_id" (located directly under the app name) and "client_secret" (next to "secret").
# 6. Paste the values for client_id, client_secret, username, and password into the configuration.

# Reddit API configuration
reddit = praw.Reddit(
    client_id="changeme",
    client_secret="changeme",
    user_agent="local research script",
    username="changeme",
    password="changeme"
)


# Fetch posts from a subreddit and embeds their comments directly into a JSON structure
# Note: In the current implementation, all comments, including replies to other comments,
# are stored in a flat structure under the "comments" field for each post.

def fetch_submissions_with_comments(p_subreddit_name, p_start_date, p_end_date):
    subreddit = reddit.subreddit(p_subreddit_name)  # Connect to the subreddit
    current_date = p_end_date  # Start from the end date
    total_days = 0
    total_posts = 0
    total_comments = 0

    # Ensure the "data" directory exists
    os.makedirs("data", exist_ok=True)


    while current_date > p_start_date:
        previous_date = current_date - timedelta(days=1)
        start_timestamp = int(previous_date.timestamp())
        end_timestamp = int(current_date.timestamp())

        posts_list = []  # List to store posts with embedded comments

        print(f"Fetching posts and comments for {previous_date.date()}...")

        after = None  # For pagination

        while True:
            # Fetch submissions with pagination
            submissions = list(subreddit.new(limit=100, params={"after": after}))
            if not submissions:
                print("No more posts available for the current pagination.")
                break  # Exit the loop if no posts are available

            for submission in submissions:
                # Filter submissions by timestamp
                if start_timestamp <= submission.created_utc < end_timestamp:
                    # Fetch comments for the submission
                    submission.comments.replace_more(limit=0)  # Remove "load more comments" placeholders
                    submission_comments = []

                    for comment in submission.comments.list():
                        submission_comments.append({
                            "id": comment.id,
                            "body": comment.body,
                            "author": comment.author.name if comment.author else None,
                            "created_utc": comment.created_utc,
                            "upvotes": comment.score
                        })

                    # Add the post along with its embedded comments
                    posts_list.append({
                        "id": submission.id,
                        "title": submission.title,
                        "selftext": submission.selftext,
                        "author": submission.author.name if submission.author else None,
                        "created_utc": submission.created_utc,
                        "upvotes": submission.score,
                        "num_comments": submission.num_comments,
                        "flair": submission.link_flair_text,
                        "comments": submission_comments  # Embed comments directly here
                    })

            # Pagination: Update "after" for the next batch of submissions
            if len(submissions) > 0:
                after = submissions[-1].fullname
            else:
                break

            # Respect Reddit API rate limits
            time.sleep(1)

        # Save the results for the current day into a single JSON file in the "data" directory
        posts_filename = f"data/{p_subreddit_name}_posts_with_comments_{previous_date.date()}.json"

        with open(posts_filename, "w") as posts_file:
            # noinspection PyTypeChecker
            # intellij bug
            json.dump(posts_list, posts_file)

        # Calculate and display the number of posts and comments for the day
        num_posts = len(posts_list)
        num_comments = sum(len(post["comments"]) for post in posts_list)
        total_posts += num_posts
        total_comments += num_comments

        print(f"Saved file: {posts_filename} with {num_posts} posts and {num_comments} comments for {previous_date.date()}.")

        # Move to the previous day
        current_date = previous_date
        total_days += 1

    # Summary of the entire operation
    print(f"Finished fetching data for {total_days} day(s).")
    print(f"Total posts: {total_posts}, Total comments: {total_comments}.")

    # Main function
if __name__ == "__main__":
    # Define the date range
    start_date = datetime(2025, 1, 23)  # Earliest date
    end_date = datetime.now()  # Current date
    # Note: Be aware that Reddit API limits fetching data, regardless of the specified date range.
    # If no posts are retrieved for certain days, it may indicate reaching this limit.
    # Consider keeping the range small.

    # Subreddit name
    subreddit_name = "austria"

    # Fetch submissions with comments
    fetch_submissions_with_comments(subreddit_name, start_date, end_date)