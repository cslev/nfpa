'''
Created on Sep 23, 2016

@author: lele
'''
import time
import invoke as invoke
import date_formatter as df

def prepareOpenFlowRules(logger, path, flowrulefile,inport,outport, bidir):
    '''
    This function will take the openflow flow rule files consisting the meta port data, and replaces
    them according to the control_vnf_inport and control_vnf_outport parameter. The original
    flow rule file will still be existed for further reusage, so a new specialized flow rule
    file will born temporary.

    :param logger Logger: the logger object from the calling class to make it possible to log
    :param flowrulefile String: the defined flow rule file with meta port data
    :param inport String: control_vnf_inport
    :param outport String: control_vnf_outport
    :param bidir Bool: to indicate whether INPORT2 and OUTPORT1 also exist in the file

    :return: new temporary flow rule file
    '''

    #shortening the got params
    l = logger
    f = flowrulefile
    fpath = path + flowrulefile

    #get a timestamp for having unique filenames for temporary flow rule files
    t=time.time()
    timestamp=str(df.getDateFormat(t))

    #start reading file and replacing (calling linux's sed is simpler than make it in python)
    l.info("Parsing file %s" % f)
    #temporary name for the temporary file
    tmp_file = path + "tmp/" + f + "_tmp_" + inport + "_" + outport + "_" + timestamp
    #first sed command for inport
    sed_cmd = 'sed "s/<INPORT1>/' + inport + '/" ' + fpath + ' > ' + tmp_file
    #invoke first sed
    invoke.invoke(sed_cmd, l)
    #second sed command for outport - From now, we already have the tmp file,
    #so we make the changes over it
    sed_cmd = 'sed -i "s/<OUTPORT2>/' + outport + '/" ' + tmp_file
    invoke.invoke(sed_cmd, l)

    #third and fourth sed if bidir is set
    if bidir:
        #note again that if there is no such inport and outport in the flow rule files
        #sed doesn't do anything, thus it won't mess the file even if we call it
        sed_cmd = 'sed -i "s/<INPORT2>/' + outport + '/" ' + tmp_file
        invoke.invoke(sed_cmd, l)
        sed_cmd = 'sed -i "s/<OUTPORT1>/' + inport + '/" ' + tmp_file
        invoke.invoke(sed_cmd, l)

    return tmp_file
