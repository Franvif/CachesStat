from xml.dom import minidom
import numpy as np
from urllib.request import urlopen
import os.path
import datetime
import folium

def sortcaches(Caches):
    """ sort caches by found date and id if same found date"""

    Caches.sort(key = lambda x: x.getElementsByTagName('groundspeak:date')[0].firstChild.data[0:10] +
                '0'*(16-len(x.getElementsByTagName('groundspeak:log')[0].attributes['id'].value)) +
                x.getElementsByTagName('groundspeak:log')[0].attributes['id'].value)


def removeotherlogs(Caches):
    """ removes logs that are not "found it" or "Attended" """
    
    for cache in Caches:
        a = cache.getElementsByTagName('groundspeak:logs')[0]
        listelogs = a.getElementsByTagName('groundspeak:log')
        for log in listelogs:
            if not (log.getElementsByTagName('groundspeak:type')[0].firstChild.data in {'Found it','Attended'}):
                a.removeChild(log)


def timezone(Caches):
    """ adjust date to time zone Paris to avoid border effect
        We considere transition between summer time and winter time 31/10 and 31/03: TO IMPROVE!!"""

    for cache in Caches:
        dateheure = cache.getElementsByTagName('groundspeak:date')[0].firstChild.data
        if (dateheure[5:7] in {'04','05','06','07','08','09','10'} and dateheure[11:13] in {'00','01'}) or (dateheure[5:7] in {'11','12','01','02','03'} and dateheure[11:13] == '00'):
            cache.getElementsByTagName('groundspeak:date')[0].firstChild.data = dateheure[0:8] + "{0:02d}".format(int(dateheure[8:10])-1) + dateheure[10:]


def gpxaddress(Caches, fichier = 'cachesadresses.gpx'):
    """ Create or complete a gpx file with the adress corresponding to the
        coordinates of the caches"""

    if not os.path.isfile(fichier):
        # creation of the gpx file
        doc = minidom.Document()
        rootgpx = doc.createElement('gpx')
        doc.appendChild(rootgpx)
    else:
        # opening of the file
        doc = minidom.parse(fichier)
        rootgpx = doc.firstChild
    wptaddr = doc.getElementsByTagName('wpt')
    
    # create a list with coordinates already in gpx file
    listcoord = []
    for wpt in wptaddr:
        listcoord.append((float(wpt.attributes['lat'].value),float(wpt.attributes['lon'].value)))
        
    # for each cache, we loog if coords are in the list. If yes, we add the reversegeocode to the cache, If no, we query it and add it
    for cache in Caches:
        lat = float(cache.attributes['lat'].value)
        long = float(cache.attributes['lon'].value)
        if (lat,long) in listcoord:
            k = listcoord.index((lat,long))
            cache.appendChild(wptaddr[k].getElementsByTagName('reversegeocode')[0].cloneNode(deep=True))
        else:
            gpxgeo = minidom.parseString(urlopen('https://nominatim.openstreetmap.org/reverse?format=xml&lat={0:f}&lon={1:f}&zoom=18&addressdetails=1/'.format(lat,long)).read())
            gpxgeo2 = gpxgeo.cloneNode(deep=True)
            if len(cache.getElementsByTagName('reversegeocode')) == 0:
                cache.appendChild(gpxgeo.firstChild)
            wpt = doc.createElement('wpt')
            wpt.setAttribute('lat','{0:f}'.format(lat))
            wpt.setAttribute('lon','{0:f}'.format(long))
            wpt.appendChild(gpxgeo2.firstChild)
            rootgpx.appendChild(wpt)
            
    with open(fichier,'wb') as fid:
        fid.write(doc.toxml('UTF-8')) # UTF-8 else gpx is not readable with minidom (windows)
    return doc



