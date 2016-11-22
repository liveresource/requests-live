import time
import urlparse
import requests

class ResourceInfo(object):
	def __init__(self):
		self.url = None
		self.longpoll_url = None
		self.poll_interval = None
		self.etag = None
		self.value = None

	def apply(self, resp):
		self.url = resp.url

		self.longpoll_url = None
		for rels, link in resp.links.iteritems():
			if 'value-wait' in rels.split(' '):
				self.longpoll_url = urlparse.urljoin(self.url, link['url'])

		if 'X-Poll-Interval' in resp.headers:
			self.poll_interval = int(resp.headers['X-Poll-Interval'])
		else:
			self.poll_interval = None

		if 'ETag' in resp.headers:
			self.etag = resp.headers['ETag']
		else:
			self.etag = None

		self.value = resp.text

	def get_poll_interval(self):
		if self.poll_interval is not None:
			return self.poll_interval
		else:
			return 120

def get(url):
	info = ResourceInfo()

	print 'GET %s' % url
	resp = requests.get(url)
	info.apply(resp)
	yield resp

	if not info.longpoll_url:
		time.sleep(info.get_poll_interval())

	while True:
		if info.longpoll_url and info.etag:
			headers = {
				'If-None-Match': info.etag,
				'Wait': '55'
			}

			print 'GET %s' % info.longpoll_url
			resp = requests.get(
				info.longpoll_url,
				headers=headers,
				timeout=60)

			if resp.status_code == 200:
				info.apply(resp)
				yield resp
			elif resp.status_code != 304:
				print 'error'
				#time.sleep(60)
				continue

			time.sleep(0.1)
		else:
			resp = requests.get(url)

			if resp.status_code == 200:
				prev_value = info.value
				info.apply(resp)
				if info.value != prev_value:
					yield resp
			else:
				print 'error'

			time.sleep(info.get_poll_interval())
