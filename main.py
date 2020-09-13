from statfoundcaches import *
from xml.dom import minidom
import matplotlib.pyplot as plt
import numpy as np


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
dist_tot = totaldist(Caches)
print("Total distance from cache to cache:",dist_tot,"km")

# statistics per day
listperday = statperday(Caches)

# stat per type
dictype = statpercarac(Caches,'groundspeak:type',disp=True)
dicsize = statpercarac(Caches,'groundspeak:container',disp=True)
diccountry = statpercarac(Caches,'country',disp=True)
diccounty = statpercarac(Caches,'county',disp=True)

# number of days for 100 caches
listedate,listenbdays = nbdaysfornbcaches(Caches,100)
ax = plt.subplot(111)
plt.plot(listenbdays)
plt.ylabel('Number of days')
locxticks = np.arange(0,NbCaches,NbCaches/8,dtype=int)
xtickslabel = [listedate[k] for k in locxticks]
plt.xticks(locxticks,xtickslabel,rotation=70)
plt.grid(True)
plt.title('Number of days to find the last 100 caches')
plt.tight_layout() # to avoid the cut of xticks labels
plt.savefig('days100caches.png')
plt.show()
