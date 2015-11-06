'''
This class is devoted to iterate through the results and insert them
into the database's measurements table
'''
import os
import divisor as div

import copy
import special_bidir_traffic_checker as sbtc
import logger as l

#required for loading DatabaseAdapter class
# import sys
# sys.path.append("db/")
# from database_adapter_postgres import DatabaseAdapter

class DatabaseHandler(object):
    
    def __init__(self, **params):
        
        self.config = params.get('config', None)
        self.results = params.get('results', None)
        self.type = params.get('type', None)
        
        #create a reference for logger
        self.log = l.getLogger( self.__class__.__name__, 
                                self.config['LOG_LEVEL'], 
                                self.config['app_start_date'],
                                self.config['LOG_PATH'])
        
        self.log.info("STARTED...")
        
        
#         self.log.debug(str(self.results))
        
        #create a reference to database helper object
        dbh = self.config['dbhelper']
        
        connect = dbh.connect()
        #connect to database
        if not connect:
            self.log.error("Database connection was working at the time NFPA " +\
                           "has been started, but now, NFPA could not connect!")
            self.log.error("EXITING")
            exit(-1)
        
        #get ids for foreign keys
        cpu = dbh.getCpu(self.config['cpu_make'], self.config['cpu_model'])
        nic = dbh.getNic(self.config['nic_make'], 
                         self.config['nic_model'],
                         self.config['port_type'])
        virtualization = dbh.getVirtualization(self.config['virtualization'])
        vnf = dbh.getVnf(self.config['vnf_name'],
                         self.config['vnf_version'], 
                         self.config['vnf_function'], 
                         self.config['vnf_driver'],
                         self.config['vnf_driver_version'])
        
        user_id = dbh.getUser(self.config['username'])
        
        repetitions = self.config['measurement_num']
        duration = self.config['measurementDuration']
        
        biDir = self.config['biDir']
        
        #create a temporary dict (Measurements_Results) where the results 
        #will be stored indexed by the database's column name, 
        #e.g., sent_pps_min
        mr = {}
        
        if self.type == "synthetic":
            #first, iterate through traffic types
            for tt in self.results:
                #check for special bidirectional measurement
                ul_dl = False
                tmp_tt = [tt,tt]
                if(sbtc.checkSpecialTraffic(tt)):
                    ul_dl = True
                    biDir = '1'
                    tmp_tt = sbtc.splitTraffic(tt)
                else:
                    #set back biDir if no special traffic is set
                    biDir = self.config['biDir']
                    
                for ps in self.results[tt]:
                    traffic = dbh.getTraffic(tmp_tt[0], ps)
                    
                    pkt_res = self.results[tt][ps]
                    for h in self.config['header_uni']:
                        for h_h in self.config['helper_header']:
                            self.log.debug("%s - %s - %s - %s: %s" %
                                           (tmp_tt[0],ps,h,h_h,
                                            pkt_res[h][h_h]))
                            #create proper column name from header and helper_header
                            measure_column = h + "_" + h_h
                            mr[measure_column] = round(float(pkt_res[h][h_h]),4)
                    
                    self.log.debug("UniDir mr: %s" % str(mr))
                    #now we need to insert a row
                    bidir_id = dbh.insertMeasurement(
                         ts = self.config['app_start_date'],
                         name = self.config['scenario_name'],
                         cpu = cpu,
                         nic = nic,
                         virtualization = virtualization,
                         vnf = vnf,
                         traffic = traffic,
                         repetitions = repetitions,
                         duration = duration,
                         sent_pps_min = mr['sent_pps_min'],
                         sent_pps_avg = mr['sent_pps_avg'],
                         sent_pps_max = mr['sent_pps_max'],
                         recv_pps_min = mr['recv_pps_min'],
                         recv_pps_avg = mr['recv_pps_avg'],
                         recv_pps_max = mr['recv_pps_max'],
                         miss_pps_min = mr['miss_pps_min'],
                         miss_pps_avg = mr['miss_pps_avg'],
                         miss_pps_max = mr['miss_pps_max'],
                         sent_bps_min = mr['sent_bps_min'],
                         sent_bps_avg = mr['sent_bps_avg'],
                         sent_bps_max = mr['sent_bps_max'],
                         recv_bps_min = mr['recv_bps_min'],
                         recv_bps_avg = mr['recv_bps_avg'],
                         recv_bps_max = mr['recv_bps_max'],
                         diff_bps_min = mr['diff_bps_min'],
                         diff_bps_avg = mr['diff_bps_avg'],
                         diff_bps_max = mr['diff_bps_max'],
                         user_id = user_id,
                         comment = self.config['vnf_comment'],
                         bidir = biDir)
                            
                    #if bidirectional measurement was carried out, we need to
                    #add another row
                    if((int(self.config['biDir']) == 1) or (ul_dl)):  
                        biDir = '1'
                        #we need to check whether the special ul-dl bidirectional
                        #traffic type was set. If so, then we also add header_bi
                        #to headers var                 
                        mr = {}
                        
                        #update traffic (necessary if special bidirectional
                        #measurement was carried out
                        traffic = dbh.getTraffic(tmp_tt[1], ps)
                        for h in self.config['header_bi']:
                            for h_h in self.config['helper_header']:
                                self.log.debug("%s - %s - %s - %s: %s" %
                                               (tmp_tt,ps,h,h_h,
                                                pkt_res[h][h_h]))
                                #we need to remove '_bidir' from header
                                #we could also append min,max,avg immediately
                                measure_column = copy.deepcopy(h)
                                measure_column = measure_column.replace('bidir', 
                                                                        h_h)
                                mr[measure_column] = round(
                                                       float(pkt_res[h][h_h]),
                                                       4)
                        
                        self.log.debug("Bidir mr: %s" % str(mr))
                        row_id = dbh.insertMeasurement(
                         ts = self.config['app_start_date'],
                         name = self.config['scenario_name'],
                         cpu = cpu,
                         nic = nic,
                         virtualization = virtualization,
                         vnf = vnf,
                         traffic = traffic,
                         repetitions = repetitions,
                         duration = duration,
                         sent_pps_min = mr['sent_pps_min'],
                         sent_pps_avg = mr['sent_pps_avg'],
                         sent_pps_max = mr['sent_pps_max'],
                         recv_pps_min = mr['recv_pps_min'],
                         recv_pps_avg = mr['recv_pps_avg'],
                         recv_pps_max = mr['recv_pps_max'],
                         miss_pps_min = mr['miss_pps_min'],
                         miss_pps_avg = mr['miss_pps_avg'],
                         miss_pps_max = mr['miss_pps_max'],
                         sent_bps_min = mr['sent_bps_min'],
                         sent_bps_avg = mr['sent_bps_avg'],
                         sent_bps_max = mr['sent_bps_max'],
                         recv_bps_min = mr['recv_bps_min'],
                         recv_bps_avg = mr['recv_bps_avg'],
                         recv_bps_max = mr['recv_bps_max'],
                         diff_bps_min = mr['diff_bps_min'],
                         diff_bps_avg = mr['diff_bps_avg'],
                         diff_bps_max = mr['diff_bps_max'],
                         user_id = user_id,
                         comment = self.config['vnf_comment'],
                         bidir_twin_id = bidir_id,
                         bidir = biDir)
                        
                        
        if self.type == "realistic":
            biDir = self.config['biDir']
            #first, iterate through traffic types
            for realistic in self.results:
                #check for special bidirectional measurement
                ul_dl = False
                tmp_tt = [realistic,realistic]
                if(sbtc.checkSpecialTraffic(realistic)):
                    ul_dl = True
                    biDir = '1'
                    tmp_tt = sbtc.splitTraffic(realistic)
                else:
                    #set back biDir if no special traffic is set
                    biDir = self.config['biDir']
                    
                #there is no packet size set  for realistic traces
                #so set here the second param to 0 (we need to use "0" instead
                #of 0, since 0 is represented as NULL, and database will throw
                #error of trying to inserting NULL value into NOT NULL column
                ps = "0"
                traffic = dbh.getTraffic(tmp_tt[0], ps)
                
                pkt_res = self.results[realistic]
                for h in self.config['header_uni']:
                    for h_h in self.config['helper_header']:
                        self.log.debug("%s - %s - %s - %s: %s" %
                                       (tmp_tt[0], ps,h,h_h,
                                        pkt_res[h][h_h]))
                        #create proper column name from header and helper_header
                        measure_column = h + "_" + h_h
                        mr[measure_column] = round(float(pkt_res[h][h_h]),4)
                
                self.log.debug("UniDir mr: %s" % str(mr))
                #now we need to insert a row
                bidir_id = dbh.insertMeasurement(
                     ts = self.config['app_start_date'],
                     name = self.config['scenario_name'],
                     cpu = cpu,
                     nic = nic,
                     virtualization = virtualization,
                     vnf = vnf,
                     traffic = traffic,
                     repetitions = repetitions,
                     duration = duration,
                     sent_pps_min = mr['sent_pps_min'],
                     sent_pps_avg = mr['sent_pps_avg'],
                     sent_pps_max = mr['sent_pps_max'],
                     recv_pps_min = mr['recv_pps_min'],
                     recv_pps_avg = mr['recv_pps_avg'],
                     recv_pps_max = mr['recv_pps_max'],
                     miss_pps_min = mr['miss_pps_min'],
                     miss_pps_avg = mr['miss_pps_avg'],
                     miss_pps_max = mr['miss_pps_max'],
                     sent_bps_min = mr['sent_bps_min'],
                     sent_bps_avg = mr['sent_bps_avg'],
                     sent_bps_max = mr['sent_bps_max'],
                     recv_bps_min = mr['recv_bps_min'],
                     recv_bps_avg = mr['recv_bps_avg'],
                     recv_bps_max = mr['recv_bps_max'],
                     diff_bps_min = mr['diff_bps_min'],
                     diff_bps_avg = mr['diff_bps_avg'],
                     diff_bps_max = mr['diff_bps_max'],
                     user_id = user_id,
                     comment = self.config['vnf_comment'],
                     bidir = biDir)
                        
                #if bidirectional measurement was carried out, we need to
                #add another row
                if((int(self.config['biDir']) == 1) or (ul_dl)):  
                    biDir = '1'
                    #we need to check whether the special ul-dl bidirectional
                    #traffic type was set. If so, then we also add header_bi
                    #to headers var                 
                    mr = {}
                    
                    #there is no packet size set  for realistic traces
                    #so set here the second param to "0"
                    traffic = dbh.getTraffic(tmp_tt[1], ps)
                    for h in self.config['header_bi']:
                        for h_h in self.config['helper_header']:
                            self.log.debug("%s - %s - %s - %s: %s" %
                                           (tmp_tt,ps,h,h_h,
                                            pkt_res[h][h_h]))
                            #we need to remove '_bidir' from header
                            #we could also append min,max,avg immediately
                            measure_column = copy.deepcopy(h)
                            measure_column = measure_column.replace('bidir', h_h)
                            mr[measure_column] = round(
                                                   float(pkt_res[h][h_h]),
                                                   4)
                    
                    self.log.debug("Bidir mr: %s" % str(mr))
                    row_id = dbh.insertMeasurement(
                     ts = self.config['app_start_date'],
                     name = self.config['scenario_name'],
                     cpu = cpu,
                     nic = nic,
                     virtualization = virtualization,
                     vnf = vnf,
                     traffic = traffic,
                     repetitions = repetitions,
                     duration = duration,
                     sent_pps_min = mr['sent_pps_min'],
                     sent_pps_avg = mr['sent_pps_avg'],
                     sent_pps_max = mr['sent_pps_max'],
                     recv_pps_min = mr['recv_pps_min'],
                     recv_pps_avg = mr['recv_pps_avg'],
                     recv_pps_max = mr['recv_pps_max'],
                     miss_pps_min = mr['miss_pps_min'],
                     miss_pps_avg = mr['miss_pps_avg'],
                     miss_pps_max = mr['miss_pps_max'],
                     sent_bps_min = mr['sent_bps_min'],
                     sent_bps_avg = mr['sent_bps_avg'],
                     sent_bps_max = mr['sent_bps_max'],
                     recv_bps_min = mr['recv_bps_min'],
                     recv_bps_avg = mr['recv_bps_avg'],
                     recv_bps_max = mr['recv_bps_max'],
                     diff_bps_min = mr['diff_bps_min'],
                     diff_bps_avg = mr['diff_bps_avg'],
                     diff_bps_max = mr['diff_bps_max'],
                     user_id = user_id,
                     comment = self.config['vnf_comment'],
                     bidir_twin_id = bidir_id,
                     bidir = biDir)