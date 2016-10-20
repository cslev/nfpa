'''
Created on Jun 17, 2015

@author: lele
'''
import os
import logger as l
import copy
import time
import datetime
import special_bidir_traffic_checker as sbtc
import read_write_config_file as rwcf
from send_mail import EmailAdapter

import subprocess
import invoke as invoke
import pdb
#required for loading DatabaseHandler class
import sys
sys.path.append("db/")
from database_adapter import SQLiteDatabaseAdapter



class ReadConfig(object):
    '''
    This class is devoted to read the config file

    Besides nfpa.cfg file, some additional info and variables
    Additional info for storing some config vars:
        trafficTypes : list [simple,tr2e, etc.]
        packetSizes : list [64,128, etc.]
        realisticTraffics : list [nick names of pcap file, e.g., wifi.
        In case of 'wifi', a PCAP file named nfpa.wifi.pcap should be placed
        in MAIN_ROOT/PCAP folder, since nfpa will look after the file
        in this manner!
        LOG_PATH String - for storing where to save log files, which is set to
        MAIN_ROOT/log
        app_start_date String - unix timestamp as String storing the start of 
        the application
    '''


    def __init__(self):
        '''
        Constructor
        '''

        #dictionary for storing configuration parameters read from config file
        self._config = {}
        #read config
        tmp_cfg = rwcf.readConfigFile("nfpa.cfg")
        #check whether it was successful
        if tmp_cfg[0] == True:
            self._config = tmp_cfg[1]
        else:
            print(tmp_cfg[1])
            exit(-1)


        
        #create a list of dictionary indexes for easier iterating though data
        #actually, these are the measured data units/names stored and placed in
        #gnuplot file as well, therefore iterating through this dictionary eases
        #the code via not accessing the fields explicitly
        #sp - sent pps, rb - recv bps, etc.
        self._config['header_uni'] = ['sent_pps', 'recv_pps', 'miss_pps', 
                                      'sent_bps', 'recv_bps', 'diff_bps']
        
        self._config['header_bi']  = ['sent_pps_bidir', 'recv_pps_bidir', 'miss_pps_bidir',
                                      'sent_bps_bidir', 'recv_bps_bidir', 'diff_bps_bidir']
        
        self._config['helper_header'] = ['min', 'avg', 'max']



        self.log = l.getLogger( self.__class__.__name__,
                                self._config['LOG_LEVEL'],
                                self._config['app_start_date'],
                                self._config['LOG_PATH'])

        # self.log=logging.getLogger(self.__class__.__name__)


        # set supported control APIs
        self._config["controllers"] = ("openflow")


        
        #create an instance of database helper and store it in config dictionary
        self._config["dbhelper"] = SQLiteDatabaseAdapter(self._config)



        # parse config params
        configSuccess = self.checkConfig()
        if (configSuccess == -1):
            return -1


        #calculate time left
        self.calculateTimeLeft()
        
        #create res dir
        self.createResultsDir()
        

        #assemble pktgen command
        self.assemblePktgenCommand()
          
        #create symlinks for lua files
        self.createSymlinksForLuaScripts()


    def checkDirectoryExistence(self, dir):
        '''
        This functions checks whether the directory dir exists
        :param dir: the path to the directory
        :return: False - if not, True - if yes
        '''
        if not (os.path.isdir(dir)):
            self.log.error("Directory \'(%s)\' does not exists!" % dir)
            return False
        return True

    def checkFileExistence(self, filename):
        '''
        This function checks whether the given filename exists
        :param filename: the path to the file
        :return:  False - if not, True - if yes
        '''
        if not (os.path.isfile(filename)):
            self.log.error("File (%s) does not exists!" % filename)
            return False
        return True


    def checkConfig(self):
        '''
        This function will check the set config parameters and correctness, i.e.,
        whether paths to binaries exist, other config parameters have the right
        type, etc. 
        return - Int: -1 error, 0 otherwise 
        '''
        #check pktgen's directory existence
        if not self.checkDirectoryExistence(self._config["PKTGEN_ROOT"]):
            return -1
            
        #ok, pktgen dir exists, check whether the binary exists as well
        pktgen_bin = self._config["PKTGEN_ROOT"] + "/" + \
                     self._config["PKTGEN_BIN"]
        if not self.checkFileExistence(pktgen_bin):
            return -1
        
        #check whether nfpa's MAIN_ROOT is set correctly
        if not self.checkDirectoryExistence(self._config["MAIN_ROOT"]):
            return -1


        #check whether NFPA is going to setup the flows in the vnf
        #make parameter to lowercase
        self._config["control_nfpa"] = self._config["control_nfpa"].lower()
        if self._config["control_nfpa"] == "true":
            #make it a boolean variable for easier checks later
            self._config["control_nfpa"]=bool("true") #this makes it True
        elif self._config["control_nfpa"] == "false":
            # make it a boolean variable for easier checks later
            self._config["control_nfpa"]=bool(0) #this makes it False
        else:
            #type
            self.log.warn("contron_nfpa has a typo (%s) -- fallback to False" %
                          self._config['control_nfpa'])
            self._config["control_nfpa"] = bool(0)  # this makes it False


        #if control_nfpa is True we check the other related parameters, otherwise
        #these are unnecessary
        if self._config["control_nfpa"]:
            #convert it first to lowercase
            self._config["control_vnf"] = self._config["control_vnf"].lower()
            #check whether it is supported
            if self._config["control_vnf"] not in self._config["controllers"]:
                self.log.error("The control_vnf (%s) is not supported!")
                self.log.error("Disable control_nfpa in nfpa.cfg and configure your vnf manually")
                exit(-1)

            #check paths to the binaries
            #directory
            if not self.checkFileExistence(self._config["control_path"]):
                return -1


        
        #### --- === check PKTGEN port masks and core masks === --- ####
        #store cpu_port_assign in temporary variable 'a'
        a = self._config["cpu_port_assign"]
        #var a contains a string like this "2.0,3.1"
        #remove head and tail double quotes
        a = a.replace('"','')
        tmp_max_core_mask = 0
        digits = []
        for i in a.split(','):
           
            #this produces ["2.0","3.1"]
            tmp_i = i.split('.')[0]
            self.log.debug("next desired core num: " + str(tmp_i))

            #check whether mutliple core was set (try to convert it to int)
            try:
                int_tmp_i = int(tmp_i)
                #this produces ['"','2','3']
                #put them to digits list
                digits.append(copy.deepcopy(int_tmp_i))
                if int(int_tmp_i) > tmp_max_core_mask:
                    #get the maximum of cpu core masks
                    tmp_max_core_mask = int(int_tmp_i)
            
            ### MULTI CORE HANDLING ###    
            except ValueError as e:
                self.log.info("Multicore coremask has been recognized: %s" % 
                              str(tmp_i))
                #this case is when multiple cores wanted to be used
                
                #split by ':' -> this results in at least a 1 element long
                #list. If there was no ':', then one element long list,
                #otherwise two elemets will be in the list
                #first, remove brackets
                tmp_i=tmp_i.replace('[','')
                tmp_i=tmp_i.replace(']','')
                multi_core_list = tmp_i.split(":")
                
                #~ print multi_core_list
                for i in range(0,len(multi_core_list)):
                #~ tmp_bool = false #indicator of found ':'
                #~ if len(multi_core_list) == 1:
                    #~ #same as before, only olny element
                    #~ multi_core = multi_core_list[0]
                    #~ tmp_bool = true
                #~ else:
                    #~ tmp_bool = false
                #parsing only if core mask is set like [2-4]
                #cut the first and last char, since they are rectangular 
                #parentheses (brackets)
                    multi_core = multi_core_list[i]
                    #~ print multi_core
                    #~ multi_core = copy.deepcopy(multi_core[1:(len(multi_core)-1)])
                    #~ print multi_core
                    #ok, we need to split the string according to the dash between
                    #the core numbers 2-4

                    try:
                      min_c = int(multi_core.split('-')[0])
                    except ValueError as e:
                      self.log.error("cpu_core_mask (%s) is wrong! Isn't there any typo?" % a)
                      self.log.error("Python error: %s" % e)
                      exit(-1)
                    
                    #if there is no range specified, i.e., there is no dash 
                    #then we won't get two separate pieces
                    if len(multi_core.split('-')) > 1:
                      max_c = int(multi_core.split('-')[1])
                    else:
                      #if no dash was specified, let the max_c be simply
                      #min_c as well -> it won't cause problems later
                      max_c = min_c
              
                    for mc in range(min_c, max_c+1):
                        #append core nums to digits
                        digits.append(copy.deepcopy(int(mc)))
                        #update max core num if necessary (required later
                        #for checking the length of the specified bit 
                        #mask for CPU core
                        if int(mc) > tmp_max_core_mask:
                            tmp_max_core_mask = int(mc)

        #alright, we got max core mask needs to be used
        #now, check whether the the main cpu_core_mask variable covers it
        #calculate how many bits are required for cpu_core_mask
        #store cpu_core_mask in temporary variable 'b'
        b = self._config["cpu_core_mask"]
        #calculate the required bits
        bin_core_mask = bin(int(b,16))[2:]
        bit_length = len(bin_core_mask)

        #this only checks whether the bitmask is long enough
        if tmp_max_core_mask > bit_length-1:
            #this means that cpu_core_mask is not set correctly, since
            #fewer core are reserved, than is required for assignment
            #define in cpu_port_assign
            self.log.error("Wrong core mask was set!")
            self.log.error("max core id (%d) assigned to ports is the (%dth)"\
                         " bit, however core mask ('%s') only reserves (%d) "\
                         "bits" % (tmp_max_core_mask,
                                   tmp_max_core_mask+1,
                                   b,
                                   bit_length))
            self.log.error("!!! %d > %d !!!" % (tmp_max_core_mask+1,bit_length))
            #~ self.log.error("Core ids to be used:")
            #~ self.log.error(digits)
            #~ self.log.error("Reserved cores:")
            #~ self.log.error(bin_core_mask)
            return -1
        #we need to check the correctness as well, as are the corresponding
        #bits are 1
        bin_core_mask = list(bin_core_mask)

