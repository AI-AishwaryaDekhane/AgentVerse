import asyncio
from datetime import datetime, time

class DoNotDisturbAgent:
    def __init__(self, start_time, end_time):
        """Initialize the agent with start and end times for Do Not Disturb mode."""
        self.start_time = start_time
        self.end_time = end_time
    
    async def check_schedule(self):
        """Check current time against the schedule and act accordingly."""
        while True:
            now = datetime.now().time()

            if self.start_time <= now < self.end_time:
                self.activate_do_not_disturb()
            else:
                self.deactivate_do_not_disturb()
            await asyncio.sleep(60)  # Check every minute

    def activate_do_not_disturb(self):
        """Simulate activation of Do Not Disturb mode."""
        print(f"Do Not Disturb activated at {datetime.now().time().strftime('%H:%M:%S')}.")

    def deactivate_do_not_disturb(self):
        """Simulate deactivation of Do Not Disturb mode."""
        print(f"Do Not Disturb deactivated at {datetime.now().time().strftime('%H:%M:%S')}.")

    async def run(self):
        """Run the agent to manage Do Not Disturb mode."""
        print("Do Not Disturb Agent started.")
        await self.check_schedule()

if __name__ == "__main__":
    # Define Do Not Disturb schedule
    dnd_start = time(22, 0)  # 10:00 PM
    dnd_end = time(7, 0)     # 7:00 AM

    agent = DoNotDisturbAgent(start_time=dnd_start, end_time=dnd_end)
    asyncio.run(agent.run())