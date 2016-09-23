'''
These helper functions are used by ReadConfig class and WEBNFPA class
'''
import datetime
import time
import os
config = {}

def readConfigFile(config_file):
    '''
    This function reads the config_file set as argument and creates a 
    dictionary containing the settings accordingly.
    returns Tuple (Bool, object) - False, msg - something went wrong and error
                                 message is also passed back
                                 - True, config - Config file reading was
                                 success, and the second element is the 
                                 dictionary itself
    '''
    #the following list variables will also stored in _config, with keys
    #as packetSize/trafficType and values as lists of the desired
    #packetSize and trafficType read from config
    #list for packetSizes
    packetSizes = []
    #list for trafficTypes
    trafficTypes = []
    #list for realistic traffics
    realisticTraffics = []
    
    config['version'] = "v2.0 alpha"
    
    
    
    
    #Logger class will check whether DEBUG is set correctly
    #DEBUG param will later updated
    
    print("Reading config file")
    with open(config_file, 'r') as lines:
        line_num = 1
        for line in lines:
            #remove blank spaces
            line = line.strip()
            #removed blank lines
            if line:
                #omit commented lines                    
                if not (line.startswith("#",0,1)):
                    #split config params
                    key_value = line.split("=")
                    
                    #handling packetSize params
                    if key_value[0] == "packetSize":
                        packetSizes.append(key_value[1])
                    #handling trafficType params
                    elif key_value[0] == "trafficType":
                        trafficTypes.append(key_value[1])
                        
                        
                    #handling realistic traffics if set
                    elif key_value[0] == "realisticTraffic":
                        #we convert it to string at this very first point
                        #since they were used as file names that should be
                        #strings for easy handling
                        realisticTraffics.append(str(key_value[1]))
                        
                    else:
                        try:
                            key = key_value[0]
                            value = key_value[1]
                            for e,i in enumerate(key_value):
                                if e < 2:
                                    continue
                                
                                #more than one '=' is present in one line
                                #let's concatenate the rest
                                value += "=" + key_value[e]
                            #handling line splitting! If something went
                            #wrong during setting up the cfg file, the 
                            #application will quit
                            config[key]=value                            
                                
                        
                        except IndexError as ie:
                            msg=str("Error during parsing %s!\n" % config_file)
                            msg += str("May a comment sign is missing at " +\
                                      "line '#%d'" % line_num)
                            return (False, msg)
            line_num += 1
     
     
                        
    #append packetSizes and trafficTypes lists to config dict

    #some packet sizes were set
    config["packetSizes"] = packetSizes
    #some traffic type were set
    config["trafficTypes"] = trafficTypes
    #append realisticTraffics as well to config dict
    config["realisticTraffics"] = realisticTraffics

    
    config["LOG_PATH"] = os.getcwd() + "/log/"
    print("Logging directory will be: %s" % config["LOG_PATH"])
    
    
    #get current timestamp8
    ts = time.time()        
    config['app_start_date'] = str(ts)
    
    # calculateTimeLeft()
    
    
    return (True,config)


