"""
This agent writes a greeting in the logs on startup.
"""

from uagents import Agent, Context, Model

class Request(Model):
    message: str

agent = Agent()

local_agent_address = "agent1qfj8gh0ah7ft0pwuqvh34kz542dxawgg7ks3wxupf9rtz5v4p3u6cy7zeah"

@agent.on_event("startup")
async def say_hello(ctx: Context):
    """Logs hello message on startup"""
    ctx.logger.info(f"Hello, I'm an agent and my address is {ctx.agent.address}.")
    await ctx.send(local_agent_address, Request(message = "hello i'm agentverse"))

if __name__ == "__main__":
    agent.run()
