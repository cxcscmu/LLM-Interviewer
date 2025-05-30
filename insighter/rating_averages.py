#!/usr/bin/env python3
import numpy as np
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError
from dotenv import load_dotenv

from dimensions import DIMENSIONS

# Load environment variables from .env file.
load_dotenv("../.env")


@retry(stop=stop_after_attempt(10), wait=wait_exponential(multiplier=1, min=1, max=16))
def make_api_call(client, rating_prompt: str):
    """
    Calls the LLM API using client.chat.completions.create.
    This function is decorated with tenacity to automatically retry on exceptions.
    """
    return client.chat.completions.create(
        model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        messages=[
            {"role": "system", "content": "You are a UX researcher. You are an expert at summarizing insights and themes from user experience interviews."},
            {"role": "user", "content": rating_prompt},
        ],
    )

def get_rating(client, class_name: str, question: str, answer: str, confident_about: str = "the rating criteria") -> str:
    """
    Constructs the prompt and calls the LLM API to get a rating.
    Uses the make_api_call helper function which retries with exponential backoff.
    """
    action = "provide a rating on a scale of 1-3."
    rating_prompt = (
        f"Based on the following user response about {DIMENSIONS.get(class_name, 'this aspect')}, "
        f"{action} Only provide the numeric rating without any explanation. If you are not confident about {confident_about}, respond 'NaN'.\n\n"
        f"Question: {question}\n"
        f"Answer: {answer}"
    )
    
    try:
        response = make_api_call(client, rating_prompt)
        rating_text = response.choices[0].message.content.strip()
        return rating_text
    except RetryError:
        print("Maximum retry attempts reached for this API call. Returning 'NaN'.")
        return "NaN"

def parse_rating(rating_text: str) -> float:
    """
    Converts the API's returned rating into a float.
    Returns np.nan if conversion fails.
    """
    try:
        return float(rating_text)
    except ValueError:
        return np.nan