def getConfigComments():
    #this dictionary stores the helping comments for the config vars
    #used to show it on the web-gui and write it as comments to config file
    config_comment = {
                    'username': 
                    "The username you will use later for sharing and " +\
                    "accessing the central web site. Register first at" +\
                    " http://ios.tmit.bme.hu/nfpa to take the " +\
                    "desired username.",
                    
                    'PKTGEN_ROOT':
                    "The root directory of your installed PktGen. Required "+\
                    "for copying helper scripts to control PktGen. OMIT THE "+\
                    "LAST '/'.",
                    
                    'PKTGEN_BIN':
                    "The path to PktGen binary under the above-set Pktgen's " +\
                    "root directory. So, pay attention that this is a " +\
                    "relative path. OMIT THE LAST '/'." ,
                    
                    'MAIN_ROOT':
                    "The root directory of NFPA. It is necessary to set it " +\
                    "correctly, since libraries and other directories are " +\
                    "accessed relatively to this. OMIT THE LAST '/'." ,
                    
                    'RES_DIR':
                    "The generated charts (plotted by Gnuplot) will be " +\
                    "saved under this directory. It will be created (if not " +\
                    "exists) under the above-set NFPA's main root." ,
                    
                    'LOG_LEVEL':
                    "The desired logging level. Log files are generated " +\
                    "in log/ directory under the above-set NFPA's main root."+\
                    "levels: DEBUG, INFO, WARNING, ERROR, CRITICAL (incase " +\
                    "sensitive)",
                    
                    'cpu_core_mask':
                    "CPU Core Mask in HEX. For instance, 'e' means 1110 in " +\
                    "binary indicating that the usable CPU cores' ids are " +\
                    "1,2,3. Or if you set 2e, it means that you want to use " +\
                    "core 5,3,2,1. Note that 1 core per NIC port should be " +\
                    "allocated.",

                    'mem_channels':
                    "Number of memory channels to use (e.g., 4). " +
                    "If not sure, use 4!",

                    'socket_mem':
                    "Size of hugepages to be used, for instance 1024. Note that for " + \
                    "using NUMA nodes this setting is like 1024,1024 - Setup for both sockets!" +\
                    "If all available hugepages are required, leave this field empty!",

                    'other_dpdk_params':
                    "For any further DPDK parameters, such as setting up a vhost " +\
                    "inteface, use this variable. Pay attention to type these additional " +\
                    "parameters properly, since NFPA is not going to check its correctness. "+\
                    "Leave it empty if NOT NEEDED!",

                    'port_mask':
                    "Port mask in HEX. For instance, '3' means (11 in BIN) " +\
                    "that two port will be used. This is the common case. " +\
                    "However, it is possible to use one port for sending and " +\
                    "receiving the traffic (for instance, if you have one 40G" +\
                    "NIC with only one port). In such cases port mask should " +\
                    "be '1' (01 in BIN) and accordingly both the sendPort " +\
                    "and recvPort (to be set later) should be '0'!",
                    
                    'cpu_port_assign':
                    'Set here which core to be used for which port ' +  
                    '(in decimal). If not sure, use "2.0,3.1".' + 
                    'To see how multicore assingment should be set, ' +
                    'go to http://pktgen.readthedocs.io/en/latest/usage_pktgen.html',
                    
                    'cpu_make':
                    "Set here the make of the CPU where the NF being " +
                    "tested is running, e.g., intel xeon, intel atom, " + 
                    "intel core, amd opteron.",
                    
                    'cpu_model':
                    "Set here the model of the CPU where the NF being " +
                    "tested is running, e.g., e5-2620, i7-4600u.",
                     
                    'nic_make':
                    "Set here the make of the NIC the NF being " +
                    "tested is using, e.g., intel, realtek, broadcom.",
                     
                    'nic_model':
                    "Set here the model of the NIC the NF being tested is " + 
                    "using, e.g., xl710, x710, 82599es, 8139.", 
                    
                    'port_type':
                    "Set up here the port type, e.g. 10G, 40G, 100M in the " +  
                    "highest INTEGER UNIT!!! So, USE 1_G instead of 1000_M!!!" +  
                    "This is important to show/plot the " + 
                    "theoretical results as well. Format: [bitrate]_[UNIT]" + 
                    "(case sensitive, use capitals for UNIT).",
                    
                    'virtualization':
                    "Set here, whether the NF being tested is VIRTUALIZED. " +
                    "If it is running on a pure bare-metal, set 'no'." + 
                    "Otherwise, set the virtualization type, e.g., lxc," + 
                    "docker, kvm, xen, virtualbox.",
                    
                    'vnf_name':
                    "Set here the NAME that the NF being tested is using, " +
                    "e.g., ovs, xdpd, my_own_NAT.",
                    
                    'vnf_version':
                    "Set here the VERSION of the NF being tested, " +
                    "e.g., 2.3.90, 0.7.5. In order to get to know the " + 
                    "version, for instance, in case of OVS type " + 
                    "ovs-vsctl -V.",
                    
                    'vnf_driver':
                    "Set here the DRIVER that the NF being tested is using, " +
                    "e.g., kernel, dpdk, netmap, odp.",
                    
                    'vnf_driver_version':
                    "Set here the VERSION of the used VNF's DRIVER, " + 
                    "e.g., 3.16 (for linux kernel driver, 1.7.1, 1.8.0, 2.0.0 "+
                    "(for DPDK driver).",
                    
                    'vnf_function':
                    "Set here the FUNCTION that the NF being tested is using, "+
                    "e.g., bridge, l2-switch, l3-router, vxlan, mpls. " + 
                    "Therefore, if only port forward rules are installed in " +
                    "the vnf, then use the term bridge. If l2-switch is set, " +
                    "then it is assumed that DMAC forwarding is used, i.e., " +
                    "corresponding L2 rules are installed in the flow table. " +
                    "It also infers that some traces, for instance, trXe and " +
                    "trXi could not be " +
                    "used in one measurement scenario. In such cases, please " +
                    "do two different measurements, even if the application " +
                    "is capable of doing both at the same time!", 
                    
                    'vnf_comment':
                    "Write here some comment to the function, for instance, " +
                    "ivshmem or userspace vhost for virtual ethernet, or " +
                    "other methods how the virtual interface are connected. " +
                    "So, anything you feel necessary to position the results.",
        
                    'pps_unit':
                    "Set up the unit of the desired packet/s results in order "+
                    "to obtain them more human readable. Set this to empty " +
                    "string if normal units shall be used!",
                    
                    'bps_unit':
                    "Set Bit/s unit here similarly to the above-set Packet/s.",
                    
                    'outlier_min_percentage':
                    "Define here the percentage of outlier results that " +
                    "should be omitted during calculating average, min and " +
                    "max values (format: 5% -> 0.05). Use 0 to take into " + 
                    "account all results!",
                    
                    'outlier_max_percentage':
                    "Define here the percentage of outlier results that " +
                    "should be omitted during calculating average, min and " +
                    "max values (format: 5% -> 0.05). Use 0 to take into " + 
                    "account all results!",

                    'control_nfpa':
                    "This feature is experimental currently. It only works with " +
                    "some predefined vnf_function use-cases, and traffic traces. " +
                    "It could be helpful if one needs a lot of common, " +
                    "reproducable measurements and does not want to configure " +
                    "the NFs in each case." +
                    "With this parameter you could indicate whether you want " +
                    "NFPA to configure your NF (true or false). If False " +
                    "the related configurations are omitted!",

                    'control_vnf':
                    "Configure here the kind of NF you have, e.g., openflow, vpp. " +
                    "Currently, only openflow is supported",

                    'control_path':
                    "Path to your control application's binary, for instance, " +
                    "in case of openflow, it needs to be the path to your " +
                    "ovs-ofctl binary. ",

                    'control_args':
                    "Additional arguments to control_path, for instance, OpenFlow " +
                    "version, i.e., -O OpenFlow13. Leave empty if not needed.",

                    'control_vnf_inport':
                    "Specify here the port ID of the remote VNF that will be used " +
                    "for input. Using 1 as inport, NFPA will update the flow rule " +
                    "files accordingly, i.e., in case of openflow it sets in_port=1 " +
                    "if such match exists in the flow table. " +
                    "You may think that in some cases, control_vnf_inport has no meaning, " +
                    "i.e., there won't be any match on the inport, but it is " +
                    "always NECESSARY to set it.",

                    'control_vnf_outport':
                    "Specify here the port ID of the remote VNF that will be used for output",

                    'control_mgmt':
                    "Connection management data to reach your VNF. " +
                    "In case of OVS, you need to start it with " +
                    "passive tcp connection set up as controller connections." +
                    "to do this, use the following command after OVS was started: "+
                    "ovs-vsctl set-controller ptcp:6634",

                    'packetSize':
                    "Define the desired packet sizes to be used. Note that " +
                    "in case of User defined synthetic traffic traces (traces "+
                    "that do not exists originally in NFPA's PCAP " + 
                    "repository), PCAP files need to be existed in PCAP " + 
                    "directory under NFPA's main root with the following " + 
                    "naming convention: nfpa.[your_special_name].[packetsize]" +
                    "bytes.pcap, for instance, nfpa.mySynthetic.64bytes.pcap. " +
                    "If you edit the config file manually, use numerous " +
                    "packetSize= lines if multiple packetSizes are needed to "+
                    "be used.", 
                    
                    'trafficType':
                    "Define here the desired syntethic traffic traces. Note " +
                    "that in case of User defined synthetic traffic traces " +
                    "(traces that do not exists originally in NFPA's PCAP " +
                    "directory under NFPA's main root with the following " + 
                    "naming convention: nfpa.[your_special_name].[packetsize]" +
                    "bytes.pcap, for instance, nfpa.mySynthetic.64bytes.pcap. " +
                    "If two traffic types are separated via 1 'PIPE (|)' " +
                    "then two different pcaps could be loaded to the two ports, "+
                    "so bidirectional measurement will be done. " +
                    "For this traffic type irrespectively whether the latter" +
                    "bidirectional property is 1 or 0. " + 
                    "On the other hand, biDir property works the same as it " + 
                    "worked for other traffic types. Similarly to packetSize, "+
                    "if you edit the config file manually, "+ 
                    "use numerous trafficType= lines if multiple trafficTypes "+
                    "are need to be used." ,
                    
                    'realisticTraffic':
                    "Set here your special realistic traffic trace, e.g., WIFI. "+ 
                    "NFPA will search for a pcap file in MAIN_ROOT/PCAP folder " +
                    "named nfpa.WIFI.pcap! So, name your pcap properly! " + 
                    "Since realistic traces are not restricted to one and only " +
                    "packet size, this setting is not related to the above-set " +
                    "Packet Sizes property. Similarly to packetSize, "+
                    "if you edit the config file manually, "+ 
                    "use numerous realisticTraffic= lines if multiple "+
                    "trafficTypes are need to be used." ,
                    
                    'measurement_num':
                    "Desired number of measurements. Pktgen will be started " +
                    "'measurement_num' times per trafficTypes per packetSize. "
                    "If not sure, use 2!",
                    
                    'measurementDuration':
                    "Time in seconds one measurement lasts, " + 
                    "For instance, 20 means that traffic will be generated " +
                    "for 20 seconds for each pre-set packet sizes, or even 20 " +
                    "seconds long will be the pcap-files replayed (in case of " +
                    "synthetic or realistic traffic traces). If not sure, use 20! " + 
                    "Use 0 to indicate an infinite, never ending measurement " + 
                    "for running in the background. In this case, measurement_num " + 
                    "argument has no meaning",
                    
                    'sendPort':
                    "The port desired to be used for sending. In case of " +
                    "bidirectional measurement, the word 'send' has no meaning, " +
                    "it is only for identifying the ports. If not sure, use 0!",
                     
                    'recvPort':
                    "The port desired to be used for receiving. In case of " +
                    "bidirectional measurement, the word 'receive' has no " +
                    "meaning, it is only for identifying the ports. " + 
                    "If not sure, use 1!", 
                    
                    'biDir':
                    "Set this to 1 for bi-directional (duplex) measurement, or "+
                    "set it to 0 for uni-directional scenario (simplex)."
                    }
    
    return config_comment


