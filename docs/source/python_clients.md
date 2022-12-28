# Python Clients

There are two different python clients used to interact with the Web API.

The first client, defined {doc}` here <./apiclient>` is a standard python client, where a client instance has all the required methods to interact with the Web API.

The second client, defined {doc}` here <./apiproxy>` is a python client where the client returns different instances, depending on what method is called on the client. The returned instances themselves have defined methods and attributes. The returned instances from the client is documented  {doc}` here <./poco>`.

Usage of both clients can be found in the {doc}`notebooks`. 

```{toctree}
:maxdepth: 3

apiclient.md
apiproxy
poco
```

