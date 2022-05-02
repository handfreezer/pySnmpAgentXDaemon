# -*- coding: utf-8 -*-

# --------------------------------------------
import logging
from pyagentx3.updater import Updater
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
        pyagentx3.setup_logging(debug=False)
        try:
            agt = snmpAgent(confData)
            agt.start()
        except Exception as ex:
            print("Unhandled exception: %s" % ex)
            agt.stop()
        except KeyboardInterrupt:
            agt.stop()

class snmpAgent(pyagentx3.Agent):
    def __init__(self, confData, agent_id='snmpAgent', socket_path=None):
        oid_base = confData["oid_base"]
        logger.info("Log level requested : %s", confData["log"]["level"])
        logger.info("Socket path : %s", confData["socket_path"])
        logger.info("Base OID : %s", oid_base)
        for agentName,agentConf in confData["agents"].items():
            logger.info("Agent : %s [plugin=%s on oid_ext=%s]", agentName, agentConf["plugin"], agentConf["oid_ext"])
        super().__init__(agent_id, confData["socket_path"]) #socket_path)

    def setup(self):
        #self.register('1.3.6.1.4.1.8072.2.1', NetSnmpTestMibScalar, freq=10, data_store=data)
        pass


class snmpAgentProcess(pyagentx3.Updater):
    def __init__(self, conf):
        pyagentx3.Updater.__init__(self)
        self._listPIDs = conf["list_pids"]
        self._processes2Watch = conf["processes"]

    def update(self):
        for processKey,processConf in self._processes2Watch.items():
            logger.info("%s : %s : %s - %s",
                self.__class__.__name__, processKey,
                processConf["oid"], processConf["regex"])
