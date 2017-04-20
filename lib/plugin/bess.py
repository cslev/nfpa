import subprocess
import time
from os import path
from plugin.base import VNFControl as Base

"""
Plugin to start the bess daemon, load a pipeline, and stop the daemon

It relies on the following config parameters:

"MAIN_ROOT": (absolute) path of nfpa.py
"control_path": (absolute) filename of bessctl
"control_mgmt": location of the remote bessd in the form of hostname:filename
"control_vnf_inport": (dpdk) input port number
"control_vnf_outport: (dpdk) output port number
"vnf_function": name of the bess script.
                (filename:  $MAIN_ROOT/bess/$vnf_function.bess)
"biDir": must be 0
"""

class VNFControl(Base):

  def __init__(self, config):
    super(VNFControl, self).__init__(config, __name__)
    self.base_cmd = config['control_path']
    try:
      [self.hostname, self.bessd] = config['control_mgmt'].split(':')
    except Exception as e:
      self.log.error('Failed to parse config arg "control_mgmt"')
      raise e

  def configure_remote_vnf(self, traffictype):
    '''
    Configure the remote vnf via pre-installed tools located on the
    same machine where NFPA is.

    :return: True - if success, False - if not
    '''
    if int(self.config["biDir"]) != 0:
      raise Exception("biDir is not 0")

    bess_path = path.abspath(path.join(path.dirname(__file__),
                                       '..', '..', 'bess'))

    # Start the daemon

    cmd = 'ssh -L 127.0.0.1:10514:127.0.0.1:10514 %s sudo %s -f -k'
    cmd = cmd % (self.hostname, self.bessd)
    self.logfile = open('/tmp/nfpa-bessd.log', 'w')
    try:
      self.daemon = subprocess.Popen(cmd, shell=True,
                                     stdout=self.logfile, stderr=self.logfile)
    except Exception as e:
      self.log.error('Failed to start daemon with %s' % cmd)
      raise e
    time.sleep(2)   # Wait for the daemon to start
                    # FIXME: Should read deamon output

    inport = self.config["control_vnf_inport"]
    outport = self.config["control_vnf_outport"]
    pipeline = self.config["vnf_function"] + '.bess'
    cmd = self.base_cmd
    cmd += ' run file %s/%s ' % (bess_path, pipeline)
    args = []
    self.config['scenario_infix'] = traffictype
    for var in ['control_vnf_inport', 'control_vnf_outport',
                'scenario_infix', 'vnf_args', 'MAIN_ROOT']:
      args.append('%s=\\"%s\\"' % (var, self.config.get(var, '')))
    cmd = cmd + ', '.join(args)
    self.invoke(cmd, 'Starting pipeline')

    return True

  def stop_remote_vnf(self):
    cmd = self.base_cmd + ' daemon stop'
    self.invoke(cmd, 'Stoping bess')
    time.sleep(1)
    self.daemon.terminate()
    time.sleep(1)
    self.daemon.kill()
    self.logfile.close()
