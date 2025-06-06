import os
from enum import Enum

from uagents import Agent, Context, Model
from uagents.experimental.quota import QuotaProtocol, RateLimit
from uagents_core.models import ErrorMessage

from chat_proto import chat_proto, struct_output_client_proto
from LinguisticAnalysis import generate_linguistic_analysis_report, LinguisticAnalysisRequest, LinguisticAnalysisResponse

agent = Agent(
    name='linguistic_analysis_agent',
    port=8011,
    mailbox=True,
    seed='linguistic_analysis_agent_seed'
)

proto = QuotaProtocol(
    storage_reference=agent.storage,
    name="Linguistic-Analysis-Protocol",
    version="0.1.0",
    default_rate_limit=RateLimit(window_size_minutes=60, max_requests=30),
)

@proto.on_message(
    LinguisticAnalysisRequest, replies={LinguisticAnalysisResponse, ErrorMessage}
)
async def handle_request(ctx: Context, sender: str, msg: LinguisticAnalysisRequest):
    ctx.logger.info("Received team info request")
    try:
        results = await generate_linguistic_analysis_report(msg.text)
        ctx.logger.info(f'printing results in function {results}')
        ctx.logger.info("Successfully fetched team information")
        await ctx.send(sender, LinguisticAnalysisResponse(results=results))
    except Exception as err:
        ctx.logger.error(err)
        await ctx.send(sender, ErrorMessage(error=str(err)))

agent.include(proto, publish_manifest=True)

### Health check related code
def agent_is_healthy() -> bool:
    """
    Implement the actual health check logic here.
    For example, check if the agent can connect to the AllSports API.
    """
    try:
        import asyncio
        asyncio.run(generate_linguistic_analysis_report("Artificial Intelligence"))
        return True
    except Exception:
        return False

class HealthCheck(Model):
    pass

class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"

class AgentHealth(Model):
    agent_name: str
    status: HealthStatus

health_protocol = QuotaProtocol(
    storage_reference=agent.storage, name="HealthProtocol", version="0.1.0"
)

@health_protocol.on_message(HealthCheck, replies={AgentHealth})
async def handle_health_check(ctx: Context, sender: str, msg: HealthCheck):
    status = HealthStatus.UNHEALTHY
    try:
        if agent_is_healthy():
            status = HealthStatus.HEALTHY
    except Exception as err:
        ctx.logger.error(err)
    finally:
        await ctx.send(sender, AgentHealth(agent_name="arxiv_agent", status=status))

agent.include(health_protocol, publish_manifest=True)
agent.include(chat_proto, publish_manifest=True)
agent.include(struct_output_client_proto, publish_manifest=True)

if __name__ == "__main__":
    agent.run() 
