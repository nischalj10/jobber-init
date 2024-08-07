from jobber.core.agents.base import BaseAgent
from jobber.core.agents.browser_nav_agent import BrowserNavAgent
from jobber.core.prompts import LLM_PROMPTS


class PlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__(system_prompt=LLM_PROMPTS["PLANNER_AGENT_PROMPT"])
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
                        "role": "user",
                        "content": f"Browser agent response: {browser_response['content']}",
                    }
                )
                response = await self.generate_reply([], None)

        return response["content"]

    async def receive_browser_message(self, message: str):
        return await self.generate_reply(
            [{"role": "user", "content": message}], self.browser_agent
        )
