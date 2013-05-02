from starcluster.clustersetup import ClusterSetup
from starcluster.logger import log

'''
A StarCluster Plugin to install and configure jets3t on nodes

[plugin jets3t]
SETUP_CLASS = pgfi.jets3t.JetS3tSetup
access_key = YOURACCESSKEY
secret_key = YOURSECRETACCESSKEY
'''
class JetS3tSetup(ClusterSetup):
    def __init__(self,access_key="XXX",secret_key="XXX"):
        self.access_key = access_key
        self.secret_key = secret_key
        log.debug("JetS3tSetup [access_key=%s, secret_key=%s]" % (self.access_key, self.secret_key))
    def run(self, nodes, master, user, user_shell, volumes):
        for node in nodes:
            self._install(node)
            self._config(node)
            self._add_path(node)
    def _install(self,node):
        node.package_install('jets3t')
    def _config(self,node):
        template = '''
accesskey=%s
secretkey=%s
acl=PRIVATE
upload.transformed-files-batch-size=5
        ''' % (self.access_key, self.secret_key)
        f = node.ssh.remote_file("/etc/jets3t/synchronize.properties","w")
        f.write(template)
        f.close()

    def _add_path(self,node):
        template = '''
JETS3T_HOME=/usr/share/jets3t
export PATH=${PATH}:${JETS3T_HOME}/bin
        '''
        f = node.ssh.remote_file("/etc/profile.d/jets3t.sh","w")
        f.write(template)
        f.close()
