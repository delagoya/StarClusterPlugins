A set of plugins for [StarCluster](http://web.mit.edu/star/cluster/docs/latest/manual/plugins.html)

## Tweaks
1. enables h_vmem complex attribute as a consumable
1. reduces the number of slots available on the master host, so that NFS and SGE services are not effected.

## USAGE

If you currently do not have custom plugins

      cd $HOME/.starcluster/
      git checkout https://github.com/delagoya/StarClusterPlugins.git plugins

If you do have custom plugins, then you most certainly know what you are doing and can figure it out :)

## Configuration

Refer to each plugin's documentation, but here is an example of one of the plugins
for modification of your StarCluster config file:


```init
[plugin gridengine_tweaks]
setup_class = delagoya.gridengine.GridEngineTweaks
# one of True / False
enable_hvmem = True
master_slots = 1
``` 

In your cluster profile section
```init
PLUGINS = gridengine_tweaks
```

Have fun!

## LICENSE 

Licensed under the MIT license http://opensource.org/licenses/MIT. Refer to the `LICENSE` file for details.
