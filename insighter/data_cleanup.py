import json
from emoji import emoji_count
import csv
from openai import OpenAI
import uuid
import os
from dotenv import load_dotenv

allowed_models = set([
  "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
  "gpt-4o",
  "us.meta.llama3-3-70b-instruct-v1:0",
  "gemini-1.5-flash",
  "deepseek-ai/DeepSeek-R1",
  "deepseek-ai/DeepSeek-V3"
])

keyphrases = [
    "here to assist you",
    "here to help you",
    "ready to assist you",
    "ready to help you",

    "As an AI,", "As an ai,", "as an AI,", "as an ai,",
    "As a virtual assistant", "as a virtual assistant",
    "As a chatbot,", "as a chatbot,",
    "As a large language model,", "as a large language model",
    "As a language model", "as a language model",

    "I'm an AI", "I'm an ai",
    "I'm the AI", "I'm the ai",
    "I'm just an AI", "I'm just an ai",
    "I'm just the AI", "I'm just the ai",
    "I'm a chatbot", "I'm a ChatBot", "I'm a Chatbot",
    "I'm the chatbot", "I'm the ChatBot", "I'm the Chatbot",
    "I'm just a chatbot", "I'm just a ChatBot", "I'm just a Chatbot",
    "I'm a virtual assistant",
    "I'm the virtual assistant",
    "I'm just a virtual assistant",
    "I'm just the virtual assistant",
    "I'm actually an AI", "I'm actually an ai",
    "I'm actually the AI", "I'm actually the ai",
    "I'm actually the chatbot",

    "How can I assist", "how can I assist", 
    "How I can assist", "how I can assist",

    "I don't have feelings",
    "I don't have emotions",
    "I don't have personal",
    "I don't experience",
    "I don't have experiences",

    "I don't have the capability",
    "I don't have access",

    "Users generally", "users generally",
    "Users typically", "users typically",
    "If a user", "if a user",
    "Users might", "users might",
    "were the user",

    "I was able to meet your needs",
    "I was able to assist",

    "#", "**",
  ]

mother_prompt = """
If any of the following criteria is observed in the input session or interview, this data point is of low quality:
1. If the user used a chatbot to complete the chatbot
2. If the user used a chatbot to complete the interview
3. If the user's responses to the chatbot did not make logical sense (e.g., did not understand the task, responded randomly, etc.)
4. If the user's responses to the interview did not make logical sense (e.g., did not understand the task, responded randomly, etc.)

Predict if the following data point is low quality or not and no need to tell me why.
# First in a new line predict if the passage is of low quality of high quality. Just say “low quality” or “high quality”, nothing else in this line.
"""

def is_high_quality(client, model, session, interview):
    """
    Uses an LLM to determine if an interview is high-quality.
    """

    passage = """
    session:
    {}

    Interview:
    {}
    """.format(json.dumps(session), json.dumps(interview))

    # Chatbot Detection
    if not session or len(session) <= 1:
        return False
    if not interview or len(interview) <= 2:
        return False
    for message in session:
        if message['role'] == 'user' and (len(message["content"]) >= 1500 or any(phrase in message['content'] for phrase in keyphrases) or emoji_count(message["content"])):
            return False

    prompt = mother_prompt + passage

    response = client.chat.completions.create(
        model=model, 
        messages=[
            {"role": "user", "content": prompt}
        ],
    )

    classification = response.choices[0].message.content.strip()
    return "high quality" in classification

def process_logs(client, model, input_file: str, chat_logs_file: str, interview_logs_file: str, csv_output_file: str):
    """
    Filters conversations, creates chat and interview logs, and outputs a CSV with quality classification.
    """
    try:
        with open(input_file, 'r') as file:
            data = json.load(file)

        chat_logs = []
        interview_logs = []
        csv_rows = []

        for record in data:
            session = record.get("session", [])
            interview = record.get("interview", [])
            
            quality = "high-quality" if is_high_quality(client, model, session, interview) else "low-quality"
            
            uid = str(uuid.uuid4())
            if quality == "high-quality":
                chat_log = {
                    "uid": uid,
                    "session_model": record.get("sessionModel", ""),
                    "session": record.get("session", []),
                    "session_start": record.get("sessionStart", ""),
                    "session_end": record.get("sessionEnd", "")
                }
                chat_logs.append(chat_log)

                interview_log = {
                    "uid": uid,
                    "session_model": record.get("sessionModel", ""),
                    "interview_model": record.get("interviewModel", ""),
                    "interview": interview,
                    "interview_start": record.get("interviewStart", ""),
                    "interview_end": record.get("interviewEnd", "")
                }
                interview_logs.append(interview_log)

            csv_rows.append([
                uid, record.get("session_model", ""),
                record.get("interview_model", ""), json.dumps(record.get("session", [])), json.dumps(interview),
                record.get("session_start", ""), record.get("session_end", ""),
                record.get("interview_start", ""), record.get("interview_end", ""), quality
            ])
        
        with open(chat_logs_file, 'w') as file:
            json.dump(chat_logs, file, indent=4)
        with open(interview_logs_file, 'w') as file:
            json.dump(interview_logs, file, indent=4)
        
        with open(csv_output_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["uid", "session_model", "interview_model", "session", "interview", "session_start", "session_end", "interview_start", "interview_end", "quality"])
            writer.writerows(csv_rows)
        
        print(f"Chat logs written to {chat_logs_file}")
        print(f"Interview logs written to {interview_logs_file}")
        print(f"CSV output written to {csv_output_file}")
    
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
if __name__ == "__main__":
    output_folder = "data"
    input_file_path = f"{output_folder}/conversations.json"
    chat_logs_path = f"{output_folder}/chat_logs.json"
    interview_logs_path = f"{output_folder}/interview_logs.json"
    csv_output_path = f"{output_folder}/conversation_quality.csv"

    load_dotenv("../.env")
    api_key = os.getenv("BEDROCK_API_KEY")
    base_url = os.getenv("BEDROCK_BASE_URL")
    client = OpenAI(api_key=api_key, base_url=base_url)
    model = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
    
    process_logs(client, model, input_file_path, chat_logs_path, interview_logs_path, csv_output_path)
