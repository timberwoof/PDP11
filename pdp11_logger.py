import time
import logging

class Logger():
    def __init__(self):
        logFormat = '%(asctime)s.%(msecs)03d000Z %(filename)s:%(funcName)s %(levelname)s : %(message)s'
        dateFormat = '%Y-%m-%dT%H:%M:%S'
        logPath = './pdp11.log'
        logging.basicConfig(filename=logPath, level=logging.DEBUG, format=logFormat,
                            datefmt=dateFormat, force=True)
        logging.Formatter.converter = time.gmtime
        logging.info(f"{logPath} begins")
