from starcluster.clustersetup import ClusterSetup
from starcluster.logger import log

'''
A StarCluster Plugin to format EC2 ephemeral storage as one large RAID0 ext4 array.

    [plugin ephemeral_scratch]
    setup_class = pgfi.ephemeral.EphemeralScratch
    device = /dev/md0
    mount_point = /mnt
'''
class EphemeralScratch(ClusterSetup):
    INSTANCE_EPHEMERAL_DEVICES = {
        "t1.mirco" : [],
        "m1.small" : ["/dev/xvdb1"],
        "m1.large" : ["/dev/xvdb1", "/dev/xvdc1"] ,
        "m1.xlarge": ["/dev/xvdb1","/dev/xvdc1", "/dev/xvdd1","/dev/xvde1"],
        "c1.medium": ["/dev/xvdb1"],
        "c1.xlarge": ["/dev/xvdb1","/dev/xvdc1", "/dev/xvdd1","/dev/xvde1"],
        "m2.xlarge": ["/dev/xvdb1"],
        "m2.2xlarge" : ["/dev/xvdb1"],
        "m2.4xlarge" :   ["/dev/xvdb1", "/dev/xvdc1"],
        "cc1.4xlarge" :  ["/dev/xvdb1", "/dev/xvdc1"],
        "cc2.8xlarge" : ["/dev/xvdb1","/dev/xvdc1", "/dev/xvdd1","/dev/xvde1"],
        "cg1.4xlarge" : ["/dev/xvdb1","/dev/xvdc1"],
    }

    def __init__(self,device="/dev/md0",mount_point="/mnt"):
        self.device = device
        self.mount_point = mount_point
        log.debug("EphemeralScratch [device=%s, mount_point=%s]" % (self.device, self.mount_point))

    def run(self, nodes, master, user, user_shell, volumes):
        self.install_pkgs(nodes,"mdadm")
        self.format_ephemeral(nodes)

    def install_pkgs(self,nodes,pkgs=None):
        return if pkgs == None
        for node in nodes:
            log.info("Installing (%s)" % ", ".join(pkgs))
            node.ssh.execute("apt-get install -y %s" % " ".join(pkgs))

    def format_ephemeral(self,nodes):
        for node in nodes:
            # unmount the first current device
            devices =  INSTANCE_EPHEMERAL_DEVICES[node.instance_type]
            log.info("unmounting /dev/xvdb1")
            node.ssh.execute("umount %s" % devices[0])
            # remove from fstab

            # create the RAID0 volume
            node.ssh.execute("mdadm --create /dev/md0 --level=0 --raid-devices=%d %s " % (len(devices),
                " ".join(devices))
            )
            # format the new device
            node.ssh.execute("mkfs.ext4 %s" % devices[0])
            # mount the device
            node.ssh.execute("mount %s %s" %(self.device, self.mount_point))
            # add to fstab


