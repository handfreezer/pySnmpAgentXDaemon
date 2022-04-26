# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger("SAXD")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)
fh = logging.FileHandler('saxd.log')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)


import json
import pyagentx3
import psutil

import sys
import ipaddress
import datetime

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

def main():
    confData = loadConf("confSAXD.json")
    if None == confData:
        logger.error("failed to open conf File")
        return 1
    else:
        logger.debug(json.dumps(confData, indent=2))
    logger.info("coucou")

if __name__ == '__main__':
    main()
