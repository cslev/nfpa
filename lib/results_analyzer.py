'''
This class is devoted for analyzing the results and create gnuplot compatible
output
'''

import divisor as div
import os
import copy
import special_bidir_traffic_checker as sbtc
import logger as l


class ResultsAnalyzer(object):
    
    def __init__(self, config, **params):
       
        #store config in local var
        self.config = config

            
        
        #self.log.error(str(self.config))
        self.log = l.getLogger( self.__class__.__name__, 
                                self.config['LOG_LEVEL'], 
                                self.config['app_start_date'],
                                self.config['LOG_PATH'])
        #create a dict of dict of dict of lists of results
        #e.g., self.resuls['simple']['128']['sent_pps'] = 
        #                                [list of results, 412421,123123,etc.]
        #see exact creations of sub dictionaries below from line 45!
        self._results = {}
    
        #create a dict for realistic traffics as well
        #since there is no defined packet size in realistic traffic,
        #storing results are simpler (not so many embeddings are needed)
        self._realistic_results = {}
                
        #get the results type
        self.type = params.get('type', None)
       
                
        if(self.type is None):
            self.log.error("Class wrongly instantiated - NO RESULTS TYPE SET!")
            
            

    
        #change directory where the res files are (PKTGEN_ROOT)
        os.chdir(self.config["PKTGEN_ROOT"])
        self.log.debug("Changed directory to %s" % str(os.getcwd()))
          
        if(self.type == "synthetic"):
            #first analyze simple traffic if it was measured
            for traffic_type in self.config['trafficTypes']:
                #special ul-dl bidirectional traffic bit
                ul_dl = False
                #check whether special ul-dl bidirectional traffic was set
                if sbtc.checkSpecialTraffic(traffic_type):
                    ul_dl = True
                
                #create a dictionary for traffic_type in main self._results dictionary
                self._results[traffic_type] = {}
                
                self.log.info("Analyzing %s traffic type:" % traffic_type)
                for packet_size in self.config['packetSizes']:
                    self.log.info("\t%s size" % packet_size)
                    file_name = self.config["PKTGEN_ROOT"] + "/nfpa." + \
                                traffic_type + "." + packet_size + \
                                "bytes.res"
                    #check file exists
                    ok = os.path.isfile(file_name)
                    if not ok:
                        self.log.error("ERROR: file %s not exists (skipping)" % 
                                    file_name)
                        continue
                    
                        
                    #create sub dictionary in self._results under the given 
                    #traffic type
                    self._results[traffic_type][packet_size] = {}
                    #create a simple pointer for the var above
                    pkt_res = self._results[traffic_type][packet_size]
                   
                    #assemble headers from header_uni and header_bi(if bidir is 
                    #set) -- We need deepcopy, to preserve original ones as they
                    #were
                    headers = copy.deepcopy(self.config['header_uni'])
                    
                    #append bidir header if biDir is set
                    if(int(self.config["biDir"]) == 1):
                        headers += self.config['header_bi']
                   
                    #check whether special ul-dl bidirectional traffic was set
                    if ul_dl:
                        #prepare for specail ul-dl bidirectional traffic
                        headers = copy.deepcopy(self.config['header_uni'])
                        #append bidir header 
                        headers += self.config['header_bi']
