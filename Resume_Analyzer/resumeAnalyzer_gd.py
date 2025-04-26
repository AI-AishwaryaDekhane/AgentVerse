import os
import json
import base64
import tempfile
import docx
import fitz  # PyMuPDF
import re
import numpy as np
from typing import List, Dict, Tuple
from sklearn.metrics.pairwise import cosine_similarity
from uagents import Agent, Context, Model
from google.generativeai import GenerativeModel, embed_content
import google.generativeai as genai
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# === Setup Gemini API ===
GEMINI_API_KEY = 'key'
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = GenerativeModel("gemini-2.0-flash")

# === Setup Google Drive ===
SERVICE_ACCOUNT_FILE = 'path'
#FOLDER_ID = '1b-hJQB2z-xTR7zPAXgDqvSkr1TjNmYC7'
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)

# === Job Description ===
JOB_DESCRIPTION = """ 
About the job
... (your full job description goes here)
"""

class FileProcessingRequest(Model):
    pdf_folder_id: str

class FileProcessingResponse(Model):
    results: str

# === Google Drive PDF Extract ===
def list_pdf_files(folder_id):
    query = f"'{folder_id}' in parents and mimeType='application/pdf'"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    return results.get('files', [])

# === File Text Extraction ===
def extract_text_from_pdf(file_content: bytes) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(file_content)
        tmp_file.flush()
        doc = fitz.open(tmp_file.name)
        text = " ".join([page.get_text("text") for page in doc])
        doc.close()
    os.unlink(tmp_file.name)
    return text

def extract_text(file_path: str) -> str:
    with open(file_path, "rb") as file:
        file_content = file.read()
    return extract_text_from_pdf(file_content)

# === Preprocess ===
def preprocess_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s]", "", text)
    return text.lower().strip()

# === Embedding ===
def get_embeddings(text: str) -> List[float]:
    try:
        result = embed_content(model="models/embedding-001", content=text, task_type="retrieval_document")
        return result["embedding"]
    except Exception as e:
        print(f"Embedding error: {e}")
        return [0.0] * 768

# === Semantic Similarity ===
def calculate_semantic_similarity(text1: str, text2: str) -> float:
    emb1 = get_embeddings(preprocess_text(text1))
    emb2 = get_embeddings(preprocess_text(text2))
    return cosine_similarity([emb1], [emb2])[0][0]

# === Gemini Resume Analysis ===
def analyze_resume_details(text: str, job_desc: str) -> Dict:
    try:
        prompt = f"""
        You are a resume analysis expert. Respond only with valid JSON.
        Analyze the following resume text and provide:
        - Skills
        - Experience
        - Education
        - Domain expertise
        - Certifications
        - Feedback to improve matching with this job: {job_desc}

        Resume Text: {text}
        """
        response = gemini_model.generate_content(prompt)
        content = response.text.strip()
        if not content.startswith('{'):
            content = content[content.find('{'):content.rfind('}')+1]
        return json.loads(content)
    except Exception as e:
        print(f"Gemini Error: {e}")
        return {
            "skills": "",
            "experience": "",
            "education": "",
            "domain": "",
            "certifications": "",
            "feedback": "Error generating analysis"
        }

# === Match Score Calculation ===
def calculate_match_score(resume_text: str, job_desc: str) -> Tuple[Dict[str, float], float, str]:
    weights = {
        'skills': 0.35,
        'experience': 0.25,
        'education': 0.15,
        'domain': 0.15,
        'certifications': 0.10
    }
    try:
        resume_analysis = analyze_resume_details(resume_text, job_desc)
        job_analysis = analyze_resume_details(job_desc, job_desc)
        scores = {}
        for cat, weight in weights.items():
            similarity = calculate_semantic_similarity(
                str(resume_analysis.get(cat, "")),
                str(job_analysis.get(cat, ""))
            )
            scores[cat] = similarity * weight
        return scores, sum(scores.values()), resume_analysis.get("feedback", "")
    except Exception as e:
        print(f"Match Score Error: {e}")
        return {cat: 0.0 for cat in weights}, 0.0, "Error calculating match."

# === Entry Point ===
def download_and_read_pdfs(files):
    result_string = ""
    for file in files:
        request = drive_service.files().get_media(fileId=file['id'])
        fh = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        fh.close()

        # Extract and analyze
        resume_text = extract_text(fh.name)
        scores, overall_score, feedback = calculate_match_score(resume_text, JOB_DESCRIPTION)
        resume_name = file['name']

        formatted_entry = (
            f"###**Resume Name**: {resume_name} \n"
            f"- **Scores**: {scores} \n"
            f"- **Overall Match**: {overall_score} \n"
            f"- **Feedback**: {feedback} \n"
        )
        result_string += formatted_entry
        os.unlink(fh.name)
    return result_string

async def analyze_resume(pdf_folder_id):
    pdf_files = list_pdf_files(pdf_folder_id)
    if not pdf_files:
        return "No PDFs found in the folder."
    else:
        return download_and_read_pdfs(pdf_files)

# if __name__ == '__main__':
#     pdf_files = list_pdf_files(FOLDER_ID)
#     if not pdf_files:
#         print("No PDFs found in the folder.")
#     else:
#         result = download_and_read_pdfs(pdf_files)
#         print(result)
