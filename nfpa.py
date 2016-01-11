'''
Created on Jun 17, 2015

@author: lele
'''
import os
import sys
import datetime
import argparse
#required for loading classes under lib/
sys.path.append("lib/")
from read_config import ReadConfig
from results_analyzer import ResultsAnalyzer
from visualizer import Visualizer
from database_handler import DatabaseHandler
import time
import copy
import special_bidir_traffic_checker as sbtc
import logger as l
import date_formatter as df
import invoke as invoke
#required for loading classes under web/
sys.path.append("web/")
from web_nfpa import WEBNFPA



class NFPA(object):
    '''This is the main class'''
    
    def __init__(self, **kwargs):
        '''
        Constructor
         - initiate config file reading and scenario name
         kwargs.scenario_name String - name of the scenario
         
        '''
        self.config = {}
        #default name TEST
        self.scenario_name = kwargs.get("scenario_name","TEST")
        
        
  
    def storePID(self, new_pid):
        '''
        This process save the new_pid variables into nfpa.pids file to be able
        to kill the whole process tree during execution
        new_pid Int - the pid to store
        '''
        
        file = open(self.pid_file,'w')
        file.write(str(new_pid))
        file.write("\n")
        file.close()
        
    def initialize(self):
#         print("Main class instantiated")
        
        
        #read config
        self.rc = ReadConfig()
        if(self.rc == -1):
            #error during reading config
            return -1
            
        self.config = self.rc.getConfig()
        
        
       
        self.log = l.getLogger( self.__class__.__name__, 
                                self.config['LOG_LEVEL'], 
                                self.config['app_start_date'],
                                self.config['LOG_PATH'])
        
        
        self.pid_file=self.config['MAIN_ROOT'] + "/" + "nfpa.pid"
        self.log.info("Deleting previous pid_file: %s" % self.pid_file)
        os.command("rm -rf " + self.pid_file)
        
        #before fresh start remove temporary files if they were not removed
        #already. This could be happen, if in some case, NFPA crashes, and
        #temporary res files in PKTGEN_ROOT/ still remains existing and can
        #influence a latter measurement results in a wrong way
        self.log.info("Clean up old .res files in PKTGEN's root dir...")
        self.deleteResFiles()
        self.log.info("[DONE]")
        
        
        self.log.info("### Measurement scenario '" + self.scenario_name + "' has been" 
              "initiated ###")
        
        
        #append scenario name to self.config dictionary for later usage
        self.config['scenario_name'] = self.scenario_name

        
        self.log.info(str(self.config))
    
        self.log.info("Log file for this measurement is: %s/%s" % 
                      (self.config['MAIN_ROOT'], 
                       df.getDateFormat(self.config['app_start_date'])))
        self.log.info("THANKS FOR USING NFPA FOR MEASURING")

        self.storePID(str(os.getpid()))
        self.log.debug("NFPA PID stored")
        
   
   
    def exiting(self):
        '''
        This small function only prints out EXITING and call system.exit with
        ERROR status -1.
        Used only for function checkConfig()'s return values 
        '''
        self.log.error("EXITING...")
        exit(-1)
        
    
    def startPktgenMeasurements(self):
        
        self.log.info("+----------------------------------------------+")
        self.log.info(str("|-    Estimated time required: %s        -|" % 
                          self.config['ETL']))
        self.log.info("+----------------------------------------------+")
        time.sleep(2)
        

        if self.config["trafficTypes"]:
            
            self.log.info(str("Pktgen will be started %s times" % 
                              self.config["measurement_num"]))
            #main loop of pktgen based measurements
            for i in range(0,int(self.config["measurement_num"])):
                #iterate through traffic types
                for trafficType in self.config["trafficTypes"]:
                    #first, measure simple scenarios (if desired)
                    if(trafficType == "simple"):
                        #create config file for LUA script
                        self.rc.generateLuaConfigFile(trafficType, 
                                                      self.config["packetSizes"],
                                                      None)
                        #append simple lua script to pktgen command
                        cmd = self.rc.assemblePktgenCommand()
                        cmd += " -f nfpa_simple.lua"
                        self.log.info("PKTgen command: %s" % cmd)
                        
                        #sleep 1s for reading command
                        time.sleep(1)
                        
                        #change dir to pktgen's main dir
                        cd_cmd = "cd " + self.config["PKTGEN_ROOT"]
                        
                        #concatenate main command
                        main_cmd = cd_cmd + " && " + cmd
                        #here should be start the actual pktgen command!
                        #we can't use our invoke function, since we could
                        #not follow pktgen's output due to forking
                        retval=os.system(main_cmd)
                        if(retval != 0):
                            self.log.error("ERROR OCCURRED DURING STARTING PKTGEN")
                            self.log.error("Error: %s" % str(retval[0]))
                            self.log.error("Exit_code: %s" % str(retval[1]))
                            exit(-1)
