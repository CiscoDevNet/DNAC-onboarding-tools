import os
DNAC= os.getenv("DNAC") or "sandboxdnac.cisco.com"
DNAC_USER= os.getenv("DNAC_USER") or "devnetuser"
DNAC_PORT=os.getenv("DNAC_PORT") or 8080
DNAC_PASSWORD= os.getenv("DNAC_PASSWORD") or "Cisco123!"