def dist_vincenty(Coord1,Coord2,nb_iter=10):
    """ calcul de la distance entre deux points de la terre (en km)
    Coord1 et Coord2 contiennent les coordonnées
    lat et long sont donnés en degrés décimal """

    # paramètres de la terre en km
    a = 6378.1370
    b = 6356.752314

    # conversion des coordonnées en rad
    lat1 = Coord1[0]*np.pi/180
    long1 = Coord1[1]*np.pi/180
    lat2 = Coord2[0]*np.pi/180
    long2 = Coord2[1]*np.pi/180

    if lat1==lat2 and long1==long2:
        return 0.0

    f = (a-b)/a # applatissement de l'ellipsoide
    U1 = np.arctan((1-f)*np.tan(lat1))
    U2 = np.arctan((1-f)*np.tan(lat2))
    L = long2 - long1
    lambdav = L

    for k in range(0,nb_iter):
        cossigma = np.sin(U1) * np.sin(U2) + np.cos(U1) * np.cos(U2) * np.cos(lambdav)
        sinsigma = np.sqrt((np.cos(U2)*np.sin(lambdav))**2 + (np.cos(U1)*np.sin(U2) - np.sin(U1)*np.cos(U2)*np.cos(lambdav))**2)
        sigma = np.arctan2(sinsigma,cossigma)
        sinalpha = np.cos(U1)*np.cos(U2)*np.sin(lambdav)/sinsigma
        coscarrealpha = 1 - sinalpha**2
        cos2sigmam = cossigma - 2*np.sin(U1)*np.sin(U2)/coscarrealpha
        C = f/16*coscarrealpha*(4+f*(4-3*coscarrealpha))
        lambda_new = L + (1-C)*f*sinalpha*(sigma + C*sinsigma*(cos2sigmam+C*cossigma*(-1+2*(cos2sigmam)**2)))
        difflambda = lambda_new - lambdav
        lambdav = lambda_new
        if difflambda==0.0:
            break

    ucarre = coscarrealpha*(a*a-b*b)/(b*b);
    A = 1 + ucarre/16384*(4096 + ucarre*(-768 + ucarre*(320-175*ucarre)))
    B = ucarre/1024*(256+ucarre*(-128+ucarre*(74-47*ucarre)))
    deltasigma = B*sinsigma*(cos2sigmam+0.25*B*(cossigma*(-1+2*cos2sigmam**2-1/6*B*cos2sigmam*(-3+4*sinsigma**2)*(-3+4*cos2sigmam**2))))
    d = b*A*(sigma - deltasigma)

    return d


def totaldist(Caches):
    """ gives the total distance from cache to cache in the order of the list """

    dist_tot = 0.0
    lat0 = float(Caches[0].attributes['lat'].value)
    long0 = float(Caches[0].attributes['lon'].value)
    for cache in Caches[1:]:
        lat1 = float(cache.attributes['lat'].value)
        long1 = float(cache.attributes['lon'].value)
        dist_tot = dist_tot + dist_vincenty([lat0,long0],[lat1,long1])
        lat0 = lat1
        long0 = long1
    return dist_tot


def statperday(Caches):
    """ gives per day statistic:
        - number of caches
        - distance
        Output is a list of lists with the date and the previously cited metrics
        Caches is a dom list sorted by found date """

    currdate = Caches[0].getElementsByTagName('groundspeak:date')[0].firstChild.data[0:10]
    currdist = 0.0
    currnbcaches = 1
    lat0 = float(Caches[0].attributes['lat'].value)
    long0 = float(Caches[0].attributes['lon'].value)
    listperday = []

    for k in range(1,Caches.length):
        newdate = Caches[k].getElementsByTagName('groundspeak:date')[0].firstChild.data[0:10]
        lat1 = float(Caches[k].attributes['lat'].value)
        long1 = float(Caches[k].attributes['lon'].value)
        if newdate == currdate:
            currnbcaches += 1
            currdist += dist_vincenty([lat0,long0],[lat1,long1])
        else:
            listperday.append((currdate, currnbcaches, currdist))
            currdist = 0.0
            currnbcaches = 1
            currdate = newdate
        lat0 = lat1
        long0 = long1
    # we do it again for the last date
    listperday.append((currdate, currnbcaches, currdist))

    a = sorted(listperday, key = lambda x:x[2]) # sort by km
    print("Distances in 1 day {0:.1f}km on {1:s}, {2:.1f}km on {3:s}".format(a[-1][2], a[-1][0], a[-2][2], a[-2][0]))
    a = sorted(listperday, key=lambda x: x[1])  # sort by nb caches
    print("Number of caches in 1 day: {0:d} on {1:s}, {2:d} on {3:s}".format(a[-1][1], a[-1][0], a[-2][1], a[-2][0]))
    return listperday


def istag(Caches,tag):
    """ print caches in Caches whose tag is absent"""

    for cache in Caches:
        a = cache.getElementsByTagName(tag)
        if len(a)==0:
            print(cache.getElementsByTagName('desc')[0].firstChild.data)


