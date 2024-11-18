#!/usr/bin/env python3

import ckanapi
import os
import datetime
import requests


def check_access(package_id, resource_id, remote=remote):
    access = remote.action.initiatives_check_access(
        package_id=package_id, resource_id=resource_id
    )
    success = access["success"]
    return success


apikey = os.getenv("BPI_APIKEY")

sixty_days_ago = datetime.datetime.now() - datetime.timedelta(days=60)
remote = ckanapi.RemoteCKAN("https://data.bioplatforms.com", apikey=apikey)
query = {"type": "ausarg-pacbio-hifi"}

results = remote.action.package_search(
    q="+".join([f"{k}:{v}" for k, v in query.items()]), rows=50000, include_private=True
)


# action shortcut
remote.action.initiatives_check_access(package_id=package_id, resource_id=resource_id)

# action call (equivalent to action shortcut)
# https://github.com/ckan/ckanapi/blob/master/README.md#remoteckan
remote.call_action(
    "initiatives_check_access",
    {"package_id": str(package_id), "resource_id": str(resource_id)},
)["success"]

resources_we_have_access_to = {}
embargoed_resources = {}

for package in results["results"]:
    package_id = package["id"]
    for resource in package["resources"]:
        url = resource["url"]
        resource_id = resource["id"]
        if check_access(package_id, resource_id):
            resources_we_have_access_to[resource_id] = resource
        else:
            embargoed_resources[resource_id] = resource


date_format = "%Y-%m-%dT%H:%M:%S.%f"
recent_resources = {}

for k, resource in resources_we_have_access_to.items():
    created_date = datetime.datetime.strptime(resource["created"], date_format)
    if created_date >= sixty_days_ago:
        recent_resources[k] = resource

# download a file for testing
if recent_resources:
    chosen_resource = list(recent_resources.values())[0]
else:
    chosen_resource = list(resources_we_have_access_to.values())[0]

resp = requests.get(chosen_resource["url"], headers={"Authorization": apikey}, stream=True)
file_name = chosen_resource["name"]
with open(file_name, "wb") as handle:
    handle.write(resp.content)
