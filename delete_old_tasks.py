import schedule
import time
import logging
from datetime import date
from bot import Bot
import argparse

logging.basicConfig(level=logging.INFO,
                    format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s')

parser = argparse.ArgumentParser()
parser.add_argument('--bot',
                    default='main',
                    type=str,
                    help='Which bot is to be started',
                    dest="bot",
                    choices=['main', 'creation', 'moderation'])
args = parser.parse_args()
logging.info('Script delete_old_task is started')


def job():
    logging.info('Process of deleting has started')

    today = date.today()
    Bot.delete_overdue_tasks_from_main(today)


schedule.every().day.at('01:00').do(job)

while True:
    if args.bot == 'main':
        schedule.run_pending()
        time.sleep(1)
