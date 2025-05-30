import json
import csv
from openai import OpenAI
import os
from tqdm import tqdm
from dotenv import load_dotenv
import numpy as np
import pandas as pd

from rating_averages import get_rating, parse_rating
from dimensions import DIMENSIONS

allowed_models = set([
    "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    "gpt-4o",
    "us.meta.llama3-3-70b-instruct-v1:0",
    "gemini-1.5-flash",
    "deepseek-ai/DeepSeek-R1",
    "deepseek-ai/DeepSeek-V3"
])

def join_message_content(messages):
    """
    Joins the 'content' field in a list of messages. If 'content' is a list, concatenate all text items into a single string.
    """
    for message in messages:
        if isinstance(message.get('content'), list):
            message['content'] = "\n".join(item['text'] for item in message['content'])
    return messages

def classify_message_class(client, messages, model):
    """
    Classify the interview question and answer pairs into different dimensions.
    """
    classifications = []
    for i, message in enumerate(messages):
        if message['role'] == 'assistant' and i + 1 < len(messages) and messages[i + 1]['role'] == 'user':
            classification_prompt = (
                "A group of users have been interviewed on their experience using a ChatBot. The interviewer's messages (questions) are marked with 'role': 'assistant', "
                "and the user's responses are marked with 'role': 'user'. Classify the last interview question in the chat history based on these types:\n"
                "RQ1: Question asking the user about how well the ChatBot understood the user's question or request.\n"
                "RQ2: Question asking the user about how well the ChatBot met their needs or solved their problems.\n"
                "RQ3: Question asking the user about how well the ChatBot provided coherent, factual, and relevant information.\n"
                "RQ4: Question asking the user about how they would rate their satisfaction.\n"
                "RQ5: Question asking the user about how the ChatBot can be improved.\n"
                "RQ6: General question asking the user about what they think about the ChatBot, overall experience, feelings\n"
                "WILD: Other questions, are you ready questions, thanking the user\n"
                "Chat history:\n"
                f"{json.dumps(messages[:i + 1], indent=2)}\n\n"
                "Output the class type and nothing else."
            )

            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a UX researcher. You are an expert at summarizing insights and themes from user experience interviews."},
                        {"role": "user", "content": classification_prompt},
                    ]
                )

                response_content = response.choices[0].message.content.strip()
                # Determine classification based on response content
                class_name = next((key for key in DIMENSIONS.keys() if key in response_content), "WILD")
                classifications.append({
                    "question": message['content'],
                    "answer": messages[i + 1]['content'],
                    "classification": class_name
                })
            except Exception as e:
                print(f"Failed to classify message: {e}", flush=True)
                raise Exception(f"Failed to classify message: {e}")
    return classifications

def save_results_as_csv(output_prefix, classifications):
    """
    Save classifications as a CSV file.
    """
    # Save classifications
    with open(f"{output_prefix}_classifications.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["question", "answer", "classification"])
        writer.writeheader()
        writer.writerows(classifications)

def process_classifications_and_ratings(output_folder: str, client, interview_logs_file: str, model: str = "gpt-4o"):
    """
    Processes each interview record to generate classifications and ratings.
    """
    try:
        # Read the interview logs JSON file
        with open(interview_logs_file, 'r') as file:
            interview_logs = json.load(file)

        models = {}
        for record in interview_logs:
            interview_model = record.get("session_model")
            if  interview_model not in allowed_models:
                continue
            if interview_model not in models:
                models[interview_model] = []
            models[interview_model].append(record)
        for interview_model, interview_logs_per_model in models.items():
            process_per_model(output_folder, client, interview_logs_per_model, model, interview_model)
    except Exception as e:
        print(f"An error occurred while processing the interview logs: {e}", flush=True)
        raise Exception(f"An error occurred while processing the interview logs: {e}")

def process_ratings(client, model_name, ratings_by_class, output_folder):
    """
    Generates one set of ratings for a specified model.
    """
    for dimension, ratings in ratings_by_class.items():
        num_trials = 5 if dimension != "RQ4" else 1
        nan_threshold = 3 if dimension != "RQ4" else 1
        trial_results = {f"trial_{i+1}": [] for i in range(num_trials)}
        avg_ratings = []

        ratings_df = pd.DataFrame(ratings)

        for index, row in tqdm(ratings_df.iterrows(), total=ratings_df.shape[0]):
            question = row["question"]
            answer = row["answer"]
            trials = []
            
            # Run 5 trials per row.
            for i in range(num_trials):
                rating_str = get_rating(client, dimension, question, answer)
                rating_val = parse_rating(rating_str)
                trials.append(rating_val)
            
            # If fewer than 3 trials yield a numeric rating, set the average to NaN.
            non_nan_count = sum(not np.isnan(val) for val in trials)
            if non_nan_count < nan_threshold:
                avg_rating = np.nan
            else:
                avg_rating = np.nanmean(trials)
                
            avg_ratings.append(avg_rating)
            for i, rating in enumerate(trials):
                trial_results[f"trial_{i+1}"].append(rating)
        
        # Update dataframe with the new ratings.
        ratings_df["rating"] = avg_ratings
        for col, values in trial_results.items():
            ratings_df[col] = values
        
        # Ensure the output folder exists.
        os.makedirs(output_folder, exist_ok=True)
        output_file = os.path.join(output_folder, os.path.basename(f"{model_name}_ratings_{dimension}.csv"))
        ratings_df.to_csv(output_file, index=False)
        print(f"Finished processing file. Output written to {output_file}.")

def process_per_model(output_folder, client, interview_logs: list, model: str = "gpt-4o", filter_model: str = None):
    """
    Processes interview records for a specified model to generate classifications and ratings.
    """
    try:
        print(f"Processing interview logs for model: {filter_model}", flush=True)
        all_classifications = []
        ratings_by_class = {}

        for record in tqdm(interview_logs):
            messages = record.get("interview", [])

            # Join the message content
            messages = join_message_content(messages)

            # Classify question-answer pairs
            classifications = classify_message_class(client, messages, model)
            all_classifications.extend(classifications)

            for classification in classifications:
                class_name = classification['classification']
                # These ratings are not used for RQ5 (Improvements) or WILD (Unknown classifications)
                if class_name in ["RQ5", "WILD"]:
                    continue
                question = classification['question']
                answer = classification['answer']

                # Generate a rating for the specific class
                if class_name not in ratings_by_class:
                    ratings_by_class[class_name] = []
                
                ratings_by_class[class_name].append({"question": question, "answer": answer})
  
        save_results_as_csv(f"{output_folder}/{filter_model}", all_classifications)
        process_ratings(client, filter_model, ratings_by_class, output_folder)

    except Exception as e:
        print(f"An error occurred while processing the interview logs: {e}")
        raise Exception(f"An error occurred while processing the interview logs: {e}")

# Example usage
if __name__ == "__main__":
    output_folder = "data"
    interview_logs_path = f"{output_folder}/interview_logs.json"
    
    load_dotenv("../.env")
    api_key = os.getenv("BEDROCK_API_KEY")
    base_url = os.getenv("BEDROCK_BASE_URL")
    client = OpenAI(api_key=api_key, base_url=base_url)
    model = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"

    process_classifications_and_ratings(output_folder, client, interview_logs_path, model)
