import os
from logger import getLogger
from invoke import invoke
from flow_rules_preparator import prepareOpenFlowRules as prepare_OF_rules

def configure_remote_vnf(config, traffictype):
    '''
    Configure the remote vnf via pre-installed tools located on the
    same machine where NFPA is.

    :return: True - if success, False - if not

    '''
    vnf_function = config['vnf_function'].lower()
    log = getLogger(__name__, config['LOG_LEVEL'], config['app_start_date'],
                    config['LOG_PATH'])
    of_path = config["MAIN_ROOT"] + "/of_rules/"   # path to the openflow rules
    bidir = int(config["biDir"]) == 1
    def invoke1(cmd, msg):
        log.debug("%s with %s" % (msg, cmd))
        invoke(command=cmd, logger=log, email_adapter=config['email_adapter'])
        log.info("%s: done" % msg)
    def check_file_exists(filename):
        if os.path.isfile(str(of_path + filename)):
            return
        log.error('Missing flow rule file: %s' % filename)
        log.error('Cannot configure VNF to act as a %s' % vnf_function)
        open(filename) # Raise exception
    def prepare_rules(path):
        prepare_OF_rules(log, of_path, path, config["control_vnf_inport"],
                         config["control_vnf_outport"], bidir)

    # First, delete the flows
    ofctl_cmd = config["control_path"] + " " + \
                config["control_args"] + " <C> " + \
                config["control_mgmt"] + " "
    cmd = ofctl_cmd.replace("<C>", "del-flows")
    invoke1(cmd, "Deleting flow rules")

    # Second, delete groups
    cmd = ofctl_cmd.replace("<C>", "del-groups")
    invoke1(cmd, "Deleting groups")

    ############     BRIDGE     ###########
    if vnf_function == "bridge":
        # Setup does not depend on the traces
        # Add birdge rules - located under of_rules
        scenario_path = vnf_function + "_unidir.flows"
        check_file_exists(scenario_path)
        if bidir:
            # Change flow rule file
            scenario_path = scenario_path.replace("unidir", "bidir")

        scenario_path = prepare_rules(scenario_path)
        cmd = ofctl_cmd.replace("<C>", "add-flows") + scenario_path
        invoke1(cmd, "Adding flows")
        return True

    ############     OTHER CASES     ###########
    # Filename convention: vnf_function.trace_direction.flows
    if bidir:
        log.error("Bi-directional scenario for this VNF is not yet supported")
        log.error("Check the value of 'biDir' in nfpa.cfg")
        return False

    scenario_path = vnf_function + "." + traffictype + "_unidir.flows"
    check_file_exists(scenario_path)

    # Try to find file for group rules
    scenario_path = scenario_path.replace(".flows", ".groups")
    log.info("Looking for group file: %s" % scenario_path)
    if (os.path.isfile(str(of_path + scenario_path))):
        log.debug("Group file found: %s" % scenario_path)
        # Prepare group file, i.e., replace port related metadata
        group_path = prepare_rules(scenario_path)  # TODO: bidir handling
        cmd = ofctl_cmd.replace("<C>", "add-groups")
        cmd += " " + group_path
        invoke1(cmd, "Adding groups")
    else:
        log.info("No group file was found...continue")

    scenario_path = scenario_path.replace(".groups", ".flows")
    # Replace metadata (e.g., port numbers) in flow rules
    scenario_path = prepare_rules(scenario_path)
    cmd = ofctl_cmd.replace("<C>", "add-flows") + scenario_path
    invoke1(cmd, "Adding flows")
    return True