def statpercarac(Caches,carac,disp = False):
    """ gives repartition according to a caracteristic such as cache size, difficulty, type, country...
        carac can be a tuple containing several caracteritics"""

    dic_carac = {}
    if not type(carac) is tuple:
        carac = (carac,)

    for cache in Caches:
        carac_value_list = []
        for k in range(len(carac)):
            carac_elem = cache.getElementsByTagName(carac[k])
            if len(carac_elem)>0:
                carac_value_list.append(carac_elem[0].firstChild.data)
            else:
                carac_value_list.append('carac_unknown')
        carac_value = tuple(carac_value_list)

        if carac_value in dic_carac.keys():
            dic_carac[carac_value] += 1
        else:
            dic_carac[carac_value] = 1
    if disp:
        for carac_value, tot in dic_carac.items():
            for c in carac_value:
                print('{0:s} '.format(c), end='')
            print(': {0:d}'.format(tot))
    return dic_carac


def nbdaysfornbcaches(Caches,nbcaches):
    """ outputs 2 lists with one with date and one with number of days up to this date to have nbcaches found
        Input Caches contains caches in the order they are found"""

    listedate = []
    listenbdays = []
    for k in range(nbcaches-1,len(Caches)):
        listedate.append(Caches[k].getElementsByTagName('groundspeak:date')[0].firstChild.data[0:10])
        newdate = datetime.date(year=int(listedate[-1][0:4]), month=int(listedate[-1][5:7]), day=int(listedate[-1][8:10]))
        olddatestr = Caches[k-nbcaches+1].getElementsByTagName('groundspeak:date')[0].firstChild.data[0:10]
        olddate = datetime.date(year=int(olddatestr[0:4]), month=int(olddatestr[5:7]), day=int(olddatestr[8:10]))
        listenbdays.append((newdate - olddate).days+1)
    return listedate, listenbdays


def consecutivedays(Caches):
    """ Input: Caches are the caches in the order they are found
        Outputs: maximum consecutive days with at least one find and the date of the last find (in a tuple)
                 maximum consecutive days without a find and the date of the last day of the serie (in another tuple)"""

    maxdaysfinds = 0
    maxdaysnofinds = 0
    currdaysfinds = 1
    currdatestr = Caches[0].getElementsByTagName('groundspeak:date')[0].firstChild.data[0:10]
    currdate = datetime.date(year=int(currdatestr[0:4]), month=int(currdatestr[5:7]), day=int(currdatestr[8:10]))
    currdatefinds = currdatestr
    for cache in Caches:
        olddate = currdate
        currdatestr = cache.getElementsByTagName('groundspeak:date')[0].firstChild.data[0:10]
        currdate = datetime.date(year=int(currdatestr[0:4]), month=int(currdatestr[5:7]), day=int(currdatestr[8:10]))
        deltadate = (currdate - olddate).days
        if deltadate == 1:
            currdaysfinds += 1
            currdatefinds = currdatestr
        elif deltadate > 1:
            if currdaysfinds > maxdaysfinds:
                maxdaysfinds = currdaysfinds
                maxdaysfindsdate = currdatefinds
            if deltadate - 1 > maxdaysnofinds:
                maxdaysnofinds = deltadate - 1
                maxdaysnofindsdate = (currdate-datetime.timedelta(days=1)).strftime('%Y-%m-%d')
            currdaysfinds = 1
            currdatefinds = currdatestr
    if currdaysfinds > maxdaysfinds:
        maxdaysfinds = currdaysfinds
        maxdaysfindsdate = currdatefinds
    return (maxdaysfinds, maxdaysfindsdate), (maxdaysnofinds, maxdaysnofindsdate)


