import logger as l
from invoke import invoke

def configure_remote_vnf(nfpa, vnf_function, traffictype):
    '''
    Configure the remote vnf via pre-installed tools located on the
    same machine where NFPA is.

    :return: True - if success, False - if not

    '''
    # Path to .bess files
    config = nfpa.config
    log = l.getLogger(__name__, config['LOG_LEVEL'], config['app_start_date'],
                      config['LOG_PATH'])

    bess_path = config["MAIN_ROOT"] + "/bess"
    def invoke1(cmd, msg):
        log.debug("%s with %s" % (msg, cmd))
        invoke(command=cmd, logger=log, email_adapter=config['email_adapter'])
        log.info("%s: done" % msg)

    # Reset bess daemon
    base_cmd = config['control_path'] + ' daemon connect %s -- '
    base_cmd = base_cmd % config.get('control_mgmt', 'localhost 10514')

    cmd = base_cmd + 'daemon reset || true'
    invoke1(cmd, 'Reseting daemon')

    inport = config["control_vnf_inport"]
    outport = config["control_vnf_outport"]
    pipeline = config["vnf_function"].lower()

    cmd = base_cmd + ('run file %s/%s vnf_inport=%s, vnf_outport=%s' %
                      (bess_path, pipeline, inport, outport))
    invoke1(cmd, 'Starting pipeline')

    assert(int(config["biDir"]) == 0)
    return True
