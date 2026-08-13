# NOMS Client

To use, add this repo as a submodule to your project.

Then, implement the gql() call as follows:

```python
from nomsclient.connections import gql

data = gql(query, variables)
```