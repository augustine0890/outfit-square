import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from concurrent.futures import ThreadPoolExecutor
from database.mongo_client import MongoDBInterface
from typing import Callable


class TaskScheduler:
    """A class for managing scheduled tasks."""

    def __init__(self, database: MongoDBInterface):
        self.db = database
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
        # Weekly Draw (Every Monday at midnight)
        self.scheduler.add_job(
            self.task_wrapper,
            args=[self.db.add_weekly_draw],
            # trigger=CronTrigger(second=15),
            trigger=CronTrigger(day_of_week="mon", hour="0", minute="0"),
        )

        logging.info("Schedules are set up.")
