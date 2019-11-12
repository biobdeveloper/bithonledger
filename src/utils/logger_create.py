import logging
import os
import logging.handlers
from config.system import project_root_dir


def logger_create(name, debug):
    try:
        os.mkdir(str(project_root_dir) + '/logs')
    except FileExistsError:
        pass
    if debug:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logger = logging.getLogger(name)
    logger.setLevel(level)
    ch = logging.StreamHandler()
    fh = logging.handlers.TimedRotatingFileHandler(filename=f"{str(project_root_dir)}/logs/bithonledger.log", when='d')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    logger.addHandler(ch)
    logger.addHandler(fh)
    return logger


if __name__ == '__main__':
    log = logger_create(__name__)
    log.debug('test')
    log.info('test')