from statfoundcaches import *
from xml.dom import minidom
import matplotlib.pyplot as plt
import numpy as np
import datetime
import webbrowser
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
print('Get geographic information...', sep='')
gpxaddress(Caches)
print(' Done')

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
dictype = statpercarac(Caches, 'groundspeak:type')
fig, ax = plt.subplots()
ax.pie(dictype.values(), labels=['{0} {1:.1f}%'.format(key[0], val*100/NbCaches) for key, val in dictype.items()],
       labeldistance=None, autopct=lambda x: '{:.1f}%'.format(x) if x > 10 else '')
ax.axis('equal')
ax.legend(loc="center left", bbox_to_anchor=(1, 0.5))
plt.title('Repartition of found caches types')
plt.savefig('cachetype.png', bbox_inches="tight")
fig.tight_layout()
doc.addchild(dochtml(typedoc='text',content='<br>'))
tab_pie = dochtml(typedoc='array', content=(1,2))
doc.addchild(tab_pie)
tab_pie.addchild(dochtml(typedoc='image', content='cachetype.png'))

dicsize = statpercarac(Caches, 'groundspeak:container')
figsize, axsize = plt.subplots()
axsize.pie(dicsize.values(), labels=['{0} {1:.1f}%'.format(key[0], val*100/NbCaches) for key, val in dicsize.items()],
           labeldistance=None, autopct=lambda x: '{:.1f}%'.format(x) if x > 10 else '')
axsize.axis('equal')
axsize.legend(loc="center left", bbox_to_anchor=(1, 0.5))
plt.title('Repartition of found caches sizes')
plt.savefig('cachesize.png', bbox_inches="tight")
figsize.tight_layout()
tab_pie.addchild(dochtml(typedoc='image', content='cachesize.png'))

diccountry = statpercarac(Caches,'country')
listcountry = sorted([(country[0],nb) for country,nb in diccountry.items()],key=lambda x:x[1], reverse=True)
doc.addchild(dochtml(typedoc='text',content='<br>'))
tab_country = dochtml(typedoc='array', content=(1,2))
doc.addchild(tab_country)
tab_country.addchild(dochtml(typedoc='text', content='<b>Country</b>'))
tab_country.addchild(dochtml(typedoc='text', content='<b>Number of found caches</b>'))
for country,nb in listcountry:
    tab_country.addchild(dochtml(typedoc='text', content=country))
    tab_country.addchild(dochtml(typedoc='text', content=str(nb)))
    
country01 = listcountry[0][0] # country with the most found caches to display more stat on it

dicstate = statpercarac(Caches,('country','state'))
liststate_01 = sorted([(state[1],nb) for state,nb in dicstate.items() if state[0]==country01 and state[1]!='carac_unknown'], key=lambda x:x[1], reverse=True)
doc.addchild(dochtml(typedoc='text',content='<br>'))
tab_state = dochtml(typedoc='array', content=(1,2))
doc.addchild(tab_state)
tab_state.addchild(dochtml(typedoc='text', content='<b>State in {0}</b>'.format(country01)))
tab_state.addchild(dochtml(typedoc='text', content='<b>Number of found caches</b>'))
for state,nb in liststate_01:
    tab_state.addchild(dochtml(typedoc='text', content=state))
    tab_state.addchild(dochtml(typedoc='text', content=str(nb)))

diccounty = statpercarac(Caches,('country','county'))
listcounty_01 = sorted([(county[1],nb) for county,nb in diccounty.items() if county[0]==country01 and county[1]!='carac_unknown'], key=lambda x:x[1], reverse=True)
doc.addchild(dochtml(typedoc='text',content='<br>'))
tab_county = dochtml(typedoc='array', content=(1,2))
doc.addchild(tab_county)
tab_county.addchild(dochtml(typedoc='text', content='<b>County in {0}</b>'.format(country01)))
tab_county.addchild(dochtml(typedoc='text', content='<b>Number of found caches</b>'))
for county,nb in listcounty_01:
    tab_county.addchild(dochtml(typedoc='text', content=county))
    tab_county.addchild(dochtml(typedoc='text', content=str(nb)))

diccity = statpercarac(Caches, 'city')
diccity.pop(('carac_unknown',), None)
list_all = [(city[0], Nb) for city, Nb in diccity.items()]
dictown = statpercarac(Caches, 'town')
dictown.pop(('carac_unknown',), None)
list_all = list_all + [(town[0], Nb) for town, Nb in dictown.items()]
dicvillage = statpercarac(Caches, 'village')
dicvillage.pop(('carac_unknown',), None)
list_all = list_all + [(village[0], Nb) for village, Nb in dicvillage.items()]
list_all.sort(key=lambda x:x[1], reverse=True)
doc.addchild(dochtml(typedoc='text',content='<br>'))
tab_city = dochtml(typedoc='array', content=(1,2))
doc.addchild(tab_city)
tab_city.addchild(dochtml(typedoc='text', content='<b>City</b>'))
tab_city.addchild(dochtml(typedoc='text', content='<b>Number of found caches</b>'))
for city,nb in list_all[:10]:
    tab_city.addchild(dochtml(typedoc='text', content=city))
    tab_city.addchild(dochtml(typedoc='text', content=str(nb)))

# number of days for 100 caches
listedate,listenbdays = nbdaysfornbcaches(Caches,100)
ind = listenbdays.index(min(listenbdays))
tab1.addchild(dochtml(typedoc='text', content='Minimum number of days to find 100 caches'))
tab1.addchild(dochtml(typedoc='text', content='{0} days ({1})'.format(listenbdays[ind],listedate[ind])))
tab1.addchild(dochtml(typedoc='text', content='Last 100 caches'))
tab1.addchild(dochtml(typedoc='text', content='{0} days ({1})'.format(listenbdays[-1],listedate[-1])))
date0 = datetime.date(year=int(listedate[0][0:4]), month=int(listedate[0][5:7]), day=int(listedate[0][8:10]))
listedeltadays = [(datetime.date(year=int(currdate[0:4]), month=int(currdate[5:7]), day=int(currdate[8:10]))-date0).days for currdate in listedate]
fig2, ax2 = plt.subplots()
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

webbrowser.open(fichierhtml, new=2)