def splitter(comment):
    '''
    This function is devoted to split always the first closely-58 length part
    of the sentence and return it! This function will called recursively.
    comment String - the (remaining) part of the comment
    '''
    #we use  basically 58 char length lines, so split them to 58 length lines
    required_length = 58
    #this variable will store the closest approximation to 58 length
    splitter_approximater = 100
    
    index = 0
    best_index = 100
    
    #check whether the comment is long enough
    if len(comment) < required_length:
        return str("#%s" % comment)
    
    for c in comment:
        #look for whitespace
        if c == " ":
            #first look for white spaces in order to properly split sentences
            
            best = (required_length-index)
            if best < splitter_approximater:
                splitter_approximater = best
                best_index = index
        #break the loop if splitter_approximater is too big
        if splitter_approximater < 1:
            break 
        #increase index
        index += 1
    
    one_line = "#" + comment[0:best_index]
    return one_line

def splitToMultipleLines(comment, filepointer):
    '''
    This function is devoted to split the comments (find above) into
    multiple lines with correctly inserted comment lines to properly write out
    them into the confing file
    comment String - the comment to be writed out
    filepointer FilePointer - the actual file pointer, since this function
    will do the actual write outs to simplify the operation
    '''
    #original length of comment
    comment_length = len(comment)
    #boolean variable to indicate when to stop splitting
    process = True
    while process:
        #get one line
        one_line = splitter(comment)
        #write out
        filepointer.write(one_line + "\n")
        #update comment
        comment = comment[len(one_line):]
        comment_length -= len(one_line)
        #less then two because of the one '#' sign
        if comment_length < 2:
            process = False
        
        

