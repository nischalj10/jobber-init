import json
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

# all functions that we sent to the LLM will be available for execution as well unlike autogen where you have to separetly register for llm and execution
executable_functions = {func.__name__: func for func, _ in functions}


async def browser_nav_agent(query: str):
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
        print("navigator agent response", response)

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        # Step 2: check if the model wanted to call a function
        if tool_calls:
            # Step 3: call the function
            # Note: the JSON response may not always be valid; be sure to handle errors
            available_functions = executable_functions
            messages.append(
                response_message
            )  # extend conversation with assistant's reply

            # Step 4: send the info for each function call and function response to the model
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)
                # TODO handle both async and sync function
                function_response = await function_to_call(**function_args)
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": str(function_response),
                    }
                )  # extend conversation with function response
            second_response = litellm.completion(
                model=os.environ["MODEL_NAME"],
                messages=messages,
            )  # get a new response from the model where it can see the function response
            print("\nSecond LLM response:\n", second_response)
            return second_response

    except Exception as e:
        print(f"Error occurred: {e}")


# # Use asyncio to run the async function
# asyncio.run(browser_nav_agent("go to amazon.in"))
