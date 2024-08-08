from string import Template

from jobber.core.agents.base import BaseAgent
from jobber.core.agents.browser_nav_agent import BrowserNavAgent
from jobber.core.memory import ltm
from jobber.core.prompts import LLM_PROMPTS


class PlannerAgent(BaseAgent):
    def __init__(self):
        ltm = self.__get_ltm()
        system_prompt: str = LLM_PROMPTS["PLANNER_AGENT_PROMPT"]

        # Add useer ltm to system prompt
        ltm = "\n" + ltm
        system_prompt = Template(system_prompt).substitute(basic_user_information=ltm)

        super().__init__(system_prompt=system_prompt)
        self.browser_agent = BrowserNavAgent(self)

    async def process_query(self, query: str):
        response = await super().process_query(query)

        while not response["terminate"]:
            browser_response = await self.browser_agent.process_query(
                response["content"]
            )

            if browser_response["terminate"]:
                self.messages.append(
                    {"role": "assistant", "content": browser_response["content"]}
                )
                response = await self.generate_reply([], None)
            else:
                self.messages.append(
                    {
                        "role": "assistant",
                        "content": f"Browser agent response: {browser_response['content']}",
                    }
                )
                response = await self.generate_reply([], None)

        return response["content"]

    async def receive_browser_message(self, message: str):
        return await self.generate_reply(
            [{"role": "user", "content": message}], self.browser_agent
        )

    def __get_ltm(self):
        return ltm.get_user_ltm()
