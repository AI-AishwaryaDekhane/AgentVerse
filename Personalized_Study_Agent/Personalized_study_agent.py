from uagents import Agent, Context, Model
import datetime
import asyncio

class StudySession(Model):
    subject: str
    start_time: datetime.datetime

class ReminderRequest(Model):
    message: str

agent = Agent()

# Placeholder for user-specific configuration
user_name = "Student"
study_subjects = ["Mathematics", "Science", "History"]

@agent.on_event("startup")
async def initialize_study_agent(ctx: Context):
    """Logs a personalized greeting message and schedules a study session."""
    ctx.logger.info(f"Hello {user_name}, I'm your Study Assistant agent. My address is {ctx.agent.address}.")
    
    # Schedule a study session for demonstration purposes
    if study_subjects:
        subject = study_subjects[0]  # Start with the first subject
        start_time = datetime.datetime.now() + datetime.timedelta(seconds=10)  # 10-second delay for demonstration
        study_session = StudySession(subject=subject, start_time=start_time)
        
        ctx.logger.info(f"Scheduling your {study_session.subject} session at {study_session.start_time.strftime('%Y-%m-%d %H:%M:%S')}.")
        await schedule_study_reminder(ctx, study_session)

async def schedule_study_reminder(ctx: Context, study_session: StudySession):
    """Schedules and sends a reminder for a study session."""
    current_time = datetime.datetime.now()
    time_to_wait = (study_session.start_time - current_time).total_seconds()
    
    if time_to_wait > 0:
        ctx.logger.info(f"Waiting {time_to_wait:.1f} seconds to send reminder...")
        await asyncio.sleep(time_to_wait)
        
    reminder_message = f"Time to start your {study_session.subject} study session!"
    ctx.logger.info(reminder_message)
    await ctx.send("example_recipient_address", ReminderRequest(message=reminder_message))

if __name__ == "__main__":
    asyncio.run(agent.run())