#                         pkt_res = self._special_results[traffic_type][packet_size]
                   
                    #create sub dicts of the list of  measured components
                    #(sent(pps),recv(pps), etc.)
                    for h in headers:
                        pkt_res[h] = []
                        
                    with open(file_name, 'r') as lines:
                        
                        for line in lines:
                            #remove blank spaces
                            line = line.strip()
                            #removed blank lines
                            if not line:
                                continue
                            #print out first line, but only print out!
                            #in the following we omit it, when results are
                            #parsed
                            self.log.debug(line)
                            #omit commented lines in analyzing                    
                            if (line.startswith("#", 0, 1)):
                                continue
                            #split config params
                            #self.log.info(line)
                            
                            #split line according to tabs, then we got
                            #0=snt(pps)
                            #1=rec(pps)
                            #2=miss(pps)
                            #3=snt(bps)
                            #4=rec(bps)
                            #5=diff(bps)
                            #from 6 comes the same results, but for 
                            #bidirectional results
                            results_as_list = line.split("|")
                            #append results
                            for i,h in enumerate(headers):
                                try:
                                    pkt_res[h].append(results_as_list[i])
                                except IndexError as ie:
                                    self.log.error("Error during parsing res file")
                                    self.log.error("splitted line: %s" % 
                                                 str(results_as_list))
                                    self.log.error(ie)
                                    exit(-1)
                                    
                                
                        # ALRIGHT - WE GOT ALL MEASURED DATA
     

        #we analyze realistic traffic here separately, since there is no packet
        #size in this case, and accordingly only one .res file is created
        if self.type == "realistic":
            
            
            for realistic in self.config["realisticTraffics"]:
                self.log.info("\t%s" % realistic)
                
                #special ul-dl bidirectional traffic bit
                ul_dl = False
                #check whether special ul-dl bidirectional traffic was set
                if sbtc.checkSpecialTraffic(realistic):
                    ul_dl = True
                
                #create a dictionary for traffic_type in main self._results 
                #dictionary
                self._realistic_results[realistic] = {}
                #create a simple pointer for the var above
                pkt_res = self._realistic_results[realistic]
               
                #pcap file
                file_name = self.config["PKTGEN_ROOT"] + "/nfpa." + \
                            realistic + ".res"
                            
                
                #check file exists
                ok = os.path.isfile(file_name)
                if not ok:
                    self.log.error("ERROR: file %s not exists (skipping)" % file_name)
                    continue
                #res file exists
                                
                #assemble headers from header_uni and header_bi(if bidir is 
                #set) -- We need deepcopy, to preserve original ones as they
                #were
                headers = copy.deepcopy(self.config['header_uni'])
                
                #append bidir header if biDir is set
                if(int(self.config["biDir"]) == 1):
                    headers += self.config['header_bi']
               
                #check whether special ul-dl bidirectional traffic was set
                if ul_dl:
                    #prepare for specail ul-dl bidirectional traffic
                    headers = copy.deepcopy(self.config['header_uni'])
                    #append bidir header 
                    headers += self.config['header_bi']
                
                #create lists for results
                for h in headers:
                    pkt_res[h] = []

                with open(file_name, 'r') as lines:
                    
                    for line in lines:
                        #remove blank spaces
                        line = line.strip()
                        #removed blank lines
                        if not line:
                            continue
                        #print out first line, but only print out!
                        #in the following we omit it, when results are
                        #parsed
                        self.log.debug(line)
                        #omit commented lines in analyzing                    
                        if line.startswith("#",0,1):
                            continue
                        #split config params
                        #self.log.info(line)
                        
                        #split line according to tabs, then we got
                        #0=snt(pps)
                        #1=rec(pps)
                        #2=miss(pps)
                        #3=snt(bps)
                        #4=rec(bps)
                        #5=diff(bps)
                        #from 6 comes the same results, but for 
                        #bidirectional results
                        results_as_list = line.split("|")
                        #append results
                        for i,h in enumerate(headers):
                            pkt_res[h].append(results_as_list[i])
                            

                    # ALRIGHT - WE GOT ALL MEASURED DATA
 
               
        
        
        #if results are empty, stop execution
        if ((len(self._results.values()) == 0) and 
            (len(self._realistic_results.values()) == 0)):
            self.log.error("There is no results to process! Something went wrong")
            self.log.error("EXITING...")
            exit(-1)

        else:
            if self._results:           
                self.log.debug("synthetic results")
                                    
                self.log.debug(str(self._results))
                #process read result data for synthetic            
                self.processResultsData()
            
            if self._realistic_results:
                self.log.debug("Realistic results")
                self.log.debug(str(self._realistic_results))
                #process read results data for realistic results
                self.processRealisticResultsData()
        
    
    def calculateTheoreticalMax(self, packetsize):
        '''
        This process will calculate the theoretical maximum according to the 
        given packet size and the set port_type in nfpa.cfg. 
        Then it converts it to the desired unit.
        return int - the theoretical maximum 
        '''    
        #get the port type from config file
        port_type = str(self.config['port_type']).split("_")[0]
        port_unit = str(self.config['port_type']).split("_")[1]
        
        #port rate will be an int according to port_type and the calculated
        #divisor for the given unit, for instance, in case of 10_G this will
        #be 10 * 1000000000 = 10.000.000.000 (dots are not commas, just for 
        #easier reading!
        port_rate = int(port_type) * div.divisor(str(port_unit))
        
