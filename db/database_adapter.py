'''
This class is devoted for database functions, i.e., it has many built-in
functions to handle/query/insert/etc. the nfpa.db
The database has: 
= enum tables with two columns:
 - cpu_makes (id, make)
 - cpu_models (id, model)
 - nic_makes (id, make)
 - nic_models (id, model)
 - traffic_names (id, name)
 - traffic_packet_sizes (id, packet_size)
 - vnf_drivers (id, driver)
 - vnf_functions (id,function)
 - vnf_names (id, name)
 - virtualization (id, name)
= abstract tables with a few columns
 - cpu (id, make, model)
 - nic (id, make, model, capacity_GB)
 - traffic (id, name, packet_size, comment)
 - vnf (id, name, version, function, driver)
= user table for authentication 
 - columns: username, password, email 
== main measurement table
 - measurements (id, ts, name, cpu, nic, virtualization, vnf, traffic,
                 repetitions, duration, [many results column], bidir_twin_id,
                 comment, user_id)  
 
'''

import sqlite3
import copy
import sys
import os
#required for loading classes under lib/
sys.path.append("../lib/")
import logger as l
import logging
import invoke as invoke
class SQLiteDatabaseAdapter(object):
        
    '''
    Constructor
    '''
    def __init__(self, config):
                       
        #for storing the configuration
        self.config = config
        
        #instantiate logger
        self.log = l.getLogger( self.__class__.__name__, 
                                self.config['LOG_LEVEL'], 
                                self.config['app_start_date'],
                                self.config['LOG_PATH'])
        
        #get the path to database (sqlite) file
        self.db_name = self.config['MAIN_ROOT'] + "/db/nfpa.db"
        
        self.log.debug("SQLiteDatabaseAdapter class instantiated")
        
        self.enum_tables = ['cpu_makes', 'cpu_models', 'nic_makes', 'nic_models',
                            'traffic_names', 'traffic_packet_sizes', 
                            'virtualization', 'vnf_drivers', 'vnf_functions',
                            'vnf_names']
        
        self.abstract_tables = ['cpu', 'nic', 'traffic', 'vnf', 'measurements']
        self.tables = copy.deepcopy(self.enum_tables)
        self.tables += self.abstract_tables
        
        self.connect()
      
        #update autoincrement sequences
