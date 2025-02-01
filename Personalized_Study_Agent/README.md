![domain:innovation-lab](https://img.shields.io/badge/innovation--lab-3D8BD3)
![domain:finance](https://img.shields.io/badge/automation-3D8BD3)

# Personalized Study Agent

## Description  
The **Personalized Study Agent** is an AI-driven assistant that helps users manage their study sessions efficiently. It schedules and sends personalized reminders to ensure users stay on track with their learning goals. By defining subjects and study times, the agent automates the scheduling process and provides timely notifications.

### How It Works  
1. When started, the agent greets the user with a personalized message.  
2. It schedules a study session for the first subject from a predefined list.  
3. The agent calculates the time until the session starts and waits accordingly.  
4. At the scheduled time, it sends a reminder notification prompting the user to begin studying.  

## Input Data Model  
```python
class StudySession(Model):
    subject: str  # The subject of the study session
    start_time: datetime.datetime  # Scheduled time for the study session
```
```python
class ReminderRequest(Model):
    message: str  # Reminder message to be sent
```

## Output  
- A scheduled reminder message prompting the user to begin their study session at the designated time.  
- Logging messages that track scheduling and reminder dispatch.  

## Created By
- Aishwarya Dekhane