#         self.log.debugug("port_rate: %d" % port_rate)
        
        #port rate is given in bit/s. Divide it by 8 to get byte/s.
        #packetsize should be extended with 20 bytes (interframe gap (12 bytes, 
        #frame start seq. (7 bytes), and start delimiter (1 byte) 
        theor_max = int(port_rate/8/(int(packetsize) + 20))
        
        return theor_max     
    
    
    def processRealisticResultsData(self):
        '''
        This process is similar to processResultsData(), but it is devoted for
        processing realistic results.
        Since those results are stored differently than simple and synthetic 
        ones
        '''
        ####################### SORTING ########################        
        self.log.info("Processing REALISTIC results...(sorting, omitting outliers)")
        
        #calculate the number of min. elements to be omitted
        #get the length of one list (each list has the same length),
        # so get length of sent_pps list
        length = 0
        #get a realistic traffic for this, e.g., get the first one
        tmp_real = self.config['realisticTraffics'][0]
        #update length accordingly
        id = self.config['header_uni'][0] 
        length = len(self._realistic_results[tmp_real][id])

        self.log.debug("Number of rows in results: %s " % length)
        
        #Let's sort all results in order to omit later the min and max outliers
        #sorting
        for realistic in self._realistic_results:
            for res in self._realistic_results[realistic]:
                self._realistic_results[realistic][res].sort()
        
        #################### OMIT OUTLIERS ####################### 
        #calculate the number of outliers to be omitted for minimum
        omit_min = float(self.config['outlier_min_percentage']) * length
        #calculate the number of outliers to be omitted for maxmimum
        omit_max = float(self.config['outlier_max_percentage']) * length
        
        self.log.debug("--- number of omitted minimums: %s" % int(omit_min))
        self.log.debug("--- number of omitted maximums: %s" % int(omit_max))
        #omit first from the minimums
        #processing
        if((int(omit_min) != 0) or (int(omit_max) != 0)):
            #only iterate if some outliers needs to be removed
            for realistic in self._realistic_results:
                for res in self._realistic_results[realistic]:
                    #check again whether it is necessary to omit outlier
                    if(int(omit_min) != 0):
                        #omit from the minimums
                        self._realistic_results[realistic][res] = \
                                            self._realistic_results[realistic]\
                                            [res][int(omit_min):]
                    #if omit_max == 0, [:-0] makes no sense for omitting
                    #i.e., it clears the list :(, so only omit if omit_max
                    #is not ZERO
                    elif(int(omit_max) != 0): 
                        
                        #omit from the maximums at the same time with list 
                        #function
                        self._realistic_results[realistic][res] = \
                                            self._realistic_results[realistic]\
                                            [res][:-int(omit_max)]
                                            
        
        ################# CALCULATE MIN, AVG, AND MAX VALUES ##################
        #here, the dataset and its type will be changed!
        #till now, self._realistic_results[realistic][res] was a list of the 
        #results!
        #from now, it will be a dictionary with keys as min, max , avg and 
        #values as results for them
        tmp_dict = {}
        
        #we already know what the min and max values are, since results are 
        #sorted
        for realistic in self._realistic_results:
            for res in self._realistic_results[realistic]:
                #lenght
                l = len(self._realistic_results[realistic][res])
                #min = first element
                min = copy.deepcopy(int(self._realistic_results[realistic]\
                                                                    [res][0]))
                #max = last element
                max = copy.deepcopy(int(self._realistic_results[realistic]\
                                                                [res][(l-1)]))
                
                #calculate avg
                avg = 0
                for i in self._realistic_results[realistic][res]:
#                         self.log.warning(i)
                    avg += int(i)
                avg = float(avg/float(l))    
                
                self.log.debug("min-max-avg for %s-%s: %d-%d-%0.4f" % 
                              (realistic, res ,min, max, avg))
                #copying calculated metrics into the temporary dictionary
                tmp_dict['max'] = copy.deepcopy(max)
                tmp_dict['min'] = copy.deepcopy(min)
                tmp_dict['avg'] = copy.deepcopy(avg)
                
                #update results dictionary by changing type of list to dict
                self._realistic_results[realistic][res] = {}
                #copy tmp_dict into the main results variable
                self._realistic_results[realistic][res] = copy.deepcopy(tmp_dict)
                #now, it is safe to delete/clear tmp_dict for the next 
                #iteration of the loops
        
        self.log.info("[DONE]")
        self.log.debug(str(self._realistic_results))
                        
        
    def processResultsData(self):
        '''
        This function is devoted for processing the results.
        It iterates through saved results, sort them, and according to the 
        preset outlier percentage (found in nfpa.cfg) removes the outliers
        '''
         
        ####################### SORTING ########################
        
        self.log.info("Processing results...(sorting, omitting outliers)")
        
        
        #calculate the number of min. elements to be omitted
        #get the length of one list (each list has the same length),
        # so get length of sent_pps list
        length = 0
        #get a traffic type for this, e.g., get the first traffic type
        tmp_tt = self.config['trafficTypes'][0]
        #get a packet size for this, e.g., get the first packet size
        tmp_ps = self.config['packetSizes'][0]
        #now, it is easy to access the results for, for instance, sent_pps
        #id for sent_pps is got from self.config['header_uni']
        id = self.config['header_uni'][0] 
        length = len(self._results[tmp_tt][tmp_ps][id])
        
        self.log.debug("Number of rows in results: %s " % length)
        
        #Let's sort all results in order to omit later the min and max
        #outliers
        #processing
        for tt in self._results:
            for ps in self._results[tt]:
                for res in self._results[tt][ps]:
                    #sort data                    
                    self._results[tt][ps][res].sort()
         
        
        
        #################### OMIT OUTLIERS ####################### 
        #calculate the number of outliers to be omitted for minimum
        omit_min = float(self.config['outlier_min_percentage']) * length
        #calculate the number of outliers to be omitted for maxmimum
        omit_max = float(self.config['outlier_max_percentage']) * length
        
