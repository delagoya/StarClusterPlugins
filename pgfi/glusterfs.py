from starcluster.clustersetup import ClusterSetup
from starcluster.logger import log

'''
A StarCluster Plugin to create a cluster of GlusterFS parallel filesystem
from all of the nodes in the cluster. You need to also define a set
of installed packages using the default package manager plugin, like so:

[plugin glusterfs-install]
SETUP_CLASS = pgfi.glusterfs.GlusterSetup
mount_point = /glfs
share_name = glfs
bricks  = /mnt/d1, /mnt/d2, /mnt/d3, /mnt/d4

'''
class GlusterSetup(ClusterSetup):
    def __init__(self,mount_point="/glfs",share_name="glfs", bricks="/mnt"):
        self.mount_point = mount_point
        self.share_name = share_name
        self.bricks = [x.strip() for x in bricks.split(",")]
        log.debug("GlusterSetup [mount_point=%s, share_name=%s, brick=\"%s\"]" % (self.mount_point, self.share_name, bricks))

    def run(self, nodes, master, user, user_shell, volumes):
        # install the packages, create the bricks and start the services
        self._install_glusterfs(master)
        for node in nodes:
            log.info("Installing/configuring GlusterFS on %s " % node)
            self._install_glusterfs(node)
            master.ssh.execute("gluster peer probe %s 2>&1 > /dev/null " % str(node.alias))
        # create the filesystem from the defined self.bricks
        brick_list = []
        for node in nodes:
            for b in self.bricks:
                brick_list.append("%s:%s" % (str(node.alias), b))
        master.ssh.execute("gluster volume create %s %s" % (self.share_name, " ".join(brick_list)))
        master.ssh.execute("gluster volume start %s" % self.share_name )
        # now mount the volume on all servers
        for node in nodes:
            log.info("GlusterFS mounting on %s" % node)
            node.ssh.execute("mount -t glusterfs %s:/%s %s" % (str(node.alias), self.share_name, self.mount_point))

    def _install_glusterfs(self,node):
        code = '''
add-apt-repository ppa:semiosis/ubuntu-glusterfs-3.3
apt-get update
apt-get install -y openssh-server wget nfs-common fuse-utils libfuse-dev glusterfs-client glusterfs-common glusterfs-server
update-rc.d glusterfs-server defaults
mkdir -p %s
''' % (self.mount_point)
        node.ssh.execute(code)
