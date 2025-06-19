from uagents import Agent, Context, Model
from sklearn.metrics.pairwise import cosine_similarity
import openai

openai.api_key = "key"

CLIENT_AGENT_ADDRESS = "agent1"

class FileProcessingRequest(Model):
    file_content: str  # Base64-encoded file content
    file_type: str
    job_description: str

class FileProcessingResponse(Model):
    extracted_text: str

similarity_agent = Agent(
    name='similarity_agent',
    port=5003,
    endpoint='http://localhost:5003/submit',
    seed='similarity_seed'
)

@similarity_agent.on_message(model=FileProcessingRequest)
async def handle_similarity(ctx: Context, sender: str, request: FileProcessingRequest):
    #embedding1 = openai.Embedding.create(input=request.file_content, model="text-embedding-ada-002")['data'][0]['embedding']
    #embedding2 = openai.Embedding.create(input=request.job_description, model="text-embedding-ada-002")['data'][0]['embedding']
    similarity = cosine_similarity([request.file_content], [request.job_description])[0][0]
    await ctx.send(CLIENT_AGENT_ADDRESS, FileProcessingResponse(similarity_score=similarity))

if __name__ == "__main__":
    similarity_agent.run()
