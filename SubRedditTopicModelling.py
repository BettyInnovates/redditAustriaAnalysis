import json
import os
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from gensim.corpora.dictionary import Dictionary
from gensim.models import CoherenceModel

# Perform topic modeling and calculate coherence
def perform_topic_modeling(texts, num_topics=5, num_words=10):
    # Vectorize texts using CountVectorizer
    vectorizer = CountVectorizer(max_df=0.95, min_df=2)
    dtm = vectorizer.fit_transform(texts)
    lda = LatentDirichletAllocation(n_components=num_topics, random_state=42)
    lda.fit(dtm)

    # Extract words and topics
    words = vectorizer.get_feature_names_out()
    topics = {f"Topic {i + 1}": [words[idx] for idx in topic.argsort()[-num_words:][::-1]] for i, topic in enumerate(lda.components_)}

    # Prepare texts for Gensim coherence model
    tokenized_texts = [text.split() for text in texts]
    dictionary = Dictionary(tokenized_texts)
    corpus = [dictionary.doc2bow(text) for text in tokenized_texts]

    # Use topics directly from LDA for Gensim coherence
    gensim_topics = [[dictionary.token2id[word] for word in topic if word in dictionary.token2id] for topic in topics.values()]
    coherence_model = CoherenceModel(
        topics=gensim_topics,
        texts=tokenized_texts,
        dictionary=dictionary,
        coherence="c_v"
    )
    coherence_score = coherence_model.get_coherence()

    return topics, coherence_score


# Main function
if __name__ == "__main__":
    # Define input and output paths
    data_directory = "data"
    results_directory = "results"
    plots_directory = os.path.join(results_directory, "plots")
    json_directory = os.path.join(results_directory, "json")
    os.makedirs(plots_directory, exist_ok=True)
    os.makedirs(json_directory, exist_ok=True)

    input_filename = "cleaned_politics_no_stopwords.json"
    filepath = os.path.join(data_directory, input_filename)

    print("Loading filtered posts...")
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}. Please run 'SubRedditTextCleaner.py' first.")
        exit()

    with open(filepath, "r", encoding="utf-8") as file:
        posts = json.load(file)

    # Preprocess texts
    print("Preprocessing texts...")
    texts = []
    for post in posts:
        # Combine title and selftext
        combined_text = post.get("title", "") + " " + post.get("selftext", "")
        texts.append(combined_text)

        # Include comments
        for comment in post.get("comments", []):
            comment_text = comment.get("cleaned_body", "")
            texts.append(comment_text)

    print(f"Total texts after preprocessing: {len(texts)}")

    # Perform topic modeling
    print("Performing topic modeling...")
    num_topics = 4
    num_words = 10
    topics, coherence_score = perform_topic_modeling(texts, num_topics, num_words)

    # Display topics and coherence score
    print(f"Topic Coherence: {coherence_score:.2f}")
    for topic, words in topics.items():
        print(f"{topic}: {', '.join(words)}")

    # Save topics to JSON
    topics_json_path = os.path.join(json_directory, "topics.json")
    with open(topics_json_path, "w", encoding="utf-8") as file:
        json.dump(topics, file, ensure_ascii=False, indent=4)
    print(f"Topics saved to {topics_json_path}.")

