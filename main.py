from statfoundcaches import *
from xml.dom import minidom


fichier = '4662145.gpx'

mygpx = minidom.parse(fichier)
Caches = mygpx.getElementsByTagName('wpt')

# remove logs other than "Found it" or "Attended"
removeotherlogs(Caches)

# adjust date for paris time zone
timezone(Caches)

# add geographic informations (country, ...)
gpxaddress(Caches)

# total number of caches
NbCaches = Caches.length
print("Number of found caches: ",NbCaches)

# sort in the order they are found
sortcaches(Caches)

# calculate total distance
dist_tot = 0.0
lat0 = float(Caches[0].attributes['lat'].value)
long0 = float(Caches[0].attributes['lon'].value)
for k in range(1,NbCaches):
    lat1 = float(Caches[k].attributes['lat'].value)
    long1 = float(Caches[k].attributes['lon'].value)
    dist_tot = dist_tot + dist_vincenty([lat0,long0],[lat1,long1])
    lat0 = lat1
    long0 = long1
print("Total distance from cache to cache:",dist_tot,"km")

# statistics per day
listperday = statperday(Caches)

# stat per type
dictype = statpercarac(Caches,'groundspeak:type',disp=True)
dicsize = statpercarac(Caches,'groundspeak:container',disp=True)
diccountry = statpercarac(Caches,'country',disp=True)
diccounty = statpercarac(Caches,'county',disp=True)
