import openai
from docx import Document
from uagents import Agent, Context, Model

# OpenAI API Key (Make sure to secure this properly)
openai.api_key = 'ley'

# Define the message model
class Message(Model):
    message: str

# Initialize the agent
my_first_agent = Agent(
    name='Feedback Agent', 
    port=4040,
    endpoint=['http://localhost:4040/submit'], 
    seed='feedback_agent_seed'
)

# Function to read content from .docx files and other text files
def read_file(file_path):
    # If it's a .docx file
    if file_path.endswith('.docx'):
        doc = Document(file_path)
        return '\n'.join([para.text for para in doc.paragraphs])
    
    # If it's a .txt file, read it normally
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# Function to generate feedback using OpenAI GPT model
def generate_feedback(resume, job_description):
    prompt = f"Compare the following resume to the job description and provide feedback on strengths, weaknesses, and areas for improvement:\n\nResume:\n{resume}\n\nJob Description:\n{job_description}\n\nFeedback:"
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Use the newer GPT-3.5 model
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message['content'].strip()

# Function to save feedback to a file
def save_feedback(feedback, output_path):
    with open(output_path, 'w') as file:
        file.write(feedback)

# Event handler for the agent's startup
@my_first_agent.on_event('startup')
async def startup_handler(ctx: Context):
    ctx.logger.info(f'My name is {ctx.agent.name} and my address is {ctx.agent.address}')
    
    # Get file paths from the user
    resume_path = input("Enter the path to the resume file (e.g., .docx): ")
    job_desc_path = input("Enter the path to the job description file (e.g., .docx): ")
    
    try:
        # Read the content of the files
        resume_content = read_file(resume_path)
        job_desc_content = read_file(job_desc_path)
        
        # Generate feedback using the OpenAI model
        feedback = generate_feedback(resume_content, job_desc_content)
        
        # Save feedback to a file
        output_file = 'feedback_report.txt'
        save_feedback(feedback, output_file)
        
        # Display feedback on the terminal
        print(f"\nFeedback Generated:\n{feedback}")
        print(f"\nFeedback saved to {output_file}")
    
    except Exception as e:
        ctx.logger.error(f"Error occurred: {e}")
        print(f"An error occurred: {e}")

# Run the agent
if __name__ == "__main__":
    my_first_agent.run()
