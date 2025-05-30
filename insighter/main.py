from openai import OpenAI
from dotenv import load_dotenv
import os

from get_data import fetch_conversations_from_folder
from data_cleanup import process_logs
from interaction_statistics import process_statistics
from insight_analysis import process_classifications_and_ratings
from ratings_per_record import process_ratings_by_record
from topic_analysis_chats import process_chat_topic_analysis
from topic_analysis_interviews import process_interview_topic_analysis
from topic_plots import create_topic_plots
from correlation_plots import create_correlation_plots

if __name__ == "__main__":
    load_dotenv("../.env")

    # Create directories if they don't exist
    directories = ["logs", "data", "plots"]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
        
    input_folder = "logs"
    output_folder = "data"
    plot_folder = "plots"
    output_file = f"{output_folder}/conversations.json"

    input_file_path = f"{output_folder}/conversations.json"
    chat_logs_path = f"{output_folder}/chat_logs.json"
    interview_logs_path = f"{output_folder}/interview_logs.json"
    csv_output_path = f"{output_folder}/conversation_quality.csv"

    api_key = os.getenv("BEDROCK_API_KEY")
    base_url = os.getenv("BEDROCK_BASE_URL")

    model = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"

    client = OpenAI(api_key=api_key, base_url=base_url)

    # 1. Compile conversations into one file
    print("CLUE-Insighter Step 1: Compile conversations into one file")
    fetch_conversations_from_folder(input_folder, output_file)

    # 2. Filter logs
    print("CLUE-Insighter Step 2: Filter logs")
    process_logs(client, model, input_file_path, chat_logs_path, interview_logs_path, csv_output_path)

    # 3. Statistics about chat and interview sessions
    print("CLUE-Insighter Step 3: Statistics about chat and interview sessions")
    process_statistics(output_folder, chat_logs_path, interview_logs_path)

    # 4. Get dimension classifications and ratings
    print("CLUE-Insighter Step 4: Get dimension classifications and ratings")
    process_classifications_and_ratings(output_folder, client, interview_logs_path, model)

    # 5. Get ratings per session
    print("CLUE-Insighter Step 5: Get ratings per session")
    process_ratings_by_record(output_folder, interview_logs_path)

    # 6. Get topic analysis of chat sessions
    print("CLUE-Insighter Step 6: Get topic analysis of chat sessions")
    process_chat_topic_analysis(chat_logs_path, output_folder)

    # 7. Get topic analysis of interview sessions
    print("CLUE-Insighter Step 7: Get topic analysis of interview sessions")
    process_interview_topic_analysis(output_folder)

    # 8. Plot topics
    print("CLUE-Insighter Step 8: Plot topics")
    create_topic_plots(f"{output_folder}/topics_*.csv")

    # 9. Plot rating correlations
    print("CLUE-Insighter Step 9: Plot rating correlations")
    create_correlation_plots(output_folder, plot_folder)

    print("CLUE-Insighter: Complete!")