def cachesonmap(Caches, htmlfile):
    """ Display caches on an interactive map. Html file is saved in htmlfile """

    m = folium.Map([45.4, 5.6], zoom_start=5, tiles='openstreetmap')
    folium.TileLayer('Stamen Terrain').add_to(m)
    folium.TileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                     attr='Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
                     name='satellite').add_to(m)
    tradi = folium.FeatureGroup(name='Traditional', show=True)
    m.add_child(tradi)
    myste = folium.FeatureGroup(name='Unknown', show=True)
    m.add_child(myste)
    multi = folium.FeatureGroup(name='Multi', show=True)
    m.add_child(multi)
    letter = folium.FeatureGroup(name='Letterbox', show=True)
    m.add_child(letter)
    earth = folium.FeatureGroup(name='Earthcache', show=True)
    m.add_child(earth)
    virt = folium.FeatureGroup(name='Virtual', show=True)
    m.add_child(virt)
    wigo = folium.FeatureGroup(name='Where I go', show=True)
    m.add_child(wigo)
    event = folium.FeatureGroup(name='Event', show=True)
    m.add_child(event)
    other = folium.FeatureGroup(name='Other', show=True)
    m.add_child(other)
    
    for cache in Caches:
        cachetype = cache.getElementsByTagName('groundspeak:type')[0].firstChild.data
        if cachetype == 'Traditional Cache':
            folium.Marker([float(cache.attributes['lat'].value), float(cache.attributes['lon'].value)],
                      icon=folium.features.CustomIcon('icones/2.gif',icon_size=(16,16)),
                      popup=folium.Popup('<a href=" {0} "target="_blank"> {1} </a>'
                                         .format(cache.getElementsByTagName('url')[0].firstChild.data,
                                                 cache.getElementsByTagName('name')[0].firstChild.data))).add_to(tradi)
        elif cachetype == 'Unknown Cache':
            folium.Marker([float(cache.attributes['lat'].value), float(cache.attributes['lon'].value)],
                      icon=folium.features.CustomIcon('icones/8.gif',icon_size=(16,16)),
                      popup=folium.Popup('<a href=" {0} "target="_blank"> {1} </a>'
                                         .format(cache.getElementsByTagName('url')[0].firstChild.data,
                                                 cache.getElementsByTagName('name')[0].firstChild.data))).add_to(myste)
        elif cachetype == 'Multi-cache':
            folium.Marker([float(cache.attributes['lat'].value), float(cache.attributes['lon'].value)],
                      icon=folium.features.CustomIcon('icones/3.gif',icon_size=(16,16)),
                      popup=folium.Popup('<a href=" {0} "target="_blank"> {1} </a>'
                                         .format(cache.getElementsByTagName('url')[0].firstChild.data,
                                                 cache.getElementsByTagName('name')[0].firstChild.data))).add_to(multi)
        elif cachetype == 'Letterbox Hybrid':
            folium.Marker([float(cache.attributes['lat'].value), float(cache.attributes['lon'].value)],
                      icon=folium.features.CustomIcon('icones/5.gif',icon_size=(16,16)),
                      popup=folium.Popup('<a href=" {0} "target="_blank"> {1} </a>'
                                         .format(cache.getElementsByTagName('url')[0].firstChild.data,
                                                 cache.getElementsByTagName('name')[0].firstChild.data))).add_to(letter)
        elif cachetype == 'Earthcache':
            folium.Marker([float(cache.attributes['lat'].value), float(cache.attributes['lon'].value)],
                      icon=folium.features.CustomIcon('icones/earthcache.gif',icon_size=(16,16)),
                      popup=folium.Popup('<a href=" {0} "target="_blank"> {1} </a>'
                                         .format(cache.getElementsByTagName('url')[0].firstChild.data,
                                                 cache.getElementsByTagName('name')[0].firstChild.data))).add_to(earth)
        elif cachetype == 'Virtual Cache':
            folium.Marker([float(cache.attributes['lat'].value), float(cache.attributes['lon'].value)],
                      icon=folium.features.CustomIcon('icones/4.gif',icon_size=(16,16)),
                      popup=folium.Popup('<a href=" {0} "target="_blank"> {1} </a>'
                                         .format(cache.getElementsByTagName('url')[0].firstChild.data,
                                                 cache.getElementsByTagName('name')[0].firstChild.data))).add_to(virt)
        elif cachetype == 'Wherigo Cache':
            folium.Marker([float(cache.attributes['lat'].value), float(cache.attributes['lon'].value)],
                      icon=folium.features.CustomIcon('icones/1858.gif',icon_size=(16,16)),
                      popup=folium.Popup('<a href=" {0} "target="_blank"> {1} </a>'
                                         .format(cache.getElementsByTagName('url')[0].firstChild.data,
                                                 cache.getElementsByTagName('name')[0].firstChild.data))).add_to(wigo)
        elif cachetype == 'Event Cache':
            folium.Marker([float(cache.attributes['lat'].value), float(cache.attributes['lon'].value)],
                      icon=folium.features.CustomIcon('icones/6.gif',icon_size=(16,16)),
                      popup=folium.Popup('<a href=" {0} "target="_blank"> {1} </a>'
                                         .format(cache.getElementsByTagName('url')[0].firstChild.data,
                                                 cache.getElementsByTagName('name')[0].firstChild.data))).add_to(event)
        else:
            folium.Marker([float(cache.attributes['lat'].value), float(cache.attributes['lon'].value)],
                      icon=folium.features.CustomIcon('cache_icon_type_traditional-2.png',icon_size=(14,14)),
                      popup=folium.Popup('<a href=" {0} "target="_blank"> {1} </a>'
                                         .format(cache.getElementsByTagName('url')[0].firstChild.data,
                                                 cache.getElementsByTagName('name')[0].firstChild.data))).add_to(other)
    folium.LayerControl(position='topright', collapsed=False, autoZIndex=True).add_to(m)
    m.save(htmlfile)
    return m.get_root().render()

    
    
