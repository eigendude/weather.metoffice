#A basic way of caching files associated with URLs
#with emphasis on caching results from urlretrieve.

from datetime import datetime, timedelta
import time
import os
import shutil
import urllib
import json
from utilities import log

class URLCache(object):
    TIME_FORMAT = "%a %b %d %H:%M:%S %Y"

    def __init__(self, filename, folder):
        self._cachefilename = filename
        self._cachefolder = folder

    def __enter__(self):
        try:
            file = open(self._cachefilename, 'r')
        except IOError:
            #create the file and try again.
            open(self._cachefilename, 'a').close()
            file = open(self._cachefilename, 'r')            
        try:
            self._cachetable = json.load(file)
        except ValueError:
            self._cachetable = dict()
        file.close()
        return self

    def __exit__(self, type, value, traceback):
        with open(self._cachefilename, 'w+') as file:
            json.dump(self._cachetable, file, indent=2)

    def put(self, url, src, expiry):
        #takes a file and copies it into the cache
        #returns resource location in cache
        shutil.copy(src, self._cachefolder)
        resource = os.path.join(self._cachefolder, os.path.basename(src))
        self._cachetable[url] = {'resource':resource, 'expiry': expiry.strftime(self.TIME_FORMAT)}
        return resource

    def get(self, url):
        return self._cachetable[url]

    def remove(self, url):
        os.remove(self._cachetable[url]['resource'])
        del self._cachetable[url]

    def flush(self):
        #flush should 1) delete expired, 2) remove null targets 3) remove null sources
        expired = list()
        for entry in self._cachetable:
            if self.isexpired(entry):
                expired.append(entry)
        for e in expired:
            del self._cachedata[e]

    def isexpired(self, entry):
        #the entry has expired, according to the 'expiry' field.
        expiry = datetime.fromtimestamp(time.mktime(time.strptime(entry['expiry'], self.TIME_FORMAT)))
        return expiry < datetime.now()

    def ismissing(self, entry):
        #the resource indicated by the entry no longer exists
        return not os.path.exists(entry['resource'])

    def urlretrieve(self, url, expiry):
        """
        Checks to see if an item is in cache
        Uses urllib.urlretrieve to fetch the item
        NB. Assumes the url header type contains a valid file
        extension. This is true for application/json and image/png
        """
        try:
            log("Checking cache for '%s'" % url)
            entry = self.get(url)
            if self.ismissing(entry):
                raise MissingError
            elif self.isexpired(entry):
                raise ExpiredError
            else:
                log("Returning cached item.")
                return entry['resource']
        except (KeyError, MissingError):
            log("Not in cache. Fetching from web.")
            (src, headers) = urllib.urlretrieve(url)
            if len(src.split('.')) == 1:
                ext = headers.type.split('/')[1]
                shutil.move(src, src+'.'+ext)
                src = src+'.'+ext
            return self.put(url, src, expiry)
        except ExpiredError:
            log("Cached item has expired. Fetching from web.")
            resource = entry['resource']
            try:
                (src, headers) = urllib.urlretrieve(url)
                if len(src.split('.')) == 1:
                    ext = headers.type.split('/')[1]
                    shutil.move(src, src+'.'+ext)
                    src = src+'.'+ext
                resource = self.put(url, src, expiry)
            except URLError:
                log("Fetch from web failed. Returning expired item.")
            finally:
                return resource


class MissingError(Exception):
    pass

class ExpiredError(Exception):
    pass