from starcluster.clustersetup import ClusterSetup
from starcluster.logger import log

'''
A StarCluster Plugin to run OpsCode Chef.

        [plugin chef_run]
        solo_config = /path/to/solo.config.rb
        chef_role = /path/to/chef/role.json
        cookbooks = /path/to/cookbooks_dir_1, /path/to/cookbooks_dir_2
        # alternatively, you can define and URL for cookbooks
        # cookbooks_url = http://some.url/cookbooks.tar.gz
'''

class ChefRun(ClusterSetup):
    def __init__(self,solo_config=None,chef_role=None,cookbooks=None):
        self.solo_config = chef_config
        self.chef_role = chef_role
        self.cookbooks = cookbooks
        log.debug("ChefRun [solo_config=%s],[chef_role=%s],[cookbooks=(%s)]" % \
            (self.chef_role, self.solo_config, ", ".join(self.cookbooks)))

    def run(self, nodes, master, user, user_shell, volumes):
