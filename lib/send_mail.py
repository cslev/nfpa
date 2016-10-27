import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.mime.text import MIMEText
import date_formatter as df
import logger as l
# import pdb


class EmailAdapter(object):
    '''
    This class is devoted to send emails with the results to the given
    email address using a configurable email service chosen by the user
    I only tested it with GMAIL, and it works
    '''

    def __init__(self, config):
        '''
        Constructor
        :param config: dictionary of the configration from nfpa.cfg
        '''
        self.config = config
        if self.config['email_service'].lower() != "true":
            return 0

        self.log = l.getLogger(self.__class__.__name__,
                               self.config['LOG_LEVEL'],
                               self.config['app_start_date'],
                               self.config['LOG_PATH'])

        # get current timestamp
        self.st = df.getDateFormat(self.config['app_start_date'])

        self.SUBJECT = "[NFPA-SERVICE]"




    def sendResultsMail(self, current_trace, is_trace_synthetic):
        '''
        This function sends practically the email after it is assembled
        :param current_trace: The last trace used for measurement
        :param is_trace_synthetic: bool -- indicate synthetic or realistic trace
        :return: True if success, False otherwise
        '''
        self.log.info("Sending email with the results...")

        addition_to_subject="Finished: " + \
                            self.config['vnf_name'] + " as " + \
                            self.config['vnf_function'] + " with trace " +\
                            current_trace


        self.msg = MIMEMultipart()
        self.msg['Subject'] = self.SUBJECT + addition_to_subject
        self.msg['From'] = self.config['email_from']
        self.msg['To'] = self.config['email_to']


        # assembling payload, starting with the text message
        self.tmp_text = self._assembleDetails()
        self.tmp_text += "\n\nwith trace " + current_trace + \
                         " has been finished.\n"
        # pdb.set_trace()
        if is_trace_synthetic:
            #synthetic traffic traces generate more files with different
            #naming convenctions
            trace = current_trace
            self.res_file_postfix = [
                     ".data",
                     "_diff_" + self.config['bps_unit'] + "bps.eps",
                     "_miss_" + self.config['pps_unit'] + "pps.eps",
                     "_sent_recv_" + self.config['bps_unit'] + "bps.eps",
                     "_sent_recv_" + self.config['pps_unit'] + "pps.eps"]

        else:
            #realistic traces have a 'realistic_' prefix, and less files
            #are produced for one measurement
            trace = "realistic_" + current_trace
            self.res_file_postfix = [
                ".data",
                "__" + self.config['bps_unit'] + "bps.eps",
                "__" + self.config['pps_unit'] + "pps.eps"]



        #assembling prefix for the trace (same as visualizer.py) also does
        # biDir prefix
        dir = "uniDir"
        if (int(self.config['biDir']) == 1):
            dir = "biDir"

        self.prefix = self.config['RES_PATH'] + "/" + \
                      self.config['vnf_name'] + "/" + \
                      self.config['vnf_driver'] + "/" + \
                      self.config['cpu_make'] + "/" + \
                      "virt_" + self.config['virtualization'] + "/" + \
                      self.config['port_type'] + "/"

        self.filename = self.config['scenario_name'] + "_" + \
                        trace + "." + dir + "_" + str(self.st)

        self.path = self.prefix + self.filename



        self._addFooter()


        text=MIMEText(self.tmp_text)
        self.msg.attach(text)


        #attach res files
        for postfix in self.res_file_postfix:
            tmp_path=self.path + postfix
            f=file(tmp_path)
            attachment=MIMEText(f.read())
            attachment.add_header('Content-Disposition', 'attachment',filename=self.filename+postfix)
            self.msg.attach(attachment)

        #attach log file to message
        self._attachLogFile()

        self.log.debug('Email message ready')

        #call the practical sending function
        return self._sendEmail()

    def _assembleDetails(self):
        '''
        This function assembles the main body of the email containing the measurement details
        :return - String: the email body
        '''
        body = "Your measurement " + self.config['scenario_name'] + \
                   " with the following setup:" + \
                   "\nDetails (that you may forget so far): \n" + \
                   "vnf_name: " + self.config['vnf_name'] + "\n" + \
                   "vnf_version: " + self.config['vnf_version'] + "\n" + \
                   "vnf_driver: " + self.config['vnf_driver'] + "\n" + \
                   "vnf_driver_version: " + self.config['vnf_driver_version'] + "\n" + \
                   "vnf_function: " + self.config['vnf_function'] + "\n" + \
                   "vnf_num_cores: " + self.config['vnf_num_cores'] + "\n" + \
                   "vnf_comment: " + self.config['vnf_comment'] + "\n\n" + \
                   "cpu_make: " + self.config['cpu_make'] + "\n" + \
                   "cpu_model: " + self.config['cpu_model'] + "\n" + \
                   "nic_make: " + self.config['nic_make'] + "\n" + \
                   "nic_model: " + self.config['nic_model'] + "\n" + \
                   "port_type:" + self.config['port_type'] + "\n\n"

        return body

    def _addFooter(self):
        '''
        This function adds standard footer to the email's text message
        :return:
        '''
        self.tmp_text += "Thanks for using NFPA " + self.config['version'] + "\n" + \
                         "Observed a problem?! Go to http://nfpa.tmit.bme.hu and/or \n" + \
                         "Subscribe to the nfpa-users mailing list under " + \
                         "http://lendulet.tmit.bme.hu/cgi-bin/mailman/listinfo/nfpa-users'>"

    def sendErrorMail(self):
        '''
        This function only send log files and error message
        :return:
        '''

        addition_to_subject="ERROR: " + \
                            self.config['vnf_name'] + " as " + \
                            self.config['vnf_function'] + " with trace " +\
                            current_trace

        self.msg = MIMEMultipart()
        self.msg['Subject'] = self.SUBJECT + addition_to_subject
        self.msg['From'] = self.config['email_from']
        self.msg['To'] = self.config['email_to']


        self.log.info("Sending email with the log file...")

        self.tmp_text = "ERROR occurred during measurement...log file attached.\n\n\n"
        self.tmp_text += self._assembleDetails()

        self._addFooter()

        text = MIMEText(self.tmp_text)
        self.msg.attach(text)

        #attach log file to message
        self._attachLogFile()

        return  self._sendEmail()

    def _sendEmail(self):
        '''
        This function do practically the email sending
        :return: success
        '''
        try:
            conn=smtplib.SMTP(self.config['email_server'],
                              self.config['email_port'],
                              self.config['email_timeout'])
            # conn.set_debuglevel(10)
            self.log.debug("Connected to SMTP server %s" % self.config['email_server'])

            conn.starttls()
            conn.ehlo()
            self.log.debug('Authenticated')
            conn.login(self.config['email_username'],
                       self.config['email_password'])

            self.log.debug('Logged in')


            self.log.debug('Send email.')
            conn.sendmail(self.config['email_from'],
                          self.config['email_to'],
                          self.msg.as_string())
            self.log.debug('SUCCESS')
            conn.quit()
            return True
        except Exception as error:
            self.log.warn(error)
            self.log.warn("Unable to connect, or just timed out")
            self.log.warn("Email sending feature won't work for now")
            return False



    def _attachLogFile(self):
        '''
        This function just attaches the log file to the email
        :param message: the message whereto the log file is going to be attached
        :return: message with log file attached
        '''
        # attach log file as well
        log_file = "log_" + self.st + ".log"
        f = file(self.config['LOG_PATH'] + log_file)
        attachment = MIMEText(f.read())
        attachment.add_header('Content-Disposition', 'attachment', filename=log_file)
        self.msg.attach(attachment)

