from uagents import Agent, Context, Model
#import fitz  # PyMuPDF
import docx
import os
import tempfile
import base64  # Required for decoding binary data
from starlette.staticfiles import StaticFiles
import os

ANALYSIS_AGENT_ADDRESS = "agent1qwps5fs7k46fgd9uuhdrvdqjuzqsn44nawlhfssc3fq6hghquctdcllttpk"

class FileProcessingRequest(Model):
    file_content: str  # Base64-encoded file content
    file_type: str
    job_description: str
    jd_type: str

class FileProcessingResponse(Model):
    extracted_text: str
    similarity:float

file_processing_agent = Agent(
    name="file_processing_agent",
    port=5001,
    #endpoint="http://localhost:5001/submit",
    seed="file_processing_seed",
    mailbox= True
)

@file_processing_agent.on_message(model=FileProcessingRequest)
async def handle_file_processing(ctx: Context, sender: str, request: FileProcessingRequest):
    try:
        file_bytes = base64.b64decode(request.file_content)  # Decode Base64 to bytes
        file_bytes_jd = base64.b64decode(request.job_description)  # Decode Base64 to bytes

        # def extract_text_from_pdf(content):
        #     with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        #         tmp_file.write(content)
        #         tmp_file.flush()
        #         doc = fitz.open(tmp_file.name)
        #         text = " ".join([page.get_text("text") for page in doc])
        #         doc.close()
        #         os.unlink(tmp_file.name)
        #         return text

        def extract_text_from_docx(content):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_file:
                tmp_file.write(content)
                tmp_file.flush()
                doc = docx.Document(tmp_file.name)
                os.unlink(tmp_file.name)
                return "\n".join([para.text for para in doc.paragraphs])

        extracted_text_resume = ""
        print(request.file_type)
        if request.file_type == "application/pdf":
            print("extracting pdf")
            #extracted_text_resume = extract_text_from_pdf(file_bytes)
        elif request.file_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
            extracted_text_resume = extract_text_from_docx(file_bytes)
        else:
            ctx.logger.error("Unsupported file format.")
            return
        
        extracted_text_jd = ""
        print(request.jd_type)
        if request.jd_type == "application/pdf":
            print("extracting pdf")
            #extracted_text_jd = extract_text_from_pdf(file_bytes_jd)
        elif request.jd_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
            print("extracting docx")
            extracted_text_jd = extract_text_from_docx(file_bytes_jd)
        else:
            ctx.logger.error("Unsupported file format.")
            return
        print('=' * 100)
        print('JOB Description')
        print(extracted_text_jd)
        print('=' * 100)
        print('RESUME')
        print(extracted_text_jd)
        print('=' * 100)
        # Now we send only the resume's extracted text along with the job description to the embedding agent
        request = FileProcessingRequest(
            file_type=request.file_type, 
            file_content=extracted_text_resume,  # extracted text from resume
            job_description=extracted_text_jd,  # job description remains unchanged
            jd_type=request.jd_type
        )
        # Send the request to the embedding agent
        await ctx.send(ANALYSIS_AGENT_ADDRESS, request)

    except Exception as e:
        ctx.logger.error(f"Error processing file: {str(e)}")

if __name__ == "__main__":
    file_processing_agent.run()
