# HTTP

HTTP or HTTPS requests take place through the core/net module.

To request the class from within a module:

`http = self.server.rget('http.url')`

## Creating a request

`response = http.request(url, code="GET", params={}, body=None, headers={}, timeout=None)`

| Parameter | Description |
| ---- | ---- |
| `url` | Resource to request from. |
| `code` | Can be "POST" or "GET", if "POST" then send `params` through the POST body (assuming `body` is `None`), otherwise send `params` through the URL. |
| `params` | CGI Parameters. |
| `body` | POST body, will send POST if `body` is set. |
| `headers` | HTTP Headers. |
| `timeout` | Timeout in seconds. |

## Reading from a request

| Attribute | Description |
| ---- | ---- |
| `Response.headers` | The headers in a dictionary. |
| `Response.raw()` | Get the raw response from the server. |
| `Response.read()` | The response, decoded into a string. |
| `Response.json()` | The response, decoded into a string and loaded as JSON. |

## Handling Errors

| Exception | Description |
| ---- | ---- |
| `http.Error` | Base exception. |
| `http.TimeoutError` | Timeout happened. |
| `http.ResolveError` | Unable to resolve hostname. |
| `http.HTTPError` | HTTP Error, same as urllib.errors.HTTPError. The `code` attribute contains the error.|

