![domain:innovation-lab](https://img.shields.io/badge/innovation--lab-3D8BD3)
![domain:finance](https://img.shields.io/badge/automation-3D8BD3)

# Email Checker Agent

## Description
The **Email Checker Agent** is an automated tool that connects to an email server, retrieves unseen emails, and checks their content for specific keywords. If a keyword is detected, the agent triggers a predefined action, such as notifying the user. This agent helps users monitor important messages efficiently without manually scanning their inbox.

## Input Data Model
```python
class EmailCredentials(Model):
    username: str  # Email account username
    password: str  # Email account password
    server: str = "imap.gmail.com"  # Email server (default: Gmail IMAP)

class KeywordFilter(Model):
    keywords: List[str]  # List of keywords to check in email content
```

## Output Data Model
```python
class EmailCheckResult(Model):
    email_id: str  # Unique identifier for the email
    subject: str  # Subject of the email
    keyword_found: bool  # Whether a keyword was detected in the email content
    action_taken: Optional[str]  # Description of the action taken (if any)
```

## Created By
- Aishwarya Dekhane


