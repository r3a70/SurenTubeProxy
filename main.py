
import os
import logging
from datetime import timedelta
import time


from apscheduler.schedulers.background import BackgroundScheduler

from services import setup, changer, health_check
from utils.times import now


logging.basicConfig(
    level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

scheduler: BackgroundScheduler = BackgroundScheduler()


scheduler.add_job(
    func=setup.main,
    trigger="date",
    run_date=now() + timedelta(seconds=5)
)
scheduler.add_job(
    func=setup.main,
    trigger="interval",
    hours=6
)
scheduler.add_job(
    func=changer.main,
    trigger="date",
    run_date=now() + timedelta(seconds=5)
)
scheduler.add_job(
    func=changer.main,
    trigger="interval",
    hours=2
)
scheduler.add_job(
    func=health_check.health_check_ips,
    trigger="interval",
    minutes=5
)

if __name__ == '__main__':

    if not os.path.exists("downloads"):

        os.mkdir("downloads")

    scheduler.start()

    logging.info('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
        while scheduler.running:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