def writeConfigFile(c):
    '''
    This function is devoted to write out the config file according to
    the setup done via Web-GUI.
    c dict - the configuration parameters
    
    '''
    #first we get the related comments
    cc = getConfigComments()
    if not (os.path.isdir(c['MAIN_ROOT'])):
        return -1
        
    config_file_path = c['MAIN_ROOT'] + "/nfpa.cfg" 
    
    if not (os.path.isfile(config_file_path)):
        return -1
    
    file = open(config_file_path, 'w')
    
    file.write("### ----------------- User Settings ------------------ ###\n")
    splitToMultipleLines(cc['username'], file)
    file.write("username=" + c['username'] + "\n")
    file.write("### ================================================== ###\n\n")
    
    file.write("### ------ Filesystem & OS Related Settings ---------- ###\n")
#     file.write("#" + cc['PKTGEN_ROOT'] + "\n")
    splitToMultipleLines(cc['PKTGEN_ROOT'], file)
    file.write("PKTGEN_ROOT=" + c['PKTGEN_ROOT'] + "\n\n")
    splitToMultipleLines(cc['PKTGEN_BIN'], file)
    file.write("PKTGEN_BIN=" + c['PKTGEN_BIN'] + "\n\n")
    splitToMultipleLines(cc['MAIN_ROOT'], file)
    file.write("MAIN_ROOT=" + c['MAIN_ROOT'] + "\n\n")
    splitToMultipleLines(cc['RES_DIR'], file)
    file.write("RES_DIR=" + c['RES_DIR'] + "\n\n")
    splitToMultipleLines(cc['LOG_LEVEL'], file)
    file.write("LOG_LEVEL=" + c['LOG_LEVEL'] + "\n")
    file.write("### ================================================== ###\n\n")
    
    file.write("### ------------- DPDK and Pktgen arguments  ------------- ###\n")
    splitToMultipleLines(cc['cpu_core_mask'], file)
    file.write("cpu_core_mask=" + c['cpu_core_mask'] + "\n\n")
    splitToMultipleLines(cc['mem_channels'], file)
    file.write("mem_channels=" + c['mem_channels'] + "\n\n")
    splitToMultipleLines(cc['socket_mem'], file)
    file.write("socket_mem=" + c['socket_mem'] + "\n\n")
    splitToMultipleLines(cc['other_dpdk_params'], file)
    file.write("other_dpdk_params=" + c['other_dpdk_params'] + "\n\n")
    splitToMultipleLines(cc['port_mask'], file)
    file.write("port_mask=" + c['port_mask'] + "\n\n")
    splitToMultipleLines(cc['cpu_port_assign'], file)
    file.write("cpu_port_assign=" + c['cpu_port_assign'] + "\n")
    file.write("### ================================================== ###\n\n")
    
    file.write("### Network Function Hardware & Software Related Settings# \n")
    splitToMultipleLines(cc['cpu_make'], file)
    file.write("cpu_make=" + c['cpu_make'] + "\n\n")
    splitToMultipleLines(cc['cpu_model'], file)
    file.write("cpu_model=" + c['cpu_model'] + "\n\n")
    splitToMultipleLines(cc['nic_make'], file)
    file.write("nic_make=" + c['nic_make'] + "\n\n")
    splitToMultipleLines(cc['nic_model'], file)
    file.write("nic_model=" + c['nic_model'] + "\n\n")
    splitToMultipleLines(cc['port_type'], file)
    file.write("port_type=" + c['port_type'] + "\n\n")
    splitToMultipleLines(cc['virtualization'], file)
    file.write("virtualization=" + c['virtualization'] + "\n\n")
    splitToMultipleLines(cc['vnf_name'], file)
    file.write("vnf_name=" + c['vnf_name'] + "\n\n")
    splitToMultipleLines(cc['vnf_version'], file)
    file.write("vnf_version=" + c['vnf_version'] + "\n\n")
    splitToMultipleLines(cc['vnf_driver'], file)
    file.write("vnf_driver=" + c['vnf_driver'] + "\n\n")
    splitToMultipleLines(cc['vnf_driver_version'], file)
    file.write("vnf_driver_version=" + c['vnf_driver_version'] + "\n\n")
    splitToMultipleLines(cc['vnf_function'], file)
    file.write("vnf_function=" + c['vnf_function'] + "\n\n")
    splitToMultipleLines(cc['vnf_comment'], file)
    file.write("vnf_comment=" + c['vnf_comment'] + "\n")
    file.write("### ================================================== ###\n\n")
    
    file.write("### ----- Gnuplot/Presenting Related Settings -------- ###\n")
    splitToMultipleLines(cc['pps_unit'], file)
    file.write("pps_unit=" + c['pps_unit'] + "\n\n")
    splitToMultipleLines(cc['bps_unit'], file)
    file.write("bps_unit=" + c['bps_unit'] + "\n\n")
    splitToMultipleLines(cc['outlier_min_percentage'], file)
    file.write("outlier_min_percentage=" + c['outlier_min_percentage'] + "\n\n")
    splitToMultipleLines(cc['outlier_max_percentage'], file)
    file.write("outlier_max_percentage=" + c['outlier_max_percentage'] + "\n")    
    file.write("### ================================================== ###\n\n")

    file.write("### ------------- Let NFPA configure your VNF -------- ###\n")
    splitToMultipleLines(cc['control_nfpa'], file)
    file.write("control_nfpa=" + c['control_nfpa'] + "\n\n")
    splitToMultipleLines(cc['control_vnf'], file)
    file.write("control_vnf=" + c['control_vnf'] + "\n\n")
    splitToMultipleLines(cc['control_path'], file)
    file.write("control_path=" + c['control_path'] + "\n\n")
    splitToMultipleLines(cc['control_args'], file)
    file.write("control_args=" + c['control_args'] + "\n\n")
    splitToMultipleLines(cc['control_vnf_inport'], file)
    file.write("control_vnf_inport=" + c['control_vnf_inport'] + "\n\n")
    splitToMultipleLines(cc['control_vnf_outport'], file)
    file.write("control_vnf_outport=" + c['control_vnf_outport'] + "\n\n")
    splitToMultipleLines(cc['control_mgmt'], file)
    file.write("control_mgmt=" + c['control_mgmt'] + "\n\n")

    file.write("### ================================================== ###\n\n")
    
    file.write("### --- Traffic Generating/PktGen Related Settings --- ###\n")
    splitToMultipleLines(cc['packetSize'], file)
    #properties that can be empty need to be commented
    if(c['packetSizes'] is not None):
        for i in c['packetSizes']:
            file.write("packetSize=" + str(i) + "\n")
    else:
        file.write("#packetSize=\n")
    file.write("\n")
    
    splitToMultipleLines(cc['trafficType'], file)
    if(c['trafficTypes'] is not None):        
        for i in c['trafficTypes']:
            file.write("trafficType=" + str(i) + "\n")
    else:
        file.write("#trafficType=\n")
    file.write("\n")
    
    splitToMultipleLines(cc['realisticTraffic'], file)

    if(c['realisticTraffics'] is not None):
        for i in c['realisticTraffics']:
            file.write("realisticTraffic=" + str(i) + "\n")
    else:
        file.write("#realisticTraffic=\n")
    file.write("\n")
    splitToMultipleLines(cc['measurement_num'], file)
    file.write("measurement_num=" + c['measurement_num'] + "\n\n")
    splitToMultipleLines(cc['measurementDuration'], file)
    file.write("measurementDuration=" + c['measurementDuration'] + "\n\n")
    splitToMultipleLines(cc['sendPort'], file)
    file.write("sendPort=" + c['sendPort'] + "\n\n")
    splitToMultipleLines(cc['recvPort'], file)
    file.write("recvPort=" + c['recvPort'] + "\n\n")
    splitToMultipleLines(cc['biDir'], file)
    file.write("biDir=" + c['biDir'] + "\n")
    file.write("### ================================================== ###\n\n")
    file.write("\n")

    
    file.close()











