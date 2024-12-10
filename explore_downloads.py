#!/usr/bin/env python3

import ckanapi
import os
import datetime
import requests
import copy
import pandas as pd
import json

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

with open("results.json", "w") as json_file:
    json.dump(results["results"], json_file, indent=4)

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

# add a key to each resource to indicate if we have access
results_copy = copy.deepcopy(results)

for package in results_copy["results"]:
    package_id = package["id"]
    for resource in package["resources"]:
        resource_id = resource["id"]
        is_accessible = check_access(package_id, resource_id, remote)
        resource["is_accessible"] = is_accessible


# write some csv so we can take a squiz
normalised_dict = pd.json_normalize(results_copy["results"])

results_results = copy.deepcopy(results_copy["results"])

x = pd.DataFrame.from_dict(results_copy["results"])

def flatten_ckan_results(my_results, result_dict={}):
    # if the item is a dictionary, we need to check if any of the values are dicts or lists
    if isinstance(my_results, dict):
        for k, v in my_results.items():
            if isinstance(v, dict):
                flatten_ckan_results(v, result_dict)
            elif isinstance(v, list):
                pass                
            else:
                result_dict[k].append(v)


flatten_ckan_results(results_results)


# Identify list columns
list_columns = [
    col
    for col in normalised_dict.columns
    if isinstance(normalised_dict[col].iloc[0], list)
]


# Explode list columns and normalize the resulting dictionaries
for col in list_columns:
    exploded_df = normalised_dict.explode(col).reset_index(drop=True)
    if isinstance(exploded_df[col].iloc[0], dict):
        normalized_col_df = pd.json_normalize(exploded_df[col])
        exploded_df = exploded_df.drop(columns=[col]).join(normalized_col_df)
    normalised_dict = exploded_df


# investigate these two packages because they are the same library run on different flowcells
package_ids = [
    "bpa-ausarg-pacbio-hifi-456328-m84073_231123_060607_s1",
    "bpa-ausarg-pacbio-hifi-456328-m84073_230825_020111_s2",
]

package_id = package_ids[0]

available_resources_by_package[package_id]
package_metadata[package_id]["specimen_id"]  # returns TBA

# this looks to be a systematic identifier linking the sample across packages
package_metadata[package_id]["sample_id"]


[package_metadata[x]["sample_id"] for x in package_ids]
[package_metadata[x]["library_id"] for x in package_ids]

package_metadata[package_id].keys()

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
