import os

from plugin.base import VNFControl as Base
from flow_rules_preparator import prepareOpenFlowRules as prepare_OF_rules

class VNFControl(Base):

  def __init__(self, config):
    super(VNFControl, self).__init__(config, __name__)
    # Path to the openflow rules
    self.of_path = config["MAIN_ROOT"] + "/of_rules/"
    self.ofctl_cmd_str = config["control_path"] + " " + \
                         config["control_args"] + " <C> " + \
                         config["control_mgmt"] + " "
    self.bidir = int(self.config["biDir"]) == 1


  def check_file_exists(self, filename):
    if os.path.isfile(str(self.of_path + filename)):
      return
    self.log.error('Missing flow rule file: %s' % filename)
    self.log.error('Cannot configure VNF to act as a %s' %
                   self.config['vnf_function'])
    open(filename) # Raise exception

  def prepare_rules(self, path):
    return prepare_OF_rules(self.log, self.of_path, path,
                            self.config["control_vnf_inport"],
                            self.config["control_vnf_outport"],
                            self.bidir)

  def invoke_ofctl(self, msg, cmd, rest=""):
    cmd = self.ofctl_cmd_str.replace("<C>", cmd) + rest
    self.invoke(cmd, msg)

  def configure_remote_vnf(self, traffictype):
    '''
    Configure the remote vnf via pre-installed tools located on the
    same machine where NFPA is.

    :return: True - if success, False - if not
    '''
    log = self.log
    vnf_function = self.config['vnf_function'].lower()

    self.invoke_ofctl("Deleting flow rules", "del-flows")
    self.invoke_ofctl("Deleting groups", "del-groups")

    ############     BRIDGE     ###########
    if vnf_function == "bridge":
      # Setup does not depend on the traces
      # Add birdge rules - located under of_rules
      scenario_path = vnf_function + "_unidir.flows"
      self.check_file_exists(scenario_path)
      if self.bidir:
        # Change flow rule file
        scenario_path = scenario_path.replace("unidir", "bidir")

      scenario_path = self.prepare_rules(scenario_path)
      self.invoke_ofctl("Adding flows", "add-flows", scenario_path)
      return True

    ############     OTHER CASES     ###########
    # Filename convention: vnf_function.trace_direction.flows
    if self.bidir:
      log.error("Bi-directional scenario for this VNF is not yet supported")
      log.error("Check the value of 'biDir' in nfpa.cfg")
      return False

    scenario_path = vnf_function + "." + traffictype + "_unidir.flows"
    self.check_file_exists(scenario_path)

    # Try to find file for group rules
    scenario_path = scenario_path.replace(".flows", ".groups")
    log.info("Looking for group file: %s" % scenario_path)
    if (os.path.isfile(str(self.of_path + scenario_path))):
      log.debug("Group file found: %s" % scenario_path)
      # Prepare group file, i.e., replace port related metadata
      group_path = self.prepare_rules(scenario_path)  # TODO: bidir handling
      self.invoke_ofctl("Adding groups", "add-groups", group_path)
    else:
      log.info("No group file was found...continue")

    scenario_path = scenario_path.replace(".groups", ".flows")
    # Replace metadata (e.g., port numbers) in flow rules
    scenario_path = self.prepare_rules(scenario_path)
    self.invoke_ofctl("Adding flows", 'add-flows', scenario_path)
    return True

  def stop_remote_vnf(self):
    pass
