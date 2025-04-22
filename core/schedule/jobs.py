from apscheduler.schedulers.asyncio import AsyncIOScheduler
from core.handlers.moderator import update_ticket_message
from services.db.storage import Storage


def db_check(db_pool):


    async def func():
        await Storage(db_pool()).close_old_tickets(update_ticket_message)

    return func


async def two_weeks_status_scheduler(func) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(func, "interval", minutes=1, id='status')
    return scheduler
