from starcluster.clustersetup import ClusterSetup
from starcluster.logger import log

'''
A StarCluster Plugin to format EC2 ephemeral storage as one large RAID0 btrfs array.

    [plugin ephemeral_scratch]
    setup_class = pgfi.ephemeral.EphemeralScratch
    mount_point = /mnt

'''
class EphemeralScratch(ClusterSetup):
    INSTANCE_EPHEMERAL_DEVICES = {
        "t1.mirco" : [],
        "m1.small" : ["/dev/xvdb"],
        "m1.large" : ["/dev/xvdb", "/dev/xvdc"] ,
        "m1.xlarge": ["/dev/xvdb","/dev/xvdc", "/dev/xvdd","/dev/xvde"],
        "c1.medium": ["/dev/xvdb"],
        "c1.xlarge": ["/dev/xvdb","/dev/xvdc", "/dev/xvdd","/dev/xvde"],
        "m2.xlarge": ["/dev/xvdb"],
        "m2.2xlarge" : ["/dev/xvdb"],
        "m2.4xlarge" :   ["/dev/xvdb1", "/dev/xvdc1"],
        "cc1.4xlarge" :  ["/dev/xvdb", "/dev/xvdc"],
        "cc2.8xlarge" : ["/dev/xvdb","/dev/xvdc", "/dev/xvdd","/dev/xvde"],
        "cg1.4xlarge" : ["/dev/xvdb","/dev/xvdc"],
    }
    def __init__(self,device="/dev/md0",mount_point="/mnt"):
        self.device = device
        self.mount_point = mount_point
        log.debug("EphemeralScratch [device=%s, mount_point=%s]" % (self.device, self.mount_point))

    def run(self, nodes, master, user, user_shell, volumes):
        log.info("Installing (btrfs-tools)")
        for node in nodes:
            self._install_btrfs(node)
            self._format_ephemeral(node)
            node.ssh.mkdir("/mnt/sgeadmin")
            node.ssh.execute("chown sgeadmin:sgeadmin /mnt/sgeadmin")

    def _install_btrfs(self,node):
        node.ssh.execute("apt-get install -y btrfs-tools")

    def _format_ephemeral(self,node):
        if (node.instance_type == "t1.micro"):
            return
        # unmount the first current device
        devices =  self.INSTANCE_EPHEMERAL_DEVICES[node.instance_type]
        log.info("unmounting first device")
        node.ssh.execute("umount %s" % devices[0])
        # TO-DO: remove from fstab
        # create the RAID0 volume
        log.info("formatting BTRFS ephemeral device")
        node.ssh.execute("mkfs.btrfs  %s" % " ".join(devices))
        # mount the device
        node.ssh.execute("mount %s %s" %(devices[0], self.mount_point))
        # TO-DO: add to fstab