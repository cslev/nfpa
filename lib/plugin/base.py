from logger import getLogger
from invoke import invoke


class VNFControl(object):
    def __init__(self, config, name=__name__):
        self.config = config
        self.log = getLogger(name, config['LOG_LEVEL'],
                             config['app_start_date'], config['LOG_PATH'])

    def invoke(self, cmd, msg):
        self.log.debug("%s with %s" % (msg, cmd))
        invoke(command=cmd, logger=self.log,
               email_adapter=self.config['email_adapter'])
        self.log.info("%s: done" % msg)
