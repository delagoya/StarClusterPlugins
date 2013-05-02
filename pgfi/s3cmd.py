from starcluster.clustersetup import ClusterSetup
from starcluster.logger import log

'''
A StarCluster Plugin to install and configure jets3t on nodes

[plugin s3cmd]
SETUP_CLASS = pgfi.s3cmd.S3CmdSetup
access_key = YOURACCESSKEY
secret_key = YOURSECRETACCESSKEY
'''
class S3CmdSetup(ClusterSetup):
    def __init__(self,access_key="XXX",secret_key="XXX"):
        self.access_key = access_key
        self.secret_key = secret_key
        log.debug("S3CmdSetup [access_key=%s, secret_key=%s]" % (self.access_key, self.secret_key))
    def run(self, nodes, master, user, user_shell, volumes):
        # install the packages, create the bricks and start the services
        for node in nodes:
            self._install(node)
            self._config(node)

    def _install(self,node):
        node.package_install('s3cmd')

    def _config(self,node):
        f = node.ssh.remote_file("/root/.s3cfg",'w')
        f.write(self._get_s3cmd_config_file())
        f.close()

    def _get_s3cmd_config_file(self):
        template = '''[default]
access_key = %s
bucket_location = US
cloudfront_host = cloudfront.amazonaws.com
cloudfront_resource = /2010-07-15/distribution
default_mime_type = binary/octet-stream
delete_removed = False
dry_run = False
encoding = UTF-8
encrypt = False
follow_symlinks = False
force = False
get_continue = False
gpg_command = /usr/bin/gpg''' % self.access_key
        template += '''
gpg_decrypt = %(gpg_command)s -d --verbose --no-use-agent --batch --yes --passphrase-fd %(passphrase_fd)s -o %(output_file)s %(input_file)s
gpg_encrypt = %(gpg_command)s -c --verbose --no-use-agent --batch --yes --passphrase-fd %(passphrase_fd)s -o %(output_file)s %(input_file)s
gpg_passphrase =
guess_mime_type = True
host_base = s3.amazonaws.com
host_bucket = %(bucket)s.s3.amazonaws.com
human_readable_sizes = False
list_md5 = False
log_target_prefix =
preserve_attrs = True
progress_meter = True
proxy_host =
proxy_port = 0
recursive = False
recv_chunk = 4096
reduced_redundancy = False'''
        template += '''
secret_key = %s
send_chunk = 4096
simpledb_host = sdb.amazonaws.com
skip_existing = False
socket_timeout = 10
urlencoding_mode = normal
use_https = True
verbosity = WARNING''' % self.secret_key
        return template
