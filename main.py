from statfoundcaches import *
from xml.dom import minidom
import matplotlib.pyplot as plt
import numpy as np
import datetime
from genhtml import *

fichier = '4662145.gpx'
fichierhtml = 'mystat.html'

mygpx = minidom.parse(fichier)
Caches = mygpx.getElementsByTagName('wpt')

doc = dochtml()
txt = dochtml(typedoc='text',content='A few numbers')
doc.addchild(txt)
tab1 = dochtml(typedoc='array', content=(5,2))
doc.addchild(tab1)

# remove logs other than "Found it" or "Attended"
removeotherlogs(Caches)

# adjust date for paris time zone
timezone(Caches)

# add geographic informations (country, ...)
gpxaddress(Caches)

# total number of caches
NbCaches = Caches.length
tab1.addchild(dochtml(typedoc='text', content='Number of found caches'))
tab1.addchild(dochtml(typedoc='text', content=str(NbCaches)))

# sort in the order they are found
sortcaches(Caches)

# calculate total distance
dist_tot = totaldist(Caches)
print("Total distance from cache to cache:",dist_tot,"km")
tab1.addchild(dochtml(typedoc='text', content='Total distance from cache to cache'))
tab1.addchild(dochtml(typedoc='text', content='{0:d} km'.format(int(dist_tot))))

# statistics per day
listperday = statperday(Caches)
a = sorted(listperday, key=lambda x: x[1])  # sort by nb caches
tab1.addchild(dochtml(typedoc='text', content='Best days'))
tab1.addchild(dochtml(typedoc='text', content="{0:d} caches on {1:s}, {2:d} caches on {3:s}".format(a[-1][1], a[-1][0], a[-2][1], a[-2][0])))
a = sorted(listperday, key=lambda x: x[2])  # sort by nb km
tab1.addchild(dochtml(typedoc='text', content='Best days'))
tab1.addchild(dochtml(typedoc='text', content="{0:.1f} km on {1:s}, {2:.1f} km on {3:s}".format(a[-1][2], a[-1][0], a[-2][2], a[-2][0])))

# stat per type
dictype = statpercarac(Caches,'groundspeak:type',disp=True)
dicsize = statpercarac(Caches,'groundspeak:container',disp=True)
diccountry = statpercarac(Caches,'country',disp=True)
diccounty = statpercarac(Caches,'county',disp=True)

# number of days for 100 caches
listedate,listenbdays = nbdaysfornbcaches(Caches,100)
ind = listenbdays.index(min(listenbdays))
tab1.addchild(dochtml(typedoc='text', content='Minimum number of days to find 100 caches'))
tab1.addchild(dochtml(typedoc='text', content='{0} days ({1})'.format(listenbdays[ind],listedate[ind])))
tab1.addchild(dochtml(typedoc='text', content='Last 100 caches'))
tab1.addchild(dochtml(typedoc='text', content='{0} days ({1})'.format(listenbdays[-1],listedate[-1])))
date0 = datetime.date(year=int(listedate[0][0:4]), month=int(listedate[0][5:7]), day=int(listedate[0][8:10]))
listedeltadays = [(datetime.date(year=int(currdate[0:4]), month=int(currdate[5:7]), day=int(currdate[8:10]))-date0).days for currdate in listedate]
plt.plot(listedeltadays,listenbdays)
plt.ylabel('Number of days')
locxticks = np.arange(0,listedeltadays[-1]+1,listedeltadays[-1]/12,dtype=int)
xtickslabel = [(date0+datetime.timedelta(int(delta))).strftime('%y/%m/%d') for delta in locxticks]
plt.xticks(locxticks,xtickslabel,rotation=70)
plt.grid(True)
plt.title('Number of days to find the last 100 caches')
plt.tight_layout() # to avoid the cut of xticks labels
plt.savefig('days100caches.png')
# plt.show()

listedate,listenbdays = nbdaysfornbcaches(Caches,1000)
ind = listenbdays.index(min(listenbdays))
tab1.addchild(dochtml(typedoc='text', content='Minimum number of days to find 1000 caches'))
tab1.addchild(dochtml(typedoc='text', content='{0} days ({1})'.format(listenbdays[ind],listedate[ind])))
tab1.addchild(dochtml(typedoc='text', content='Last 1000 caches'))
tab1.addchild(dochtml(typedoc='text', content='{0} days ({1})'.format(listenbdays[-1],listedate[-1])))

# series
(nbdaysfinds, datesuite), (nbdaysnofinds, datenosuite) = consecutivedays(Caches)
tab1.addchild(dochtml(typedoc='text', content='Maximum consecutive days with finds'))
tab1.addchild(dochtml(typedoc='text', content='{0} days (last: {1})'.format(nbdaysfinds,datesuite)))
tab1.addchild(dochtml(typedoc='text', content='Maximum consecutive days without any finds'))
tab1.addchild(dochtml(typedoc='text', content='{0} days (last: {1})'.format(nbdaysnofinds,datenosuite)))

# map of found caches
cachesonmap(Caches, "map.html")
linkmap = dochtml(typedoc='text',content='<a href="map.html"> Interactive map of found caches </a>')
doc.addchild(linkmap)

doc.writehtmlfile(fichierhtml)