#         self.log.debug(str(bin_core_mask))
        #reverse list for getting the right order -> will be easier to access
        #and check bits via length of the list
        bin_core_mask.reverse()

        self.log.debug("Required CPU ids  :" + str(digits))
        #starts from core num 0 on the left
        self.log.debug("Reserved Core mask:" + str(bin_core_mask) + " (reversed)")

        #check correctness (whether corresponding bit is set in core mask)
        for bit in digits:
            cpu_id = bin_core_mask[int(bit)]
            if(cpu_id != '1'):
                self.log.error("Core mask is not set properly.")
                self.log.error("Required CPU id (%d) is not enabled in core"\
                             " mask!" % int(bit))
                self.log.error("core mask: %s" % str(bin_core_mask))
                self.log.error("Required digits needs to be enabled: %s" %
                             str(digits))
                return -1
        
        self.log.info("CORE MASKS SEEM TO BE CORRECT!")


        #check port_mask
        pm = self._config["port_mask"]
        #~ print(pm)
        if (pm != '1' and pm != '3'):
            #port mask is mis-configured
            self.log.error("Port mask could be only 1 or 3!")
            return -1
        else:
            if(pm == '1'):
                self.log.debug("PORT MASK IS 1")
#                 self.log.debug("sendPort: %s" % self._config["sendPort"])
#                 self.log.debug("recvPort: %s" % self._config["recvPort"])
                if(self._config["sendPort"] != '0' and 
                   self._config["recvPort"] != '0'):
                    self.log.error("In case of Port mask 1, sendPort and " +\
                                    "recvPort need to be 0!")
                    return -1
 
        #port mask is ok, sendPort and recvPort could be different, for instance,
        #dpdk and/or pktgen is enabled for multiple interfaces, but you only need
        #2 interfaces from them
