import os

import litellm
from dotenv import load_dotenv

from jobber.core.prompts import LLM_PROMPTS
from jobber.utils.extract_json import extract_json

load_dotenv()

messages = [
    {
        "role": "system",
        "content": LLM_PROMPTS["PLANNER_AGENT_PROMPT"],
    }
]


def planner_agent(query: str):
    try:
        messages.append({"role": "user", "content": query})
        response = litellm.completion(
            model=os.environ["MODEL_NAME"],
            messages=messages,
        )
        # print("\nFirst LLM Response:\n", response.choices[0].message.content)
        # print("JSON", extract_json(response.choices[0].message.content))

        response = extract_json(response.choices[0].message.content)

    except Exception as e:
        print(f"Error occurred: {e}")


planner_agent(
    "Task: Go to amazon and get order the book Zero to one using COD and my default address. Current page: www.google.com"
)