#                       
                    else:
                        
                        for ps in self.config['packetSizes']:
                            #create config file for LUA script
                            self.rc.generateLuaConfigFile(trafficType, 
                                                          [ps],
                                                          None)
                            #create the command first part
                            cmd = self.rc.assemblePktgenCommand()
                            #no special bidirectional traffic was not set
                            if not sbtc.checkSpecialTraffic(trafficType):
                                cmd += " -f nfpa_traffic.lua -s " + \
                                      self.config["sendPort"] + ":" + \
                                      self.config['MAIN_ROOT'] + \
                                      "/PCAP/nfpa." +\
                                      trafficType + "." + ps + "bytes.pcap" 
                            
                                #if bidDir is set, we need to set pcap file for the 
                                #other port as well (add this part to the cmd)
                                if(int(self.config["biDir"]) == 1):
                                    cmd +=  " -s " + self.config["recvPort"] +\
                                            ":" + self.config['MAIN_ROOT'] +\
                                            "/PCAP/nfpa." +\
                                            trafficType + "." + ps + "bytes.pcap" 
                            else:
                                #special bidirectional traffic was set
                                tmp_tt = sbtc.splitTraffic(trafficType)
                                cmd += " -f nfpa_traffic.lua -s " + \
                                        self.config["sendPort"] + ":" + \
                                        self.config['MAIN_ROOT'] + \
                                        "/PCAP/nfpa." + tmp_tt[0] + "." + \
                                        ps + "bytes.pcap"
                                cmd +=  " -s " + self.config["recvPort"] + \
                                        ":" + self.config['MAIN_ROOT'] + \
                                        "/PCAP/nfpa." + tmp_tt[1] + "." + \
                                        ps + "bytes.pcap"        
                            
                            self.log.info(cmd)
                            
                            #sleep 1s for reading command
                            time.sleep(1)
                            
                            
                            #change dir to pktgen's main dir
                            cd_cmd = "cd " + self.config["PKTGEN_ROOT"]
                            #concatenate main command
                            main_cmd = cd_cmd + " && " + cmd
                            #here should be start the actual pktgen command!
                            #we can't use our invoke function, since we could
                            #not follow pktgen's output due to forking
                            retval=os.system(main_cmd)
                            if(retval != 0):
                                self.log.error("ERROR OCCURRED DURING STARTING PKTGEN")
                                self.log.error("Error: %s" % str(retval[0]))
                                self.log.error("Exit_code: %s" % str(retval[1]))
                                exit(-1)
        
            #Pktgen (re)start(s) finished, analyze results
            self.results_analyzer = ResultsAnalyzer(self.config, type="synthetic")
            
            #after analyzation is done, visualize results
            self.results = self.results_analyzer.getResultsDict()  
            self.visualizer = Visualizer(config=self.config, 
                                         results=self.results,
                                         type="synthetic")
            self.database_handler = DatabaseHandler(config=self.config, 
                                         results=self.results,
                                         type="synthetic")
          
        
        if self.config["realisticTraffics"]:                
            #check realistic traffic traces
            for realistic in self.config["realisticTraffics"]:
                #create config file for LUA script
                self.rc.generateLuaConfigFile(None, 
                                              None,
                                              realistic)
                cmd = self.rc.assemblePktgenCommand()

                #no special bidirectional traffic was not set
                if not sbtc.checkSpecialTraffic(realistic):
                    cmd +=" -f nfpa_realistic.lua -s " + \
                          self.config["sendPort"] + ":" + \
                          self.config['MAIN_ROOT'] + "/PCAP/nfpa." +\
                          realistic + ".pcap" 
                
                    #if bidDir is set, we need to set pcap file for the 
                    #other port as well (add this part to the cmd)
                    if(int(self.config["biDir"]) == 1):
                        cmd += " -s " + self.config["recvPort"] + ":" + \
                               self.config['MAIN_ROOT'] + "/PCAP/nfpa." +\
                               realistic + ".pcap"
                
                #special bidirectional traffic was set
                else:
                    tmp_tt = sbtc.splitTraffic(realistic)
                    cmd += " -f nfpa_realistic.lua -s " + \
                           self.config["sendPort"] + ":" + \
                           self.config['MAIN_ROOT'] + "/PCAP/nfpa." +\
                           tmp_tt[0] + ".pcap" 
                    
                    cmd +=  " -s " + self.config["recvPort"] + \
                            ":" + self.config['MAIN_ROOT'] + \
                            "/PCAP/nfpa." + tmp_tt[1] + ".pcap"         
                    
                self.log.info(cmd)
                
                #sleep 1s for reading command
                time.sleep(1)
                
                #change dir to pktgen's main dir
                cd_cmd = "cd " + self.config["PKTGEN_ROOT"]
                #concatenate main command
                main_cmd = cd_cmd + " && " + cmd
                #here should be start the actual pktgen command!
                #we can't use our invoke function, since we could
                #not follow pktgen's output due to forking
                retval=os.system(main_cmd)
                if(retval != 0):
                    self.log.error("ERROR OCCURRED DURING STARTING PKTGEN")
                    self.log.error("Error: %s" % str(retval[0]))
                    self.log.error("Exit_code: %s" % str(retval[1]))
                    exit(-1)
             
            #Pktgen (re)start(s) finished, analyze results
            self.realistic_results_analyzer = ResultsAnalyzer(self.config, 
                                                              type="realistic")
            
            #after analyzation is done, visualize results
            self.realistic_results = self.realistic_results_analyzer.getRealisticResultsDict()  
            self.realistic_visualizer = Visualizer(config=self.config, 
                                         results=self.realistic_results,
                                         type="realistic")
            self.database_handler = DatabaseHandler(config=self.config, 
                                         results=self.realistic_results,
                                         type="realistic")   
        
        #after everything is done, delete unnecessary res files
        self.deleteResFiles()
       
            
            
            
            
            
        
        
        stop = time.time()        
        start = self.config['app_start_date'] 
         
        running_time =  float(stop) - float(start)
        running_time = str(datetime.timedelta(seconds=running_time))
        self.log.info(str("Time elapsed: %s") % running_time)
        log = self.config['LOG_PATH'] + \
              "log_" + \
              str(df.getDateFormat(self.config['app_start_date']) + \
              ".log")
        self.log.info("Log file can be found under: %s" % str(log))
        self.log.info("THANK YOU FOR USING NFPA %s" % self.config['version']) 
              
    
    def deleteResFiles(self):
        '''
        This function will delete all the temporary results files under
        pktgen's main directory
        '''
        #all files look like nfpa.[traffic_type].[packetsize]bytes.res
        #besides those, only 2 symlinks exist, which could also be deleted,
        #since each restart it is recreated. However, we do not delete them!
        del_cmd = "rm -rf " + self.config["PKTGEN_ROOT"] + "/nfpa.*.res"
        retval = invoke.invoke(del_cmd)
           
        if(retval[1] != 0):
            self.log.error("ERROR OCCURRED DURING REMOVING .RES FILES")
            self.log.error("Error: %s" % str(retval[0]))
            self.log.error("Exit_code: %s" % str(retval[1]))
            exit(-1)




if __name__ == '__main__':
    
    #parse CLI
    parser = argparse.ArgumentParser(description="NFPA usage")
    parser.add_argument('-n', '--name',nargs=1, 
                        help="Specify a name for the scenario",
                        required=True)
    parser.add_argument('-w', '--web', nargs=1, 
                        help="Enable web-based GUI on hostname:port." +  
                        "This will launch the web-based GUI that could be" +\
                        " accessed via http://[hostname]:[port]/nfpa" +\
                        "Argument should look like hostname:port, " + 
                        "e.g., localhost:8000",
                        required=False)
    
    args = parser.parse_args()
    
    #initialize main NFPA class, which can be passed as as pointer to WEBNFPA
    #as well
        
    main = NFPA(scenario_name=args.name[0])
        
    
    #web based gui
    if(args.web):
        #split web argument
      
        web_nfpa = WEBNFPA(args.name[0], args.web[0], main)
#         web_nfpa.start()
    #cli
    else:        
        #initiliaze if no web GUI was started
        status = main.initialize()
        if(status == -1):
            main.exiting()
        #start PktGen based measurements
        main.startPktgenMeasurements()
        
