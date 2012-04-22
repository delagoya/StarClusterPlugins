from starcluster.clustersetup import ClusterSetup
from starcluster.logger import log

'''
A StarCluster Plugin to enable h_vmem as a consumable.
[plugin grindengine_tweaks]
setup_class = pgfi.gridengine.GridEngineTweaks
enable_hvmem = True # enable h_vmem as a consumable complex attribute
master_slots = 1 # number of slots the master host should have.
'''
class GridEngineTweaks(ClusterSetup):
    def __init__(self,enable_hvmem="True",master_slots=0):
        if enable_hvmem == "False":
            self.enable_hvmem = False
        else:
            self.enable_hvmem = True
        self.master_slots = master_slots
        log.debug("enable_hvmem = %s , master_slots = %s" % (self.enable_hvmem, self.master_slots))

    def run(self, nodes, master, user, user_shell, volumes):
        if self.enable_hvmem:
            self.enable_hvmem_f(master,nodes)
        self.set_master_slots(master,nodes)

    def set_master_slots(self,master,nodes):
        log.info("Setting the number of slots on master to %s" % self.master_slots)
        master.ssh.execute("qconf -mattr queue slots '[%s=%s]' all.q" % (master.alias, self.master_slots), source_profile=True)

    def enable_hvmem_f(self,master,nodes):
        log.info("Enabling h_vmem as a consumable")
        master.ssh.execute("qconf -sc > /tmp/complex.conf", source_profile=True)
        master.ssh.execute("sed -i.bak -E \"s/^(h_vmem.*)/h_vmem  h_vmem   MEMORY <=  YES  YES 1g 0/\" /tmp/complex.conf")
        master.ssh.execute("qconf -Mc /tmp/complex.conf", source_profile=True)
        log.info("Setting sge_request defaults")
        default_sge_params = '''-q all.q
-l h_vmem=1g
-l h_stack=256m
'''
        master.ssh.execute('echo "' + default_sge_params + '"> $SGE_ROOT/$SGE_CELL/common/sge_request', source_profile=True)
        # set the slots and h_vmem for the nodes
        for node in nodes:
            atts = (node.num_processors, node.memory, node.alias)
            if master.alias == node.alias:
                atts = (self.master_slots, master.memory, master.alias)
            master.ssh.execute("qconf -rattr exechost complex_values slots=%s,h_vmem=%sm %s" % atts, source_profile=True)
