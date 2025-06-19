from uagents import Agent, Context, Model
import json

# Define the similarity agent address
SIMILARITY_AGENT_ADDRESS = "agent1q0fdgc2yptwtvf90p8jhujh37qslr9d9xjwkufrpx8k65pw3ak5zgqyp54z"

# Define models for receiving responses
class AnalysisResponse(Model):
    extracted_text: str
    similarity: float

# SDK Agent for handling responses
sdk_agent_2 = Agent(
    name="sdk_response_handler",
    port=6001,
    endpoint="http://localhost:6001/submit",
    seed="sdk_response_seed"
)

@sdk_agent_2.on_message(model=AnalysisResponse)
async def handle_analysis_response(ctx: Context, sender: str, response: AnalysisResponse):
    print(f"[SDK Response Agent] Received similarity score: {response.similarity}")
    
    # Forward the result to the user
    print(f"Final Processed Resume Analysis: {json.dumps(response.dict(), indent=4)}")

if __name__ == "__main__":
    sdk_agent_2.run()
