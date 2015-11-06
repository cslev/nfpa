'''
This module is used for checking whether a special traffic type has been set,
indicating that two different pcaps should be used for the two different ports
'''
import copy
def checkSpecialTraffic(traffic_type):
    '''
    This function will check whether a special traffic type was set for
    ul-dl traffics, e.g., different pcaps should be loaded to different ports,
    and bidirectional measurements need to be made by default
    '''
    tmp_tt = copy.deepcopy(traffic_type)
    tmp_tt = tmp_tt.split("|")
    if len(tmp_tt) == 2:
        #if split('---') returns a one element list, then
        #nothing special happens, only a special traffic 
        #type is set. Otherwise, special treatment is
        #required
        return True
    
    return False
    

def splitTraffic(traffic_type):
    '''
    This function only divides the special traffic types via the pipe (|), and
    returns them as a list of strings
    '''    
    tmp_tt = copy.deepcopy(traffic_type)
    tmp_tt = tmp_tt.split("|")
    
    return tmp_tt 
