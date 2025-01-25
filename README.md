# What Moves r/Austria?

TBA

# SubReddit Data Collector

This script is the foundation for all further analysis of subreddit data. It allows you to fetch posts and their comments from a specified subreddit and saves them as JSON files. The collected data serves as the basis for other scripts and analyses in this repository.

## Key Features
- Fetches posts from a specified subreddit using the Reddit API.
- Retrieves all comments associated with each post.
- Saves the data in daily JSON files, stored in the `data` directory.
- Designed to respect Reddit's API limits.

## Requirements
- **Reddit API Credentials**: You must provide your own Reddit API credentials (client ID, secret, username, and password). To obtain them:
    1. Create a Reddit account if you don’t already have one.
    2. Visit [Reddit's App Preferences](https://www.reddit.com/prefs/apps) and create a new app.
    3. Select "script" as the app type.
    4. Add the credentials to the script.

## Usage
1. Update the script with your Reddit API credentials.
2. Define the subreddit name and the start/end date (the script automatically fetches starting from today).
3. Run the script to fetch data. All collected data will be saved in the `data` directory as JSON files.

### Note on Reddit API Limits
- Reddit's API only allows fetching data to a **limited time frame** in the past, regardless of the specified date range.
- If no posts are retrieved for certain days, it may indicate that this limit has been reached.
- Consider keeping the range small (approximately the last 3 weeks).
- Ensure compliance with [Reddit's Data API Terms](https://www.redditinc.com/policies/data-api-terms-of-use).

## JSON Data Structure
Each JSON file contains posts and their associated comments. The data structure for each post is as follows:

### Post Metadata:
- `id`: Unique ID of the post.
- `title`: Title of the post.
- `selftext`: Content of the post.
- `author`: Username of the post's author.
- `created_utc`: Timestamp of post creation (UTC).
- `upvotes`: Number of upvotes.
- `num_comments`: Number of comments on the post.
- `flair`: Post flair (if any).

### Comments:
Each post includes a `comments` field, which is a list of all comments:
- `id`: Unique ID of the comment.
- `body`: Content of the comment.
- `author`: Username of the comment's author.
- `created_utc`: Timestamp of comment creation (UTC).
- `upvotes`: Number of upvotes.

> **Note**: Replies to comments are stored in a flat structure, meaning the parent-child relationships between comments are not preserved.

## Foundation for Further Scripts
This script is **required to run first** to gather the initial dataset. Other scripts in this repository rely on the JSON data created by this script. Ensure that you have collected your data before running additional scripts.

> **Note**: By using this script, you acknowledge that you are responsible for complying with Reddit's API policies.

# Subreddit Statistics Analyzer

This Python script analyzes data from a Reddit subreddit, including posts and their comments. It calculates various statistics, performs correlations and regressions, and visualizes the results.

## Features

- **Load Data**: Imports subreddit data from nested JSON files.
- **Calculate Statistics**:
  - Total posts, comments, and upvotes.
  - Daily statistics (posts, comments, upvotes).
  - Correlation between posts and comments or upvotes and comments.
  - Linear regression to model relationships.
- **Save Results**:
  - Saves statistics, correlations, and regression results in CSV format.
- **Visualize**:
  - Daily posts and comments as an overlay bar chart.
  - Scatter plots with regression lines for:
    - Daily posts vs. comments.
    - Post upvotes vs. comments.


> **Note**: Ensure the `data` directory contains JSON files collected using the **SubRedditDataCollector** script.

# Subreddit Flair Engagement Analyzer

This script is designed to analyze Reddit posts and comments based on their associated flairs. It calculates detailed statistics, saves results in structured formats (JSON, CSV), and generates visualizations to highlight engagement across flairs.

## Features

- **Load Data**:
  - Imports subreddit data from JSON files stored in the `data` directory.

- **Calculate Statistics**:
  - Total engagement statistics for each flair:
    - **Posts**: Total number of posts for each flair.
    - **Upvotes**: Total number of upvotes, including comment upvotes (if specified).
    - **Comments**: Total number of comments, with the option to include or exclude comment data.
  - Coverage metrics:
    - Percentage of posts and comments tagged with any flair.
  - Flexibility to include or exclude comments in the analysis.

- **Save Results**:
  - JSON & CSV Files
    
- **Visualize**:
  - Bar Charts, Pie Charts, Stacked Bar Charts
    
## Specific Flairs
Specific flairs were pre-defined for visualization purposes, including **"Memes & Humor"**, **"Politik | Politics"**, **"Frage | Question"**, and **"Nachrichten | News"**. They are pre-selected based on their strong representation in the subreddit **r/Austria**. These flairs are **manually defined** and not automatically generated.
- Users can modify the list of flairs and the corresponding colors to match the context of a different subreddit or their specific needs. The `flairs_of_interest` and `flair_colors` parameters allow for full customization.

> **Note**: Ensure the `data` directory contains JSON files collected using the **SubRedditDataCollector** script.

# SubReddit Text Cleaner

This script processes subreddit data (posts and comments) for further analysis. It is essential for all text-based analyses, such as **word cloud generation**, **topic modeling**, and **sentiment analysis**.
It processes subreddit data (posts and comments) by cleaning text, removing unnecessary elements, and outputting datasets with or without stopwords. Flair-specific subsets can also be generated.

## Features
- **Data Cleaning**:
  - Removes URLs, emojis, special characters, and converts text to lowercase.
  - Supports stopword removal for **German** and **English**, with additional custom stopwords.
- **File Outputs**:
  - `cleaned_all.json`: All posts and comments (stopwords retained).
  - `cleaned_all_no_stopwords.json`: All posts and comments (stopwords removed).
  - `cleaned_[flair].json`: Flair-specific subset (stopwords retained).
  - `cleaned_[flair]_no_stopwords.json`: Flair-specific subset (stopwords removed).
- **Statistics**:
  - Provides counts of total posts, comments, and top flairs.

## Requirements
- JSON files from **SubRedditDataCollector.py** in the `data` directory.
- Languages supported for stopword filtering: **German** and **English**.
  - For other languages, stopwords need to be manually adjusted in the code.

# SubReddit Word Cloud Generator

This script generates **word clouds** and **word frequency analysis** plots from subreddit data that has been preprocessed using the **SubRedditTextCleaner.py** script.

A **word cloud** visualizes the most frequently occurring words by displaying them in varying font sizes. The more frequently a word appears in the data, the larger it is displayed in the word cloud. Optionally, you can use a **mask image** (e.g., a country shape) to influence the shape of the word cloud.

## Features
- **Word Cloud Generation**:
  - Creates a visually appealing word cloud where word size represents frequency.
  - Optionally uses a **mask image** (e.g., country outlines or custom shapes) to customize the word cloud's shape.
  - Supports **custom color palettes** for word cloud styling.
  - Outputs high-resolution transparent PNG files.
- **Word Frequency Analysis**:
  - Counts the frequency of words across all posts and comments.
  - Saves word frequency data as a CSV file.
  - Generates a horizontal bar chart of the most frequent words (formatted for A4 size).
- **Support for Custom Mask Shapes**:
  - Use a PNG mask (e.g., `WordCloudMask.png`) for specific shapes. 
  - Ensure the **pixel dimensions** of the mask match the size of the generated word cloud (e.g., 7000x3823 pixels by default).
  - Falls back to a square word cloud if no mask is provided.

> **Note**: Ensure the `data` directory contains JSON files cleaned by the **01_SubRedditTextCleaner.py** script. Run the cleaner once before using **SubRedditWordCloud.py**.  
