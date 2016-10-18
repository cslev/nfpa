'''
This class is taking part of visualizing the results via Gnuplot according
to the preset configurations, e.g., it takes into account the desired units for
the axes.
As the main part, first, it creates a gnuplot ready data file, which is 
processable by gnuplot

@todo: gnuplot res files' names should be placed in self.results, then
it could be accessed later from anywhere. For now, it's not necessary (20150624)
'''



import os
import divisor as div
#for timestamping gnuplot files
import date_formatter as df
import copy
import special_bidir_traffic_checker as sbtc
import logger as l
import invoke as invoke


class Visualizer(object):
    
        
    def __init__(self, **params):
        '''
        Two main params are: config, and results, but for further possible 
        extensions, some other params could also be passed and processed
        '''
        
        self.config = params.get('config', None)
        self.results = params.get('results', None)
        self.type = params.get('type', None)
        self.tt = params.get('traffic_trace', None)
        
        
        #create a reference for logger
        self.log = l.getLogger( self.__class__.__name__, 
                                self.config['LOG_LEVEL'], 
                                self.config['app_start_date'],
                                self.config['LOG_PATH'])
        
        self.log.info("STARTED...")
        
        
        if(self.type is None):
           self.log.error("Class wrongly instantiated - NO RESULTS TYPE SET!")
        
        #get current timestamp        
        st = df.getDateFormat(self.config['app_start_date'])
        
        #biDir prefix
        dir = "uniDir"
        if(int(self.config['biDir']) == 1):
            dir = "biDir"
            
        
        
        #create prefix for results/gnuplot files with lower granularity
        #vnf_name -> vnf_driver -> cpu -> virt -> port_type 
        self.prefix = self.config['RES_PATH'] + "/" + \
                      self.config['vnf_name'] + "/" + \
                      self.config['vnf_driver'] + "/" + \
                      self.config['cpu_make'] + "/" + \
                      "virt_" + self.config['virtualization'] + "/" + \
                      self.config['port_type'] + "/"
  

        #check whether directory exists
        if not os.path.exists(self.prefix):
            os.makedirs(self.prefix)


        
        
                      
        self.prefix += self.config['scenario_name']  + "_" + \
                      "TRAFFICTYPE." + dir +"_" + str(st) + ".data"
                      #TRAFFICTYPE will be replaced later to the actual traffic
                      
        
        
        
        #if any of the variable above are non-exist vars, we need to TERMINATE
        if(self.config is None or self.results is None):
            self.log.error("config and results dictionaries are EMPTY")
            self.log.error("Something went wrong during initialization")
            self.log.error("EXITING...")
            os.exit(-1)
        
        #create gnuplot readable file
        self.createGnuplotDataFile()
        
        
        #ready
        self.log.info("[DONE]")
        self.log.info("Charts could be found in " + self.config['MAIN_ROOT'] +\
                    "/" + self.config['RES_DIR'])

    
        
    def createGnuplotDataFile(self):    
        '''
        This procedure will create a gnuplot readable file from the results
        analyzed so far. One gnuplot file will represent one
        traffic scenario with the used packetsizes.
        ''' 
        #we need to divide the results according to the preset units!
        
        #just for easier usage
        pu = self.config['pps_unit']
        bu = self.config['bps_unit']
        
        #simple list for easier handling average, minimum and maximum values
        #store in results dictionaries
        helper_header = self.config['helper_header']
    
        #if synthetic traffic is needed to be plotted
        if self.type == "synthetic":

            #all right, we got the header data

            ul_dl = False
            if(sbtc.checkSpecialTraffic(self.tt)):
                ul_dl = True

            #assemble headers for accessing results dictionary
            headers = copy.deepcopy(self.config['header_uni'])
            if((int(self.config['biDir']) == 1) or (ul_dl)):
                #we need to check whether the special ul-dl bidirectional
                #traffic type was set. If so, then we also add header_bi
                #to headers var
                headers += self.config['header_bi']

            #theoretical
            header = "Size, Theor_max(p), "
                
            #assemble header to write out in gnuplot file
            #the following variables are necessary to know when to stop
            #writing commas
            headers_cnt = 1
            headers_len = len(headers) * len(helper_header)
            for h in headers:
                for h_h in helper_header:
                    if headers_cnt < headers_len:
                        comma = ", "
                    else:
                        comma = " "
                    header += h_h + "(" + h + ")" + comma
                    #increase headers counter
                    headers_cnt += 1

            header += "\n"

            #update units
            header = header.replace("pps", str("%spps" % pu))
            header = header.replace("bps", str("%sbps" % bu))


            #replace traffic type in file name to the current one
            data_file = self.prefix.replace("TRAFFICTYPE", str(self.tt))

            #update direction irrespectively whether biDir was set,so
            #replace uniDir to biDir - if biDir was set, nothing will happen
            if(ul_dl):
                data_file = data_file.replace("uniDir", "biDir")

            self.log.debug("Gnuplot data file will be: %s " % data_file)

            #assemble gnuplot arguments (input file will be the data file
            #that stores the results
            if not ul_dl:
                #if both ports are using the same pcap, we set that type
                #for both sent, and recv property in gnuplot params
                tmp_tt = [self.tt, self.tt]

            else:
                #indicate in ports which traffic is what
                tmp_tt = sbtc.splitTraffic(self.tt)

            gp_params = str("\"input_file='%s';"
                            "pps_unit='%s';"
                            "bps_unit='%s';"
                            "tr1='%s';"
                            "tr2='%s';\"" %
                             (data_file,
                              self.config['pps_unit'],
                              self.config['bps_unit'],
                              tmp_tt[0],
                              tmp_tt[1]))

            self.log.debug("Gnuplot params will be %s " % gp_params)

            try:
                #open file
                gp_data_file = open(data_file, 'w')
                #write out header
                gp_data_file.write(header)

                self.log.debug("create gnuplot file for traffic type: %s " % (self.tt))

                #we need to sort the results according to the packetsizes,
                #since data rows should be sorted for gnuplot, otherwise
                #very weird charts are generated
                #NOTE: it could be sorted via linux cat file|sort -n, but
                #do not want to restrict to BASH
                tmp_ps_list = []


                #iterate through the packet sizes
                for ps in self.results:

                    #so, we store the ps numbers in a list, then sort it, and
                    #iterate through the new list
                    tmp_ps_list.append(int(ps))

                tmp_ps_list.sort()

                self.log.debug(str(tmp_ps_list))


                for ps in tmp_ps_list:
                    ps = str(ps)

                    #create a simple pointer to main results dict
                    pkt_res = self.results[ps]

                    #theoretical
                    one_line = ps + ", " + \
                    str(round(float(pkt_res['theor_max']/div.divisor(pu)), 4)) + ", "

                    #getting results and print out
                    #the following variable is necessary to know when to stop
                    #writing commas
                    headers_cnt = 1
                    headers_len = len(headers) * len(helper_header)
                    for h in headers:
                        for h_h in helper_header:
                            if 'pps' in h:
                                #pps results needs to be divided by pps divisor
                                d = div.divisor(pu)
                            elif 'bps' in h:
                                #bps results needs to be divided by bps divisor
                                d = div.divisor(bu)
                            else:
                                #this part could be happened (ony if someone
                                #extends the programcode in a wrong manner)
                                self.log.error("Wrong headers are used...Segfault")
                                self.log.error("EXITING...")
                                if (self.config['email_adapter'] is not None) and \
                                    (not self.config['email_adapter'].sendErrorMail()):
                                    self.log.error("Sending ERROR email did not succeed...")
                                exit(-1)

                            #assemble one line with this embedded for loops
                            if headers_cnt < headers_len:
                                comma = ", "
                            else:
                                comma = " "

                            one_line += str(round(float(pkt_res[h][h_h]/d), 4)) + comma

                            #increase headers counter
                            headers_cnt += 1

                    one_line += "\n"

                    #write out one line
                    gp_data_file.write(one_line)

                #close file
                gp_data_file.close()
            except IOError as e:
                self.log.error("Cannot open results file GNUPLOT")
                self.log.error(str(e))
                self.log.error("EXITING...")
                if (self.config['email_adapter'] is not None) and \
                    (not self.config['email_adapter'].sendErrorMail()):
                    self.log.error("Sending ERROR email did not succeed...")
                exit(-1)

            #call gnuplot command to create chart
            self.drawChartViaGnuplot(gp_params, ul_dl=ul_dl)
        
        #if realistic traffic is needed to be plotted
        elif self.type == "realistic":

            self.log.debug("Visualizing %s" % self.tt)

            ul_dl = False
            if(sbtc.checkSpecialTraffic(self.tt)):
                ul_dl = True

            #assemble headers for accessing results dictionary
            headers = copy.deepcopy(self.config['header_uni'])
            if((int(self.config['biDir']) == 1) or (ul_dl)):
                #we need to check whether the special ul-dl bidirectional
                #traffic type was set. If so, then we also add header_bi
                #to headers var
                headers += self.config['header_bi']

            #assemble header in data file
            header = "Unit(" + self.config['pps_unit']
            header += "pps-" + self.config['bps_unit']
            header += "bps), Min, Avg, Max\n"
            #replace traffic type in file name to the current one
            data_file = self.prefix.replace("TRAFFICTYPE", str("realistic_%s"
                                                               % self.tt))

            #update direction irrespectively whether biDir was set,so
            #replace uniDir to biDir - if biDir was set, nothing will happen
            if(ul_dl):
                data_file = data_file.replace("uniDir", "biDir")

            self.log.debug("Gnuplot data file will be: %s " % data_file)

            #assemble gnuplot arguments (input file will be the data file
            #that stores the results
            if not ul_dl:
                #if both ports are using the same pcap, we set that type
                #for both sent, and recv property in gnuplot params
                tmp_tt = [self.tt, self.tt]

            else:
                #indicate in ports which traffic is what
                tmp_tt = sbtc.splitTraffic(self.tt)

            gp_params = str("\"input_file='%s';"
                            "pps_unit='%s';"
                            "bps_unit='%s';"
                            "tr1='%s';"
                            "tr2='%s';\"" %
                            (data_file,
                              self.config['pps_unit'],
                              self.config['bps_unit'],
                              tmp_tt[0],
                              tmp_tt[1]))


            self.log.debug("Gnuplot params will be %s " % gp_params)
            try:
                #open file
                gp_data_file = open(data_file, 'w')
                #write out header
                gp_data_file.write(header)

                self.log.debug("create gnuplot file for %s " % (self.tt))

                #create a simple pointer to main results dict
                pkt_res = self.results


                one_line = ""


                #getting results and print out
                for h in headers:
                    #print out unit as the first column
                    one_line += h + ", "
                    headers_cnt = 1
                    for h_h in helper_header:
                        if 'pps' in h:
                            #pps results needs to be divided by pps divisor
                            d = div.divisor(pu)
                        elif 'bps' in h:
                            #bps results needs to be divided by bps divisor
                            d = div.divisor(bu)
                        else:
                            #this part could be happened (only if someone
                            #extends the programcode in a wrong manner)
                            self.log.error("Wrong headers are used...Segfault")
                            self.log.error("EXITING...")
                            if (self.config['email_adapter'] is not None) and \
                                (not self.config['email_adapter'].sendErrorMail()):
                                self.log.error("Sending ERROR email did not succeed...")
                            exit(-1)

                        if(headers_cnt < 3):
                            comma = ", "
                        else:
                            comma = " "


                        one_line += str(round(float(pkt_res[h][h_h]/d), 4)) + comma

                        headers_cnt += 1
                    one_line += "\n"

                #update unit in the first column
                one_line = one_line.replace("pps", str("%spps" % pu))
                one_line = one_line.replace("bps", str("%sbps" % bu))
                #update column with the traffic types used for ports
