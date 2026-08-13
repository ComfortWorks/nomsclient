import requests
import json
import re
import time
import hashlib
import sys
from secrets import getSecret


gqlEndpoint = "https://__store__.myshopify.com/admin/api/__version__/graphql.json"


headers = {
		"X-Shopify-Access-Token": None,
		"Content-Type": "application/json",
		"User-agent": "Comfort Works",
		"Accept": "*/*",
		"Connection": "keep-alive"
	}


TOKEN_GEN_TIME = time.time()


def getToken(store, password = None):
    if not password:
        NOMSEC = {}
        for item in secrets.getSecret("noms_secret").split("\n"):
            key, value = item.split("=")
            NOMSEC[key.strip()] = value.strip().replace('"', '').replace("'", "")
        password = NOMSEC.get("PASSWORD")
        print(password)
    nonce = str(int(time.time()))
    localKey = hashlib.sha256((nonce + password).encode('utf-8')).hexdigest()
    token = json.loads(requests.get(f"https://nomshopify.comfort-works.com/token?store={store}.myshopify.com&nonce={nonce}&key={localKey}").content)["token"]
    if isinstance(token, str):
        return token
    elif isinstance(token, list):
        return token[0]


def gql(query, variables, shopifyStore = "comfortworkscovers", gqlVersion = "2026-07", password = None):
    global TOKEN_GEN_TIME
    currentTime = time.time()
    if currentTime - TOKEN_GEN_TIME > 1800 or not headers["X-Shopify-Access-Token"]:
        headers["X-Shopify-Access-Token"] = getToken(shopifyStore, password)
        print(headers["X-Shopify-Access-Token"])
        TOKEN_GEN_TIME = currentTime
    gqlEP = gqlEndpoint.replace("__store__", shopifyStore).replace("__version__", gqlVersion)
    returned = requests.post(gqlEP, headers=headers, json={"query": query, "variables": variables}, timeout=360)
	
    retries = 3
    while retries > 0 and (returned.status_code < 200 or returned.status_code > 299):
        returned.close()
        retries = retries - 1
        time.sleep(5)
        headers["X-Shopify-Access-Token"] = getToken(shopifyStore, password)
        returned = requests.post(gqlEP, headers=headers, json={"query": query, "variables": variables}, timeout=360)
        print("-----gql error")
        print(returned.content)
    returned.close()

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
    password = sys.argv[1]

    print(gql(productsQuery, {}, password=password))