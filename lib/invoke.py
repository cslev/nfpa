from subprocess import (PIPE, Popen)

    
def invoke(command):
    '''
    This helper function uses subprocess lib to execute system command.
    This could be helpful in case of errors, since reading the return value
    passed by this function enables to write out system command errors into the
    log file.
    '''

    process = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
    stdout,stderr= process.communicate()
    exit_code = process.wait()
    
    #create a list of the elements
    retList = [stdout, exit_code]
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
    
    return retList


def check_retval(self, cmd, retval):
    '''
    This function is devoted to check return values got from calling invoke()
    If return value is not 0, then an error occured. Error message and error code will be printed out
    Otherwise, the exact value (e.g.,output of the command) is being returned
    :param cmd: Strgin - the command that was executed
    :param retval: List - return value: [0] error msg, [1] error code
    '''
    if (retval[1] != 0):
        self.log.error("Error during executing command: %s" % cmd)
        self.log.error("Error: %s" % str(retval[0]))
        self.log.error("Exit_code: %s" % str(retval[1]))
        exit(-1)

    return retval[0]