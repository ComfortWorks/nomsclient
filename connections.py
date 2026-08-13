import requests
import json
import re
import time
import hashlib
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
        for item in getSecret("noms_secret").split("\n"):
            key, value = item.split("=")
            NOMSEC[key.strip()] = value.strip().replace('"', '').replace("'", "")
        password = NOMSEC.get("PASSWORD")
    nonce = str(int(time.time()))
    localKey = hashlib.sha256((nonce + password).encode('utf-8')).hexdigest()
    requests.get(f"https://nomshopify.comfort-works.com/token?store={store}.myshopify.com&nonce={nonce}&key={localKey}")


def gql(query, variables, shopifyStore = "comfortworkscovers", gqlVersion = "2026-07", password = None):
    global TOKEN_GEN_TIME
    currentTime = time.time()
    if currentTime - TOKE_GEN_TIME > 3600:
        headers["X-Shopify-Access-Token"] = getToken(store, password)
        TOKEN_GEN_TIME = currentTime
	gqlEP = re.sub(r"__store__", shopifyStore, gqlEndpoint)
	gqlEP = re.sub(r"__version__", gqlVersion, gqlEP)
	returned = requests.post(gqlEP, headers=headers, json={"query": query, "variables": variables}, timeout=360)
	retries = 3

	while retries > 0 and (returned.status_code < 200 or returned.status_code > 299):
		returned.close()
		retries = retries - 1
		time.sleep(5)
		returned = requests.post(gqlEP, headers=headers, json={"query": query, "variables": variables}, timeout=360)
		print("-----gql error")
		print(returned.content)
	returned.close()
    
	return json.loads(returned.content)


