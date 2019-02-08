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

## 00_pnp_devices.py
formatted list of devices in the PnP database.  

## no_serial_claim.py
this script takes a mapping file and looks for unclaimed devices in the PnP database.  If a match on subnet and upstream interfaces is found,
a new workflow will be create (matching the configuration file provided) and thte device will be claimed using the workflow.

