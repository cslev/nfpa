import logger as l
from invoke import invoke

def configure_remote_vnf(config, traffictype):
    '''
    Configure the remote vnf via pre-installed tools located on the
    same machine where NFPA is.

    :return: True - if success, False - if not

    '''
    log = l.getLogger(__name__, config['LOG_LEVEL'], config['app_start_date'],
                      config['LOG_PATH'])
    def invoke1(cmd, msg):
        log.debug("%s with %s" % (msg, cmd))
        invoke(command=cmd, logger=log, email_adapter=config['email_adapter'])
        log.info("%s: done" % msg)
    if int(config["biDir"]) != 0:
        raise Exception("biDir is not 0")

    bess_path = config["MAIN_ROOT"] + "/bess"     # Path to .bess files

    base_cmd = config['control_path'] + ' daemon connect %s -- '
    base_cmd = base_cmd % config.get('control_mgmt', 'localhost 10514')

    cmd = base_cmd + 'daemon reset || true'
    invoke1(cmd, 'Reseting daemon')

    inport = config["control_vnf_inport"]
    outport = config["control_vnf_outport"]
    pipeline = config["vnf_function"].lower()
    cmd = 'run file %s/%s vnf_inport=%s, vnf_outport=%s, traffictype=%s'
    cmd = base_cmd + cmd % (bess_path, pipeline, inport, outport, traffictype)
    invoke1(cmd, 'Starting pipeline')

    return True
