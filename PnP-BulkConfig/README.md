# PnP-BulkConfig
Bulk upload of intent for onboarding network devices.

The scripts in this directory take a CSV file of device serial number plus a workflow to be applied to them.
A PnP rule is created for each device, linking the serialnumber of the device to a predefined workflow in DNAC

When the device is connected to the network, it will discover DNA-C and begin the onboading process.

DNA-C will recognise the serial number of the device, and run the pre-defined workflow.

A simple example could include an initial configuration template, which contains varaibles.
The script will recognise template variables and fill them in from the CSV file.

## work_files
Contains the inventory files.  These are CSV files with the device name, serial number, pid, workflow name and any variables required for the workflow template

## running the scripts
./10_add_and_claim.py work_files/test.csv

creates a pnp device rule and then claims it with a workflow and template variables.

you need to define the workflow and the template used.

./12_delete.py <serialnumber>
shows the rendered configuration for the device with serial number <serialnumber>.

./12_delete.py work_files/test.csv
cleans up afterwards. deleting pnp rules for all devices in the csv file
