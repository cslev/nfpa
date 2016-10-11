from subprocess import (PIPE, Popen)

    
def invoke(command, logger):
    '''
    This helper function uses subprocess lib to execute system command.
    This could be helpful in case of errors, since reading the return value
    passed by this function enables to write out system command errors into the
    log file.

    :param command: the system command itself
    :param logger: logger object from the calling class to make it possible to log
    :return: if no error: list of [stdout, exit code, stderr], otherwise it exits the application and prints the exit_code
    and the corresponding error
    '''

    process = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
    stdout,stderr= process.communicate()
    exit_code = process.wait()
    
    #create a list of the elements
    retList = [stdout, exit_code, stderr]
    #this will look like
    #[('stdout of command','stderr_if_happened'), exit_code]
    #for instance:
    #NO ERROR
    #invoke("cat /proc/meminfo|grep -i hugePages_free")
    #[('HugePages_Free:        0\n', ''), 0]
    #
    #ERROR:
    #invoke("cat /proc/meminfod|grep -i hugePages_free")
    #[('', 'cat: /proc/meminfod: No such file or directory\n'), 1]

    if (retList[1] != 0):
        if(logger is None):
            print("Error during executing command: %s" % command)
            print("Error: %s" % str(retList[2]))
            print("Exit_code: %s" % str(retList[1]))
        else:
            logger.error("Error during executing command: %s" % command)
            logger.error("Error: %s" % str(retList[2]))
            logger.error("Exit_code: %s" % str(retList[1]))
        exit(-1)

    return retList


# def check_retval(cmd, retval, logger_instance):
#     '''
#     This function is devoted to check return values got from calling invoke()
#     If return value is not 0, then an error occured. Error message and error code will be printed out
#     Otherwise, the exact value (e.g.,output of the command) is being returned
#     :param cmd: Strgin - the command that was executed
#     :param retval: List - return value: [0] error msg, [1] error code
#     :param logger_instance: Logger instance of the class where from this function is called
#     '''
#     if (retval[1] != 0):
#         logger_instance.error("Error during executing command: %s" % cmd)
#         logger_instance.error("Error: %s" % str(retval[2]))
#         logger_instance.error("Exit_code: %s" % str(retval[1]))
#         exit(-1)
#
#     return retval[0]