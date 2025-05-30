import os
import json
import random

def fetch_conversations_from_folder(input_folder: str, output_file: str):
    """
    Fetch conversations from a local folder and compile them into a single JSON file.
    """
    try:
        conversations = []

        for filename in os.listdir(input_folder):
            if filename.endswith(".json"):
                file_path = os.path.join(input_folder, filename)
                with open(file_path, 'r', encoding='utf-8') as infile:
                    try:
                        data = json.load(infile)
                        conversations.append(data)
                    except json.JSONDecodeError as e:
                        print(f"Error decoding {filename}: {e}")

        # Write data to a JSON file
        with open(output_file, "w", encoding="utf-8") as outfile:
            json.dump(conversations, outfile, indent=4)

        print(f"data successfully saved to {output_file}")

    except Exception as e:
        print(f"Error fetching data from database: {e}")

# Example usage
if __name__ == "__main__":
    input_folder = "logs"
    output_file = "analysis/conversations.json"
    fetch_conversations_from_folder(input_folder, output_file)
