from umap import UMAP
from hdbscan import HDBSCAN
import openai
from sklearn.feature_extraction.text import CountVectorizer
from bertopic import BERTopic
from bertopic.representation import OpenAI
from bertopic.backend import OpenAIBackend

import json
import numpy as np
import pandas as pd
import argparse
import os
from dotenv import load_dotenv

def extract_qa_from_chat_logs(chat_logs_file):
    """
    Extract Q&A pairs from chat logs where the assistant asks questions and the user responds.
    Organize them by model.

    The document index for each model is cumulative (across all chat logs) so that later analyses 
    using these indices are consistent.
    """
    qa_by_model = {}
    doc_to_session = {}
    session_counter = {}
    
    with open(chat_logs_file, 'r') as file:
        chat_logs = json.load(file)
    
    for chat_log in chat_logs:
        model_name = chat_log.get("session_model", "unknown")
        messages = chat_log.get("session", [])
        
        if model_name not in qa_by_model:
            qa_by_model[model_name] = []
            doc_to_session[model_name] = []
            session_counter[model_name] = 0
        
        current_session = session_counter[model_name]
        start_idx = len(qa_by_model[model_name])
        for i in range(len(messages) - 1):
            # Pair a user message with the following assistant message.
            if messages[i].get("role") == "user" and messages[i+1].get("role") == "assistant":
                qa_by_model[model_name].append((messages[i]["content"], messages[i+1]["content"]))
                doc_to_session[model_name].append((start_idx, current_session))
                start_idx += 1
        
        session_counter[model_name] += 1
    
    return qa_by_model, doc_to_session

