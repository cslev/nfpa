from bottle import Bottle, route, get, post, request, run, static_file,  view, template, redirect
#for loading other libs in different directories
import sys
from time import sleep
sys.path.append("lib/")
import read_write_config_file as rwcf
import logger as l
import date_formatter as df



import os
import signal
import threading
import time
class MeasureThread(threading.Thread):
    '''
    This class is called and initiated in a separate thread in order to
    avoid blocking web site presenting main WEBNFPA thread.
    '''
    
    
    def __init__(self, threadID, name, nfpa_class_reference, webnfpa_class_reference):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.nfpa_class = nfpa_class_reference
        self.webnfpa_class = webnfpa_class_reference
        
        #initialize nfpa main class
        self.status = self.nfpa_class.initialize()
        if(self.status == -1):
            #this will cause thread execution error
            return -1
        
    def run(self):
        self.webnfpa_class.log.debug("%s thread started" % self.name)
    
        self.nfpa_class.startPktgenMeasurements()

        self.webnfpa_class.log.debug("Exiting thread %s " % self.name)
        
        self.webnfpa_class.stop()
    

    

class WEBNFPA(object):
    def __init__(self, scenario_name, host_port, nfpa_class):
        '''
        This class initializes a bottle python webserver on the given
        host_port, which is passed as host:port!
        scenario_name String - the name for identifying the scenario
        host_port String - looks like localhost:8000
        nfpa_class NFPA - this is a pointer to main class to be able to access
        its startPktgenMeasurements function
        '''
        
        host_port_string_input = host_port  #used only line 84 for printing out
        
        host_port = host_port.split(":")
        self.host = host_port[0]
        self.port = host_port[1]
        
        #read config
        tmp_cfg = rwcf.readConfigFile("nfpa.cfg")
        #check whether it was successful
        if tmp_cfg[0] == True:
            self.config = tmp_cfg[1]
        else:
            print(tmp_cfg[1])
            exit(-1)
        
        self.config_comment = rwcf.getConfigComments()
        
        #instantiate logger
        self.log = l.getLogger( self.__class__.__name__, 
                                self.config['LOG_LEVEL'], 
                                self.config['app_start_date'],
                                self.config['LOG_PATH'])
        
        self.log.info("### Measurement scenario '" + scenario_name + "' has been" 
              "initiated with Web-GUI ###")
        self.log.info("NFPA Web interface can be reached under: %s/nfpa" %
                      host_port_string_input)
#         print("ETL: %s" % self.config['ETL'])
        
        #append scenario name to self.config dictionary for later usage
        self.config['scenario_name'] = scenario_name
        
        self.nfpa_class = nfpa_class
        
        
#         print("in config: %s" % self.config['scenario_name'])
        self._app = Bottle()
        
        self._route()
        
#         self.note_pic = self._serve_pictures('note.png')
        
        self.start()
        
        
        
        
    
    def showEndMeasurement(self):
        '''
        This function is called right after measurement has finished.
        It only redirects to a new website to indicate that measurement is
        really finished 
        '''
        self._route.redirect("/test")
#         return template('web/template.tpl', 
#                         config=False,
#                         running=False, 
#                         data=self.config)
#     
    def _route(self):
        #if route('/nfpa') -> go the self.FillConfiguration() function
        self._app.route('/nfpa', callback=self._fillConfiguration)
        self._app.route('/static/<filepath:path>', callback=self.getFile)
        self._app.route('/nfpa', method="POST", callback=self._startMeasurement)    
        self._app.route('/test', callback=self.test)

    def start(self):
        self._app.run(host=self.host, port=self.port, debug=True)   
         
    def stop(self):
        #show the 'end measurement' html
#         self.showEndMeasurement()
        os.kill(os.getpid(), signal.SIGTERM)
        exit(-1)

    def getFile(self,filepath):
        curr_dir = os.getcwd() + "/web/static/"
#         print(curr_dir)
        return static_file(filepath, root=curr_dir)
    
    def test(self):
        
        return template('web/select.tpl')
    
    def _fillConfiguration(self):
        '''
        This function is called, when /nfpa route is set, and it passes the
        config variable (read from config file) to a web-site template in order
        to fill the forms with previously used data.
        '''
        
        return template('web/template.tpl', 
                        config=True, 
                        data=self.config,
                        data_comment=self.config_comment)
#     
#     def _serve_pictures(self, picture):
#         try:
#             img = static_file(picture, root='')
#         except e:
#             print(e)
#         print("get pic: ")
#         print(img)
#         print(picture)
#         
#         return img       
    

       
    
    def _startMeasurement(self):


        self.log.info("Reading configuration parameters...")
        #create temporary shortened variable pointing at self.config
        c = self.config
        tmp_lists = ["realisticTraffics", 
                     "trafficTypes", 
                     "packetSizes"]
        
        #the following config elements should not be checked, since they are
        #initialized by ReadConfig class, and they could be None if
        #once the configuration parameters were set wrong via web-form, and
        #back button was pressed and the whole process is restarting without
        #restarting the whole application
        no_check_list = ["helper_header",
                         "header_uni",
                         "header_bi",
                         "dbhelper",
                         "version",
                         "other_dpdk_params",
                         "socket_mem",
                         "control_vnf",
                         "control_path",
                         "control_mgmt"]
     
        for i in c:
            #different traffic types and packet sizes are needed to be
            #lists, so we need to split them according to the commas
            if i in tmp_lists:
                #get data, which is comma separated string
                l = request.forms.get(str('%s' % i))
                if l == '':
                    # their properties can be empty, so we set their
                    #values to None, and later while writing
                    #them out into the config file, we can check whether
                    #they are None
                    l = None
                else:
                    #otherwise, create list of it according to the commas
                    l = l.split(',')
                #set this list as value in self.config for key i
                c[i] = l
            else:
                #otherwise, nothing to do with the data
                c[i] = request.forms.get(str('%s' % i))
#         print(c)
        
        #check whether everything was set
        list_of_values = list(c.values())
        for i in c:
                
            if c[i] is None or c[i] == '':
                #property cannot be empty
                if (i not in tmp_lists) and (i not in no_check_list):
                    error_msg = str("Property %s was set to None or '' (null string)"
                                    % i)
                    self.log.error(error_msg)
                    return template('web/error_msg.tpl', 
                                    error=error_msg)
                
                #otherwise, no problem - handling them is done in
                #read_write_config_file.py
                
            
        #update self.config
        status = rwcf.writeConfigFile(c)
        if(status == -1):
            error_msg = str("Path to config file does not exist!" +\
                            "Wrong path: %s" % (self.config["MAIN_ROOT"])) 
            self.log.error(error_msg)
            return template('web/error_msg.tpl', 
                                    error=error_msg)
            
        self.log.info("Updating configuration file was done")  
        
        
        try:
            measureThread = MeasureThread(1, "measureThread", self.nfpa_class, self)
            
            measureThread.start()
            return template('web/template.tpl', 
                        config=False,
                        running=True,
                        data=self.config,
                        log_timestamp=df.getDateFormat\
                                                (self.config['app_start_date']))
        except:
            error_msg = "Error: Unable to start measurement! " +\
                        "Check terminal output for more details!"
            self.log.error(error_msg)
            return template('web/error_msg.tpl',
                            version=self.config['version'],
                            error=error_msg)
    
       
        
        
        
        
        
    



