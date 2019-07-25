# Onboarding Tools

## Intent 
Predefine an automated onbording workflow for new devices being connected to the network.

## PnP-BulkConfig
Allows uploading of "predefined" rules to onboard network devices.
variables can be supplied to fill in device specific parameters.

The scripts in this directory take a CSV file of device serialNumber plus a workflow to be applied to them.
A PnP rule is created for each device, linking the serialNumber of the device to a predefined workflow in Cisco DNA Center.

When the device is connected to the network, it will discover Cisco DNA Center and begin the onboading process.

Cisco DNA Center will recognise the serial number of the device, and run the pre-defined workflow.

A simple example of a workflow would include an initial configuration template, which contains variables (such as hostname).
The script will recognise template variables and fill them in from the CSV file.


## PnP-BulkConfig-128
Modified for version 1.2.8 which integrates the onboarding process into provisioning.
Instead of a workflow, uses a "site" and a day-0 template to configure the device.

## PnPNoSerialClaim
A tool to allow auto-claiming of devices based on IP address and CDP neighbour uplink (as opposed to serialNumber).

It is only possible to do this using unclaimed flow as you need to get the IP address and CDP neighbour information after the 
device contacts Cisco DNA Center.

This approach uses a workflow (configured via API) and mapped into a static config file.
