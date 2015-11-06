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

