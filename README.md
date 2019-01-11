# Onboarding Tools

## Intent 
Predefine an automated onbording workflow for new devices being connected to the network.

## PnP-BulkConfig
Allows uploading of "predefined" rules to onboard network devices.
variables can be supplied to fill in device specific parameters.

The scripts in this directory take a CSV file of device serialNumber plus a workflow to be applied to them.
A PnP rule is created for each device, linking the serialNumber of the device to a predefined workflow in DNAC

When the device is connected to the network, it will discover DNA-C and begin the onboading process.

DNA-C will recognise the serial number of the device, and run the pre-defined workflow.

A simple example of a workflow would include an initial configuration template, which contains variables (such as hostname).
The script will recognise template variables and fill them in from the CSV file.


## PnP-BulkConfig-128
Modified for version 1.2.8 which integrates the onboarding process into provisioning.
Instead of a workflow, uses a "site" and a day-0 template to configure the device.