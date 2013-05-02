from starcluster.clustersetup import ClusterSetup
from starcluster.logger import log

'''
A StarCluster Plugin to format EC2 ephemeral storage as individual ext4 disks.
Disks will be mounted as "/mnt/d{0,1,2,3}".

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
        "cr1.8xlarge" : ["/dev/xvdb","/dev/xvdc"],

    }
    def __init__(self,mount_point="/mnt"):
        self.mount_point = mount_point
        log.debug("EphemeralScratch [mount_point=%s]" % self.mount_point)

    def run(self, nodes, master, user, user_shell, volumes):
        for node in nodes:
            log.info("Formatting node %s" % node)
            # self._install_pkgs(node)
            self._format_ephemeral(node)
            # reinstate the sgeadmin scratch share that StarCluster expects.
            log.debug("Re-Creating the StarCluster scratch space target")
            if not node.ssh.isdir("/mnt/sgeadmin"):
                node.ssh.mkdir("/mnt/sgeadmin")
                node.ssh.execute("chown sgeadmin:sgeadmin /mnt/sgeadmin")

    def _format_ephemeral(self,node):
        if (node.instance_type == "t1.micro"):
            return
        # unmount the first current device
        devices =  self.INSTANCE_EPHEMERAL_DEVICES[node.instance_type]
        log.info("Unmounting first device for {node}".format(node=node))
        try:
            node.ssh.execute("umount {0}".format(devices[0]))
        except Exception, e:
            log.error("Device {0} not mounted.".format(devices[0]))
            log.error(e)

        log.info("Formatting ephemeral devices for {node}".format(node=node))
        for device_index,device in enumerate(devices):
            # format
            log.debug("Attempting to format {0}".format(device))
            try:
                node.ssh.execute("mkfs.ext4 %s" % device)
            except Exception, e:
                log.error("Device {0} not able to be formatted".format(device))
                log.error(e)
            # mount
            mount_dir = '/mnt/d{0}'.format(device_index)
            log.debug("Attempting to mount {device} on {mount_dir}".format(
                device=device, mount_dir=mount_dir))
            if not node.ssh.isdir(mount_dir):
                node.ssh.execute("mkdir {0}".format(mount_dir))
            try:
                node.ssh.execute("mount {device} {mount_dir}".format(
                    device=device,mount_dir=mount_dir)
                )
            except Exception, e:
                log.error("Device {device} not able to mount to {mount_dir}".format(device=device,mount_dir=mount_dir))
                log.error(e)
