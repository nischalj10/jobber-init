from datetime import datetime
from string import Template
from typing import Any, Callable, Dict, List, Optional

from ae.core.memory.static_ltm import get_user_ltm
from ae.core.post_process_responses import (
    final_reply_callback_planner_agent as print_message_as_planner,
)

from jobber.core.prompts import LLM_PROMPTS
from jobber.core.skills.get_user_input import get_user_input


class PlannerAgent:
    def __init__(self, config_list: List[Dict[str, Any]], user_proxy_agent):
        """
        Initialize the PlannerAgent.

        Parameters:
        - config_list: A list of configuration parameters required for the agent.
        - user_proxy_agent: An instance of the UserProxyAgent class.
        """
        self.name = "planner_agent"
        self.config_list = config_list
        self.user_proxy_agent = user_proxy_agent
        self.llm_config = {
            "config_list": config_list,
            "cache_seed": None,
            "temperature": 0.0,
            "top_p": 0.001,
            "seed": 12345,
        }

        user_ltm = self.__get_ltm()
        system_message = LLM_PROMPTS["PLANNER_AGENT_PROMPT"]

        if user_ltm:
            user_ltm = "\n" + user_ltm
            system_message = Template(system_message).substitute(
                basic_user_information=user_ltm
            )

        system_message = (
            system_message
            + "\n"
            + f"Today's date is {datetime.now().strftime('%d %B %Y')}"
        )
        self.system_message = system_message

        self.function_map = {}
        self.register_function(get_user_input, LLM_PROMPTS["GET_USER_INPUT_PROMPT"])
        user_proxy_agent.register_function({get_user_input.__name__: get_user_input})

        self.reply_func_list = [
            {
                "trigger": [PlannerAgent, None],
                "reply_func": print_message_as_planner,
                "config": {"callback": None},
            }
        ]

    def __get_ltm(self) -> Optional[str]:
        """
        Get the long term memory of the user.
        Returns: str | None - The user LTM or None if not found.
        """
        return get_user_ltm()

    def register_function(self, func: Callable, description: str):
        """
        Register a function to be used by the agent.

        Parameters:
        - func: The function to be registered.
        - description: A description of the function.
        """
        self.function_map[func.__name__] = {
            "function": func,
            "description": description,
        }

    def generate_reply(self, messages: List[Dict[str, Any]], sender) -> str:
        """
        Generate a reply based on the conversation history.

        Parameters:
        - messages: A list of message dictionaries representing the conversation history.
        - sender: The sender of the last message.

        Returns:
        - A string containing the generated reply.
        """
        # This is a placeholder. In a real implementation, you would use an LLM to generate the reply.
        # You would need to implement the logic to use the system message, conversation history,
        # and registered functions to generate an appropriate response.
        return "This is a placeholder response from the PlannerAgent."

    def send(self, message: str, recipient):
        """
        Send a message to another agent.

        Parameters:
        - message: The message to be sent.
        - recipient: The recipient agent.
        """
        recipient.receive(message, self)

    def receive(self, message: str, sender):
        """
        Receive a message from another agent and generate a reply.

        Parameters:
        - message: The received message.
        - sender: The sender of the message.
        """
        reply = self.generate_reply([{"role": "user", "content": message}], sender)
        self.send(reply, sender)

    def execute_function(self, func_name: str, **kwargs) -> Any:
        """
        Execute a registered function.

        Parameters:
        - func_name: The name of the function to execute.
        - **kwargs: The arguments to pass to the function.

        Returns:
        - The result of the function execution.
        """
        if func_name in self.function_map:
            return self.function_map[func_name]["function"](**kwargs)
        else:
            raise ValueError(f"Function {func_name} is not registered.")
