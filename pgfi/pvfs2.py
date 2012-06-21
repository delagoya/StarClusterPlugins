from starcluster.clustersetup import ClusterSetup
from starcluster.logger import log

'''
A StarCluster Plugin to create a cluster of PVFS2 parallel filesystem
from all of the nodes in the cluster. You need to also define a set
of installed packages using the default package manager plugin, like so:

[plugin pvfs2-deps]
SETUP_CLASS = starcluster.plugins.pkginstaller.PackageInstaller
# list of apt-get installable packages
PACKAGES = build-essential, flex, bison, libdb4.8-dev, db4.8-util

[plugin pvfs2]
setup_class = pgfi.pvfs2.Pvfs2Setup
data_dir = /mnt/pvfs2-data
mount_point = /pvfs2

'''
class Pvfs2Setup(ClusterSetup):
    def __init__(self,data_dir="/mnt/pvfs2-data",mount_point="/pvfs2"):
        self.data_dir = data_dir
        self.mount_point = mount_point
        log.debug("Pvfs2 [data_dir=%s, mount_point=%s]" % (self.data_dir, self.mount_point))

    def run(self, nodes, master, user, user_shell, volumes):
        node_list = []
        for node in nodes:
            node_list.append(str(node.alias))
        # install and start needed services on all nodes.
        for node in nodes:
            self._install_pvfs2(node,node_list)

    def _install_pvfs2(self,node,node_list):
        '''
        Private method that builds and installs PVFS2
        '''
        hostname = str(node.alias)
        node_list = ",".join(node_list)
        code = '''
        apt-get install -y linux-headers-`uname -r`
        cd /tmp
        wget http://orangefs.org/downloads/2.8.5/source/orangefs-2.8.5.tar.gz
        tar xzf orangefs-2.8.5.tar.gz
        cd orangefs-2.8.5
        ./configure --with-kernel=/usr/src/linux-headers-`uname -r` --prefix=/usr
        make
        make kmod
        make install
        make kmod_install
        make install_doc
        pvfs2-genconfig --protocol tcp \\
        --tcpport 3334 \\
        --ioservers %s \\
        --metaservers %s \\
        --storage %s \\
        --logfile /var/log/pvfs2-server.log \\
        --quiet \\
        /etc/pvfs2-fs.conf
        insmod /lib/modules/`uname -r`/kernel/fs/pvfs2/pvfs2.ko
        pvfs2-server /etc/pvfs2-fs.conf -f
        pvfs2-server /etc/pvfs2-fs.conf
        pvfs2-client
        mkdir %s
        echo "tcp://%s:3334/pvfs2-fs %s pvfs2 defaults,noauto 0 0\n" >> /etc/fstab
        mount %s
        ''' % (node_list, node_list, self.data_dir,
            self.mount_point, hostname, self.mount_point, self.mount_point)
        node.ssh.execute(code)
