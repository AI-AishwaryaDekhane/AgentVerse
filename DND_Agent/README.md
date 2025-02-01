![domain:innovation-lab](https://img.shields.io/badge/innovation--lab-3D8BD3)
![domain:finance](https://img.shields.io/badge/automation-3D8BD3)

# Do Not Disturb Agent

![domain:innovation-lab](https://img.shields.io/badge/innovation--lab-3D8BD3)  
![domain:finance](https://img.shields.io/badge/finance-3D8BD3)  

## Description
The **Do Not Disturb Agent** is an AI-powered tool designed to manage your "Do Not Disturb" schedule efficiently. By automatically toggling Do Not Disturb mode on your device at predefined start and end times, this agent helps enhance productivity and minimize interruptions. Whether during work hours or nighttime rest, it ensures that notifications do not disturb you, allowing for better focus and tranquility. Users can easily configure their schedules with customizable settings.

## Input Data Model
```python
class DoNotDisturbSchedule(Model):
    start_time: time  # The time of day when Do Not Disturb mode should start
    end_time: time    # The time of day when Do Not Disturb mode should end
```

## Output Data Model
```python
class DoNotDisturbStatus(Model):
    is_active: bool       # Indicates if Do Not Disturb mode is currently active
    activation_time: datetime  # Timestamp when Do Not Disturb mode was activated
    deactivation_time: datetime  # Timestamp when Do Not Disturb mode was deactivated (if applicable)
```

## Features
- **Automated Scheduling:** Set start and end times for Do Not Disturb mode.
- **Customizable Settings:** Easily configure schedules based on user preferences.
- **Real-time Status Updates:** Check if Do Not Disturb mode is active.
- **Productivity Enhancement:** Minimize interruptions and maintain focus.

## Usage
1. Define your preferred **start_time** and **end_time** using the `DoNotDisturbSchedule` model.
2. The agent will automatically activate and deactivate Do Not Disturb mode at the specified times.
3. Retrieve the current status using the `DoNotDisturbStatus` model to check if the mode is active.

## Created By
- Aishwarya Dekhane
