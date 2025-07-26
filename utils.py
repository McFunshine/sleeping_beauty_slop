import json
import os
from mistralai import Mistral
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_paper_text(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
            text = file.read()
    
    return text


def read_prompt_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()
    

def load_json(file_path):
    """
    Load and return data from a JSON file.

    Parameters:
    file_path (str): The path to the JSON file.

    Returns:
    dict or list: The data loaded from the JSON file.
    """

    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data
    

def call_mistral_api(
    prompt,
    model="mistral-large-latest",
    api_key=None
):
    # Initialize the Mistral client
    client = Mistral(api_key=api_key)

    # Make the API call with the combined prompt and paper text
    chat_response = client.chat.complete(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )

    # Extract and return the response content
    return chat_response.choices[0].message.content