#         for i in (self._results['simple']['64']['sent_pps']):
#             self.log.info(i)
        self.log.debug("--- number of omitted minimums: %s" % int(omit_min))
        self.log.debug("--- number of omitted maximums: %s" % int(omit_max))
        #omit first from the minimums
        #processing
        if((int(omit_min) != 0) or (int(omit_max) != 0)):
            #only iterate if some outliers needs to be removed
            for tt in self._results:
                for ps in self._results[tt]:
                    for res in self._results[tt][ps]:
                        #check again whether it is necessary to omit outlier
                        if(int(omit_min) != 0):
                            #omit from the minimums
                            self._results[tt][ps][res] = self._results[tt][ps]\
                                                        [res][int(omit_min):]
                        #if omit_max == 0, [:-0] makes no sense for omitting
                        #i.e., it clears the list :(, so only omit if omit_max
                        #is not ZERO
                        elif(int(omit_max) != 0): 
                            
                            #omit from the maximums at the same time with list function
                            self._results[tt][ps][res] = self._results[tt][ps]\
                                                        [res][:-int(omit_max)]
#                         self.log.debug(str(self._results[tt][ps][res]))
            
            
        
        ################# CALCULATE MIN, AVG, AND MAX VALUES ##################
        #here, the dataset and its type will be changed!
        #till now, self._results[tt][ps][res] was a list of the results!
        #from now, it will be a dictionary with keys as min, max , avg and values
        #as results for them
        tmp_dict = {}
        
        #we already know what the min and max values are, since results are 
        #sorted
        for tt in self._results:
            for ps in self._results[tt]:
                for res in self._results[tt][ps]:
                    #lenght
                    l = len(self._results[tt][ps][res])
                    #min = first element
                    min = copy.deepcopy(int(self._results[tt][ps][res][0]))
                    #max = last element
                    max = copy.deepcopy(int(self._results[tt][ps][res][(l-1)]))
                    
                    #calculate avg
                    avg = 0
                    for i in self._results[tt][ps][res]:
#                         self.log.warning(i)
                        avg += int(i)
                    avg = float(avg/float(l))    
                    
                    self.log.debug("min-max-avg for %s-%s-%s: %d-%d-%0.4f" % 
                                  (tt,ps,res,min,max,avg))
                    #copying calculated metrics into the temporary dictionary
                    tmp_dict['max'] = copy.deepcopy(max)
                    tmp_dict['min'] = copy.deepcopy(min)
                    tmp_dict['avg'] = copy.deepcopy(avg)
                    
                    #update results dictionary by changing type of list to dict
                    self._results[tt][ps][res] = {}
                    #copy tmp_dict into the main results variable
                    self._results[tt][ps][res] = copy.deepcopy(tmp_dict)
                    #now, it is safe to delete/clear tmp_dict for the next 
                    #iteration of the loops
                    
        #append self._results with a new key,value pair
        for tt in self._results:
            for ps in self._results[tt]:
                #add theoretical value
                self._results[tt][ps]['theor_max'] = \
                                            self.calculateTheoreticalMax(ps)

        self.log.info("[DONE]")
        self.log.debug(str(self._results))
        
        
    def getResultsDict(self):
        '''
        This procedure returns the results dictionary that is possible
        to pass later to different modules, such as Visualizer
        return self._results - dictionary
        '''
        return self._results  
    
    def getRealisticResultsDict(self):
        '''
        This procedure returns the realistic results dictionary that is possible
        to pass later to different modules, such as Visualizer
        return dictionary
        '''
        return self._realistic_results 
    