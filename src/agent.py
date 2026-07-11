import sys
from openai import OpenAIError
from config import client, messages
from env_vars import model

def agent_ask(user_content):
    messages.append(
        {"role": "user", "content": user_content},
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
        )
    except OpenAIError as e:
        print(f"::error:: OpenAI API request failed: {e}.")
        sys.exit(1)

    return response.choices[0].message.content.strip()