#                 one_line = one_line.replace("sent_pps",
#                                             str("sent_%spps_%s" % (pu,
#                                                                    tmp_tt[0])))
#                 one_line = one_line.replace("recv_pps",
#                                             str("recv_%spps_%s" % (pu,
#                                                                    tmp_tt[0])))
#                 one_line = one_line.replace("miss_pps",
#                                             str("miss_%spps_%s" % (pu,
#                                                                    tmp_tt[0])))
#                 one_line = one_line.replace("sent_bps",
#                                             str("sent_%sbps_%s" % (bu,
#                                                                    tmp_tt[0])))
#                 one_line = one_line.replace("recv_bps",
#                                             str("recv_%sbps_%s" % (bu,
#                                                                    tmp_tt[0])))
#                 one_line = one_line.replace("diff_bps",
#                                             str("diff_%sbps_%s" % (bu,
#                                                                    tmp_tt[0])))
#
#                 #update bidirectional header elements as well
#                 if((int(self.config['biDir']) == 1) or (ul_dl)):
#                     one_line = one_line.replace(
#                                            "sent_pps_bidir",
#                                            str("sent_%spps_%s" % (pu,
#                                                                   tmp_tt[1])))
#                     one_line = one_line.replace(
#                                            "recv_pps_bidir",
#                                            str("recv_%spps_%s" % (pu,
#                                                                   tmp_tt[1])))
#
#                     one_line = one_line.replace(
#                                            "miss_pps_bidir",
#                                            str("miss_%spps_%s" % (pu,
#                                                                   tmp_tt[1])))
#
#                     one_line = one_line.replace(
#                                            "sent_bps_bidir",
#                                            str("sent_%sbps_%s" % (bu,
#                                                                   tmp_tt[1])))
#
#                     one_line = one_line.replace(
#                                            "recv_bps_bidir",
#                                            str("recv_%sbps_%s" % (bu,
#                                                                   tmp_tt[1])))
#
#                     one_line = one_line.replace(
#                                            "diff_bps_bidir",
#                                            str("diff_%sbps_%s" % (bu,
#                                                                   tmp_tt[1])))


                #write out one line
                gp_data_file.write(one_line)

                #close file
                gp_data_file.close()
            except IOError as e:
                self.log.error("Cannot open results file GNUPLOT")
                self.log.error(str(e))
                self.log.error("EXITING...")
                if (self.config['email_adapter'] is not None) and \
                    (not self.config['email_adapter'].sendErrorMail()):
                    self.log.error("Sending ERROR email did not succeed...")
                exit(-1)
            #call gnuplot command to create chart
            self.drawChartViaGnuplot(gp_params, ul_dl=ul_dl)
                

    def drawChartViaGnuplot(self, gnuplot_arguments, **params):
        '''
        This function will call gnuplot with the passed arguments and creates
        .eps charts from the results.
        Should be called from self.createGnuplotDataFile() function, since
        that function creates the data files and knows what the filenames are.
        '''
        
        #if special ul_dl bidirectional traffic was set, then we need to use
        #the plotter_bidir gnuplot file for visualizing
        ul_dl = params.get('ul_dl', False)
        
        
        self.log.debug(gnuplot_arguments)
        #synthetic traffic/measurements have different GNUplot plotter files
        if(self.type == "synthetic"):
            plotter_file = "/lib/plotter.gp"
            #if bi directional measurement was set, we use different gnuplot file
            if((int(self.config["biDir"]) == 1) or ul_dl):
                plotter_file = "/lib/plotter_bidir.gp"
                
            #assemble gnuplot command
            gnuplot_command = "gnuplot -e " + gnuplot_arguments + " " + \
                              self.config['MAIN_ROOT'] + plotter_file
                              
        #Realistic traffic/measurements have different GNUplot plotter files
        elif(self.type == "realistic"):
            plotter_file = "/lib/plotter_realistic.gp"
            #if bi directional measurement was set, we use different gnuplot file
            if((int(self.config["biDir"]) == 1) or ul_dl):
                plotter_file = "/lib/plotter_realistic_bidir.gp"
                
            #assemble gnuplot command
            gnuplot_command = "gnuplot -e " + gnuplot_arguments + " " + \
                              self.config['MAIN_ROOT'] + plotter_file   
                              
                                             
                                             
        self.log.debug("======= GNUPLOT =======")
        self.log.debug(gnuplot_command)
        retval = (invoke.invoke(command=gnuplot_command,
                                logger=self.log,
                                email_adapter=self.config['email_adapter']))[0]
        if retval is not None or retval != '':
            self.log.info(retval)
            

    def getPrefixToPlots(self):
        '''
        This function is devoted to pass the path to the plot files
        :return: almost whole path to the plots (until timestamp)
        '''
        return self.prefix
        
        
        
        
        
        