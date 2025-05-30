import os
import re
import glob
import json
from collections import defaultdict
from tqdm import tqdm

import pandas as pd
from umap import UMAP
from hdbscan import HDBSCAN
from sklearn.feature_extraction.text import CountVectorizer

import openai
from bertopic import BERTopic
from bertopic.backend import OpenAIBackend
from bertopic.representation import OpenAI

from dotenv import load_dotenv

# Define common variants of "yes" and "no"
yes_variants = [
    "yes", "yeah", "yep", "yup", "sure", "of course", "certainly", "absolutely",
    "indeed", "definitely", "affirmative", "correct", "right", "ok", "okay"
]
no_variants = [
    "no", "nah", "nope", "not really", "never", "absolutely not",
    "negative", "incorrect", "wrong", "no way", "not at all"
]


allowed_models = set([
  "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
  "gpt-4o",
  "us.meta.llama3-3-70b-instruct-v1:0",
  "gemini-1.5-flash",
  "deepseek-ai_DeepSeek-R1",
  "deepseek-ai_DeepSeek-V3"
])

# Create regex pattern to match standalone words and common phrases
yes_no_pattern = r'\b(?:' + '|'.join(map(re.escape, yes_variants + no_variants)) + r')\b'

def clean_answer(answer):
    """
    Remove yes/no variants and extra spaces from an answer.
    """
    cleaned = re.sub(yes_no_pattern, '', answer, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def is_generic_response(text):
    """
    Check if the response is generic and lacks meaningful insights.
    """
    generic_responses = [
        "yes", "no", "thank you", "it was good", "it was okay", "not sure",
        "nothing much", "i don't know", "can't think of anything",
        "it helped", "it didn't help", "everything was fine", "nothing to add"
    ]
    text = text.lower().strip()
    return text in generic_responses or len(text) < 10

def extract_insights(client, response_text):
    """
    Use a LLM to extract meaningful insights from an answer.
    Returns a list of insights (or an empty list if generic, on error, or no insights).
    """
    if is_generic_response(response_text):
        return []  # Skip generic responses

    prompt = f"""You are a user experience researcher extracting insights from feedback.
Your task is to:
- Ignore any basic yes or no responses
- If the response contains many useful insights, break them into key points.
- Only include as many points as necessary (if there's only one insight, return just one).

Examples:
  Answer: The chatbot seemed to understand my questions and my intentions very well. It understood that I was interested in supplements for strength training and it provided me with an overview of the most popular and useful supplements. When I switched my focus to vitamin B12, it gave me the chemical names of the injectable forms and helped with my concerns. I thought the chatbot did very well at understanding why I was asking the questions.
  Insights: [
      "Strong intent recognition across different topics",
      "Able to provide detailed, specific information about supplements and vitamins",
      "Demonstrated contextual understanding and adaptability in conversation"
    ]

  Answer: yes it was fast
  Insights: []

  Answer: yes
  Insights: []

Provide the insights as a **Python list** (e.g., ["Insight 1", "Insight 2"]). Keep these insights concise.

Answer: "{response_text}"
Insights:"""
    try:
        response = client.chat.completions.create(
            model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
            messages=[
                {"role": "system", "content": "You are an AI assistant that extracts key insights from user feedback."},
                {"role": "user", "content": prompt}
            ]
        )
        # Use eval to convert the returned text to a Python list
        insights = eval(response.choices[0].message.content.strip())
        return insights if isinstance(insights, list) else []
    except Exception as e:
        # On error, simply return an empty list.
        return []

def extract_qa_from_csv(csv_files):
    """
    Extract Q&A pairs from CSV files with columns 'question', 'answer', and 'classification'.
    The model is inferred from the filename (assumes format: <model>_classifications.csv).
    Returns a nested dictionary:
         { model: { classification: [(question, answer), ...] } }
    """

    qa_by_model = defaultdict(lambda: defaultdict(list))
    for file in csv_files:
        basename = os.path.basename(file)
        # Assume filename ends with _classifications.csv
        model = basename.replace("_classifications.csv", "")
        try:
            df = pd.read_csv(file)
        except Exception as e:
            print(f"Error reading {file}: {e}")
            continue
        if {"question", "answer", "classification"}.issubset(df.columns):
            for classification, q, a in zip(df["classification"].astype(str),
                                            df["question"].astype(str),
                                            df["answer"].astype(str)):
                qa_by_model[model][classification].append((q, a))
    return qa_by_model

def process_interview_topic_analysis(csv_directory: str = None):
    """
    Process interview logs to compute topic statistics for each model and across all models for each dimension.
    """
    load_dotenv("../.env")

    # This will hold the Q&A pairs organized as: { model: { classification: [ (q, a), ... ] } }
    qa_by_model = defaultdict(lambda: defaultdict(list))

    # If a CSV directory is provided, process all CSV files matching *classifications.csv
    if csv_directory:
        csv_files = glob.glob(os.path.join(csv_directory, "*classifications.csv"))
        csv_qa = extract_qa_from_csv(csv_files)
        # Merge the CSV Q&A pairs into qa_by_model
        for model, classifications in csv_qa.items():
            for classification, pairs in classifications.items():
                qa_by_model[model][classification].extend(pairs)

    if not qa_by_model:
        print("No Q&A pairs found from chat logs or CSVs.")
        return

    # Use a dedicated client for insight extraction.
    insight_client = openai.OpenAI(api_key=os.getenv("BEDROCK_API_KEY"), base_url=os.getenv("BEDROCK_BASE_URL"))
    
    print("Extracting insights from each answer (including duplicates)...", flush=True)
    
    # Dictionaries to hold the document lists.
    # documents_by_classification: aggregated across all models.
    # documents_by_model: nested as { model: { classification: [documents] } }
    documents_by_classification = defaultdict(list)
    documents_by_model = defaultdict(lambda: defaultdict(list))
    
    insights_file = f"{csv_directory}/answers_insights.json"
    if os.path.exists(insights_file):
        with open(insights_file, "r", encoding="utf-8") as f:
            all_answer_insights = json.load(f)

    
        # Process each entry from the loaded data.
        for entry in all_answer_insights:
            model = entry["model"]
            classification = entry["classification"]
            insights = entry["insights"]

            # For each insight, add it (possibly truncated) to our document lists.
            for insight in insights:
                doc = insight[:8000]  # Truncate the insight to 8000 characters if necessary.
                documents_by_classification[classification].append(doc)
                documents_by_model[model][classification].append(doc)
    else:
        print("Answer insights have not been extracted. Extracting them now.")
        # List to store each answer and its extracted insights.
        all_answer_insights = []
        
        # Process each Q&A pair, extracting insights per instance.
        for model in qa_by_model:
            for classification in tqdm(qa_by_model[model]):
                for _, answer in tqdm(qa_by_model[model][classification]):
                    # Normalize the answer (clean and lowercase) for consistency.
                    normalized_answer = clean_answer(answer).lower()
                    insights = extract_insights(insight_client, normalized_answer)
                    
                    # Save the answer and its insights.
                    all_answer_insights.append({
                        "model": model,
                        "classification": classification,
                        "answer": answer,
                        "insights": insights
                    })
                    
                    # For each insight, add it (possibly truncated) to our document lists.
                    for insight in insights:
                        doc = insight[:8000]
                        documents_by_classification[classification].append(doc)
                        documents_by_model[model][classification].append(doc)
        
        # Save all answers and insights to a JSON file for inspection.
        with open(f"{csv_directory}/answers_insights.json", "w", encoding="utf-8") as f:
            json.dump(all_answer_insights, f, indent=2)
        print("All answer and insight data saved to 'answers_insights.json'")
    
        for classification, docs in documents_by_classification.items():
            out_fname = f"{csv_directory}/documents_{classification}.json"
            with open(out_fname, "w", encoding="utf-8") as f:
                json.dump(docs, f, indent=2)
            print(f"Aggregated documents for classification '{classification}' saved to {out_fname}")

    def run_topic_model(documents, output_prefix):
        """
        Given a list of documents, run BERTopic topic modeling.
        Saves a CSV file with topic information and returns the topic model.
        """

        # Skip generic and user explicit rating classification
        skip = ["RQ4", "WILD"]
        if output_prefix in skip:
            print(f"Skipping topic modeling for classification 'WILD'.")
            return None

        # Use a client for embedding/topic modeling.
        topic_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        embedding_model = OpenAIBackend(topic_client, "text-embedding-3-small", delay_in_seconds=1, batch_size=128)
        umap_model = UMAP(n_neighbors=5, n_components=5, min_dist=0.0, metric='cosine', random_state=42)
        hdbscan_model = HDBSCAN(min_cluster_size=5, metric='euclidean', cluster_selection_method='eom', prediction_data=True)
        vectorizer_model = CountVectorizer(stop_words="english", min_df=2, ngram_range=(1, 2))
        rep_client = openai.OpenAI(api_key=os.getenv("BEDROCK_API_KEY"), base_url=os.getenv("BEDROCK_BASE_URL"))
        representation_model = OpenAI(rep_client, "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
                                    exponential_backoff=True, chat=True)

        topic_model = BERTopic(
            embedding_model=embedding_model,
            umap_model=umap_model,
            hdbscan_model=hdbscan_model,
            vectorizer_model=vectorizer_model,
            representation_model=representation_model,
            top_n_words=10,
            verbose=True
        )

        topic_model.fit_transform(documents)
        topic_info = topic_model.get_topic_info()

        csv_out = f"{csv_directory}/topics_ranked_{output_prefix}.csv"
        topic_info.to_csv(csv_out, index=False)
        print(f"Topics ranked saved to '{csv_out}' for {output_prefix}", flush=True)

        # Save the topic model (including its embedding model) to a directory.
        model_out_dir = os.path.join(csv_directory, "dimension-models", output_prefix)
        os.makedirs(model_out_dir, exist_ok=True)
        topic_model.save(model_out_dir, serialization="safetensors", save_ctfidf=True,
                        save_embedding_model=embedding_model)
        print(f"Topic model saved to '{model_out_dir}'")
        return topic_model

    print("\nRunning aggregated topic modeling (across all models) per classification...")
    for classification, docs in documents_by_classification.items():
        out_prefix = classification  # e.g., "RQ1", "RQ2", etc.
        run_topic_model(docs, output_prefix=out_prefix)

    print("\nRunning topic modeling per model per classification...")
    for model, class_docs in documents_by_model.items():
        for classification, docs in class_docs.items():
            out_prefix = f"{model}_{classification}"
            try:
                run_topic_model(docs, output_prefix=out_prefix)
            except Exception as e:
                print(f"Error running topic modeling for {out_prefix}: {e}", flush=True)

    print("Topic analysis complete.")

if __name__ == "__main__":
    csv_directory = "data"
    process_interview_topic_analysis(csv_directory)
