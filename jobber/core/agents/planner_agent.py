import os

import litellm
from dotenv import load_dotenv

from jobber.core.agents.browser_nav_agent import browser_nav_agent
from jobber.core.prompts import LLM_PROMPTS
from jobber.utils.extract_json import extract_json

load_dotenv()

messages = [
    {
        "role": "system",
        "content": LLM_PROMPTS["PLANNER_AGENT_PROMPT"],
    }
]


async def planner_agent(query: str):
    try:
        messages.append({"role": "user", "content": query})
        response = litellm.completion(
            model=os.environ["MODEL_NAME"],
            messages=messages,
        )

        response_content = response.choices[0].message.content
        extracted_response = extract_json(response_content)
        print("planner response", extracted_response)
        print("planner response", response)

        if extracted_response.get("terminate") == "yes":
            print("final response", extracted_response.get("final_response"))
        elif extracted_response.get("next_step"):
            await browser_nav_agent(extracted_response["next_step"])

    except Exception as e:
        print(f"Error occurred: {e}")
