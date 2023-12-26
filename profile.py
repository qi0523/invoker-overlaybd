"""Variable number of VMs.

Instructions:
Log into your node, use `sudo` to poke around.
"""

# A comment.    

import geni.portal as portal
import geni.rspec.pg as pg
import geni.rspec.pg as rspec
import geni.rspec.emulab

#
# This is a typical list of images.
#
imageList = [
    ('urn:publicid:IDN+cloudlab.umass.edu+image+containernetwork-PG0:k8s-reg-dlcl', 'k8s-reg-dlcl'),
    ('urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU20-64-STD', 'UBUNTU 20.04'),
    ('urn:publicid:IDN+emulab.net+image+testbed//gufi-test', 'GUFI Test')]

pc = portal.Context()
request = pc.makeRequestRSpec()

pc.defineParameter("N", "Number of virtual nodes (containers)",
                   portal.ParameterType.INTEGER, 4)
pc.defineParameter("X", "Number of containers per physical node",
                   portal.ParameterType.INTEGER, 16)
pc.defineParameter("osImage", "Select OS image",
                   portal.ParameterType.IMAGE,
                   imageList[0], imageList,
                   longDescription="Most clusters have this set of images.")
pc.defineParameter("masterIP", 
                   "Master ip address",
                   portal.ParameterType.STRING, 
                   "172.17.1.1")

pc.defineParameter("disk",
                   "Invoker gc disk",
                   portal.ParameterType.INTEGER,
                   1024,
                   longDescription="Invoker bandwidth.")

pc.defineParameter("bandwidth",
                   "Invoker bandwidth",
                   portal.ParameterType.INTEGER,
                   500000,
                   longDescription="Invoker bandwidth.")

pc.defineParameter("registryIP", 
                   "Registry ip address",
                   portal.ParameterType.STRING, 
                   "172.17.1.1")

pc.defineParameter("lan",  "Put all nodes in a LAN",
                   portal.ParameterType.BOOLEAN, True)
pc.defineParameter("shared",  "Try to use shared nodes",
                   portal.ParameterType.BOOLEAN, False)
# pc.defineParameter("nobw",  "Disable BW and Shaping",
#                    portal.ParameterType.BOOLEAN, False)
pc.defineParameter("publicips",  "Request Public IPs",
                   portal.ParameterType.BOOLEAN, True)
pc.defineParameter("phystype",  "Optional physical node type",
                   portal.ParameterType.NODETYPE, "",
                   longDescription="d710-vm, etc. Be sure to pick the correct cluster on the next step")
pc.defineParameter("physnode",  "Optional physical node",
                   portal.ParameterType.STRING, "",
                   longDescription="pc606, etc. Be sure to pick the correct cluster on the next step")
                   
#pc.defineParameter("phystype2",  "Filtered physical node type",
#                   portal.ParameterType.NODETYPE, "",
#                   longDescription="{'arch'  : 'x86_64', 'cores' : '>2', 'mem_size': '>=16384', 'disksize': '>=400'}",
#                   inputConstraints={'arch'  : 'x86_64', 'cores' : '>2', 'mem_size': '>=16384', 'disksize': ">=400"})

#pc.defineParameter("pubkey",  "public key",
#                   portal.ParameterType.PUBKEY, "")
params = pc.bindParameters()

#
# This option sets the maximum number of VMs that will be packed onto any single
# physical node (subject to other constraints such as memory usage). For example,
# if you set this number to 5 and ask for 10 VMs, the resource mapper will place no
# more then 5 VMs on each physical node (that the mapper picks). The default number
# if you do not set this option, is typically around 10 VMs (again, subject to
# other constraints).
#
request.setCollocateFactor(params.X)
#
# But the mapper is a very fickle beast, and sometimes it will decide to put
# less then the maximum number on each physical node, and sometimes it will,
# but you want things spread out more evenly. This option can be set to either
# "pack" or "balance" to change how the mapper's brain chemistry. But like
# any antidepressant, every day is a new day. 
#
#request.setPackingStrategy("pack")
lan = request.LAN()

if (params.lan):
    lan.vlan_tagging = True
    # if params.nobw:
    #     lan.trivial_ok = False
    #     lan.setNoBandwidthShaping()
    # else:
    lan.trivial_ok = True
    lan.bandwidth = params.bandwidth 
    lan.setForceShaping() 
        # pass
    pass

for i in range(1, params.N+1):
  node = request.XenVM("ow%d" % i)
  node.ram = 8192
  node.cores = 2
  if params.shared:
      node.exclusive = False
  else:
      node.exclusive = True
      pass
  if params.publicips:
      node.routable_control_ip = True
  node.setUseTypeDefaultImage() 
  node.startVNC()
  node.disk = 0
  if params.physnode != "":
      node.component_id = params.physnode
  elif params.phystype != "":
      node.xen_ptype = params.phystype + "-vm"
      pass
  node.disk_image = params.osImage
    
  if params.lan:
    iface = node.addInterface("eth1")
    iface1.addAddress(pg.IPv4Address("172.17.200."+str(i), "255.255.0.0"))
    lan.addInterface(iface)
  node.addService(rspec.Execute(shell="sh", command="bash /local/repository/start.sh {} {} {} {} &".format(params.masterIP, params.bandwidth, params.registryIP, params.disk * 1024 * 1024)))

pc.printRequestRSpec(request)