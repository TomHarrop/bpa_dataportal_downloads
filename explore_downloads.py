#!/usr/bin/env python3

import ckanapi
import os
import datetime
import requests


def check_access(package_id, resource_id, remote):
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
# remote.action.initiatives_check_access(package_id=package_id, resource_id=resource_id)

# action call (equivalent to action shortcut)
# https://github.com/ckan/ckanapi/blob/master/README.md#remoteckan
# remote.call_action(
#     "initiatives_check_access",
#     {"package_id": str(package_id), "resource_id": str(resource_id)},
# )["success"]


# a "package" is a dataset
# a "resource" is one file from the dataset
available_resources_by_package = {}
embargoed_resources_by_package = {}
package_metadata = {}

for package in results["results"]:
    package_id = package["id"]
    package_metadata[package_id] = package
    available_resources = {}
    embargoed_resources = {}
    for resource in package["resources"]:
        url = resource["url"]
        resource_id = resource["id"]
        if check_access(package_id, resource_id, remote):
            try:
                available_resources[resource_id].append(resource)
            except KeyError:
                available_resources[resource_id] = [resource]
        else:
            try:
                embargoed_resources[resource_id].append(resource)
            except KeyError:
                embargoed_resources[resource_id] = [resource]
    if available_resources:
        available_resources_by_package[package_id] = available_resources
    if embargoed_resources:
        embargoed_resources_by_package[package_id] = embargoed_resources


my_package = list(available_resources_by_package.keys())[0]
my_resource = list(available_resources_by_package[my_key].keys())[0]
package_metadata[my_package]

available_resources_by_package[my_package][my_resource][0]['url']


for package in results["results"]:
    try:
        print(package["project_aim"])
        print(package["common_name"])
        print(package["sequencing_platform"])
        print(package["library_id"])
    except KeyError as e:
        print(package.keys())
        raise e

package["name"]


package = results["results"][0]
package["data_context"]
for resource in package["resources"]:
    pass


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

resp = requests.get(
    chosen_resource["url"], headers={"Authorization": apikey}, stream=True
)
file_name = chosen_resource["name"]
with open(file_name, "wb") as handle:
    handle.write(resp.content)
