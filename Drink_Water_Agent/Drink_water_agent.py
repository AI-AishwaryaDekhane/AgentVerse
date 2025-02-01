import asyncio
from plyer import notification
from uagents import Agent, Context

# Initialize the agent
agent = Agent()

def send_notification():
    """Send a desktop notification reminding to drink water."""
    notification.notify(
        title="Hydration Reminder",
        message="It's time to drink water! Stay hydrated.",
        app_name="Water Reminder",
        timeout=10
    )

@agent.on_event("startup")
async def drink_water_reminder(ctx: Context):
    """Periodically remind to drink water every hour."""
    ctx.logger.info("Water Reminder Agent started. You'll be reminded to drink water every hour.")
    while True:
        send_notification()  # Trigger the notification
        ctx.logger.info("Reminder sent: Drink water!")  # Log the reminder event
        await asyncio.sleep(3600)  # Wait for an hour before sending the next reminder

if __name__ == "__main__":
    agent.run()