def process_chat_topic_analysis(chat_logs_file: str, output_folder: str):
    """
    Process chat logs to compute topic statistics for each model and across all models.
    """
    if not chat_logs_file:
        return {}
    
    # --- Main Extraction ---
    qa_by_model, doc_to_session_mapping = extract_qa_from_chat_logs(chat_logs_file)
    
    topic_models = {}
    summary_data = []
    session_details_list = []
    aggregated_session_counts = {}  # Per model: { model: { session_id: {"non_minus1": set(), "minus1_count": int} } }
    
    # Initialize embedding and representation models.
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    embedding_model = OpenAIBackend(client, "text-embedding-3-small", delay_in_seconds=1, batch_size=1024)
    
    umap_model = UMAP(n_neighbors=15, n_components=5, min_dist=0.0, metric='cosine', random_state=42)
    hdbscan_model = HDBSCAN(min_cluster_size=15, metric='euclidean', cluster_selection_method='eom', prediction_data=True)
    vectorizer_model = CountVectorizer(stop_words="english", min_df=2, ngram_range=(1, 2))
    
    client = openai.OpenAI(api_key=os.getenv("BEDROCK_API_KEY"), base_url=os.getenv("BEDROCK_BASE_URL"))
    representation_model = OpenAI(client, "us.anthropic.claude-3-5-sonnet-20241022-v2:0", exponential_backoff=True, chat=True)
    
    # --- Process Each Model Individually ---
    for model_name, qa_pairs in qa_by_model.items():
        print(f"Processing model: {model_name}")
        all_documents = [f"Q: {q[:500]}, A: {a[:8000]}" for q, a in qa_pairs]
        
        # Fit the model for this set of documents.
        topic_model = BERTopic(
            embedding_model=embedding_model,
            umap_model=umap_model,
            hdbscan_model=hdbscan_model,
            vectorizer_model=vectorizer_model,
            representation_model=representation_model,
            top_n_words=10,
            verbose=True
        )
        
        try:
            topics, _ = topic_model.fit_transform(all_documents)
            topic_model.get_topic_info().to_csv(f"{output_folder}/topics_{model_name.replace('/', '_')}.csv", index=False)
        except Exception as e:
            print(e)
        
        # Aggregate session counts using the precomputed mapping.
        doc_info = topic_model.get_document_info(all_documents)
        session_topic_counts = {}
        for doc_idx, session_id in doc_to_session_mapping[model_name]:
            topic = doc_info.iloc[doc_idx]["Topic"]
            if session_id not in session_topic_counts:
                session_topic_counts[session_id] = {"non_minus1": set(), "minus1_count": 0}
            if topic == -1:
                session_topic_counts[session_id]["minus1_count"] += 1
            else:
                session_topic_counts[session_id]["non_minus1"].add(topic)
        aggregated_session_counts[model_name] = session_topic_counts
        
        # Save session details for this model.
        for session_id, topics_data in session_topic_counts.items():
            unique_count = len(topics_data["non_minus1"]) + topics_data["minus1_count"]
            session_details_list.append({
                "model": model_name,
                "session_id": session_id,
                "unique_topic_count": unique_count,
                "data": "per_model"
            })
        session_topic_count_list = [len(data["non_minus1"]) + data["minus1_count"] for data in session_topic_counts.values()]
        avg_topics_per_session = np.mean(session_topic_count_list) if session_topic_count_list else 0
        summary_data.append({
            "model": model_name, 
            "avg_unique_topics_per_session": avg_topics_per_session,
            "total_sessions": len(session_topic_count_list)
        })
        
        topic_models[model_name] = topic_model

    # --- Global Model Processing ---
    print("Processing topics across all models...")
    all_documents_global = []
    global_session_mapping = []  # Composite key: "model_sessionID"
    for model_name in qa_by_model:
        for idx, (q, a) in enumerate(qa_by_model[model_name]):
            all_documents_global.append(f"Q: {q[:500]}, A: {a[:8000]}")
            _, session_id = doc_to_session_mapping[model_name][idx]
            composite_session = f"{model_name}_{session_id}"
            global_session_mapping.append(composite_session)
    
    global_topic_model = BERTopic(
        embedding_model=embedding_model,
        umap_model=umap_model,
        hdbscan_model=hdbscan_model,
        vectorizer_model=vectorizer_model,
        representation_model=representation_model,
        top_n_words=10,
        verbose=True
    )
    
    global_topic_model.fit_transform(all_documents_global)
    global_topic_model.get_topic_info().to_csv(f"{output_folder}/topics_global.csv", index=False)
    
    global_doc_info = global_topic_model.get_document_info(all_documents_global)
    aggregated_global_counts = {}
    for i, composite_session in enumerate(global_session_mapping):
        topic = global_doc_info.iloc[i]["Topic"]
        if composite_session not in aggregated_global_counts:
            aggregated_global_counts[composite_session] = {"non_minus1": set(), "minus1_count": 0}
        if topic == -1:
            aggregated_global_counts[composite_session]["minus1_count"] += 1
        else:
            aggregated_global_counts[composite_session]["non_minus1"].add(topic)
    
    # Save global session details.
    for composite_session, topics_data in aggregated_global_counts.items():
        unique_count = len(topics_data["non_minus1"]) + topics_data["minus1_count"]
        session_details_list.append({
            "model": "global",
            "session_id": composite_session,
            "unique_topic_count": unique_count,
            "data": "global"
        })
    global_session_topic_count_list = [len(data["non_minus1"]) + data["minus1_count"] for data in aggregated_global_counts.values()]
    global_avg_topics_per_session = np.mean(global_session_topic_count_list) if global_session_topic_count_list else 0
    summary_data.append({
        "model": "global", 
        "avg_unique_topics_per_session": global_avg_topics_per_session,
        "total_sessions": len(global_session_topic_count_list)
    })
    topic_models["global"] = global_topic_model

    # --- Save Summaries and Models ---
    pd.DataFrame(summary_data).to_csv(f"{output_folder}/model_topic_summary.csv", index=False)
    pd.DataFrame(session_details_list).to_csv(f"{output_folder}/session_topic_details.csv", index=False)
    
    for k, m in topic_models.items():
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        embedding_model_save = OpenAIBackend(client, "text-embedding-3-small", delay_in_seconds=1, batch_size=128)
        save_path = os.path.join(f"{output_folder}/chat-models", k)
        m.save(save_path, serialization="safetensors", save_ctfidf=True, save_embedding_model=embedding_model_save)
    
    return topic_models

# Example usage:
if __name__ == "__main__":
    load_dotenv("../.env")
    input_file = "analysis/chat_logs.json"
    output_folder = "data"
    
    process_chat_topic_analysis(input_file, output_folder)
