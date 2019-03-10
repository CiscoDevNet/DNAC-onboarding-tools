# Claim PnP devices without using serial number
There are a set of use cases where devices are onbaorded using PnP, without knowing the serial number in advance.
A common scenario is when a site has a specific IP subnet allocated to it and potentially we know the upstream interface on the parent device.

The other consideration is a discrete configuration vs using a template.  If using some off-box configuration creation tool, the requirement is 
to allocate the file to a specifc device.

With the 1.2.8 PnP process, a workflow is no longer used (the API exist), and the only option is to use a template(rather than specific configuration file).

These scripts address these requirements.  Specifically, they:
- provide a mechansm to sync off-box configuration files into DNAC
- create a workflow mapped to a specific configuration file
- a mapping betwen IP subnet and upstream CDP interface on parent device and a configration file.

Note, as this is an "unclaimed" process, the device will have to contact Cisco DNA Center before being claimed.  When the device
contacts DNAC, information such as it's IP address and CDP information are available via API.  I have used interface in this 
example, but hostname of the parent device could also be included.

## 00_file_sync.py
This script will sync the files in work_files/configs with DNAC.  If a file is modified it will be updated. 
If a file does not exist, it will be uploaded.

```buildoutcfg
$ ./00_file_sync.py 
Skipping File:new-perth.cfg (a623c7e2-339e-4a96-9d96-b331e834e517) SHA1hash:4d545f3c6d1071a2402c223c82dcfc1536db1ad7
Skipping File:perth.cfg (fbc8064b-6f22-42fc-ae76-afb7e012ae92) SHA1hash:607af7a1d858c3286402b6a97af33162e5e99f1c
Skipping File:pnp-9k.cfg (dad21f4e-c8bf-4bc5-afc6-9b44f7ff01f1) SHA1hash:503904f43461aca7dcb8fb02314c9ec4ef84b932
POST https://10.66.104.121:443/api/v1/file/config
Uploaded File:.gitignore (87f4a176-12ce-4d14-ab1a-480137a3da91)
POST https://10.66.104.121:443/api/v1/file/config
Uploaded File:access1.cfg (4d492a0f-691e-4cff-92c6-4cc04cdcf1d1)
POST https://10.66.104.121:443/api/v1/file/config
Uploaded File:access2.cfg (a943e69f-b6bf-4053-a600-e0ff2a06916c)
Skipping File:pnp-stack.cfg (4b5aac74-b9c9-434b-b764-de99cf0050e4) SHA1hash:dfc14e00899089ff4c579e948278198cf38e49c5
{'response': {'nameSpace': 'config', 'name': 'new-conf.cfg', 'downloadPath': '/file/11f08606-60ac-422f-894e-7c694c10cf43', 'fileSize': '126', 'fileFormat': 'text/plain', 'md5Checksum': '7974529437dbc958511e5e4a2dc1b733', 'sha1Checksum': '6c7650c308de00e43ac1bf781b42905aacf2c00a', 'sftpServerList': [{'sftpserverid': '4903486e-d007-460e-ab99-7164a4cb3f96', 'downloadurl': '/config/11f08606-60ac-422f-894e-7c694c10cf43/new-conf.cfg', 'status': 'SUCCESS', 'createTimeStamp': '02/07/2019 22:41:24', 'updateTimeStamp': '02/07/2019 22:41:24', 'id': '595ba540-c57f-4deb-9fc2-90946cb98436'}], 'id': '11f08606-60ac-422f-894e-7c694c10cf43'}, 'version': '1.0'}
Updated File:new-conf.cfg (11f08606-60ac-422f-894e-7c694c10cf43)
```
## 00_pnp_devices.py
formatted list of devices in the PnP database. 
 
 The two devices at the bottom of the list are eligable for claiming.  They are both in the same subnet, but have different uplinks.
```buildoutcfg
$ ./00_pnp_devices.py 
Name         PID              State       Source  IP Address      Neighbour Interface       Workflow Name             
adam-9800-ap AIR-AP3802I-B-K9 Onboarding  Network 10.10.32.3                                Default_5c377767552b2e0007d009aa
11223344556  C9300-48P        Planned     User                                              Default_5c52cde5552b2e0007d010df
FOC2224Z000  C9300-24P        Provisioned Network 10.10.50.2      GigabitEthernet0/0/0      10.10.50.2:               
FCW2220L000  C9300-48U        Unclaimed   Network 10.10.14.6      GigabitEthernet1/0/20                               
FDO1732Q000  WS-C3650-48PQ-E  Unclaimed   Network 10.10.14.4      gi2,GigabitEthernet1/0/5 
```
## no_serial_claim.py
this script takes a mapping file and looks for unclaimed devices in the PnP database.  If a match on subnet and upstream interfaces is found,
a new workflow will be create (matching the configuration file provided) and thte device will be claimed using the workflow.

In the example below, the first rule applies to a device just using the IP address.  Rules #2 and #3 are differentiating two devices in the same
subnet, but with different uplinks
```buildoutcfg
$ cat work_files/mapping.adam 
subnet,upLink,configFile
10.10.50.0/24,*,new-perth.cfg
10.10.14.0/24,GigabitEthernet1/0/5,pnp-stack.cfg
10.10.14.0/24,GigabitEthernet1/0/20,pnp-9k.cfg

```

Can now run the script and the workflows will be created (using the configuration files uploaded earlier) and the devices will be claimed
```buildoutcfg
$ ./no_serial_claim.py work_files/mapping.adam 
Using device file: work_files/mapping.adam
##########################
Trying to find mapping for 10.10.14.6
No Link match upstream
5c5cf2ba552b2e0007d0480e:10.10.14.0/24:GigabitEthernet1/0/20:dad21f4e-c8bf-4bc5-afc6-9b44f7ff01f1
Claiming 10.10.14.6 with file dad21f4e-c8bf-4bc5-afc6-9b44f7ff01f1
creating workflow
Deleting Old workflow
Workflow created, id 5c5cf56e552b2e0007d04864
claim device
{"message": "Device(s) Claimed", "statusCode": 200}
Trying to find mapping for 10.10.14.4
5c5cf3d3552b2e0007d0482a:10.10.14.0/24:GigabitEthernet1/0/5:4b5aac74-b9c9-434b-b764-de99cf0050e4
Claiming 10.10.14.4 with file 4b5aac74-b9c9-434b-b764-de99cf0050e4
creating workflow
Deleting Old workflow
Workflow created, id 5c5cf56e552b2e0007d04866
claim device
{"message": "Device(s) Claimed", "statusCode": 200}

```