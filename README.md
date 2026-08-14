# NOMS Client

To use, add this repo as a submodule to your project.

Then, implement the gql() call as follows:
```python
from nomsclient.connections import gql

data = gql(query, variables)
```

If you only want to grab the GQL access token:
```python
from nomsclient.connections import getToken

token = getToken()
```
