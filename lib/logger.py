import logging
import date_formatter as df
#for create log directory
import os
import invoke as invoke
logger = None
colors = {
          'info': '\033[1;92m', 
          'debug': '\033[0;94m',
          'warning':'\033[1;93m',
          'error':'\033[1;31m',
          'critical':'\033[1;31m'          
          }
no_color = '\033[0m'


def getLogger(class_name, level, timestamp, path):
    '''
    This function will create a logger and returns it. The logger object is 
    logging to stdout considering the given logging level, and also logs into
    a file with loglevel DEBUG to print out everything
    class_name String - the class name that asks for a logger object
    level String - the desired logging level (DEBUG, INFO, WARNING, ERROR, 
    CRITICAL
    timestamp - time stamp for the name of the log file
    path - the path the log file should be saved
    '''
    logger = logging.getLogger(class_name)
    
    timestamp = df.getDateFormat(timestamp)
    
    #remove log/ from the path, and check the parent directory's existence
    path_parent_dir = path[:-4]

    if not (os.path.isdir(path_parent_dir)):
            print("Path to create log/ directory (%s) does not exist!" % 
                          path_parent_dir)
            print("EXITING...")
            exit(-1)
    #create the log directory
    log_dir_cmd = "mkdir -p " + path
    retval = invoke.invoke(log_dir_cmd)
    if(retval[1] != 0):
        print("Error during creating log file")
        print("Error: %s" % str(retval[0]))
        print("Exit_code: %s" % str(retval[1]))
        exit(-1)
    
     # create file handler which logs even debug messages
    fh = logging.FileHandler(path + '/log_' + timestamp + ".log")
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    
    
    level = level.upper()
    if level == "DEBUG":
        logger.setLevel(logging.DEBUG)
        ch.setLevel(logging.DEBUG)
    elif level == "INFO":
        logger.setLevel(logging.INFO)
        ch.setLevel(logging.INFO)
    elif level == "WARNING":
        logger.setLevel(logging.WARNING)
        ch.setLevel(logging.WARNING)
    elif level == "ERROR":
        logger.setLevel(logging.ERROR)
        ch.setLevel(logging.ERROR)
    elif level == "CRITICAL":
        logger.setLevel(logging.CRITICAL)
        ch.setLevel(logging.CRITICAL)
    else:
        print("Log level was not set properly...set to default DEBUG")
        logger.setLevel(logging.DEBUG)
    
            
        
    
    logging.addLevelName( logging.INFO, str("%s%s%s" % 
                                       (colors['info'], 
                                        logging.getLevelName(logging.INFO),
                                        no_color)))
    logging.addLevelName( logging.DEBUG, str("%s%s%s" % 
                                       (colors['debug'], 
                                        logging.getLevelName(logging.DEBUG),
                                        no_color)))
    logging.addLevelName( logging.WARNING, str("%s%s%s" % 
                                       (colors['warning'], 
                                        logging.getLevelName(logging.WARNING),
                                        no_color)))
    logging.addLevelName( logging.ERROR, str("%s%s%s" % 
                                       (colors['error'], 
                                        logging.getLevelName(logging.ERROR),
                                        no_color)))
    logging.addLevelName( logging.CRITICAL, str("%s%s%s" % 
                                       (colors['critical'], 
                                        logging.getLevelName(logging.CRITICAL),
                                        no_color)))
    
#     logging.addLevelName( logging.ERROR, "\033[1;41m%s\033[1;0m" % logging.getLevelName(logging.ERROR))
   
    # create formatter and add it to the handlers
#     formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    formatter = logging.Formatter('[%(name)s] - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    # add the handlers to logger
    logger.addHandler(ch)
    logger.addHandler(fh)
    
    return logger