from starcluster.clustersetup import ClusterSetup
from starcluster.logger import log

'''
A StarCluster Plugin to download/build/install The OpenLava scheduler (http://www.openlava.org/home.html)

You will likely want to disable the SGE default configuration and set th like so:

[cluster smallcluster]
# ...
DISABLE_QUEUE=True
PLUGINS=openlava

[plugin openlava]
setup_class = pgfi.openlava.OpenLavaSetup
# Set the number of slots on the master node. Default = 0
master_slots = 1
# Tcl packages for build. For Ubuntu this defaults to 'tcl tcl-dev'.
# For RedHat systems, you will need to specify this as the following
# tcl_packages = tcl tcl-devel

'''

class OpenLavaSetup(ClusterSetup):
    _config_make_install_script = '''
cd /tmp/openlava-2.0
./configure
make
make install
'''
    _cp_files_script = '''
cp /opt/openlava-2.0/etc/openlava /etc/init.d/openlava
chmod 755 /etc/init.d/openlava
cp /opt/openlava-2.0/etc/openlava.*sh /etc/profile.d/.
chown -R openlava:openlava /opt/openlava-2.0
'''

    def __init__(self,master_slots=0, tcl_packages='tcl tcl-dev'):
        self.master_slots = master_slots
        self.tcl_packages = tcl_packages


    def run(self, nodes, master, user, user_shell, volumes):
        # install the packages, create the bricks and start the services
        log.info("Installing/configuring OpenLava")
        self._install_openlava(nodes)
        master.ssh.execute("service openlava restart")

    def _install_openlava(self,nodes):
        for node in nodes:
            log.info("Installing/configuring OpenLava on %s " % node)
            node.package_install(self.tcl_packages)
            if not node.getpwnam("openlava"):
                node.add_user('openlava',2001)
            if node.alias == 'master':
                if not node.ssh.isfile("/tmp/openlava-2.0.tar.gz"):
                    node.ssh.execute(" cd /tmp && wget https://github.com/downloads/openlava/openlava/openlava-2.0.tar.gz")
                if not node.ssh.isdir("/tmp/openlava-2.0"):
                    node.ssh.execute("cd /tmp && tar -xzf openlava-2.0.tar.gz")
                if not node.ssh.isdir("/opt/openlava-2.0"):
                    node.ssh.execute(self._config_make_install_script)
                self._configure_openlava_master(node,nodes)
            else:
                node.ssh.execute('rsync -r master:/opt/openlava-2.0 /opt/.')
            node.ssh.execute(self._cp_files_script)
            node.ssh.execute("service openlava start")

    def _configure_openlava_master(self,master,nodes):
        """This function writes out the various files needed for OpenLava
        to function at all. It will set the maximum slot limit on the master
        node, as well as add all of the nodes to the set of execution hosts.
        """
        # collect the set of nodes, set the
        hosts = ['master ! linux 1 - -']
        server_index = 1
        for node in nodes:
            if node.alias == 'master':
                continue
            else:
                hosts.append('{node} ! linux {server_index} - -'.format(node=node.alias, server_index=server_index))
                server_index += 1
        # lsf.cluster.openlava file
        f = master.ssh.remote_file('/opt/openlava-2.0/etc/lsf.cluster.openlava')
        f.write(self._format_lsf_cluster_openlava_file(hosts))
        f.close()
        # lsb.hosts file
        f = master.ssh.remote_file('/opt/openlava-2.0/etc/lsb.hosts')
        f.write(self._format_lsb_hosts_file(master, self.master_slots, nodes))
        f.close()
        # lsf.conf file - allow root user bsub execution
        master.ssh.execute("echo 'LSF_ROOT_REX=all' >> /opt/openlava-2.0/etc/lsf.conf")

    def _format_lsf_cluster_openlava_file(self,hosts):
        """This function returns a formatted lsf.cluster.openlava file"""
        template = """#-----------------------------------------------------------------------
# T H I S   I S   A    O N E   P E R   C L U S T E R    F I L E
#
# This is a sample cluster definition file.  There is a cluster
# definition file for each cluster.  This file's name should be
# lsf.cluster..
# See lsf.cluster(5) and the "LSF Administrator's Guide".
#

Begin   ClusterAdmins
Administrators = openlava
End    ClusterAdmins

Begin   Host
HOSTNAME          model          type  server  r1m  RESOURCES
{hosts}
End     Host

Begin ResourceMap
RESOURCENAME  LOCATION
# tmp2          [default]
# nio           [all]
# console       [default]
End ResourceMap
"""
        return template.format(hosts="\n".join(hosts))
    def _format_lsb_hosts_file(self,master,master_slots,nodes):
        """This function returns a formatted lsb.hosts file"""

        entries = ['{node}     {slots}   ()     ()    ()    ()     ()     ()'.format(node=master.alias,slots=master_slots)]
        for node in nodes:
            if node.alias == 'master':
                continue
            else:
                entries.append('{node}     {slots}   ()     ()    ()    ()     ()     ()'.format(node=node.alias, slots=node.num_processors))

        template = '''Begin Host
HOST_NAME     MXJ JL/U   r1m    pg    ls     tmp  DISPATCH_WINDOW  # Keywords
{entries}
default       !   ()     ()    ()    ()     ()     ()          # Example
End Host
'''
        return template.format(entries="\n".join(entries))