#         else:
             #port_mask is set correctly, we need to check sendPort and recvPort
#             #accordingly
#             if(pm == 1):
#                 #port mask is 1
#                 if(sendPort != 0 and recvPort != 0):
#                     self.log.error("In case of Port mask 1, sendPort and " +\
#                                    "recvPort need to be 0!")
#                     self.log.error("EXITING...")
#                     exit(-1)
#             else:
#                 #port mask is 3
#                 if(sendPort > 1 and recvPort > 1):
#                     #ports can only be 0 or 1
#                     self.log.error("sendPort and recvPort could only be 0 or 1")
#                     self.log.error("EXITING...")
#                     exit(-1)
#                 else:
#                     #port are in the correct range
#                     if (sendPort == recvPort):
#                         self.log.error("sendPort and recvPort must be " +\
#                                        "different in case of port_mask: %s" % 
#                                        pm)
#                     self.log.error("EXITING...")
#                     exit(-1)
        #PORT MASK = OK


        #Check available hugepages
        # first get the relevant information from the OS
        #commands for getting hugepage information
        free_hugepages_cmd = "cat /proc/meminfo |grep HugePages_Free"
        total_hugepages_cmd = "cat /proc/meminfo | grep HugePages_Total"
        hugepage_size_cmd = "cat /proc/meminfo|grep Hugepagesize"

        #get the data - invoce.check_retval will analyze the return values as well, and as a third
        #parameter, we need to pass him our self.log instance to make him able to write out error messages
        free_hugepages = (invoke.invoke(command=free_hugepages_cmd,
                                        logger=self.log))[0]
        total_hugepages = (invoke.invoke(command=total_hugepages_cmd,
                                        logger=self.log))[0]
        hugepage_size = (invoke.invoke(command=hugepage_size_cmd,
                                        logger=self.log))[0]

        #get the second part of the outputs
        free_hugepages = free_hugepages.split(":")[1]
        total_hugepages = total_hugepages.split(":")[1]
        tmp_hugepage_size = copy.deepcopy(hugepage_size)
        #this looks like : "Hugepagesize:       2048 kB"
        #first we get the right part after the colon, then we remove the whitespaces from '       2048 kB.
        #Finally we split that again with whitespace, and gets the first apart of the list, which is 2048
        hugepage_size = hugepage_size.split(":")[1].strip().split(" ")[0]
        hugepage_size_unit = tmp_hugepage_size.split(":")[1].strip().split(" ")[1]
        #remove whitespaces
        free_hugepages = free_hugepages.strip()
        total_hugepages = total_hugepages.strip()
        hugepage_size = hugepage_size.strip()
        hugepage_size_unit = hugepage_size_unit.strip()

        #convert them to int
        free_hugepages = int(free_hugepages)
        total_hugepages = int(total_hugepages)
        #save total hugepages in self.config in order to calculate with it when the whole process'
        #estimated time is calculated - zeroiung 1 hugepage takes approx. 0.5s
        self._config["total_hugepages"]=total_hugepages

        hugepage_size = int(hugepage_size)
        #check wheter hugepage size unit is kB (until now (2016), there are defined in kB)
        if(hugepage_size_unit == "kB"):
            hugepage_size = hugepage_size/1024
        else:
            self.error("Cannot determine Hugepage size (check lines 364-405 in read_config.py to improve code) :(")
            return -1

        self.log.info("Hugepage size in MB: %s" % hugepage_size)
        self.log.info("Total hugepages: %s" % total_hugepages)
        self.log.info("Free hugepages: %s " % free_hugepages)

        if(total_hugepages == 0):
            self.log.error("Hugepages are not enabled? Check the output of: cat /proc/meminfo |grep -i hugepages")
            return -1

        if(free_hugepages == 0):
            self.log.error("There is no hugepages left! Check the output of: cat /proc/meminfo |grep -i hugepages")
            return -1

        # check socket_mem param if exists or not empty
        if (("socket_mem" in self._config) and (len(self._config["socket_mem"]) > 0)):
            # socket_mem parameter could have more than one important value due to the NUMA awareness
            # In this case, it is separated via a ',' (comma), so parse this value
            socket_mem_list = self._config["socket_mem"].split(',')
            # check if the required number of hugepages are enough
            usable_hugepages = free_hugepages * hugepage_size
            for i in socket_mem_list:
                # no NUMA config was set
                socket_mem = int(i)
                usable_hugepages-=socket_mem
            if(usable_hugepages >= 0):
                self.log.info("There were enough hugepages to initialize pktgen (req: %s (MB), avail:%s! (MB)" % (self._config["socket_mem"],
                                                                                                      (free_hugepages*hugepage_size)))
            else:
                self.log.error("Insufficient hugepages! Your required setting '%s' (MB) does not correspond to the available " \
                               "resources %s (MB)" %(self._config["socket_mem"], (free_hugepages*hugepage_size)))
                self.log.error("Check the output of: cat /proc/meminfo |grep -i hugepages")
                return -1


    #check biDir param
        try:
            self._config["biDir"] = int((self._config["biDir"]))
            #check the value
            if((self._config["biDir"] != 0) and (self._config["biDir"] != 1)):
                self.log.error("biDir (%s) can only be 1 or 0!" % 
                             self._config["biDir"])
                return -1
        except ValueError as ve:
            self.log.error("biDir (%s) IS NOT A NUMBER!!!" % self._config["biDir"])
            return -1

        #check pcap files
        #check config file consistency (traffic types and packet sizes)
        if not self.checkPcapFileExists():
            #there is no pcap file for the given packet size and traffic type
            #or there is no pcap file for realistic traffics
            return -1
            
        warning = False
        #check whether packetsize is set, but no synthetic traffictype is set
        if self._config['packetSizes'] and not self._config["trafficTypes"]:
            self.log.warning("Packetsize(s) set without synthetic traffic type(s)")
            self.log.warning("SKIPPING...")
            warning = True
            time.sleep(1)
            
        elif not self._config['packetSizes'] and self._config["trafficTypes"]:
            self.log.warning("Synthetic traffic type(s) set without packet size(s)")
            self.log.warning("SKIPPING...")
            warning = True
            time.sleep(1)
        if warning and not self._config['realisticTraffics']:
            self.log.error("Nothing to DO! Check configuration!")
            return -1
            
        self.log.debug("cpu_make: %s" % self._config['cpu_make'])    
        self.log.debug("cpu_model: %s" % self._config['cpu_model'])
        self.log.debug("nic_make: %s" % self._config['nic_make'])
        self.log.debug("nic_model: %s" % self._config['nic_model'])
        self.log.debug("virtualization: %s" % self._config['virtualization'])
        self.log.debug("vnf_name: %s" % self._config['vnf_name'])
        self.log.debug("vnf_driver: %s" % self._config['vnf_driver'])
        self.log.debug("vnf_driver_version: %s" % 
                        self._config['vnf_driver_version'])
        self.log.debug("vnf_version: %s" % self._config['vnf_version'])
        self.log.debug("vnf_function: %s" % self._config['vnf_function'])
        self.log.debug("vnf_num_cores: %s" % self._config['vnf_num_cores'])
        self.log.debug("vnf_comment: %s" % self._config['vnf_comment'])
        self.log.debug("username: %s" % self._config['username'])
        self.log.debug("control_nfpa: %s" % self._config['control_nfpa'])
        self.log.debug("control_vnf: %s" % self._config['control_vnf'])
        self.log.debug("control_path: %s" % self._config['control_path'])
        self.log.debug("control_args: %s" % self._config['control_args'])
        self.log.debug("control_mgmt: %s" % self._config['control_mgmt'])
        self.log.debug("email_service: %s" % self._config['email_service'])
        if self._config['email_service'].lower() == "true":
            self.log.debug("email_from: %s" % self._config['email_from'])
            self.log.debug("email_to: %s" % self._config['email_to'])
            self.log.debug("email_server: %s" % self._config['email_server'])
            self.log.debug("email_port: %s" % self._config['email_port'])
            self.log.debug("email_username: %s" % self._config['email_username'])
            self.log.debug("email_password: HIDDEN to not store in logs")
            self.log.debug("email_timeout: %s" % self._config['email_timeout'])


         

        self._config['dbhelper'].connect()
        #check user
        self._config['dbhelper'].getUser(self._config['username'])
        self._config['dbhelper'].disconnect()
        
        return 0



    def calculateTimeLeft(self):
        '''
        This function will calculate the estimated time required for the
        whole measurement and prints out at the beginning
        '''
        # Each variable represents time in seconds
        #initializing and biringing up the interface takes approx. 5 secs, while
        #zeroing one hugepage takes aprrox. 0.5s
        time_to_start_pktgen = 5 + (self._config["total_hugepages"] * 0.5)

        # number of packet sizes
        num_ps = len(self._config["packetSizes"])
        #         self.log.debug("packetsizes: %d" % num_ps )
        # one measurement lasts for measurementDuration + 2 times 3 seconds
        # as heating up and cooling down

        # if measurementDuration is set to infinite via 0, we don't
        # calculate remaing time, just set it to 0 and return!
        if int(self._config['measurementDuration']) == 0:
            self._config['ETL_seconds'] = 0
            # convert it to datetime
            sum = str(datetime.timedelta(seconds=0))
            # store Estimated Time Left in the config dictionary to access it later
            self._config['ETL'] = sum
            return

        measurement = (int(self._config['measurementDuration']) + 6)
        iteration = int(self._config['measurement_num'])

        # 'simple' should be handled different, since there is no pktgen restart
        # among packet sizes
        # smt = simple measurement time
        smt = 0
        # number of synthetic traffics
        num_synthetic = len(self._config["trafficTypes"])
        if "simple" in self._config['trafficTypes']:
            smt = time_to_start_pktgen * iteration
            smt += num_ps * measurement * iteration
            # remove 'simple' from latter calculation
            num_synthetic -= 1

        synthetic_time = 0
        # calculate only if there are synthetic traffic set
        if num_synthetic > 0:
            # sum up synthetic time
            # measurement time
            synthetic_time = num_synthetic * num_ps * measurement
            # time of pktgen restarts
            synthetic_time += num_synthetic * num_ps * time_to_start_pktgen
            # how many times the whole process is running
            synthetic_time *= iteration


            # number of realistic traffic
        num_realistic = len(self._config['realisticTraffics'])

        realistic_time = 0
        # calculate only if there are realistic traffic set
        if num_realistic > 0:
            # measurement time
            realistic_time = num_realistic * measurement
            # time of pktgen restarts
            realistic_time += num_realistic * time_to_start_pktgen
            # how many times the whole process is running
            realistic_time *= iteration

            #         self.log.debug("Estimated time for simple traffic: %d" % smt)
            #         self.log.debug("Estimated time for synthetic traffic: %d" % synthetic_time)
            #         self.log.debug("Estimated time for realistic traffic: %d" % realistic_time)

        sum = smt + synthetic_time + realistic_time
        # add additional 5 seconds for analyzing results
        sum += 5
        self._config['ETL_seconds'] = sum
        # convert it to datetime
        sum = str(datetime.timedelta(seconds=sum))

        # store Estimated Time Left in the config dictionary to access it later
        self._config['ETL'] = sum

    def createResultsDir(self):
        '''
        This function creates the results dir according to the config
        '''
        #read path from config
        path = self._config["MAIN_ROOT"] + "/" + self._config["RES_DIR"]
        #append a new value to config dictionary
        self._config['RES_PATH'] = path
        
        if not os.path.exists(path):
            os.makedirs(path)


    def createSymlinksForLuaScripts(self):
        '''
        This function creates symlinks in pktgen's main root directory that
        point to nfpa_simple.lua and nfpa_traffic.lua
        These symlinks are always freshly generated and old one are deleted.
        '''
        #remove all existing nfpa lua scripts
        self.log.info("Remove old symlinks...")
        remove_cmd = "rm -rf " + self._config["PKTGEN_ROOT"] + "/nfpa_simple.lua"  
        invoke.invoke(command=remove_cmd,
                      logger=self.log)


        remove_cmd = "rm -rf " + self._config["PKTGEN_ROOT"] + "/nfpa_traffic.lua"                       
        invoke.invoke(command=remove_cmd,
                      logger=self.log)

        
        remove_cmd = "rm -rf " +  self._config["PKTGEN_ROOT"] + \
                     "/nfpa_realistic.lua"                       
        invoke.invoke(command=remove_cmd,
                      logger=self.log)

        
        self.log.info("DONE")
        #create symlink for nfpa_simple.lua
        self.log.info("create symlinks")
        symlink_cmd = "ln -s " + self._config["MAIN_ROOT"] + \
                "/lib/nfpa_simple.lua " + self._config["PKTGEN_ROOT"] + \
                "/nfpa_simple.lua"
        self.log.info(symlink_cmd)  
        invoke.invoke(command=symlink_cmd,
                      logger=self.log)

        #create symlink for nfpa_traffic.lua
        self.log.info("create symlinks")
        symlink_cmd = "ln -s " + self._config["MAIN_ROOT"] + \
                "/lib/nfpa_traffic.lua " + self._config["PKTGEN_ROOT"] + \
                "/nfpa_traffic.lua"
        self.log.info(symlink_cmd)  
        invoke.invoke(command=symlink_cmd,
                      logger=self.log)

         
        #create symlink for nfpa_realistic.lua
        self.log.info("create symlinks")
        symlink_cmd = "ln -s " + self._config["MAIN_ROOT"] + \
                "/lib/nfpa_realistic.lua " + self._config["PKTGEN_ROOT"] + \
                "/nfpa_realistic.lua"
        self.log.info(symlink_cmd)  
        invoke.invoke(command=symlink_cmd,
                      logger=self.log)

    
            
    def checkPcapFileExists(self):
        '''
        This functions checks whether a pcap file exists for the desired
        packet size and traffic type
        (called from checkConfig())
        '''
        
        simple_traffic_set = False
        if self._config["trafficTypes"]:
            #only if any traffic type was set
            for traffic_type in self._config["trafficTypes"]:
                #there is no pcap file for simple scenarios, skipping file check
                if traffic_type == "simple":
                    self.log.info("Simple traffic type was set")
                    simple_traffic_set = True
                    continue

                        
                
                else:
                    self.log.info("Checking synthetic traffictype: %s" % traffic_type)
                    for packetSize in self._config["packetSizes"]:               
                        
                        #special traffic type for ul-dl traffic
                        self.log.info("Special bidirectional"
                                          " traffictype: %s ?" % traffic_type)
                        if sbtc.checkSpecialTraffic(traffic_type):
                            self.log.info("### SPECIAL TRAFFICTYPE FOUND - "
                                          "USING DIFFERENT PCAPS FOR DIFFERENT"
                                          "PORTS ###")
                            tmp_tt = sbtc.splitTraffic(traffic_type)
                            #check for the first one
                            pcap1 = self._config["MAIN_ROOT"].strip() 
                            pcap1 += "/PCAP/nfpa." + tmp_tt[0] + "." 
                            pcap1 += packetSize + "bytes.pcap"
                            #check for the second one
                            pcap2 = self._config["MAIN_ROOT"].strip() 
                            pcap2 += "/PCAP/nfpa." + tmp_tt[1] + "." 
                            pcap2 += packetSize + "bytes.pcap"
                            
                            #check pcap file existance for both of them
                            self.log.info("check pcap file existence %s " % 
                                          pcap1)
                            ok1 = os.path.isfile(pcap1)
                            
                            self.log.info("check pcap file existence %s " % 
                                          pcap2)
                            ok2 = os.path.isfile(pcap2)
                            
                            #if any pcap is missing, then nothing can be done
                            #with this setting
                            if ok1 and ok2:
                                ok = True
                            else:
                                ok = False
                                
                        
                        else:
                            self.log.info("-------------------------------- NO")
                            #no special ul-dl traffic type was set
                            pcap = self._config["MAIN_ROOT"].strip()
                            pcap += "/PCAP/nfpa." + traffic_type + "." 
                            pcap +=  packetSize + "bytes.pcap"
                            self.log.info("check pcap file existence %s " % pcap)
                            #if special traffic type was set, check the existence of the
                            #corresponding pcap files
                            ok = os.path.isfile(pcap)
                        
                        if not ok:
                            #PCAP file not found
                            self.log.error("Missing PCAP file for traffic type: %s "
                                         "and packet size: %s not exists" % 
                                         (traffic_type, packetSize))
                            self.log.error("Are you sure you have the corresponding "
                                         "PCAP file(s) in directory: %s/PCAP ?" % 
                                         self._config["MAIN_ROOT"])

                            return False
                        else:
                            self.log.info("[FOUND]")
             
        
        #check for realistic traffics
        if(self._config["realisticTraffics"]):
            self.log.info("Realistic Traffics was defined...")
            for realistic in self._config["realisticTraffics"]:
                
                ok = False
                #special traffic type for ul-dl traffic
                self.log.info("Checking for special bidirectional"
                                  " traffictype: %s" % realistic)
                if sbtc.checkSpecialTraffic(realistic):
                    self.log.info("### SPECIAL TRAFFICTYPE FOUND - "
                                  "USING DIFFERENT PCAPS FOR DIFFERENT"
                                  "PORTS ###")
                    tmp_tt = sbtc.splitTraffic(realistic)
                    #check for the first one
                    pcap1 = self._config["MAIN_ROOT"].strip() 
                    pcap1 += "/PCAP/nfpa." + tmp_tt[0] + ".pcap" 
                    
                    #check for the second one
                    pcap2 = self._config["MAIN_ROOT"].strip() 
                    pcap2 += "/PCAP/nfpa." + tmp_tt[1] + ".pcap"
                    
                    #check pcap file existance for both of them
                    self.log.info("check pcap file existence %s " % 
                                  pcap1)
                    ok1 = os.path.isfile(pcap1)
                    
                    self.log.info("check pcap file existence %s " % 
                                  pcap2)
                    ok2 = os.path.isfile(pcap2)
                    
                    #if any pcap is missing, then nothing can be done
                    #with this setting
                    if ok1 and ok2:
                        ok = True
                    else:
                        ok = False
                        
                        
                else:
                    #assemble complete path for realistic traffic   
                    pcap = self._config["MAIN_ROOT"] + "/PCAP/nfpa." +\
                                     realistic + ".pcap"
                    self.log.info("Looking for %s" % pcap)
                    ok = os.path.isfile(pcap)
                  
                    
                if not ok:
                    #PCAP file not found
                    self.log.error("Missing PCAP file for traffic type: %s "
                                  % realistic)
                    self.log.error("Are you sure you have the corresponding "
                                 "PCAP file(s) in directory: %s/PCAP ?" % 
                                 self._config["MAIN_ROOT"])
                    return False
                else:
                    self.log.info("[FOUND]")
                    

        #everything is good, pcap files were found for the given 
        #packetsizes and traffic types (including realistic ones if they were 
        #set)
        return True
          
            
    def getConfig(self):
        '''
        This function returns the private variable self._config, which
        holds the parsed configurations as a dictionary
        '''
        return self._config
    
    
    def assemblePktgenCommand(self):
        '''This functions assemble the Pktgen main command from config'''
        pktgen = self._config["PKTGEN_BIN"] 
        pktgen += " -c " +  self._config["cpu_core_mask"]
        pktgen += " -n " +  self._config["mem_channels"]
        if (("socket_mem" in self._config) and (len(self._config["socket_mem"]) > 0)):
            pktgen += " --socket-mem " + self._config["socket_mem"]
        if(("other_dpdk_params" in self._config) and (len(self._config["other_dpdk_params"]) > 0)):
            pktgen += " " + self._config["other_dpdk_params"]
        pktgen += " -- -T"
        pktgen += " -p " + self._config["port_mask"]
        pktgen += " -P "
        pktgen +=  " -m " + self._config["cpu_port_assign"] 
