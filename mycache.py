import pickledb
from datetime import datetime as dt


class MyCache(pickledb.pickledb):

    def __init__(self, location, option):
        """
        Creates a database object and loads the data from the location path.
        If the file does not exist it will be created on the first update.
        Special item 'ttl' is created as a store for tracking time to live of
        objects with such parameters
        """
        super(MyCache, self).__init__(location, option)
        self.dcreate('ttl')

    def set(self, key, value, ttl=None):
        """
        Set the (string,int,whatever) value of a key + time to live, in seconds
        """
        if ttl and (type(ttl) is int) and (ttl > 0):
            ttl += int(dt.now().strftime('%s'))
            self.dadd('ttl', (key, ttl))
        return super(MyCache, self).set(key, value)

    def get(self, key):
        """
        Get the value of a key if its ttl is not expired,
        if so, it will return None
        """
        if self.dexists('ttl', key) and int(dt.now().strftime('%s')) >= self.dget('ttl', key):
            self.rem(key)
            return None
        return super(MyCache, self).get(key)

    def dexists(self, name, key):
        """
        Determine if a key exists or not in dict value by name
        """
        return key in self.db[name]

    def rem(self, key):
        """
        Delete item by key, and its record in 'ttl' dict
        """
        if self.dexists('ttl', key):
            self.dpop('ttl', key)
        return super(MyCache, self).rem(key)

    def drem(self, name):
        """
        Remove a dict and all of its pairs
        """
        return self.rem(name)

    def lrem(self, name):
        """
        Remove a list and all of its values
        """
        return self.rem(name)