#         self.updateAutoIncrementSequences()
    
    def connect(self):
        '''
        This function will connect to the database, which name is stored
        in db_name global variable.
        Note: It connects to database in each case, e.g., if db file not exists,
        it creates a new one! So, pay attention to name the db file correctly
        '''
        self.log.debug(str("connecting to database %s" % self.db_name))
        
        #check whether database file exists
        if not (os.path.isfile(self.db_name)):
	    self.log.warn("DATABASE FILE NOT EXISTS...creating a new from scratch!")
            create_cmd = "cat db/create_nfpadatabase.sql | sqlite3 " + self.db_name
            invoke.invoke(create_cmd, self.log)

            self.log.info("DATABASE FILE CREATED")
				
        else:
	    self.log.debug("DATABASE FILE EXISTS")
	    #the connection var itself - required for committing and closing
	    self.conn = sqlite3.connect(self.db_name)
	    #cursor - required for each database function calls
	    self.c = self.conn.cursor()
                
        return True
    
    def disconnect(self):
        '''
        This function commits all uncommitted statements and closes the 
        connection
        '''
        #save changes if it has not been done
        self.conn.commit()
        #close connection
        self.conn.close()
    
    def getRowById(self, table, id):
        '''
        This function is devoted to get any row from any table identified by id.
        It is useful for getting additional information when selecting a row
        in measurements table, since there are a lot of foreign keys that
        identify other hw/sw elements in other tables
        id String/int - the required id
        table String - the name of the table
        
        returns tuple
        '''
        
        id = str(id)
        #check input params
        if id is None or table is None:
            self.log.error("ID or Table is NULL! Unable to look for a row!")
            return None
        #create tuple from id
        t = (id, )
        query = "SELECT * FROM " + table + " WHERE id=?"
        res = self.c.execute(query, t)
        data = res.fetchone()
        
        return data
        

    def _getEnum(self, **params):
        '''
        This inner function is a private function for getting enum tables. 
        All enum tables have their own public get functions outside this.
        This is just a helper class to reduce the number of repeated codes
        params:
        enum_table String - the name of the enum table, e.g. cpu_models
        column String - the column name for which the where statement applies
        where_st String - where statement - for filtering and get only one data
        '''
        
        enum_table = params.get('enum_table', None)
        #convert SQL query parts to lower case if they are not None
        if enum_table:
            enum_table = enum_table.lower()
        else:
            self.log.error("No enum table was set!")
            self.log.error("Nothing to do")
            return None
        
        column = params.get('column', None)
        if column:
            column = column.lower()
            
        
        where_st = params.get('where_st', None)
        if where_st:
            where_st = where_st.lower()
        
        res = None
        id = None
        if where_st and column:
            #create a temporary tuple of where_st
            t = (where_st, )
            
            res = self.c.execute("SELECT * FROM " + \
                                 enum_table + " WHERE " + column +"=?", 
                                 t)
            
            data = res.fetchone()
            self.log.debug(str(data))
            if(data is None):
                self.log.info(str("There is no '%s' in the database" % where_st))
                self.log.info("Inserting...")
                ### handle here what to do ###
                id = self._insertEnum(enum_table = enum_table,
                            column = column,
                            new_element = where_st)
            
            else:
                #tuple's first element is the id
                id = data[0]
            
            return id
    
    def _insertEnum(self, **params):
        '''
        This function will insert a new item into an enum table
        params:
        enum_table String - the name of the enum table, e.g. cpu_models
        column String - the column name for which the where statement applies
        new_element String - the new element to be added
        '''    
        enum_table = params.get('enum_table', None)
        #convert SQL query parts to lower case if they are not None
        if enum_table:
            enum_table = enum_table.lower()
        else:
            self.log.error("Enum name was not set") 
            return None
        
         
        column = params.get('column', None)
        if column:
            column = column.lower()
        else:
            self.log.error("Column name was not set") 
            return None
        
        new_element = params.get('new_element', None)
        if new_element:
            new_element = new_element.lower()
        else:
            self.log.error("New element was not set") 
            return None
        
        new_element = (new_element, )
        query = "INSERT INTO " + enum_table + " (" + column + ") VALUES (?)"
        self.c.execute(query,new_element)
        
        #commit
        self.conn.commit()
        #return new id        
        return self.c.lastrowid    
    
    def _getMakeModel(self, make, model, abstract_table, enum_tables):
        '''
        This inner function will returns the id of the required row in CPU or
        NIC table.
        If there is no such CPU or NIC model and CPU or NIC make, then it 
        creates a new entry in both enum tables, inserts a new row accordingly 
        in the abstract CPU or NIC table, and then returns the id of the newly 
        inserted row.
        This is only an inner helper function, public versions of it is named
        getCpu() and getNic()
        make String - the make of the CPU or NIC
        model String - the model of the CPU or NIC
        abstract_table String - the name of the abstract table (CPU or NIC)
        enum_tables List of strings - the name of the enum tables: 
                      [cpu_makes, cpu_models] or [nic_makes, nic_models]
                      IMPORTANT: 0th element is make, 1st element is model
        '''
        #first get make
        make_id = self._getEnum(enum_table = enum_tables[0], 
                                   column = "make",
                                   where_st = make)
 
        
        #get model
        model_id = self._getEnum(enum_table = enum_tables[1], 
                                   column = "model",
                                   where_st = model)
       
        #OK, we got everything, now check for existing configuration in 
        #abstract table
        #create a temporary tuple of where_st
        tuple = (make_id, model_id)
        
        res = self.c.execute("SELECT * FROM " + abstract_table + " WHERE " 
                             + " make=? AND model=?", 
                             tuple)
        
        data = res.fetchone()
        id = None
        if data is None:
            #configuration not found, inserting
