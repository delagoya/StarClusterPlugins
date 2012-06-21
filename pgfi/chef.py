from starcluster.clustersetup import ClusterSetup
from starcluster.logger import log
from starcluster import config

'''
A StarCluster Plugin to run OpsCode Chef using chef-solo.

        [plugin chef_run]
        setup_class = pgfi.chef.ChefSoloRun
        s3_bucket_name = my-chef-bucket
        json_attribs = /path/to/chef/attributes.json
        cookbook_path = /path/to/cookbooks_dir_1, /path/to/cookbooks_dir_2
        role_path = /path/to/roles_dir
        # alternatively, you can define and URL for cookbooks
        # recipe_url = http://some.url/cookbooks.tar.gz
'''

class ChefSoloRun(ClusterSetup):
    def __init__(self,json_attribs=None,cookbook_path=None,role_path=None,recipe_url=None):
        self.json_attribs = json_attribs
        # split the cookbook path
        self.cookbook_path = []
        for p in cookbook_path.split(","):
            self.cookbook_path.append(p.strip())
        self.role_path = role_path
        self.recipe_url = recipe_url
        log.debug("ChefRun [json_attribs=%s],[cookbook_path=(%s)],[role_path=(%s)],[recipe_url=(%s)]" % \
            (self.json_attribs, ", ".join(self.cookbook_path), self.role_path,self.recipe_url))

    def run(self, nodes, master, user, user_shell, volumes):
        for p in self.cookbook_path:
            code = '''
            tar czf %s.tar.gz
            '''
            system("cp -r %s/* cookbooks/." % p)
        system("tar -czf cookbooks.tar.gz %s cookbooks" % self.role_path)
        # create a bucket
        s3 = config.get_easy_s3()
        b = s3.get_or_create_bucket("%s" )
        solo_rb = '''
file_cache_path "/var/chef-solo"
recipe_url %s
role_path "/var/chef-solo/roles"
        ''' % ", ".join(cp)
        for node in nodes:
            # install ruby + gems + chef
            self._install_chef(node)
            # copy chef files
            node.ssh.execute("echo '%s' > /var/chef-solo/solo.rb" % solo_rb)
            self._transfer_chef_files(node)
            # run chef solo
            self._chef_run(node)

    def _install_chef(self,node):
        node.ssh.execute("gem install chef --no-ri --no-rdoc")

    def _transfer_chef_files(self,node):
        node.ssh.mkdir("/var/chef-solo",ignore_failure=True)
        node.ssh.scp.put(self.json_attribs,"/var/chef-solo/dna.json")
        for p in self.cookbook_path:
            node.ssh.scp.put(p,"/var/chef-solo/.", recursive=True)

    def _chef_run(self,node):
        node.ssh.execute("chef-solo -c /var/chef-solo/solo.rb -j /var/chef-solo/dna.json")
