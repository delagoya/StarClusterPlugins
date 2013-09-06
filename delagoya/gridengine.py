# The MIT License (MIT)
# 
# Copyright (c) 2013 Angel Pizarro
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from starcluster.clustersetup import ClusterSetup
from starcluster.logger import log

'''
A StarCluster Plugin to enable h_vmem as a consumable, set the num of slots for the master, and create the make parallel environment

    [plugin grindengine_tweaks]
    setup_class = delagoya.gridengine.GridEngineTweaks
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
            self._enable_hvmem(master,nodes)
        self._set_master_slots(master)
        self._make_pe(master)

    def _set_master_slots(self,master):
        log.info("Setting the number of slots on master to %s" % self.master_slots)
        master.ssh.execute("qconf -mattr queue slots '[%s=%s]' all.q" % (master.alias, self.master_slots), source_profile=True)

    def _enable_hvmem(self,master,nodes):
        log.info("Enabling h_vmem as a consumable")
        master.ssh.execute("qconf -sc > /tmp/complex.conf", source_profile=True)
        master.ssh.execute("sed -i.bak -E \"s/^(h_vmem.*)/h_vmem  h_vmem   MEMORY <=  YES  YES 1g 0/\" /tmp/complex.conf")
        master.ssh.execute("qconf -Mc /tmp/complex.conf", source_profile=True)
        log.info("Setting sge_request defaults")
        master.ssh.execute('echo "-l h_vmem=1g" >>  $SGE_ROOT/$SGE_CELL/common/sge_request', source_profile=True)
        master.ssh.execute('echo "-l h_stack=256m" >>  $SGE_ROOT/$SGE_CELL/common/sge_request', source_profile=True)
        # set the slots and h_vmem for the nodes
        for node in nodes:
            atts = (node.num_processors, node.memory, node.alias)
            if master.alias == node.alias:
                atts = (self.master_slots, master.memory, master.alias)
            master.ssh.execute("qconf -rattr exechost complex_values slots=%s,h_vmem=%sm %s" % atts, source_profile=True)
    def _make_pe(self,master):
        log.info("Creating the make parallel environment")
        template = '''pe_name            make
slots              999
user_lists         NONE
xuser_lists        NONE
start_proc_args    /bin/true
stop_proc_args     /bin/true
allocation_rule    $pe_slots
control_slaves     FALSE
job_is_first_task  TRUE
urgency_slots      min
accounting_summary FALSE
'''
        master.ssh.execute("echo '%s' > /tmp/make.pe" % template)
        try:
            master.ssh.execute("qconf -Ap /tmp/make.pe")
        except Exception, e:
            pass