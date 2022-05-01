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


import ulukai
ulukai.setLog(True)

import json

def main():
    confData = ulukai.loadConf("confSAXD.json")
    if None == confData:
        logger.error("failed to open conf File")
        exit(code=1)
    else:
        logger.debug(json.dumps(confData, indent=2))
    logger.info("coucou")

if __name__ == '__main__':
    main()
    ulukai.daemonSnmpAgentx()
