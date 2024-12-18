#!/usr/bin/env python3

import os
import requests

# This is a hack. Redefine requests.get to include the Authorization header.
# snakemake_storage_plugin_http only supports predifined AuthBase classes, see
# https://github.com/snakemake/snakemake-storage-plugin-http/issues/27
requests_get = requests.get

def requests_get_with_auth_header(url, **kwargs):
    if 'headers' not in kwargs:
        kwargs['headers'] = {}
    kwargs['headers']['Authorization'] = apikey
    return requests_get(url, **kwargs)

requests.get = requests_get_with_auth_header

apikey = os.getenv("BPI_APIKEY")

if not apikey:
    raise ValueError(
        "Set the BPI_APIKEY environment variable. "
        "This Snakefile uses a hack to pass the API key to `requests.get`. "
        "See  https://github.com/snakemake/snakemake-storage-plugin-http/issues/27."
        )

url_to_get = "https://data.bioplatforms.com/dataset/bpa-ausarg-pacbio-hifi-456326-m84073_230814_035937_s4/resource/9580d824c68743f1068c6991d431416d/download/456326_AusARG_AGRF_m84073_230814_035937_s4.ccs.bam"
# url_to_get = "https://data.bioplatforms.com/dataset/bpa-ausarg-pacbio-hifi-414129-da235386/resource/b16c34442b5abef6d0871b102d1efdcf/download/414129_AusARG_AGRF_DA235386.pdf"

# register storage provider (not needed if no custom settings are to be defined here)
storage bpadp:
    provider="http",
    allow_redirects=True,

rule example:
    input:
        storage.http(
            url_to_get,
        ),
    output:
        "test.bam",
    shell:
        "cp {input} {output}"
