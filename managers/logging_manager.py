from datetime import datetime
import logging

import globals


class AppFilter(logging.Filter):
    def filter(self, record):
        record.utc = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        record.lc = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return True


def manage_logging():
    logger = logging.getLogger('SAT_SYSTEM')
    logger.addFilter(AppFilter())
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(globals.TEMP + '/' + 'log.txt')
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter('#################### %(lc)s CLT - %(utc)s UTC ####################\n%(message)s\n###########################################################################################\n')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.info("program startup")
    return logger
