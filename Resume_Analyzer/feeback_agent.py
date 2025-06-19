import os
import base64
import openai
from uagents import Agent, Context, Model

# Address of the client agent (File Processing Agent)
CLIENT_AGENT_ADDRESS = "agent1"

# OpenAI API Key (Make sure this is securely stored)
OPENAI_API_KEY = "key"

# Define request and response models
class FileProcessingRequest(Model):
    file_content: str  # Base64-encoded file content
    file_type: str
    job_description: str
    jd_type: str

class FileProcessingResponse(Model):
    extracted_text: str
    similarity: float

# Define the feedback agent
feedback_agent = Agent(
    name="feedback_agent",
    port=5070,
    #endpoint="http://localhost:5070/submit",
    seed="feedback_agent_seed",
    mailbox=True
)

@feedback_agent.on_event("startup")
async def request_files(ctx: Context):
    """Requests resume and job description files from the client agent."""
    print("\nRequesting resume and job description files from client agent...\n")
    await ctx.send(CLIENT_AGENT_ADDRESS, FileProcessingRequest(
        file_content="", file_type="", job_description="", jd_type=""
    ))
    print("\nReceived resume and job description files from client agent...\n")

@feedback_agent.on_message(model=FileProcessingResponse)
async def generate_feedback(ctx: Context, sender: str, msg: FileProcessingResponse):
    """Receives extracted resume and job description text, then generates feedback."""
    
    print("\nReceived extracted text from client agent. Generating feedback...\n")
    
    resume_text = msg.extracted_text
    similarity_score = msg.similarity

    # Generate feedback using OpenAI GPT
    openai.api_key = OPENAI_API_KEY
    prompt = f"""
    You are an HR expert analyzing a resume against a job description.

    Resume:
    {resume_text}

    Based on the resume, provide:
    - A summary of how well the resume matches the job.
    - Strengths in the resume.
    - Weaknesses or gaps.
    - Recommendations for improvement.

    Also, mention the similarity score: {similarity_score}.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )

    feedback = response["choices"][0]["message"]["content"]

    # Save feedback to a text file
    feedback_file = "feedback_report.txt"
    with open(feedback_file, "w") as file:
        file.write(feedback)

    # Print output on terminal
    print("\n===== Resume Feedback =====\n")
    print(feedback)
    print("\nFeedback has been saved in 'feedback_report.txt'\n")

if __name__ == "__main__":
    feedback_agent.run()
