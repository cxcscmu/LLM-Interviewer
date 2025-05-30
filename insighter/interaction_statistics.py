import json
import csv
from datetime import datetime
from collections import defaultdict

def compute_time_difference(start_time, end_time):
    """
    Simple utility function to compute the time difference from two strings.
    """
    start = datetime.fromisoformat(start_time.strip("Z"))
    end = datetime.fromisoformat(end_time.strip("Z"))
    return (end - start).total_seconds()

def compute_tokens(text):
    """
    Compute tokens as the number of words.
    """
    return len(text.split())

def compute_message_tokens(content):
    """
    Compute tokens for a message.
    """
    if isinstance(content, list):
        total_tokens = sum(compute_tokens(part['text']) if isinstance(part, dict) and 'text' in part else compute_tokens(part) for part in content if isinstance(part, (str, dict)))
        return total_tokens
    elif isinstance(content, str):
        return compute_tokens(content)
    return 0

def compute_rounds(session, role1, role2):
    """
    Compute the number of rounds for a given session.
    """
    count = 0
    prev_role = None
    for message in session:
        if prev_role == role1 and message.get('role') == role2:
            count += 1
        prev_role = message.get('role')
    return count

def compute_session_statistics(session_data):
    """
    Compute chat statistics.
    """
    session = session_data.get("session", [])
    session_start = session_data.get("session_start")
    session_end = session_data.get("session_end")
    session_model = session_data.get("session_model", "unknown")

    if not session:
        return {"session_model": session_model, "rounds": 0, "user_tokens": 0, "assistant_tokens": 0, "engagement_time": 0}

    user_tokens = sum(compute_message_tokens(msg['content']) for msg in session if msg.get('role') == 'user')
    assistant_tokens = sum(compute_message_tokens(msg['content']) for msg in session if msg.get('role') == 'assistant')
    engagement_time = compute_time_difference(session_start, session_end) if session_start and session_end else 0
    rounds = compute_rounds(session, 'user', 'assistant')

    return {"session_model": session_model, "rounds": rounds, "user_tokens": user_tokens, "assistant_tokens": assistant_tokens, "engagement_time": engagement_time}

def compute_interview_statistics(interview_data):
    """
    Compute interview statistics.
    """
    interview = interview_data.get("interview", [])
    session_model = interview_data.get("session_model", "unknown")

    if not interview:
        return {"session_model": session_model, "rounds": 0, "user_tokens": 0, "assistant_tokens": 0, "engagement_time": 0, "session_model": session_model}

    user_tokens = sum(compute_message_tokens(msg['content']) for msg in interview if msg.get('role') == 'user')
    assistant_tokens = sum(compute_message_tokens(msg['content']) for msg in interview if msg.get('role') == 'assistant')
    engagement_time = compute_time_difference(interview_data.get("interview_start"), interview_data.get("interview_end")) if interview_data.get("interview_start") and interview_data.get("interview_end") else 0
    rounds = compute_rounds(interview, 'assistant', 'user')

    return {"rounds": rounds, "user_tokens": user_tokens, "assistant_tokens": assistant_tokens, "engagement_time": engagement_time, "session_model": session_model}

