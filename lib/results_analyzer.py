'''
This class is devoted for analyzing the results and create gnuplot compatible
output
'''

import divisor as div
import os
import copy
import special_bidir_traffic_checker as sbtc
import logger as l

import inspect

class ResultsAnalyzer(object):

    def __init__(self, config, **params):
        '''
        Constructor
        params -
        the config
        the current traffic type
        the current packet size
        '''

        # store config in local var
        self.config = config
        self.tt=params.get("trafficType", None)
        self.trace=params.get("traffic_trace", None)




        if(self.tt is None or self.trace is None):
            self.log.error("Something went wrong: no traffic type or traffic trace was passed")

        self.log = None
        # self.log.error(str(self.config))
        self.log = l.getLogger(self.__class__.__name__,
                             self.config['LOG_LEVEL'],
                             self.config['app_start_date'],
                             self.config['LOG_PATH'])

        print("========Caller method=========")
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        self.log.debug('caller name: %s' % calframe[1][3])

        #create a dictionary for the results
        self._results = {}

        # change directory where the res files are (PKTGEN_ROOT)
        os.chdir(self.config["PKTGEN_ROOT"])
        self.log.debug("Changed directory to %s" % str(os.getcwd()))


        # special ul-dl bidirectional traffic bit
        ul_dl = False
        # check whether special ul-dl bidirectional traffic was set
        if sbtc.checkSpecialTraffic(self.trace):
            ul_dl = True

        # assemble headers from header_uni and header_bi(if bidir is
        # set) -- We need deepcopy, to preserve original ones as they
        # were
        headers = copy.deepcopy(self.config['header_uni'])

        # append bidir header if biDir is set
        if (int(self.config["biDir"]) == 1):
            headers += self.config['header_bi']

        # check whether special ul-dl bidirectional traffic was set
        if ul_dl:
            # prepare for specail ul-dl bidirectional traffic
            headers = copy.deepcopy(self.config['header_uni'])
            # append bidir header
            headers += self.config['header_bi']

        if self.tt == "simple":
            # create subdictionaries for the different packet sizes
            for ps in self.config['packetSizes']:
                self._results[ps] = {}

                # create sub dicts of the list of  measured components
                # (sent(pps),recv(pps), etc.)
                for h in headers:
                    self._results[ps][h] = []

                # assemble res file path
                file_name = self.config["PKTGEN_ROOT"] + "/nfpa." + \
                           "simple." + ps + \
                          "bytes.res"
                # check file exists
                ok = os.path.isfile(file_name)
                if not ok:
                    self.log.error("ERROR: file %s not exists (skipping)" %
                                     file_name)
                # Open res file and parse each line of it
                with open(file_name, 'r') as lines:
                    for line in lines:
                        # remove blank spaces
                        line = line.strip()
                        # removed blank lines
                        if not line:
                            continue
                        # print out first line, but only print out!
                        # in the following we omit it, when results are
                        # parsed
                        self.log.debug(line)
                        # omit commented lines in analyzing
                        if (line.startswith("#", 0, 1)):
                            continue
                        # split config params
                        # self.log.info(line)

                        # split line according to tabs, then we got
                        # 0=snt(pps)
                        # 1=rec(pps)
                        # 2=miss(pps)
                        # 3=snt(bps)
                        # 4=rec(bps)
                        # 5=diff(bps)
                        # from 6 comes the same results, but for
                        # bidirectional results
                        results_as_list = line.split("|")
                        # append results
                        for i, h in enumerate(headers):
                            try:
                                self._results[ps][h].append(results_as_list[i])
                            except IndexError as ie:
                                self.log.error("Error during parsing res file")
                                self.log.error("splitted line: %s" %
                                             str(results_as_list))
                                self.log.error(ie)
                                if (self.config['email_adapter'] is not None) and \
                                      (not self.config['email_adapter'].sendErrorMail()):
                                    self.log.error("Sending ERROR email did not succeed...")
                                exit(-1)

        ######### SYNTHETIC TRAFFIC TYPE CASE ############
        elif self.tt == "synthetic":

            #create subdictionaries for the different packet sizes
            for ps in self.config['packetSizes']:
                self._results[ps] = {}

            # create sub dicts of the list of  measured components
            # (sent(pps),recv(pps), etc.)
            for h in headers:
                self._results[ps][h] = []


            # assemble res file path
            file_name = self.config["PKTGEN_ROOT"] + "/nfpa." + \
                      self.trace + "." + ps + \
                      "bytes.res"
            # check file exists
            ok = os.path.isfile(file_name)
            if not ok:
                self.log.error("ERROR: file %s not exists (skipping)" %
                             file_name)
            # Open res file and parse each line of it
            with open(file_name, 'r') as lines:
                for line in lines:
                    # remove blank spaces
                    line = line.strip()
                    # removed blank lines
                    if not line:
                        continue
                    # print out first line, but only print out!
                    # in the following we omit it, when results are
                    # parsed
                    self.log.debug(line)
                    # omit commented lines in analyzing
                    if (line.startswith("#", 0, 1)):
                        continue
                    # split config params
                    # self.log.info(line)

                    # split line according to tabs, then we got
                    # 0=snt(pps)
                    # 1=rec(pps)
                    # 2=miss(pps)
                    # 3=snt(bps)
                    # 4=rec(bps)
                    # 5=diff(bps)
                    # from 6 comes the same results, but for
                    # bidirectional results
                    results_as_list = line.split("|")
                    # append results
                    for i, h in enumerate(headers):
                        try:
                            self._results[ps][h].append(results_as_list[i])
                        except IndexError as ie:
                            self.log.error("Error during parsing res file")
                            self.log.error("splitted line: %s" %
                            str(results_as_list))
                            self.log.error(ie)
                            if (self.config['email_adapter'] is not None) and \
                            (not self.config['email_adapter'].sendErrorMail()):
                                self.log.error("Sending ERROR email did not succeed...")
                            exit(-1)

        ######### REALISTIC TRAFFIC TYPE CASE ############
        elif self.tt == "realistic":

            # create sub dicts of the list of  measured components
            # (sent(pps),recv(pps), etc.)
            for h in headers:
                self._results[h] = []

            # assemble res file path
            file_name = self.config["PKTGEN_ROOT"] + "/nfpa." + \
                      self.trace + ".res"

            # check file exists
            ok = os.path.isfile(file_name)
            if not ok:
                self.log.warn("File %s not exists (skipping)" % file_name)
              # res file exists

            # Open res file and parse each line of it
            with open(file_name, 'r') as lines:
                for line in lines:
                    # remove blank spaces
                    line = line.strip()
                    # removed blank lines
                    if not line:
                        continue
                    # print out first line, but only print out!
                    # in the following we omit it, when results are
                    # parsed
                    self.log.debug(line)
                    # omit commented lines in analyzing
                    if (line.startswith("#", 0, 1)):
                        continue
                    # split config params
                    # self.log.info(line)

                    # split line according to tabs, then we got
                    # 0=snt(pps)
                    # 1=rec(pps)
                    # 2=miss(pps)
                    # 3=snt(bps)
                    # 4=rec(bps)
                    # 5=diff(bps)
                    # from 6 comes the same results, but for
                    # bidirectional results
                    results_as_list = line.split("|")
                    # append results
                    for i, h in enumerate(headers):
                        try:
                            self._results[h].append(results_as_list[i])
                        except IndexError as ie:
                            self.log.error("Error during parsing res file")
                            self.log.error("splitted line: %s" %
                                            str(results_as_list))
                            self.log.error(ie)
                            if (self.config['email_adapter'] is not None) and \
                            (not self.config['email_adapter'].sendErrorMail()):
                                self.log.error("Sending ERROR email did not succeed...")
                            exit(-1)
        else:
            self.log.error("Unknown traffic type %s" % self.tt)
            exit(-1)

        self.processResultsData()




    def calculateTheoreticalMax(self, packetsize):
        '''
        This process will calculate the theoretical maximum according to the
        given packet size and the set port_type in nfpa.cfg.
        Then it converts it to the desired unit.
        return int - the theoretical maximum
        '''
        # get the port type from config file
        port_type = str(self.config['port_type']).split("_")[0]
        port_unit = str(self.config['port_type']).split("_")[1]

        # port rate will be an int according to port_type and the calculated
        # divisor for the given unit, for instance, in case of 10_G this will
        # be 10 * 1000000000 = 10.000.000.000 (dots are not commas, just for
        # easier reading!
        port_rate = int(port_type) * div.divisor(str(port_unit))

        #         self.log.debugug("port_rate: %d" % port_rate)

        # port rate is given in bit/s. Divide it by 8 to get byte/s.
        # packetsize should be extended with 20 bytes (interframe gap (12 bytes,
        # frame start seq. (7 bytes), and start delimiter (1 byte)
        theor_max = int(port_rate / 8 / (int(packetsize) + 20))

        return theor_max




    def processResultsData(self):
        '''
        This function is devoted for processing the results.
        It iterates through saved results, sort them, and according to the
        preset outlier percentage (found in nfpa.cfg) removes the outliers
        :param traffic_type: the actual traffic type for which the results are processed
        :param packet_size: the actual packet size for which the results are processed
        :return:

        '''

        ####################### SORTING ########################

        self.log.info("Processing results...(sorting, omitting outliers)")

        # calculate the number of min. elements to be omitted
        # get the length of one list (each list has the same length),
        # so get length of sent_pps list
        length = 0
        # get a traffic type for this, e.g., get the first traffic type
        tmp_tt = self.trace
        # get a packet size for this, e.g., get the first packet size
        tmp_ps = self.config['packetSizes'][0]
        # now, it is easy to access the results for, for instance, sent_pps
        # id for sent_pps is got from self.config['header_uni']
        id = self.config['header_uni'][0]

        if self.tt != "realistic":
            length = len(self._results[tmp_ps][id])
        else:
            length = len(self._results[id])

        self.log.debug("Number of rows in results: %s " % length)

        # Let's sort all results in order to omit later the min and max
        # outliers
        # processing
        # SIMPLE and SYNTHETIC CASE
        if self.tt != "realistic":
            for ps in self._results:
                for res in self._results[ps]:
                    self._results[ps][res].sort()
        # REALISTIC CASE
        else:
            for res in self._results:
                self._results[res].sort()

        #################### OMIT OUTLIERS #######################
        # calculate the number of outliers to be omitted for minimum
        omit_min = float(self.config['outlier_min_percentage']) * length
        # calculate the number of outliers to be omitted for maxmimum
        omit_max = float(self.config['outlier_max_percentage']) * length

        #         for i in (self._results['simple']['64']['sent_pps']):
        #             self.log.info(i)
        self.log.debug("--- number of omitted minimums: %s" % int(omit_min))
        self.log.debug("--- number of omitted maximums: %s" % int(omit_max))
        # omit first from the minimums
        # processing
        if ((int(omit_min) != 0) or (int(omit_max) != 0)):
            # SIMPLE and SYNTHETIC CASE
            if self.tt != "realistic":
                # only iterate if some outliers needs to be removed
                for ps in self._results:
                    for res in self._results[ps]:
                        if (int(omit_min) != 0):
                            # omit from the minimums
                            self._results[ps][res] = self._results[ps][res][int(omit_min):]

                        # if omit_max == 0, [:-0] makes no sense for omitting
                        # i.e., it clears the list :(, so only omit if omit_max
                        # is not ZERO
                        elif (int(omit_max) != 0):
                            # omit from the maximums at the same time with list function
                            self._results[ps][res] = self._results[ps][res][:-int(omit_max)]
            else:
                # REALISTIC CASE
                # only iterate if some outliers needs to be removed
                for res in self._results:
                    if (int(omit_min) != 0):
                        # omit from the minimums
                        self._results[res] = self._results[res][int(omit_min):]

                    # if omit_max == 0, [:-0] makes no sense for omitting
                    # i.e., it clears the list :(, so only omit if omit_max
                    # is not ZERO
                    elif (int(omit_max) != 0):
                        # omit from the maximums at the same time with list function
                        self._results[res] = self._results[res][:-int(omit_max)]


        ################# CALCULATE MIN, AVG, AND MAX VALUES ##################
        # here, the dataset and its type will be changed!
        # till now, self._results[tt][ps][res] was a list of the results!
        # from now, it will be a dictionary with keys as min, max , avg and values
        # as results for them
        tmp_dict = {}

        # we already know what the min and max values are, since results are
        # sorted
        if self.tt != "realistic":
            for ps in self._results:
                for res in self._results[ps]:
                    # lenght
                    l = len(self._results[ps][res])
                    # min = first element
                    min = copy.deepcopy(int(self._results[ps][res][0]))
                    # max = last element
                    max = copy.deepcopy(int(self._results[ps][res][(l - 1)]))

                    # calculate avg
                    avg = 0
                    for i in self._results[ps][res]:
                        avg += int(i)

                    avg = float(avg / float(l))

                    self.log.debug("min-max-avg for %s-%s-%s: %d-%d-%0.4f" %
                                 (self.trace, ps, res, min, max, avg))
                    # copying calculated metrics into the temporary dictionary
                    tmp_dict['max'] = copy.deepcopy(max)
                    tmp_dict['min'] = copy.deepcopy(min)
                    tmp_dict['avg'] = copy.deepcopy(avg)

                    # update results dictionary by changing type of list to dict
                    self._results[ps][res] = {}
                    # copy tmp_dict into the main results variable
                    self._results[ps][res] = copy.deepcopy(tmp_dict)
                    # now, it is safe to delete/clear tmp_dict for the next
                    # iteration of the loops

                # append self._results with a new key,value pair
                # add theoretical value
                self._results[ps]['theor_max'] = self.calculateTheoreticalMax(ps)
        else:
            for res in self._results:
                # lenght
                l = len(self._results[res])
                # min = first element
                min = copy.deepcopy(int(self._results[res][0]))
                # max = last element
                max = copy.deepcopy(int(self._results[res][(l - 1)]))

                # calculate avg
                avg = 0
                for i in self._results[res]:
                    avg += int(i)

                avg = float(avg / float(l))

                self.log.debug("min-max-avg for %s-%s: %d-%d-%0.4f" %
                             (self.trace, res, min, max, avg))
                # copying calculated metrics into the temporary dictionary
                tmp_dict['max'] = copy.deepcopy(max)
                tmp_dict['min'] = copy.deepcopy(min)
                tmp_dict['avg'] = copy.deepcopy(avg)

                # update results dictionary by changing type of list to dict
                self._results[res] = {}
                # copy tmp_dict into the main results variable
                self._results[res] = copy.deepcopy(tmp_dict)
                # now, it is safe to delete/clear tmp_dict for the next
                # iteration of the loops



        self.log.info("[DONE]")
        self.log.debug(str(self._results))



    def getResultsDict(self):
        '''
        This procedure returns the results dictionary that is possible
        to pass later to different modules, such as Visualizer
        return self._results - dictionary
        '''
        return self._results