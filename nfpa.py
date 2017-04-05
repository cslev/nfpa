'''
Created on Jun 17, 2015

@author: lele
'''
import os
import sys
import datetime
import argparse
import re #required for regural expression check
#required for loading classes under lib/
sys.path.append("lib/")
from read_config import ReadConfig
from results_analyzer import ResultsAnalyzer
from visualizer import Visualizer
from database_handler import DatabaseHandler
from send_mail import EmailAdapter
import time
import importlib

import special_bidir_traffic_checker as sbtc
import logger as l
import date_formatter as df
import invoke as invoke

#required for loading classes under web/
sys.path.append("web/")
from web_nfpa import WEBNFPA

import inspect
import pdb

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
        self.reset_terminal = kwargs.get("reset_terminal", True)
        self.no_database = kwargs.get("no_database", False)
        self.config_file = kwargs.get("config_file", "nfpa.cfg")

        self.no_plot = kwargs.get("no_plot", False)


        
  
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

        
        #read config
        self.rc = ReadConfig(self.config_file)
        if(self.rc == -1):
            #error during reading config
            return -1
            
        self.config = self.rc.getConfig()



        self.log = l.getLogger(self.__class__.__name__,
                               self.config['LOG_LEVEL'],
                               self.config['app_start_date'],
                               self.config['LOG_PATH'])
        
        
        self.pid_file=self.config['MAIN_ROOT'] + "/" + "nfpa.pid"
        self.log.info("Deleting previous pid_file: %s" % self.pid_file)
        os.system("rm -rf " + self.pid_file)
        
        #before fresh start remove temporary files if they were not removed
        #already. This could be happen, if in some case, NFPA crashes, and
        #temporary res files in PKTGEN_ROOT/ still remains existing and can
        #influence a latter measurement results in a wrong way
        self.log.info("Clean up old .res files in PKTGEN's root dir...")
        self.deleteResFiles()
        self.log.info("[DONE]")

        #create a tmp directory for flow rules under nfpa/of_rules
        path=self.config["MAIN_ROOT"] + "/of_rules/tmp"
        if not os.path.exists(path):
            os.makedirs(path)

        self.log.debug("tmp directory created under of_rules")
        
        
        self.log.info("### Measurement scenario '" + self.scenario_name + \
                      "' has been initiated ###")
        
        
        #append scenario name to self.config dictionary for later usage
        self.config['scenario_name'] = self.scenario_name

        
        self.log.debug(str(self.config))
        #assembling log file path
        self.log_file_path = self.config['MAIN_ROOT'] + "/log/log_" + \
                             df.getDateFormat(self.config['app_start_date']) +\
                             ".log"

        self.log.info("Log file for this measurement is: %s" % self.log_file_path)
        self.log.info("THANKS FOR USING NFPA FOR MEASURING")

        self.storePID(str(os.getpid()))
        self.log.debug("NFPA PID stored")

        # create an instance of the EmailAdapter and store this object in self.config
        # if email service was enabled in the config file
        if self.config['email_service'].lower() == "true":
            self.config['email_adapter'] = EmailAdapter(self.config)
        else:
            self.config['email_adapter'] = None

        #adding no_plot variable to self.config to be able to share it later with visualizer
        self.config['no_plot'] = self.no_plot


    def exit(self, msg="EXITING..."):
        '''
        Print out MSG and call system.exit with ERROR status -1.
        '''
        self.log.error(msg)
        if (self.config['email_adapter'] is not None) and \
            (not self.config['email_adapter'].sendErrorMail()):
            self.log.error("Sending ERROR email did not succeed...")
        exit(-1)
        
    def configureVNFRemote(self, traffictype):
        '''
        Configure the remote vnf via pre-installed tools located on the same
        machine where NFPA is.  Only works for some predefined vnf_function
        and traffictraces.
        '''
        if not self.config["control_nfpa"]:
            return # Nothing to do

        mod = self.config.get("control_mod")
        ok = True
        if not mod:
            self.exit("Plugin for control_vnf not found: %s" % mod)
        try:
            ok = mod.configure_remote_vnf(self.config, traffictype)
        except Exception as e:
            self.log.debug('%s' % e)
        if not ok:
            self.exit("Failed to configure vnf. Traffictype: %s" % traffictype)


    def startAnalyzing(self, traffic_type, traffic_trace):
        '''
        This function actually called after pktgen measurements are done, and it instantiate
        results_analyzer and visualizer class, to analyze the successful result files and
        create plots of the results
        :return:
        '''


        tt = traffic_type
        trace = traffic_trace

        #to indicate the email_adapter, which traffic type is analyzed
        is_synthetic = True
        if tt == "realistic":
            is_synthetic=False


        self.log.debug("Analyzing trace (%s,%s)" % (tt,trace))
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        self.log.debug('caller name: %s' % calframe[1][3])

        # #synthetic and realistic results are process differently, so
        # #different class variables are used to store the data

        # Pktgen (re)start(s) finished, analyze results
        results_analyzer = ResultsAnalyzer(self.config,
                                            trafficType=tt,
                                            traffic_trace=trace)

        # after analyzation is done, visualize results
        results = results_analyzer.getResultsDict()

        visualizer = Visualizer(config=self.config,
                                results=results,
                                type=tt,
                                traffic_trace=trace)

        #check whether user wants to store the results in the database
        if not self.no_database:
            database_handler = DatabaseHandler(config=self.config,
                                                results=results,
                                                type=tt,
                                                traffic_trace=trace)
        # send notification email -- Last boolean parameter indicates synthetic case
        if (self.config['email_adapter'] is not None) and \
            (not self.config['email_adapter'].sendResultsMail(trace, is_synthetic)):
            self.log.warn("Sending email did not succeed...SKIPPING")

    def repeatedly_call_pktgen(self, cmd):
        self.log.info("PKTgen command: %s" % cmd)

        #sleep 1s for reading command
        time.sleep(1)

        #change dir to pktgen's main dir
        cd_cmd = "cd " + self.config["PKTGEN_ROOT"]

        #concatenate main command
        main_cmd = cd_cmd + " && " + cmd

        #start pktgen in measurement_num times
        for i in range(0, int(self.config["measurement_num"])):
            #here should be start the actual pktgen command!
            #we can't use our invoke function, since we could
            #not follow pktgen's output due to forking
            retval = os.system(main_cmd)
            if (retval != 0):
                self.exit("ERROR OCCURRED DURING STARTING PKTGEN")

    def startPktgenMeasurements(self):
        '''
        This  function is actually doing the stuff. It assembles the pktgen command
        and corresponding lua scripts, then starts the measurements
        :return:
        '''
        self.log.info("+----------------------------------------------+")
        self.log.info(str("|-    Estimated time required: %s        -|" % 
                          self.config['ETL']))
        self.log.info("+----------------------------------------------+")
        time.sleep(2)


        if self.config["trafficTypes"]:
            
            self.log.info(str("Pktgen will be started %s times" % 
                              self.config["measurement_num"]))

            #iterate through traffic types
            for trafficType in self.config["trafficTypes"]:
                self.log.info("Traffic type: %s" % trafficType)
                self.configureVNFRemote(trafficType)

                #first, measure simple scenarios (if desired)
                if(trafficType == "simple"):
                    #create config file for LUA script
                    self.rc.generateLuaConfigFile(trafficType,
                                                  self.config["packetSizes"],
                                                  None)
                    #append simple lua script to pktgen command
                    cmd = self.rc.assemblePktgenCommand()
                    cmd += " -f nfpa_simple.lua"

                    self.repeatedly_call_pktgen(cmd)

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

                        self.repeatedly_call_pktgen(cmd)
                    #ok, we got measurements for a given traffic trace
                    #with all the defined packetsizes

                # Start analyzing existing results, make plots and insert
                #data into the database
                self.startAnalyzing("synthetic", trafficType)

        
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
                    
                self.repeatedly_call_pktgen(cmd)

                # Start analyzing existing results
                self.startAnalyzing("realistic", realistic)



        #after everything is done, delete unnecessary res files
        self.deleteResFiles()

        stop = time.time()        
        start = self.config['app_start_date'] 
         
        running_time =  float(stop) - float(start)
        running_time = str(datetime.timedelta(seconds=running_time))
        self.log.info(str("Time elapsed: %s") % running_time)

        self.log.info("Log file can be found under: %s" % self.log_file_path)
        self.log.info("THANK YOU FOR USING NFPA %s" % self.config['version'])

        if(self.reset_terminal):
            self.log.info("Resetting terminal...")
            time.sleep(1)
            os.system("reset")
            #print out log automatically in this case to simulate 'no-reset' effect
            print_log_cmd="cat " + self.log_file_path
            os.system(print_log_cmd)
              
    
    def deleteResFiles(self):
        '''
        This function will delete all the temporary results files under
        pktgen's main directory
        '''
        #all files look like nfpa.[traffic_type].[packetsize]bytes.res
        #besides those, only 2 symlinks exist, which could also be deleted,
        #since each restart it is recreated. However, we do not delete them!
        del_cmd = "rm -rf " + self.config["PKTGEN_ROOT"] + "/nfpa.*.res"
        invoke.invoke(command=del_cmd,
                      logger=self.log)


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
    parser.add_argument('-r','--noreset',
                        action="store_false",
                        default=True,
                        help="DO NOT RESET the terminal after measurement is done. " +
                        "Reset is enabled by default, since NFPA could only quit " +
                        "from Pktgen via Lua.exit(), it confuses the terminal and " +
                        "one may need to logout and login again to clear that mess. " +
                        "If you want to disable, however, the use this argument.",
                        required=False)
    parser.add_argument('-d', '--nodatabase',
                        action="store_true",
                        default=False,
                        help="DO NOT STORE results in the database! This feature is " +
                        "mainly for development purposes, however in some testing phases one "+
                        "may do not want to make mess in the database!",
                        required=False)
    parser.add_argument('-p', '--noplot',
                        action="store_true",
                        default=False,
                        help="DO NOT CREATE PLOTS: only result files will be created.",
                        required=False)
    parser.add_argument('-c', '--cfg', nargs=1,
                        default=['nfpa.cfg'],
                        help="Specify a path to the config file. [Default: nfpa.cfg]",
                        required=False)
    
    args = parser.parse_args()
    
    #check the scenario's name argument! It needs to be compatible with
    #linux naming conventions for directories, thus it must not contain
    #special characters like '/'.
    pattern = re.compile(r'^[a-zA-Z0-9_]*$') #alphanumeric + underscore
    if pattern.match(args.name[0]) is None:
      print("\033[1;31m[NFPA] Error during parsing scenario's name!")
      print("\033[1;31m[NFPA] Only alphanumeric characters and underscore are allowed!\033[0m")
      exit(-1)



    #initialize main NFPA class, which can be passed as a pointer to WEBNFPA
    #as well
    main = NFPA(scenario_name=args.name[0],
                reset_terminal=args.noreset,
                no_database=args.nodatabase,
                config_file=args.cfg[0],
                no_plot=args.noplot)

    
    #web based gui
    if(args.web):
        #split web argument
      
        web_nfpa = WEBNFPA(args.name[0], args.web[0], args.cfg[0], main)
#         web_nfpa.start()
    #cli
    else:        
        #initiliaze if no web GUI was started
        status = main.initialize()
        if(status == -1):
            main.exit()

        try:
            #start PktGen based measurements
            main.startPktgenMeasurements()
        except Exception as e:
            main.log.error(e)
            time.sleep(1)
            os.system("reset")
            # print out log automatically in this case to simulate 'no-reset' effect
            print_log_cmd = "cat " + main.log_file_path
            os.system(print_log_cmd)

        
