from uagents import Agent, Context, Model
import json

# Define the existing resume analysis agent address
RESUME_ANALYSIS_AGENT_ADDRESS = "agent1qdjckrv66ks5pm9g0mu8a2allgjyerxrwa7vmm5k6vgfy7f9rhq8u4l0t7f"

# Define models for sending requests and receiving responses
class UserRequest(Model):
    file_content: str  # Base64-encoded resume content
    file_type: str
    job_description: str
    jd_type: str

class AnalysisResponse(Model):
    extracted_text: str
    similarity: float

# SDK Agent for handling user requests
sdk_agent_1 = Agent(
    name="sdk_request_handler",
    port=6000,
    endpoint="http://localhost:6000/submit",
    seed="sdk_request_seed"
)

@sdk_agent_1.on_message(model=UserRequest)
async def handle_user_request(ctx: Context, sender: str, request: UserRequest):
    print(f"[SDK Agent] Received user request, forwarding to resume analysis agent...")

    # Forward request to the resume analysis agent
    await ctx.send(RESUME_ANALYSIS_AGENT_ADDRESS, request)

if __name__ == "__main__":
    sdk_agent_1.run()
