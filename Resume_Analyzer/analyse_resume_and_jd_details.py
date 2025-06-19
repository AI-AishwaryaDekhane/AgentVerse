import json
import openai
from uagents import Agent, Context, Model

openai.api_key = "key"

EMBEDDING_AGENT_ADDRESS = "address"

# Define Models
class FileProcessingRequest(Model):
    file_content: str  # Base64-encoded file content
    file_type: str
    job_description: str
    jd_type: str

class FileProcessingResponse(Model):
    extracted_text: str
    similarity:float

# Define the embedding agent
embedding_agent = Agent(
    name="analysis_agent",
    port=5042,
    #endpoint="http://localhost:5042/submit",
    seed="analysis_seed",
    mailbox= True
)

# This is the function where we analyze the resume
def analyze_resume_details(text: str, job_desc: str) -> dict:
    """Analyze resume text and provide actionable feedback."""
    try:
        prompt = f"""Please analyze the following resume text and provide insights in the following categories:
        - Skills
        - Experience
        - Education
        - Domain expertise
        - Certifications

        Additionally, provide actionable feedback on how the candidate can improve their resume to better match the following job description:

        Job Description: {job_desc}

        Resume Text: {text}

        Provide the analysis in valid JSON format with these exact keys: skills, experience, education, domain, certifications, feedback"""
        
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a resume analysis expert. Respond only with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9
        )
        
        # Get the response and ensure it's valid JSON
        content = response['choices'][0]['message']['content'].strip()
        if not content.startswith('{'):  # Fix for common GPT formatting issues
            content = content[content.find('{'):content.rfind('}')+1]
        return json.loads(content)
    except Exception as e:
        return {
            "skills": "",
            "experience": "",
            "education": "",
            "domain": "",
            "certifications": "",
            "feedback": "Unable to generate feedback due to an error."
        }

# Define the behavior when a message is received by this agent
@embedding_agent.on_message(model=FileProcessingRequest)
async def handle_resume_analysis(ctx: Context, sender: str, request: FileProcessingRequest):
    print(f"[Resume Analysis Agent] Analyzing resume: {request.file_content[:100]}...")

    # Analyze the resume text with the provided job description
    resume_analysis_result = analyze_resume_details(request.file_content, request.job_description)
    
    # Convert the analysis result to a JSON string
    resume_analysis_result_str = json.dumps(resume_analysis_result)
    print(resume_analysis_result_str)
    print('-' * 100)

    # Analyze the resume text with the provided job description
    jd_analysis_result = analyze_resume_details(request.job_description, request.job_description)
    
    # Convert the analysis result to a JSON string
    jd_analysis_result_str = json.dumps(jd_analysis_result)
    print(jd_analysis_result_str)
    print('-' * 100)

    # Send the analysis result as a string (JSON formatted)
    await ctx.send(EMBEDDING_AGENT_ADDRESS, FileProcessingRequest(file_type=request.file_type, 
                                                                   file_content=resume_analysis_result_str, 
                                                                   job_description=jd_analysis_result_str,
                                                                   jd_type=request.jd_type))

if __name__ == "__main__":
    # Run the agent
    embedding_agent.run()
