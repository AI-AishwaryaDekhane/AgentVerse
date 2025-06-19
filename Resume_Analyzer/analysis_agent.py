from uagents import Agent, Context, Model
from textstat import flesch_reading_ease, gunning_fog, dale_chall_readability_score, smog_index, automated_readability_index, coleman_liau_index
import language_tool_python
import re
from collections import Counter

language_tool = language_tool_python.LanguageToolPublicAPI('en-US')

class ResumeAnalysisRequest(Model):
    resumes: list
    job_description: str

class ResumeAnalysisResponse(Model):
    analysis_results: dict
    compatibility: dict

analysis_agent = Agent(
    name='analysis_agent',
    port=5004,
    endpoint='http://localhost:5004/submit',
    seed='analysis_seed'
)

def extract_keywords(text):
    words = re.findall(r'\b\w+\b', text.lower())
    return Counter(words)

def calculate_compatibility(resume_keywords, job_keywords):
    common_keywords = resume_keywords & job_keywords
    return len(common_keywords) / len(job_keywords)

@analysis_agent.on_message(model=ResumeAnalysisRequest)
async def handle_analysis(ctx: Context, sender: str, request: ResumeAnalysisRequest):
    results = {}
    compatibility_results = {}

    job_keywords = extract_keywords(request.job_description)

    for idx, resume in enumerate(request.resumes):
        readability_scores = {
            "Flesch Reading Ease": flesch_reading_ease(resume),
            "Gunning Fog Index": gunning_fog(resume),
            "Dale-Chall Readability Score": dale_chall_readability_score(resume),
            "SMOG Index": smog_index(resume),
            "Automated Readability Index": automated_readability_index(resume),
            "Coleman-Liau Index": coleman_liau_index(resume)
        }

        grammar_errors = language_tool.check(resume)
        grammar_feedback = [{"error": error.message, "suggestion": error.replacements} for error in grammar_errors[:5]]

        resume_keywords = extract_keywords(resume)
        missing_keywords = [word for word in job_keywords if word not in resume_keywords]

        linguistic_score = sum(readability_scores.values()) / len(readability_scores) - len(grammar_errors) * 2
        compatibility_score = calculate_compatibility(resume_keywords, job_keywords)

        results[f"Resume {idx+1}"] = {
            "Readability Scores": readability_scores,
            "Grammar Issues": grammar_feedback,
            "Missing Keywords": missing_keywords[:10],
            "Linguistic Score": round(linguistic_score, 2)
        }

        compatibility_results[f"Resume {idx+1}"] = compatibility_score >= 0.5

    await ctx.send(sender, ResumeAnalysisResponse(analysis_results=results, compatibility=compatibility_results))

if __name__ == "__main__":
    analysis_agent.run()
