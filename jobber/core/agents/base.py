import json
from typing import Any, Callable, Dict, List, Optional, Tuple

import litellm
import openai
from dotenv import load_dotenv

from jobber.utils.extract_json import extract_json
from jobber.utils.function_utils import get_function_schema


class BaseAgent:
    def __init__(
        self,
        system_prompt: str = "You are a helpful assistant",
        tools: Optional[List[Tuple[Callable, str]]] = None,
    ):
        load_dotenv()
        self.name = self.__class__.__name__
        self.messages = [{"role": "system", "content": system_prompt}]
        self.tools_list = []
        self.executable_functions_list = {}
        self.llm_config = {"model": "anthropic.claude-3-5-sonnet-20240620-v1:0"}
        if tools:
            self._initialize_tools(tools)
            self.llm_config.update({"tools": self.tools_list, "tool_choice": "auto"})
        print("model", self.llm_config)

    def _initialize_tools(self, tools: List[Tuple[Callable, str]]):
        for function, description in tools:
            self.tools_list.append(
                get_function_schema(function, description=description)
            )
            self.executable_functions_list[function.__name__] = function

    async def generate_reply(
        self, messages: List[Dict[str, Any]], sender
    ) -> Dict[str, Any]:
        self.messages.extend(messages)

        while True:
            litellm.logging = False
            litellm.success_callback = ["langsmith"]

            try:
                response = litellm.completion(
                    messages=self.messages,
                    **self.llm_config,
                    metadata={
                        "run_name": f"{self.name}Run",
                    },
                )
            except openai.BadRequestError as e:
                should_retry = litellm._should_retry(e.status_code)
                print(f"should_retry: {should_retry}")

            response_message = response.choices[0].message
            print("response", response_message)
            tool_calls = response_message.tool_calls

            if tool_calls:
                self.messages.append(response_message)
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_to_call = self.executable_functions_list[function_name]
                    function_args = json.loads(tool_call.function.arguments)
                    function_response = await function_to_call(**function_args)
                    self.messages.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": str(function_response),
                        }
                    )
                continue

            print("uiewbeiu")

            content = response_message.content
            if "##TERMINATE TASK##" in content or "## TERMINATE TASK ##" in content:
                return {
                    "terminate": True,
                    "content": content,
                }
            else:
                extracted_response = extract_json(content)
                print("lovely", extracted_response)
                if extracted_response.get("terminate") == "yes":
                    print("should terminate now")
                    return {
                        "terminate": True,
                        "content": extracted_response.get("final_response"),
                    }
                else:
                    print("retunring next step")
                    return {
                        "terminate": False,
                        "content": extracted_response.get("next_step"),
                    }

    def send(self, message: str, recipient):
        return recipient.receive(message, self)

    async def receive(self, message: str, sender):
        reply = await self.generate_reply(
            [{"role": "assistant", "content": message}], sender
        )
        return self.send(reply["content"], sender)

    async def process_query(self, query: str) -> Dict[str, Any]:
        try:
            return await self.generate_reply([{"role": "user", "content": query}], None)
        except Exception as e:
            print(f"Error occurred: {e}")
            return {"terminate": True, "content": f"Error: {str(e)}"}

    def reset_messages(self):
        self.messages = [self.messages[0]]  # Keep the system message
