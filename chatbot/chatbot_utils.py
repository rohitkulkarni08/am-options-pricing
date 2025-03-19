import openai
from prompts import EXTRACTION_PROMPT, FOLLOW_UP_PROMPT

openai.api_key = "your_openai_api_key"

def parse_query(user_query):
    prompt = EXTRACTION_PROMPT.format(query=user_query)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=300
    )
    content = response.choices[0].message['content']

    import json
    try:
        extracted_data = json.loads(content)
    except json.JSONDecodeError:
        print("Failed to parse JSON. Check prompt output.")
        extracted_data = {}
    return extracted_data

def generate_follow_up(extracted_data):
    prompt = FOLLOW_UP_PROMPT.format(extracted_data=extracted_data)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=300
    )
    return response.choices[0].message['content']
