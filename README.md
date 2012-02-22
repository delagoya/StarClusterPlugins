A set of plugins for [StarCluster](http://web.mit.edu/star/cluster/docs/latest/manual/plugins.html)

## Tweaks
1. enables h_vmem complex attribute as a consumable
1. reduces the number of slots available on the master host, so that NFS and SGE services are not effected.

## USAGE

If you currently do not have custom plugins

      cd $HOME/.starcluster/
      git checkout git@github.com:delagoya/StarClusterPlugins.git plugins

If you do have custom plugins, then you most certainly know what you are doing and can figure it out :)

## Configuration

In your plugins section of your StarCluster config file

      [plugin gridengine_tweaks]
      setup_class = pgfi.gridengine.GridEngineTweaks
      # one of True / False
      enable_hvmem = True
      master_slots = 1

Have fun!