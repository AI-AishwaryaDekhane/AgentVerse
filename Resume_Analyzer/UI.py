import os
import openai
import streamlit as st
import fitz  # PyMuPDF
import docx
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import plotly.express as px
import plotly.graph_objects as go
import json
from typing import Dict, List, Tuple
import tempfile
from tenacity import retry, stop_after_attempt, wait_exponential

# Configure Streamlit page
st.set_page_config(
    page_title="ResumeMatch_Agent",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern UI Theme with Dark Mode Support
def set_theme():
    is_dark_theme = st.sidebar.checkbox("Dark Mode", value=False)
    
    base_colors = {
        "light": {
            "bg": "#ffffff",
            "text": "#1E293B",
            "primary": "#3B82F6",
            "secondary": "#64748B",
            "accent": "#2563EB",
            "success": "#10B981",
            "warning": "#F59E0B",
            "error": "#EF4444",
        },
        "dark": {
            "bg": "#0F172A",
            "text": "#E2E8F0",
            "primary": "#60A5FA",
            "secondary": "#94A3B8",
            "accent": "#3B82F6",
            "success": "#34D399",
            "warning": "#FBBF24",
            "error": "#F87171",
        }
    }
    
    theme = "dark" if is_dark_theme else "light"
    colors = base_colors[theme]
    
    return colors

# Apply theme colors
colors = set_theme()

# Enhanced CSS with Modern Styling
st.markdown(f"""
    <style>
        /* Base Styles */
        .main {{
            background-color: {colors['bg']};
            color: {colors['text']};
            font-family: 'Inter', sans-serif;
        }}
        
        /* Typography */
        h1, h2, h3 {{
            color: {colors['primary']};
            font-weight: 600;
        }}
        
        /* Components */
        .stTextInput, .stTextArea, .stSelectbox {{
            background-color: {colors['bg']};
            border: 1px solid {colors['secondary']};
            border-radius: 8px;
            padding: 12px;
            color: {colors['text']};
        }}
        
        .stButton>button {{
            background: linear-gradient(45deg, {colors['primary']}, {colors['accent']});
            color: white;
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            font-weight: 500;
            transition: all 0.3s ease;
            width: 100%;
        }}
        
        .stButton>button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        
        /* Cards */
        .card {{
            background-color: {colors['bg']};
            border: 1px solid {colors['secondary']};
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        /* Header */
        .header {{
            background: linear-gradient(135deg, {colors['primary']}, {colors['accent']});
            padding: 2rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            color: white;
            text-align: center;
        }}
        
        /* Metrics */
        .metric-card {{
            background-color: {colors['bg']};
            border: 1px solid {colors['secondary']};
            border-radius: 12px;
            padding: 1rem;
            text-align: center;
        }}
        
        .metric-value {{
            font-size: 2rem;
            font-weight: 600;
            color: {colors['primary']};
        }}
        
        .metric-label {{
            color: {colors['secondary']};
            font-size: 0.875rem;
        }}
        
        /* Progress Bars */
        .stProgress > div > div > div {{
            background-color: {colors['primary']};
        }}
        
        /* Tables */
        .dataframe {{
            border: 1px solid {colors['secondary']};
            border-radius: 8px;
            overflow: hidden;
        }}
        
        .dataframe th {{
            background-color: {colors['primary']};
            color: white;
            padding: 12px;
        }}
        
        .dataframe td {{
            padding: 12px;
            border-bottom: 1px solid {colors['secondary']};
        }}
        
        /* Alerts */
        .stAlert {{
            border-radius: 8px;
            border: none;
        }}
    </style>
""", unsafe_allow_html=True)

# # Set OpenAI API key
openai.api_key = "key"

# Retry logic for OpenAI API calls
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def get_embeddings(text: str) -> List[float]:
    """Get embeddings for a given text using OpenAI's API."""
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return response['data'][0]['embedding']

def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file content."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(file_content)
            tmp_file.flush()
            
            doc = fitz.open(tmp_file.name)
            text = " ".join([page.get_text("text") for page in doc])
            doc.close()
            return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        return ""
    finally:
        if 'tmp_file' in locals():
            os.unlink(tmp_file.name)

def extract_text_from_docx(file_content: bytes) -> str:
    """Extract text from DOCX file content."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
            tmp_file.write(file_content)
            tmp_file.flush()
            
            doc = docx.Document(tmp_file.name)
            return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        st.error(f"Error extracting text from DOCX: {str(e)}")
        return ""
    finally:
        if 'tmp_file' in locals():
            os.unlink(tmp_file.name)

def extract_text(file) -> str:
    """Extract text from uploaded file."""
    try:
        file_content = file.getvalue()
        file_type = file.type
        
        if file_type == "application/pdf":
            return extract_text_from_pdf(file_content)
        elif file_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
            return extract_text_from_docx(file_content)
        else:
            st.error(f"Unsupported file type: {file_type}")
            return ""
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return ""

def preprocess_text(text: str) -> str:
    """Preprocess text by removing noise and normalizing."""
    import re
    text = re.sub(r'\s+', ' ', text)  # Remove extra spaces
    text = re.sub(r'[^\w\s]', '', text)  # Remove special characters
    return text.lower().strip()

def calculate_semantic_similarity(text1: str, text2: str) -> float:
    """Calculate semantic similarity between two texts using embeddings."""
    embedding1 = get_embeddings(preprocess_text(text1))
    embedding2 = get_embeddings(preprocess_text(text2))
    similarity = cosine_similarity([embedding1], [embedding2])[0][0]
    return similarity

def analyze_resume_details(text: str, job_desc: str) -> Dict:
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
        if not content.startswith('{'): # Fix for common GPT formatting issues
            content = content[content.find('{'):content.rfind('}')+1]
        return json.loads(content)
    except Exception as e:
        st.error(f"Error in resume analysis: {str(e)}")
        return {
            "skills": "",
            "experience": "",
            "education": "",
            "domain": "",
            "certifications": "",
            "feedback": "Unable to generate feedback due to an error."
        }

def calculate_match_score(resume_text: str, job_desc: str) -> Tuple[Dict[str, float], float, Dict]:
    """Calculate detailed match scores between resume and job description."""
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
        for category, weight in weights.items():
            similarity = calculate_semantic_similarity(
                str(resume_analysis.get(category, "")),
                str(job_analysis.get(category, ""))
            )
            scores[category] = similarity * weight
        
        return scores, sum(scores.values()), resume_analysis.get("feedback", "")
    except Exception as e:
        st.error(f"Error in match calculation: {str(e)}")
        return {category: 0.0 for category in weights.keys()}, 0.0, "Unable to generate feedback due to an error."

def render_analysis_results(results_df: pd.DataFrame, detailed_results: List[Dict]):
    """Render analysis results with visualizations and detailed match table."""
    if len(results_df) == 0:
        st.warning("No results to display")
        return
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Resumes", len(results_df))
    with col2:
        st.metric("Average Match Score", f"{results_df['Overall Match'].mean():.2f}%")
    with col3:
        st.metric("Top Match Score", f"{results_df['Overall Match'].max():.2f}%")
    
    # Results table with custom formatting
    st.dataframe(
        results_df.style.format({
            'Overall Match': '{:.1f}%',
            'Skills Match': '{:.1f}%',
            'Experience Match': '{:.1f}%',
            'Education Match': '{:.1f}%',
            'Domain Match': '{:.1f}%',
            'Certifications Match': '{:.1f}%'
        }),
        use_container_width=True
    )
    
    # Dynamic detailed match table
    st.markdown("### 🎯 Detailed Match Breakdown")
    detailed_table_data = {
        "Category": ["Skills", "Experience", "Education", "Certifications", "Domain", "Overall Match"]
    }
    
    for result in detailed_results:
        resume_name = result['Resume Name']
        detailed_table_data[resume_name] = [
            f"✅ {result['skills']}" if result['skills'] else "❌ No match",
            f"✅ {result['experience']}" if result['experience'] else "❌ No match",
            f"✅ {result['education']}" if result['education'] else "❌ No match",
            f"✅ {result['certifications']}" if result['certifications'] else "❌ No match",
            f"✅ {result['domain']}" if result['domain'] else "❌ No match",
            f"✅ {result['overall_match']}"
        ]
    
    detailed_df = pd.DataFrame(detailed_table_data)
    st.dataframe(detailed_df, use_container_width=True)
    
    # Person-wise feedback
    st.markdown("### 📝 Person-Wise Feedback")
    for result in detailed_results:
        with st.expander(f"Feedback for {result['Resume Name']}"):
            st.write(result['feedback'])

    # Visualizations
    if len(results_df) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                results_df,
                x='Resume Name',
                y='Overall Match',
                title='Match Scores Comparison',
                color='Overall Match',
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            top_candidate = results_df.iloc[0]
            categories = ['Skills', 'Experience', 'Education', 'Domain', 'Certifications']
            values = [top_candidate[f'{cat} Match'] for cat in categories]
            
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name='Top Candidate'
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )),
                showlegend=False,
                title='Top Candidate Analysis'
            )
            st.plotly_chart(fig, use_container_width=True)

def main():
    # Header
    st.markdown("""
        <div class="header-container">
            <h1>🚀 Smart Resume Analyzer & Matcher</h1>
            <p>Empower Your Hiring with AI Insights</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Job Description Input with new styling
    st.markdown("### 📋 Job Description")
    job_description = st.text_area(
        "Enter the job description",
        height=200,
        help="Paste the complete job description here for accurate matching.",
        key="job_desc_input"
    )
    
    # Resume Upload
    st.markdown("### 📤 Resume Upload")
    uploaded_files = st.file_uploader(
        "Upload resumes (PDF/DOCX)",
        type=["pdf", "docx"],
        accept_multiple_files=True,
        help="You can upload multiple resumes at once"
    )

    if uploaded_files and job_description:
        with st.spinner('Analyzing resumes... Please wait.'):
            results = []
            detailed_results = []
            
            for file in uploaded_files:
                try:
                    text = extract_text(file)
                    if text:
                        scores, overall_score, feedback = calculate_match_score(text, job_description)
                        result = {
                            'Resume Name': file.name,
                            'Overall Match': overall_score * 100,
                            **{f'{k.title()} Match': v * 100 for k, v in scores.items()},
                            'feedback': feedback
                        }
                        results.append(result)
                        
                        # Detailed analysis for dynamic table
                        resume_analysis = analyze_resume_details(text, job_description)
                        detailed_results.append({
                            'Resume Name': file.name,
                            'skills': resume_analysis.get('skills', ''),
                            'experience': resume_analysis.get('experience', ''),
                            'education': resume_analysis.get('education', ''),
                            'certifications': resume_analysis.get('certifications', ''),
                            'domain': resume_analysis.get('domain', ''),
                            'overall_match': f"Strong Match for {resume_analysis.get('domain', 'General')} roles",
                            'feedback': resume_analysis.get('feedback', '')
                        })
                except Exception as e:
                    st.error(f"Error processing {file.name}: {str(e)}")
            
            if results:
                results_df = pd.DataFrame(results).sort_values('Overall Match', ascending=False)
                render_analysis_results(results_df, detailed_results)
                
                # Download results
                csv = results_df.to_csv(index=False)
                st.download_button(
                    "Download Analysis Report",
                    csv,
                    "resume_analysis_report.csv",
                    "text/csv",
                    key='download-csv'
                )
            else:
                st.warning("No valid results were generated from the analysis.")

if __name__ == "__main__":
    main()