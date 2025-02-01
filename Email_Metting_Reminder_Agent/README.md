![domain:innovation-lab](https://img.shields.io/badge/innovation--lab-3D8BD3)
![domain:finance](https://img.shields.io/badge/automation-3D8BD3)

# Email Meeting Reminder Agent

## Description
The **Email Meeting Reminder Agent** is an AI-powered assistant that monitors incoming emails for meeting-related content and automatically sets reminders. It extracts key details from unread emails and schedules a reminder notification to ensure that important meetings are not missed.

## Input Data Model
```python
class EmailData(Model):
    sender: str  # The sender's email address
    subject: str  # The subject of the email
    body: str  # The body content of the email
    received_time: datetime  # Timestamp when the email was received
```

## Output Data Model
```python
class Reminder(Model):
    meeting_subject: str  # The subject of the meeting reminder
    reminder_time: datetime  # The scheduled time for the reminder
    status: str  # Status of the reminder (e.g., pending, triggered)
```

## Created By
- Aishwarya Dekhane