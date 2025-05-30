#!/usr/bin/env python3
import csv
import json
from tqdm import tqdm

# Expected classification types
CLASS_TYPES = ["RQ1", "RQ2", "RQ3", "RQ4", "RQ6"]

def count_qapairs(messages):
    """
    Count the number of Q/A pairs in a list of messages.
    A pair is defined when a message with role "assistant" is immediately followed by one with role "user".
    """
    count = 0
    for i in range(len(messages) - 1):
        if messages[i].get("role") == "assistant" and messages[i+1].get("role") == "user":
            count += 1
    return count

def get_average(rating_list):
    """
    Given a list of rating strings, convert valid ones to float and return the average rounded to two decimals.
    If no valid ratings are found, return "N/A".
    """
    numeric_ratings = []
    for r in rating_list:
        try:
            numeric_ratings.append(float(r))
        except Exception:
            continue
    if numeric_ratings:
        return round(sum(numeric_ratings) / len(numeric_ratings), 2)
    return "N/A" if len(rating_list) > 0 else ""

def process_model(input_folder, model, records):
    """
    Process records for a given model:
      1. Count Q/A pairs per record using the interview logs.
      2. Load the per-model classifications CSV (one row per Q/A pair).
      3. Load the per-model ratings CSV files for each classification.
      4. Reconstruct the record-level ratings using deterministic ordering.
      5. Write out a CSV file named {model}_ratings_by_record.csv.
    """
    # === Step 1. Determine record boundaries for this model ===
    # For each record, we count how many Q/A pairs (i.e. classifications) it produced.
    record_boundaries = []  # List of tuples: (uid, num_pairs)
    for record in records:
        uid = record.get("uid", "nan")
        messages = record.get("interview", [])
        num_pairs = count_qapairs(messages)
        record_boundaries.append((uid, num_pairs))

    # === Step 2. Load the per-model classifications CSV ===
    classifications_csv = f"{input_folder}/{model}_classifications.csv"
    classifications = []
    try:
        with open(classifications_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Expected keys: "question", "answer", "classification"
                classifications.append(row)
    except Exception as e:
        print(f"Error reading {classifications_csv}: {e}")
        return

    # === Step 3. Load the per-model ratings CSV files for each classification type ===
    ratings_by_type = {}
    for cls in CLASS_TYPES:
        # For example: model_RQ1.csv, model_RQ2.csv, ..., model_WILD.csv
        filename = f"{input_folder}/{model}_ratings_{cls}.csv"
        ratings_list = []
        try:
            with open(filename, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Expected key: "rating"
                    ratings_list.append(row["rating"])
        except FileNotFoundError:
            print(f"Warning: {filename} not found. No ratings for classification {cls} for model {model}.")
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            return
        ratings_by_type[cls] = ratings_list

    # Pointer for each classification type to track our position in its ratings list.
    pointers = {cls: 0 for cls in CLASS_TYPES}

    # === Step 4. Reconstruct record-level ratings ===
    results = []  # List to hold each record's average ratings.
    overall_index = 0  # Pointer into the classifications list.
    for uid, num_pairs in tqdm(record_boundaries, desc=f"Processing model {model}"):
        # Create a temporary mapping: classification type -> list of ratings for this record.
        record_ratings = {cls: [] for cls in CLASS_TYPES}
        for i in range(num_pairs):
            if overall_index + i >= len(classifications):
                print(f"Warning: mismatch in expected classification count for model {model}.")
                break
            row = classifications[overall_index + i]
            cls_type = row["classification"]
            # Get the next available rating for this classification type.
            if cls_type in ratings_by_type:
                pointer = pointers[cls_type]
                if pointer < len(ratings_by_type[cls_type]):
                    rating_val = ratings_by_type[cls_type][pointer]
                    pointers[cls_type] += 1
                    record_ratings[cls_type].append(rating_val if rating_val.lower() != "nan" else "N/A")
                else:
                    record_ratings[cls_type].append("N/A")
            else:
                record_ratings.setdefault(cls_type, []).append("N/A")
        overall_index += num_pairs

        # Compute average ratings for each classification type.
        avg_ratings = {}
        for cls in CLASS_TYPES:
            avg_ratings[cls] = get_average(record_ratings.get(cls, []))
        avg_ratings["uid"] = uid
        results.append(avg_ratings)

    # === Step 5. Write out the per-model record-level ratings CSV ===
    output_csv = f"{input_folder}/{model}_ratings_by_record_recreated.csv"
    fieldnames = ["uid"] + CLASS_TYPES
    try:
        with open(output_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for rec in results:
                writer.writerow(rec)
        print(f"Processed model '{model}' and saved ratings by record to: {output_csv}")
    except Exception as e:
        print(f"Error writing output CSV {output_csv}: {e}")

def process_ratings_by_record(input_folder, interview_logs_file):
    """
    Process the ratings by record for each model.
    """
    try:
        with open(interview_logs_file, "r", encoding="utf-8") as f:
            interview_logs = json.load(f)
    except Exception as e:
        print(f"Error reading {interview_logs_file}: {e}")
        return

    # === Group records by model ===
    # Here, we use the "session_model" field from each record.
    models = {}
    for record in interview_logs:
        model = record.get("session_model", "unknown").replace("/", "_")
        if model not in models:
            models[model] = []
        models[model].append(record)

    # Process each model's records separately.
    for model, records in models.items():
        print(f"Processing records for model: {model}")
        process_model(input_folder, model, records)
    
if __name__ == "__main__":
    # Path to the original interview logs JSON file.
    input_folder = "data"
    interview_logs_file = f"{input_folder}/interview_logs.json"
    process_ratings_by_record(input_folder, interview_logs_file)
