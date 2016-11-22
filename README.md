# Requests-Live

Simple client API that returns an iterable of response objects.

```python
import requests_live

for r in requests_live.get('http://example.com/resource'):
	print r.json()
```
