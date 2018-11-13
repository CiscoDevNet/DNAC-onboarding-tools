PnPWatch is a utility to show the status of a PnP device as it is provisioned.

It requires python3 for the uniq library.

Also recommend using virtualenv.  Use the following commands as examples

```
virtualenv -p python3 env
source env/bin/activate
```
To install:
```
pip install -r requirements.txt
```

You will need to edit the apic_config.py file to change your credentials.
NOTE:  You can also use environment variables for these parameters too.
   APIC, APIC_USER, APIC_PASSWORD will be looked at first.
   export APIC_PASSWORD="mysecrete" for example

To run:

```
src/watch_provision.py <serial_number>
```



