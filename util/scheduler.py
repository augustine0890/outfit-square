import asyncio
import logging
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from concurrent.futures import ThreadPoolExecutor
from bot.discord_client import OutfitSquareBot
from typing import Callable


class TaskScheduler:
    """A class for managing scheduled tasks."""

    def __init__(self, bot: OutfitSquareBot):
        self.db = bot.mongo_client
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()
        self.executor = ThreadPoolExecutor(max_workers=4)

    async def task_wrapper(self, sync_task: Callable[..., bool]):
        task_succeeded: bool = False
        attempt_count: int = 0
        max_attempts: int = 3

        while not task_succeeded and attempt_count < max_attempts:
            attempt_count += 1
            try:
                # Run the synchronous task in a thread pool
                task_succeeded = await asyncio.get_event_loop().run_in_executor(
                    self.executor, sync_task
                )
                if task_succeeded:
                    logging.info("Task succeeded.")
                else:
                    logging.error(
                        f"Task failed to add a new draw. Attempt {attempt_count} of {max_attempts}."
                    )
                    raise Exception("Task failed.")
            except Exception as e:
                logging.error(
                    f"Task failed with error: {e}. Attempt {attempt_count} of {max_attempts}. Retrying..."
                )
                if attempt_count < max_attempts:
                    await asyncio.sleep(120)  # Retry after 2 minutes
                else:
                    logging.error(
                        "Max retry attempts reached. Moving on to the next task..."
                    )

    def setup_schedule(self):
        # Define your jobs with their specifics in a list
        jobs = [
            {
                # Weekly Draw (Every Monday at midnight)
                "func": self.task_wrapper,
                "args": [self.db.add_weekly_draw],
                "trigger": CronTrigger(second=15),
                # "trigger": CronTrigger(day_of_week="mon", hour="0", minute="0"),
                "name": "Lotto Draw Generation",
            },
            # Add more jobs here with their respective details
        ]

        for job in jobs:
            scheduled_job = self.scheduler.add_job(
                func=job["func"],
                args=job["args"],
                trigger=job["trigger"],
                name=job.get("name"),
            )

            # Calculate the time until the next trigger and log it
            if scheduled_job.next_run_time:
                now = datetime.now(scheduled_job.next_run_time.tzinfo)
                time_until_next_trigger = scheduled_job.next_run_time - now
                days_until_next_trigger = time_until_next_trigger.days
                logging.info(
                    f"[{job.get('name')}] Waiting [{days_until_next_trigger} days] until next scheduled event (next "
                    f"trigger): [{scheduled_job.next_run_time}]"
                )
            else:
                logging.warning(
                    f"Job {job.get('name')} scheduled but next_run_time is None. Check your scheduler configuration."
                )

        logging.info("Schedules are set up.")
