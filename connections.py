import requests
import json
import re
import time
import hashlib
import sys
import traceback


if sys.stdin and sys.stdin.isatty():
	pass
else:
	from google.cloud import secretmanager
from google.cloud import secretmanager

import os


def loadSecret(secret: str) -> str:
    gcp_project_id = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("GCP_PROJECT")

    if not gcp_project_id:
        try:
            resp = requests.get(
                "http://metadata.google.internal/computeMetadata/v1/project/project-id",
                headers={"Metadata-Flavor": "Google"},
                timeout=2,
            )
            if resp.status_code == 200:
                gcp_project_id = resp.text
        except Exception:
            pass

    if not gcp_project_id:
        gcp_project_id = "17379492735"

    name = f"projects/{gcp_project_id}/secrets/{secret}/versions/latest"
    client = secretmanager.SecretManagerServiceClient()
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")


def getSecret(secretName):
    try:
        return loadSecret(secretName)
    except:
        print(traceback.format_exc())
        return None


gqlEndpoint = "https://__store__.myshopify.com/admin/api/__version__/graphql.json"


headers = {
		"X-Shopify-Access-Token": None,
		"Content-Type": "application/json",
		"User-agent": "Comfort Works",
		"Accept": "*/*",
		"Connection": "keep-alive"
	}


TOKEN_GEN_TIME = time.time()


def getToken(store = "comfortworkscovers", password = None):
    if not password:
        NOMSEC = {}
        noms_secrets = getSecret("noms_secret")
        for item in noms_secrets.split("\n"):
            key, value = item.split("=")
            NOMSEC[key.strip()] = value.strip().replace('"', '').replace("'", "")
        password = NOMSEC.get("PASSWORD")
    nonce = str(int(time.time()))
    localKey = hashlib.sha256((nonce + password).encode('utf-8')).hexdigest()
    token = json.loads(requests.get(f"https://nomshopify.comfort-works.com/token?store={store}.myshopify.com&nonce={nonce}&key={localKey}").content)["token"]
    if isinstance(token, str):
        return token
    elif isinstance(token, list):
        return token[0]


def gql(query, variables, shopifyStore = "comfortworkscovers", gqlVersion = "2026-07", password = None):
    global TOKEN_GEN_TIME
    global headers
    currentTime = time.time()
    if currentTime - TOKEN_GEN_TIME > 1800 or not headers["X-Shopify-Access-Token"]:
        headers["X-Shopify-Access-Token"] = getToken(shopifyStore, password)
        TOKEN_GEN_TIME = currentTime
    print(headers["X-Shopify-Access-Token"])
    gqlEP = gqlEndpoint.replace("__store__", shopifyStore).replace("__version__", gqlVersion)
    returned = requests.post(gqlEP, headers=headers, json={"query": query, "variables": variables}, timeout=360)
	
    retries = 3
    while retries > 0 and (returned.status_code < 200 or returned.status_code > 299):
        returned.close()
        retries = retries - 1
        time.sleep(5)
        headers["X-Shopify-Access-Token"] = getToken(shopifyStore, password)
        returned = requests.post(gqlEP, headers=headers, json={"query": query, "variables": variables}, timeout=360)
    returned.close()
    print(returned.content)

    return json.loads(returned.content)


if __name__ == "__main__":
    productsQuery = """
        query GetProducts {
            products(first: 10) {
                nodes {
                id
                title
                }
            }
        }
    """
    password = None

    if len(sys.argv) > 1:
        password = sys.argv[1]

    print(gql(productsQuery, {}, password=password))
