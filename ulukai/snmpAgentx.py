# -*- coding: utf-8 -*-

# --------------------------------------------
from array import array
import logging
from pyagentx3.updater import Updater
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
logger = logging.getLogger('ulukai.snmpAgentx')
logger.addHandler(NullHandler())
# --------------------------------------------

import ulukai

import argparse
import pyagentx3

import re
import psutil
import threading
import json

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
    def __init__(self, confData, agent_id='snmpAgent'):
        self._oid_base = confData["oid_base"]
        self._agents = confData["agents"]
        logger.info("Log level requested : %s", confData["log"]["level"])
        logger.info("Socket path : %s", confData["socket_path"])
        logger.info("Base OID : %s", self._oid_base)
        super().__init__(agent_id, confData["socket_path"]) #socket_path)

    def setup(self):
        for agentName,agentConf in self._agents.items():
            oid_ext = agentConf["oid_ext"]
            plugin = agentConf["plugin"]
            conf = agentConf["conf"]
            logger.info("Agent : %s [plugin=%s on oid_ext=%s]", agentName, plugin, oid_ext)
            if "process" == plugin :
                frequency = conf["frequency"]
                logger.info("registering process plugin...")
                self.register(self._oid_base + "." + oid_ext,
                    snmpAgentProcess,
                    freq=frequency,
                    data_store=conf["processes"])
                logger.info(">registered")

class snmpAgentProcess(pyagentx3.Updater):
    def __init__(self, data_store=None):
        pyagentx3.Updater.__init__(self)
        self.conf = data_store

    def update(self):
        oids = dict()
        for key in self.conf:
            oids[key] = []
        for proc in psutil.process_iter():
            proc_dict = proc.as_dict()
            for processKey,processConf in self.conf.items():
                logger.info("%s : %s : %s - %s - %s - %b",
                    self.__class__.__name__, processKey,
                    processConf["description"], processConf["key"], processConf["regex"], processConf["list_pids"])
                if re.search(processConf["regex"], proc_dict[processConf["key"]]):
                    oids[processKey].append(proc_dict["pid"])
        for key in oids:
            pidCount = len(oids[key])
            self.set_INTEGER(self.conf[key]["oid"] + ".0",
                pidCount)
            if True == self.conf[key]["list_pids"]:
                for i in range(pidCount):
                    self.set_INTEGER(self.conf[key]["oid"] + "." + str(i+1),
                        oids[key][i])
