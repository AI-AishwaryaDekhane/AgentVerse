from uagents import Agent, Context, Model
from textstat import (
    flesch_reading_ease,
    gunning_fog,
    dale_chall_readability_score,
    smog_index,
    automated_readability_index,
    coleman_liau_index
)
import language_tool_python
from collections import Counter
import re

# Initialize grammar tool
language_tool = language_tool_python.LanguageToolPublicAPI('en-US')

# Define Resume Analysis Request Model
class LinguisticAnalysisRequest(Model):
    text: str

# Define Resume Analysis Response Model
class LinguisticAnalysisResponse(Model):
    markdown_report: str

# Function to extract keywords from text
def extract_keywords(text):
    words = re.findall(r'\b\w+\b', text.lower())
    return Counter(words)

# Core analysis logic returning markdown-formatted string
async def generate_linguistic_analysis_report(resume: str) -> str:
    resume_keywords = extract_keywords(resume)

    # Readability scores
    readability_scores = {
        "Flesch Reading Ease": flesch_reading_ease(resume),
        "Gunning Fog Index": gunning_fog(resume),
        "Dale-Chall Readability Score": dale_chall_readability_score(resume),
        "SMOG Index": smog_index(resume),
        "Automated Readability Index": automated_readability_index(resume),
        "Coleman-Liau Index": coleman_liau_index(resume)
    }

    # Grammar check
    grammar_errors = language_tool.check(resume)
    grammar_feedback = [
        f"- **Error**: {e.message} | **Suggestions**: {', '.join(e.replacements)} | **Rule**: {e.ruleId}"
        for e in grammar_errors[:5]
    ]

    # Linguistic score
    linguistic_score = round(sum(readability_scores.values()) / len(readability_scores) - len(grammar_errors) * 2, 2)

    # Generate markdown report
    markdown = "# 📄 Resume Linguistic Analysis Report\n\n"
    
    markdown += "## 🧠 Readability Scores\n"
    for k, v in readability_scores.items():
        markdown += f"- **{k}**: {v:.2f}\n"

    markdown += "\n## 📝 Grammar Feedback (Top 5)\n"
    markdown += "\n".join(grammar_feedback) if grammar_feedback else "- No grammar issues found."

    markdown += f"\n\n## 📊 Linguistic Score: **{linguistic_score}**"

    return markdown
