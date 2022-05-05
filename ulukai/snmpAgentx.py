# -*- coding: utf-8 -*-

# --------------------------------------------
from array import array
import fileinput
import logging
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
import os
import time

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
                logger.info("registering process plugin with frequency to %s ...", str(frequency))
                self.register(self._oid_base + "." + oid_ext,
                    snmpAgentProcess,
                    freq=frequency,
                    data_store=conf["processes"])
                logger.info(">registered")
            if "tailStat" == plugin :
                logger.info("registering tail plugin ...")
                self.register(self._oid_base + "." + oid_ext,
                    snmpAgentTail,
                    freq=0,
                    data_store=conf)
                logger.info(">registered")

class snmpAgentTail(pyagentx3.Updater):
    def __init__(self, data_store=None):
        pyagentx3.Updater.__init__(self)
        self.conf = data_store
        self.filePath = self.conf["filePath"]
        self.regex = self.conf["regex"]
        logger.debug("compiling regex [%s]", self.regex)
        self.regexc = re.compile(self.regex)

    def run(self):
        fileFD = None
        fileIno = None
        while not self.stop.is_set():
            try:
                if fileFD is None:
                    fileFD = open(self.filePath, 'r')
                    fileIno = os.fstat(fileFD.fileno()).st_ino
                    fileFD.seek(0,os.SEEK_END)
                    logger.info("%s : opened file [%s]",
                        __class__.__name__, self.filePath)
            except IOError:
                fileFD = None
                fileIno = None
                logger.warning("%s : failed to open file [%s]",
                    __class__.__name__, self.filePath)
            if None == fileFD:
                self.stop.wait(5)
            else:
                where = fileFD.tell()
                line = fileFD.readline()
                if not line:
                    try:
                        if os.stat(self.filePath).st_ino != fileIno:
                            fileFD.close()
                            fileFD = None
                            logger.warning("tailed file inode changed")
                        else:
                            fileFD.seek(where)
                    except OSError:
                            fileFD.close()
                            fileFD = None
                            logger.warning("tailed file disappearedi on OS FS")
                else:
                    if None == line:
                        logger.debug("no new line")
                    else:
                        logger.debug("new line [%s]", line)
                        match = self.regexc.search(line)
                        if match :
                            self.last_result = match.groups()
                            logger.debug("match result %r", self.last_result)
                            self.run_update()
        if None != fileFD:
            fileFD.close()
            fileFD = None
            fileIno = None
            logger.info("tailed file closed on stopping thread")

    def update(self):
        i = 0
        for value in self.last_result:
            i += 1
            if "int" == self.conf["groupType"][i-1]:
                self.set_INTEGER(str(i), int(value))
            elif "string" == self.conf["groupType"][i-1]:
                self.set_OCTETSTRING(str(i), str(value))
        self.set_INTEGER("0", i)

class snmpAgentProcess(pyagentx3.Updater):
    def __init__(self, data_store=None):
        pyagentx3.Updater.__init__(self)
        self.conf = data_store
        self.processKeyList = ['pid']
        for key in self.conf:
            self.conf[key]["regexc"] = re.compile(self.conf[key]["regex"])
            if self.conf[key]["key"] not in self.processKeyList:
                self.processKeyList.append(self.conf[key]["key"])

    def update(self):
        logger.info("start update of process plugin")
        timeStart = time.time()
        oids = dict()
        for key in self.conf:
            oids[key] = []
        #timeInitOids = time.time()
        for proc in psutil.process_iter(self.processKeyList):
            #timeStartParsing = time.time()
            #proc_dict = proc.as_dict()
            proc_dict = proc.info
            #logger.debug(" time parsing one process = %s - %r", time.time() - timeStartParsing, proc_dict)
            for processKey,processConf in self.conf.items():
                #logger.debug("%s : %s : %s - %s - %s - %r",
                #    self.__class__.__name__, processKey,
                #    processConf["description"], processConf["key"], processConf["regex"], processConf["list_pids"])
                #if re.search(processConf["regex"], proc_dict[processConf["key"]]):
                if None != proc_dict[processConf["key"]] and processConf["regexc"].search(proc_dict[processConf["key"]]):
                    oids[processKey].append(proc_dict["pid"])
        #timeParseProcess = time.time()
        for key in oids:
            pidCount = len(oids[key])
            self.set_INTEGER(str(key) + ".0",
                pidCount)
            logger.info("adding %s[%s] with %s count", self.conf[key]["description"], key, pidCount)
            if True == self.conf[key]["list_pids"]:
                for i in range(pidCount):
                    self.set_INTEGER(self.conf[key]["oid"] + "." + str(i+1),
                        oids[key][i])
        timeBuiltSnmp = time.time()
        logger.debug("%s Stat : update in %ss",
                self.__class__.__name__,timeBuiltSnmp - timeStart)
        #logger.debug("%s Stat : oids %s - parsing %s - snmmp %s",
        #        self.__class__.__name__,
        #        timeInitOids - timeStart,
        #        timeParseProcess - timeStart,
        #        timeBuiltSnmp - timeStart)

