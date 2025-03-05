import requests
import json
from uagents import Agent, Context, Model

# API Key for n8n (if necessary)
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Y2FmMzAwMy05N2QwLTRiYmYtYTg3ZS05MDU2YmRkMDhhYmUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzQwMzY1NjkzfQ.Bnm2PxvA0i2UxOiirnvvRi9P5XqHUcAo8eqggR36L7g"
WEBHOOK_URL = "http://localhost:5678/webhook/e7a841ec-135f-470d-96e7-9b6d3f432eaf"

# Define the request model (received request from another agent)
class requestForwardAgent(Model):
    query: str
    sender_address: str

# Define the response model (response to send back to the sender)
class responseForwardAgent(Model):
    result: str
    source: str

# Define the main agent that will forward requests
forwardingAgent = Agent(
    name="request_forwarding_agent",
    port=5069,
    endpoint="http://localhost:5069/submit",
    seed="forwarding_agent_seed"
)

# Function to forward the request to another agent (n8n)
def forward_request(query: str):
    """
    This function forwards the received query to the n8n webhook and returns the response.
    """
    payload = {
        "query": query
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    try:
        response = requests.post(WEBHOOK_URL, json=payload, headers=headers)
        response_data = response.json()
        #print(f'Response from n8n: {response_data["output"]}')
        print("Workflow sucessfully ran")
        
        # Return the relevant string from the n8n response
        return response_data.get("output", "No output found")
    except requests.exceptions.RequestException as e:
        return f"Error forwarding the request: {str(e)}"

# Handler for receiving requests from other agents
@forwardingAgent.on_message(model=requestForwardAgent)
async def handle_request(ctx: Context, sender: str, msg: requestForwardAgent):
    """
    This function handles the request received from another agent, forwards the query,
    and sends back the response.
    """
    ctx.logger.info(f"Received request from {sender}: {msg.query}")

    # Forward the request to n8n and get the response
    result = forward_request(msg.query)
    print(result)

    # Send the response back to the sender
    await ctx.send(sender, responseForwardAgent(result=result, source="Forwarded from n8n"))

# Start the forwarding agent
if __name__ == '__main__':
    forwardingAgent.run()
