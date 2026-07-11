from openai import OpenAI
from env_vars import openai_api_key, openai_org_id, openai_project

client = OpenAI(api_key=openai_api_key, organization=openai_org_id, project=openai_project)

messages=[
    {"role": "system", "content": "You are a precise technical writer."},
]