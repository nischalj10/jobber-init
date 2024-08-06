import os

import litellm
from dotenv import load_dotenv

from jobber.core.prompts import LLM_PROMPTS
from jobber.core.skills.enter_text_using_selector import bulk_enter_text, entertext
from jobber.core.skills.get_dom_with_content_type import get_dom_with_content_type
from jobber.core.skills.get_url import geturl
from jobber.core.skills.open_url import openurl
from jobber.core.skills.pdf_text_extractor import extract_text_from_pdf
from jobber.utils.function_utils import get_function_schema

load_dotenv()

messages = [
    {
        "role": "system",
        "content": LLM_PROMPTS["BROWSER_AGENT_PROMPT"],
    }
]

tools = []
functions = [
    (bulk_enter_text, LLM_PROMPTS["BULK_ENTER_TEXT_PROMPT"]),
    (entertext, LLM_PROMPTS["ENTER_TEXT_PROMPT"]),
    (get_dom_with_content_type, LLM_PROMPTS["GET_DOM_WITH_CONTENT_TYPE_PROMPT"]),
    (geturl, LLM_PROMPTS["GET_URL_PROMPT"]),
    (openurl, LLM_PROMPTS["OPEN_URL_PROMPT"]),
    (extract_text_from_pdf, LLM_PROMPTS["EXTRACT_TEXT_FROM_PDF_PROMPT"]),
]


def browser_nav_agent(query: str):
    try:
        messages.append({"role": "user", "content": query})

        for function, description in functions:
            tools.append(get_function_schema(function, description=description))

        response = litellm.completion(
            model=os.environ["MODEL_NAME"],
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        print("\nFirst LLM Response:\n", response)
        # print("JSON", extract_json(response.choices[0].message.content))
    except Exception as e:
        print(f"Error occurred: {e}")


browser_nav_agent("Go to www.amazon.com.")
