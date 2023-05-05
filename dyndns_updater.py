# A dynamic DNS updater for DigitalOcean. This script will query the existing
# record in DigitalOcean, compare it to your current external IP address as
# determined by ipify, and update it in DigitalOcean if it has changed.
# Currently only supports A records, but can be extended to AAAA records.

# Required imports
import requests
import json
import config # your local config file

# Headers including the DO token.
headers = {
  'Content-Type': 'application/json',
  'Authorization': 'Bearer ' + config.do_token
}

# URL to get the record; we need the ID later
url = f"https://api.digitalocean.com/v2/domains/{config.domain}/records?name={config.hostname}.{config.domain}&type=A"
print("Obtained domain data!")

# Get the domain data and parse into JSON.
try:
    response = requests.request("GET", url, headers=headers)
except:
    print("Unable to get domain information, exiting...")
    exit(1)
rawjson = json.loads(response.text)
# print(rawjson)

# Get the external IPv4 address
print("Getting external IP address...")
try:
    ip = requests.request("GET", 'https://api.ipify.org').content.decode('utf8')
except:
    print("Failed to get external IP, exiting...")
    exit(2)
print(f"Obtained external IP address {ip}, checking to see if DNS needs updating...")

if ip == rawjson['domain_records'][0]['data']:
    print("Record is up-to-date, exiting...")
    exit(0)

# Request URL to update the domain record
url = f"https://api.digitalocean.com/v2/domains/{config.domain}/records/{rawjson['domain_records'][0]['id']}"

# JSON record update
payload = json.dumps({"name": config.hostname, "type": "A", "data": ip})

print("Updating DNS record...")
try:
    response = requests.request("PATCH", url, headers=headers, data=payload)
except:
    print("Unable to update DNS record, exiting...")
    exit(3)
print(f"Updated {config.hostname}.{config.domain} to {ip}")

# Exit here if we are not going to update AAAA records
if config.update_ipv6 == False:
    exit(0)

## Begin IPv6 update section ##

# URL to get the record; we need the ID later
url = f"https://api.digitalocean.com/v2/domains/{config.domain}/records?name={config.hostname}.{config.domain}&type=AAAA"

# Get the domain data and parse into JSON.
try:
    response = requests.request("GET", url, headers=headers)
except:
    print("Unable to get domain information, exiting...")
    exit(1)
print("Obtained domain data!")
rawjson = json.loads(response.text)

# Test for the existence of a AAAA record.
if rawjson['meta']['total'] == 0:
    print("You do not currently have any AAAA records configured for this domain. Please create it in the DigitalOcean console and retry.")
    exit(4)

# Get the external IPv6 address
print("Getting external IP address...")
try:
    ip = requests.request("GET", 'https://api64.ipify.org').content.decode('utf8')
except:
    print("Failed to get external IP, exiting...")
    exit(2)

# Check to see if we have an IPv6 address. It's a hacky way to do it, but any
# IP address that's under 16 characters is most definitely not IPv6.
if len(ip) < 16:
    print("You do not appear to have an IPv6 address currently assigned externally. Please contact your ISP to get an IPv6 address assigned.")
    exit(6)
print(f"Obtained external IP address {ip}, checking to see if DNS needs updating...")

if ip == rawjson['domain_records'][0]['data']:
    print("Record is up-to-date, exiting...")
    exit(0)

# Request URL to update the domain record
url = f"https://api.digitalocean.com/v2/domains/{config.domain}/records/{rawjson['domain_records'][0]['id']}"

# JSON record update
payload = json.dumps({"name": config.hostname, "type": "AAAA", "data": ip})

print("Updating DNS record...")
try:
    response = requests.request("PATCH", url, headers=headers, data=payload)
except:
    print("Unable to update DNS record, exiting...")
    exit(3)
print(f"Updated {config.hostname}.{config.domain} to {ip}")

print("All updates complete! Exiting now.")