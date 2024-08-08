from string import Template
from typing import Any, Dict

from jobber.core.agents.base import BaseAgent
from jobber.core.memory import ltm
from jobber.core.prompts import LLM_PROMPTS
from jobber.core.skills.enter_text_using_selector import bulk_enter_text, entertext
from jobber.core.skills.get_dom_with_content_type import get_dom_with_content_type
from jobber.core.skills.get_url import geturl
from jobber.core.skills.open_url import openurl
from jobber.core.skills.pdf_text_extractor import extract_text_from_pdf


class BrowserNavAgent(BaseAgent):
    def __init__(self, planner_agent: BaseAgent):
        ltm = self.__get_ltm()
        system_prompt = LLM_PROMPTS["BROWSER_AGENT_PROMPT"]

        # Add user ltm to system prompt
        ltm = "\n" + ltm
        system_prompt = Template(system_prompt).substitute(basic_user_information=ltm)

        super().__init__(
            system_prompt=system_prompt,
            tools=[
                (bulk_enter_text, LLM_PROMPTS["BULK_ENTER_TEXT_PROMPT"]),
                (entertext, LLM_PROMPTS["ENTER_TEXT_PROMPT"]),
                (
                    get_dom_with_content_type,
                    LLM_PROMPTS["GET_DOM_WITH_CONTENT_TYPE_PROMPT"],
                ),
                (geturl, LLM_PROMPTS["GET_URL_PROMPT"]),
                (openurl, LLM_PROMPTS["OPEN_URL_PROMPT"]),
                (extract_text_from_pdf, LLM_PROMPTS["EXTRACT_TEXT_FROM_PDF_PROMPT"]),
            ],
        )
        self.planner_agent = planner_agent

    async def process_query(self, query: str) -> Dict[str, Any]:
        response = await super().process_query(query)

        if "##TERMINATE TASK##" in response["content"]:
            print("terminating navigator - task accoplished")
            message_for_planner = (
                response["content"].replace("##TERMINATE TASK##", "").strip()
            )
            self.reset_messages()  # Call the method to reset messages
            return await self.planner_agent.receive_browser_message(message_for_planner)

        return response

    def __get_ltm(self):
        return ltm.get_user_ltm()
