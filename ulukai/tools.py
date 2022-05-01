# -*- coding: utf-8 -*-

# --------------------------------------------
import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
logger = logging.getLogger('ulukai.tools')
logger.addHandler(NullHandler())
# --------------------------------------------

import json

def loadConf(filePath:str):
    confData = None
    confFile = None
    try:
        confFile = open(filePath, 'r')
        confData = json.load(confFile)
    except Exception as error:
        logger.error("Failed to get conf from file [{0}]".format(error))
    finally:
        if None != confFile:
            confFile.close()
    if None != confData:
        logger.info("Loaded conf file " + filePath)
    return confData