def process_statistics(output_folder, chat_logs_file, interview_logs_file):
    """
    Compute chat and interview statistics.
    """
    with open(chat_logs_file, 'r', encoding='utf-8') as chat_file:
        chat_logs = json.load(chat_file)
    with open(interview_logs_file, 'r', encoding='utf-8') as interview_file:
        interview_logs = json.load(interview_file)

    chat_stats = []
    interview_stats = []
    chat_aggregates = defaultdict(lambda: {"rounds": 0, "user_tokens": 0, "assistant_tokens": 0, "engagement_time": 0, "count": 0})
    interview_aggregates = defaultdict(lambda: {"rounds": 0, "user_tokens": 0, "assistant_tokens": 0, "engagement_time": 0, "count": 0})

    overall_chat = {"rounds": 0, "user_tokens": 0, "assistant_tokens": 0, "engagement_time": 0, "count": 0}
    overall_interview = {"rounds": 0, "user_tokens": 0, "assistant_tokens": 0, "engagement_time": 0, "count": 0}

    for chat_log in chat_logs:
        chat_statistics = compute_session_statistics(chat_log)
        chat_stats.append(chat_statistics)
        model = chat_statistics["session_model"]
        for key in chat_statistics:
            if key != "session_model":
                chat_aggregates[model][key] += chat_statistics[key]
                overall_chat[key] += chat_statistics[key]
        chat_aggregates[model]["count"] += 1
        overall_chat["count"] += 1

    with open(f"{output_folder}/chat_model_aggregates.csv", "w", newline="", encoding="utf-8") as chat_aggregate_csv:
        writer = csv.DictWriter(chat_aggregate_csv, fieldnames=["session_model", "number_of_chats", "average_rounds", "average_user_tokens", "average_assistant_tokens", "average_engagement_time"])
        writer.writeheader()
        for model, stats in chat_aggregates.items():
            count = stats["count"]
            writer.writerow({
                "session_model": model,
                "number_of_chats": count,
                "average_rounds": stats["rounds"] / count if count > 0 else 0,
                "average_user_tokens": stats["user_tokens"] / count if count > 0 else 0,
                "average_assistant_tokens": stats["assistant_tokens"] / count if count > 0 else 0,
                "average_engagement_time": stats["engagement_time"] / count if count > 0 else 0
            })
        writer.writerow({
            "session_model": "Overall",
            "number_of_chats": overall_chat["count"],
            "average_rounds": overall_chat["rounds"] / overall_chat["count"] if overall_chat["count"] > 0 else 0,
            "average_user_tokens": overall_chat["user_tokens"] / overall_chat["count"] if overall_chat["count"] > 0 else 0,
            "average_assistant_tokens": overall_chat["assistant_tokens"] / overall_chat["count"] if overall_chat["count"] > 0 else 0,
            "average_engagement_time": overall_chat["engagement_time"] / overall_chat["count"] if overall_chat["count"] > 0 else 0
        })
    print("Chat statistics saved successfully.")

    for interview_log in interview_logs:
        interview_statistics = compute_interview_statistics(interview_log)
        interview_stats.append(interview_statistics)
        model = interview_statistics["session_model"]
        for key in interview_statistics:
            if key != "session_model":
                interview_aggregates[model][key] += interview_statistics[key]
                overall_interview[key] += interview_statistics[key]
        interview_aggregates[model]["count"] += 1
        overall_interview["count"] += 1

    with open(f"{output_folder}/interview_model_aggregates.csv", "w", newline="", encoding="utf-8") as interview_aggregate_csv:
        writer = csv.DictWriter(interview_aggregate_csv, fieldnames=["session_model", "number_of_interviews", "average_rounds", "average_user_tokens", "average_assistant_tokens", "average_engagement_time"])
        writer.writeheader()
        for model, stats in interview_aggregates.items():
            count = stats["count"]
            writer.writerow({
                "session_model": model,
                "number_of_interviews": count,
                "average_rounds": stats["rounds"] / count if count > 0 else 0,
                "average_user_tokens": stats["user_tokens"] / count if count > 0 else 0,
                "average_assistant_tokens": stats["assistant_tokens"] / count if count > 0 else 0,
                "average_engagement_time": stats["engagement_time"] / count if count > 0 else 0
            })
        writer.writerow({
            "session_model": "Overall",
            "number_of_interviews": overall_interview["count"],
            "average_rounds": overall_interview["rounds"] / overall_interview["count"] if overall_interview["count"] > 0 else 0,
            "average_user_tokens": overall_interview["user_tokens"] / overall_interview["count"] if overall_interview["count"] > 0 else 0,
            "average_assistant_tokens": overall_interview["assistant_tokens"] / overall_interview["count"] if overall_interview["count"] > 0 else 0,
            "average_engagement_time": overall_interview["engagement_time"] / overall_interview["count"] if overall_interview["count"] > 0 else 0
        })
    print("Interview statistics saved successfully.")

if __name__ == "__main__":
    output_folder = "data"
    chat_logs_path = f"{output_folder}/chat_logs.json"
    interview_logs_path = f"{output_folder}/interview_logs.json"
    process_statistics(output_folder, chat_logs_path, interview_logs_path)
