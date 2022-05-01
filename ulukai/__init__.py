# -*- coding: utf-8 -*-

__version__ = '0.0.1'
__author__ = 'Handfreezer <laplagne_at_ulukai.net>'

__all__ = [
    'tools',
    'snmpAgentx',
]

import logging

from .tools import loadConf
from .snmpAgentx import snmpAgentxDaemon as daemonSnmpAgentx

def setLog(debug:bool=False, logFilePath:str=None):
    if debug:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logger = logging.getLogger('ulukai')
    logger.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    if None != logFilePath:
        fh = logging.FileHandler()
        fh.setLevel(level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