#         self.log.debug(pktgen)
        return pktgen
        
    
    def generateLuaConfigFile(self, traffic_type, packet_sizes, realistic):
        '''
        This function will create a custom config file for Pktgen LUA script
        Traffic type needs to be set in each call, thus lua script will know
        the scenario and will know under which name the results files need to 
        be saved. In each traffic type this cfg file needs to be freshly created,
        so this function is called for each traffic type
        traffic_type String - e.g. tr2e
        packet_sizes List - in order to indicate somehow to pktgen lua script
        what is it doing at any moment. in simple scenarios, we should set a 
        complete list of packet sizes, however, in special traffic types (pcap
        file with predefined packet size, e.g., PCAP/nfpa.tr2e.64bytes.pcap), 
        we indicate in the config file what is the packetsize it is using
        
        traffic_type string - traffic type
        
        packet_sizes list - desired packet sizes (common list is only used if 
        simple traffic type was set. Otherwise, a list with one element is set 
        for a given traffic type
        
        realistic string - The name of the realistic traffic type 
        '''
        #open config file in pktgen's root directory
        cfg_file_name = self._config["PKTGEN_ROOT"] + "/nfpa.cfg" 
        #open file for writing (it will erased each time 
        lua_cfg_file = open(cfg_file_name, 'w')
        
        #first, print out header info
        lua_cfg_file.write("#THIS FILE IS GENERATED FROM nfpa MAIN APP ")
        lua_cfg_file.write("FOR EACH START OF THE APP!\n")
        lua_cfg_file.write("#DO NOT MODIFY IT MANUALLY....SERIOUSLY!\n")
        lua_cfg_file.write("#ON THE OTHER HAND, IT WON'T TAKE ANY EFFECT!\n")
        lua_cfg_file.write("#THESE ARE CONFIGURATIONS FOR PKTGEN LUA SCRIPT!\n")
        lua_cfg_file.write("\n\n")

        #Check whether infinite measurementDuration was set
        if int(self._config["measurementDuration"]) == 0:
          self.log.info("### === INFINITE MEASUREMENT WAS SET === ###")
        #write out measurement duration
        lua_cfg_file.write("measurementDuration=" + 
                           self._config["measurementDuration"])
        
        lua_cfg_file.write("\n\n")
        
        #write out sending port
        lua_cfg_file.write("sendPort=" + self._config["sendPort"])
        lua_cfg_file.write("\n\n")
        #write out receiving port
        lua_cfg_file.write("recvPort=" + self._config["recvPort"])
        lua_cfg_file.write("\n\n")
        
        #write out bi-direction request
        lua_cfg_file.write("biDir=" + str(self._config["biDir"]))
        lua_cfg_file.write("\n\n")
        
        
        #write out packetSizes if set
        if packet_sizes is not None:
            for i in packet_sizes:
                lua_cfg_file.write("packetSize=" + i)
                lua_cfg_file.write("\n")
            lua_cfg_file.write("\n\n")

# 
        #write out trafficTypes if set
        if traffic_type is not None:
            lua_cfg_file.write("trafficType=" + traffic_type)
            lua_cfg_file.write("\n\n")


        #write out realistic traffic name
        #if not set, do not write out. 
        if realistic is not None:
            lua_cfg_file.write("realisticTraffic=" + realistic)
            lua_cfg_file.write("\n\n")

        
        lua_cfg_file.write("\n")
     
        #close file
        lua_cfg_file.close()

        

        
        
        
        
        
        
        
        
        
                
