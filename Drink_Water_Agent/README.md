![domain:innovation-lab](https://img.shields.io/badge/innovation--lab-3D8BD3)
![domain:finance](https://img.shields.io/badge/automation-3D8BD3)

# Drink Water Reminder Agent

## Description
The **Drink Water Reminder Agent** is an AI-powered assistant that periodically sends desktop notifications reminding users to stay hydrated. It ensures you maintain proper hydration levels by prompting you to drink water every hour. 

## Input Data Model
```python
class ReminderSchedule(Model):
    interval: int  # The time interval (in seconds) between each reminder
```

## Output Data Model
```python
class ReminderStatus(Model):
    last_reminder_time: datetime  # Timestamp of the last reminder sent
    next_reminder_time: datetime  # Timestamp of the next scheduled reminder
```

## Features
- **Automated Reminders:** Sends hourly desktop notifications to encourage water intake.
- **User-Friendly:** Runs in the background without manual intervention.
- **Customizable Timing:** Can be modified to fit personal hydration schedules.
- **Logging Support:** Logs reminder events for better tracking.

## Installation & Requirements
### Prerequisites
Ensure you have Python installed along with the required dependencies:
```sh
pip install plyer uagents
```

## How It Works
1. The agent initializes upon startup.
2. It continuously runs in the background, sending reminders every hour.
3. The reminders appear as desktop notifications, prompting the user to drink water.
4. The agent logs each reminder event for tracking purposes.

## Usage
Run the script with:
```sh
python script.py
```
The agent will start running and send hourly reminders to drink water.

## Created By
- Aishwarya Dekhane