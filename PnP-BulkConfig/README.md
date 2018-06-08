## work_files
Contains the inventory files.  These are csv files with the device name, serial number, pid, workflow name and any variables required for the workflow template

## running
./10_add_and_claim.py work_files/test.csv

creates a pnp device rule and then claims it with a workflow and template variables.

you need to define the workflow and the template used.

./11_delete.py work_files/test.csv
cleans up afterwards. deleting pnp rules for all devices in the csv file