#             self.log.warning("Configuration not exists in %s! Inserting..." %
#                           abstract_table)
            new_make_model = (make_id, model_id)
            query = "INSERT INTO " \
                    + abstract_table + " (make, model) VALUES (?,?)"
                    
            self.c.execute(query,new_make_model)
            #commit
            self.conn.commit()
            
            id = self.c.lastrowid
            
            
            self.log.debug("New make, model (%s (id: %s), %s (id: %s)) was "
                         "inserted into %s!" % 
                          (make, make_id, model, model_id, abstract_table))
        
        else:
            #configuration existed
            id = data[0]     

        return id
        
    
    def getCpu(self, make, model):
        '''
        This function will returns the id of the required row in CPU table.
        If there is no such CPU model and CPU make, then it creates a new entry
        in both enum tables, inserts a new row accordingly in the abstract CPU
        table, and then returns the id of the newly inserted row
        make String - the make of the CPU (e.g., intel xeon)
        model String - the model of the CPU (e.g., e5-2630)
        '''
        return self._getMakeModel(make, 
                                  model, 
                                  "cpu", 
                                  ["cpu_makes", "cpu_models"])
   
   
    def getNic(self, make, model, port_type):
        '''
        This function will returns the id of the required row in NIC table.
        If there is no such NIC model and NIC make, then it creates a new entry
        in both enum tables, inserts a new row accordingly in the abstract NIC
        table, and then returns the id of the newly inserted row
        make String - the make of the NIC (e.g., intel)
        model String - the model of the NIC (e.g., i350)
        '''
        nic_id = self._getMakeModel(make, 
                                  model, 
                                  "nic", 
                                  ["nic_makes", "nic_models"])
        
        t = (port_type, nic_id)
        #update NIC's port_type after it has been inserted
        query = "UPDATE nic SET port_type=? WHERE id=?"
        self.c.execute(query, t)
        #commit
        self.conn.commit()
        
        return nic_id 
    
    def getTraffic(self, name, packet_size):
        '''
        This function will get id of the traffic identified by name and 
        packet_size
        name String - name of the traffic, e.g., simple, tr2e, etc.
        packet_size String - size of packets, e.g., 64, 128 or 0 for realistic 
        trace
        comment String - any comment for the traffic (used only if traffic not
        exists and a new entry will be inserted)
        '''    
        
        #get name
        traffic_name_id = self._getEnum(enum_table = "traffic_names",
                                       column = "name",
                                       where_st = name)
        
        #get packet_size
        traffic_packetsize_id = self._getEnum(enum_table = "traffic_packet_sizes",
                                       column = "packet_size",
                                       where_st = packet_size)
        
        #OK, we got everything, now check for existing configuration in 
        #abstract table
        #create a temporary tuple of where_st
        tuple = (traffic_name_id, traffic_packetsize_id)
        
        res = self.c.execute("SELECT * FROM traffic WHERE " 
                             + " name=? AND packet_size=?", 
                             tuple)
        
        data = res.fetchone()
        id = None
        if data is None:
            #configuration not found, inserting
            self.log.info("Configuration not exists in traffic table!" 
                          "Inserting...")
            new_name_packetsize = (traffic_name_id, 
                                   traffic_packetsize_id)
            query = "INSERT INTO traffic (name, packet_size) VALUES " +\
                    "(?,?)"
                    
            self.c.execute(query,new_name_packetsize)
            #commit
            self.conn.commit()
            
            id = self.c.lastrowid
            
            self.log.debug("New name, packet_size (%s (id: %s),%s (id: %s)),"
                         " was inserted into traffic!" % 
                          (name,
                           traffic_name_id, 
                           packet_size, 
                           traffic_packetsize_id))
        
        else:
            #configuration existed
            id = data[0]     

        return id
    
    
    def getVirtualization(self, name):
        '''
        This function will get the id of the requested virtualization.
        If no such virtualization exists, then inserts it into the virtualization
        table via _getEnum() function
        name String - name of the virtualization
        
        return id
        '''
        return self._getEnum(enum_table = "virtualization", 
                                   column = "name",
                                   where_st = name) 
         
    
    def getVnf(self, name, version, function, driver, driver_version):
        '''
        This function will get id of the vnf identified by name, function and
        driver
        name String - name of the vnf, e.g., ovs, xdpd
        version String - version of vnf, e.g., 2.3.90
        function String - the function of the vnf, e.g. l2-switch, l3-router
        driver String - the used driver, e.g., dpdk, kernel, netmap, odp
        driver_version String - the version of the driver, e.g., 3.16.0, 2.0.0
        '''    
        
        #version
        version = str(version)
        
        #driver_version
        dv = str(driver_version)
        
        #get name
        name_id = self._getEnum(enum_table = "vnf_names",
                                       column = "name",
                                       where_st = name)
        
        #get function
        function_id = self._getEnum(enum_table = "vnf_functions",
                                       column = "function",
                                       where_st = function)
        
        #get driver
        driver_id = self._getEnum(enum_table = "vnf_drivers",
                                       column = "driver",
                                       where_st = driver)
        
        #OK, we got everything, now check for existing configuration in 
        #abstract table
        #create a temporary tuple of where_st
        tuple = (name_id, version, function_id, driver_id, dv)
        
        res = self.c.execute("SELECT * FROM vnf WHERE " 
                             + " name=? AND version=? AND function=? " + 
                             "AND driver=? AND driver_version=?", 
                             tuple)
        
        data = res.fetchone()
        id = None
        if data is None:
            #configuration not found, inserting
            self.log.warning("Configuration not exists in vnf table!" 
                          "Inserting...")
            new_vnf = (name_id,
                       version, 
                       function_id, 
                       driver_id,
                       dv)
            query = "INSERT INTO vnf (name, version, function, driver, " +\
                    "driver_version) " + \
                    "VALUES (?,?,?,?,?)"
                    
            self.c.execute(query,new_vnf)
            #commit
            self.conn.commit()
            id = self.c.lastrowid
            
            
            
            
            msg = str("New name, version, function and driver " + 
      "(%s (id: %s),%s, %s (id: %s), (%s (id: %s) was inserted into vnf table" % 
                      (name,
                       name_id,
                       version,
                       function,
                       function_id,
                       driver,
                       driver_id))
            
            self.log.debug(msg)
        
        else:
            #configuration existed
            id = data[0]     

        return id  
    
    
    def getUser(self, username):
        '''
        This function will gets the user id if exists, and password is correct.
        If not exists, creates a new user, if only password was wrong, then
        an error is raised via returning False
        '''
        #user id from users table (if everything went good, then this should
        #be returned
        user_id = None
        
        #user existance check
        t = (username, )
        query = "SELECT * FROM users WHERE username=?"
        res = self.c.execute(query, t)
        
        data = res.fetchone()
        
        #no such user
        if data is None:
            self.log.warning("No such user, creates a new one with the given "
                             "password")
            new_user = (username, )
            query = "INSERT INTO users (username) " + \
                    "VALUES (?)"
            self.c.execute(query, new_user)    
            #commit
            self.conn.commit()
            
            user_id = self.c.lastrowid
            
            
            
        else:
            #user exists, now check password
            user_id = data[0]
            
        return user_id
    
    def insertMeasurement(self, **params):
        '''
        This function will insert a new row in table measurements.
        params are the columns of the table
        ts Float - timestamp
        name String - name for the measurement, for instance, a scenario
        cpu Int - id of the cpu configuration
        nic Int - id of the nic configuration
        virtualization Int - id of the virtualization
        vnf Int - id of the vnf
        used_cpu_cores =  the number of cores vnf is using

        traffic Int - id of the traffic
        repetitions Int - number of measurements
        duration Int - number of seconds one measurements lasts
        
        sent_min_pps, sent_avg_pps, sent_max_pps,
        recv....
        miss...
        sent_min_bps, sent_avg_bps, sent_max_bps,
        recv....
        diff...  - Integer for min,max and Float for avg
        
        bidir_twin_id Int - id of the previous row, if bidirectional measurement
        was carried out
        comment String - a comment to the measurement, for instance, port forward
        user_id Int - id of the user 
        '''
        #create a tuple that will be inserted
        ts = params.get('ts', None)
        name = params.get('name', None)
        cpu = params.get('cpu', None)
        nic = params.get('nic', None)
        virtualization = params.get('virtualization', None)
        vnf = params.get('vnf', None)
        used_cpu_cores = params.get('used_cpu_cores', None)
        if used_cpu_cores is None:
            self.log.warning("vnf_num_cores was not set...use default 1")
        traffic = params.get('traffic', None)
        repetitions = params.get('repetitions', None)
        duration = params.get('duration', None)
        bidir = (params.get('bidir', False))
        control_nfpa = params.get('control_nfpa', False)
        #convert string bidir parameter to boolean
        bidir = bool(int(bidir))
        
        insert_tuple = (ts, name, cpu, nic, virtualization, vnf,
                        used_cpu_cores, traffic, repetitions, duration)
        
        
        
        measure_tuple = ()
        for h in self.config['header_uni']:
            for h_h in self.config['helper_header']: 
                m = h + "_" + h_h
                measure_tuple += (params.get(m, None), )
        
        
        bidir_twin_id = params.get('bidir_twin_id', None)
        comment = params.get('comment', None)
        user_id = params.get('user_id', None)
        
        rest_data_tuple = (bidir_twin_id, comment, user_id, bidir, control_nfpa)
        
        insert_tuple += measure_tuple
        insert_tuple += rest_data_tuple
        
        self.log.debug("Insert tuple:\n %s" % str(insert_tuple))
        
        #we got all data to insert a row
        query = "INSERT INTO measurements " \
                "(ts, name, cpu, nic, virtualization, " \
                "vnf, used_cpu_cores, traffic, repetitions, duration," \
                "sent_pps_min, sent_pps_avg, sent_pps_max, " \
                "recv_pps_min, recv_pps_avg, recv_pps_max, " \
                "miss_pps_min, miss_pps_avg, miss_pps_max, " \
                "sent_bps_min, sent_bps_avg, sent_bps_max, " \
                "recv_bps_min, recv_bps_avg, recv_bps_max, " \
                "diff_bps_min, diff_bps_avg, diff_bps_max, " \
                "bidir_twin_id, comment, user_id, bidir, control_nfpa) VALUES " \
                "(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
                
        self.c.execute(query, insert_tuple)
        
        #commit
        self.conn.commit()
        
        #return the row id in order to know the bidir_twin_id if needed
        return self.c.lastrowid        
         
        
        
