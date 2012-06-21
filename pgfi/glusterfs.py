from starcluster.clustersetup import ClusterSetup
from starcluster.logger import log

'''
A StarCluster Plugin to create a cluster of GlusterFS parallel filesystem
from all of the nodes in the cluster. You need to also define a set
of installed packages using the default package manager plugin, like so:


[plugin glusterfs-deps]
SETUP_CLASS = starcluster.plugins.pkginstaller.PackageInstaller
# list of apt-get installable packages
PACKAGES = build-essential, flex, bison, autoconf, fuse-utils, libfuse-dev, openssh-server, wget, nfs-common

[plugin glusterfs-install]
SETUP_CLASS = pgfi.glusterfs.GlusterSetup
data_dir = /mnt/glfsbrick
mount_point = /glfs
share_name = glfs

'''
class GlusterSetup(ClusterSetup):
    def __init__(self,data_dir="/mnt/brick",mount_point="/glfs",share_name="glfs"):
        self.data_dir = data_dir
        self.mount_point = mount_point
        self.share_name = share_name
        log.debug("GlusterSetup [data_dir=%s, mount_point=%s]" % (self.data_dir, self.mount_point))

    def run(self, nodes, master, user, user_shell, volumes):
        # install the packages, create the bricks and start the services
        for node in nodes:
            self._install_glusterfs(node)
            master.ssh.execute("gluster peer probe %s 2>&1 > /dev/null " % str(node.alias))

        # create the filesystem from the bricks
        brick_list = []
        for node in nodes:
            brick_list.append("%s:%s" % (str(node.alias), self.data_dir))
        master.ssh.execute("gluster volume create %s %s" % (self.share_name, " ".join(brick_list)))
        master.ssh.execute("gluster volume start %s" % self.share_name )
        # now mount the volume on all servers
        for node in nodes:
            node.ssh.execute("mount -t glusterfs %s:/%s %s" % (str(node.alias), self.share_name, self.mount_point))

    def _install_glusterfs(self,node):
        code = '''
apt-get install -y openssh-server wget nfs-common fuse-utils libfuse-dev
cd /tmp
wget 'http://download.gluster.org/pub/gluster/glusterfs/LATEST/Ubuntu/11.04/glusterfs_3.2.6-1_amd64.deb'
dpkg -i glusterfs_3.2.6-1_amd64.deb
/etc/init.d/glusterd start
update-rc.d glusterd defaults
mkdir -p %s
mkdir -p %s
        ''' % (self.data_dir, self.mount_point)
        node.ssh.execute(code)
