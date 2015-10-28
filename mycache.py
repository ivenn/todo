import pickledb
from datetime import datetime as dt

class MyCache(pickledb.pickledb):
	
	def __init__(self, location, option):
		super(MyCache, self).__init__(location, option)
		self.dcreate('ttl')

	def set(self, key, value, ttl=None):
		if ttl and (type(ttl) is int) and (ttl > 0):
			ttl += int(dt.now().strftime('%s'))
			self.dadd('ttl', (key, ttl))
		return super(MyCache, self).set(key, value)

	def get(self, key):
		if self.dexists('ttl', key) and int(dt.now().strftime('%s')) >= self.dget('ttl', key):
			self.rem(key)
			return None
		return super(MyCache, self).get(key)

	def dexists(self, name, key):
		return key in self.db[name]

	def rem(self, key):
		if self.dexists('ttl', key):
			self.dpop('ttl', key)
		return super(MyCache, self).rem(key)

	def drem(self, name):
		if self.dexists('ttl', name):
			self.dpop('ttl', name)
		return super(MyCache, self).drem(name)

	def lrem(self, name):
		if self.dexists('ttl', name):
			self.dpop('ttl', name)
		return super(MyCache, self).lrem(name)

