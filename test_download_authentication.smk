#!/usr/bin/env python3

import os
import requests

class ApiKeyAuth(requests.auth.AuthBase):
    """Attaches API Key Authentication to the given Request object."""

    def __init__(self, api_key):
        self.api_key = api_key

    def __call__(self, r):
        r.headers["Authorization"] = self.api_key
        return r


apikey = os.getenv("BPI_APIKEY")
url_to_get = "https://data.bioplatforms.com/dataset/bpa-ausarg-pacbio-hifi-456326-m84073_230814_035937_s4/resource/9580d824c68743f1068c6991d431416d/download/456326_AusARG_AGRF_m84073_230814_035937_s4.ccs.bam"

auth = ApiKeyAuth(apikey)
resp = requests.get(url_to_get, auth=auth, stream=True)

issubclass(ApiKeyAuth, requests.auth.AuthBase)

type(ApiKeyAuth)

# resp = requests.get(url_to_get, auth=auth, stream=True)
# file_name = "test.bam"
# with open(file_name, "wb") as handle:
#     handle.write(resp.content)

# register storage provider (not needed if no custom settings are to be defined here)
storage bpadp:
    provider="http",
    auth=auth,
    allow_redirects=True,

rule example:
    input:
        storage.bpadp(
            url_to_get
        ),
    output:
        "test.bam"
    shell:
        "cp {input} {output}"

