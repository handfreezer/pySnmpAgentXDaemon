# -*- coding: utf-8 -*-

# --------------------------------------------
import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
logger = logging.getLogger('ulukai.snmpAgentx')
logger.addHandler(NullHandler())
# --------------------------------------------

import ulukai
import json

import pyagentx3
import argparse
import threading

class SnmpAgentxDaemonThread(threading.Thread):
    def __init__(self):
        pass
    def run(self) -> None:
        pass

def snmpAgentxDaemon():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('confFilePath', help="file path of configuration for the daemon")
    args = parser.parse_args()
    print(args)

    logger.info("Loading conf file " + args.confFilePath)
    confData = ulukai.loadConf(args.confFilePath)
    if None == confData:
        logger.error("failed to open conf File")
        exit(code=1)
    else:
        #logger.debug(json.dumps(confData, indent=2))
        pass

