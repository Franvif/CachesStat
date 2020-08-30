from xml.dom import minidom
import numpy as np


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


def statperday(Caches):
    """ gives per day statistic:
        - Maximum number of caches
        - Maximum distance
        Caches is a dom list sorted by found date """

    MaxDist = 0.0
    MaxDist2 = 0.0
    MaxNbCaches = 0
    MaxNbCaches2 = 0
    currdate = Caches[0].getElementsByTagName('groundspeak:date')[0].firstChild.data[0:10]
    currdist = 0.0
    currnbcaches = 1
    lat0 = float(Caches[0].attributes['lat'].value)
    long0 = float(Caches[0].attributes['lon'].value)

    for k in range(1,Caches.length):
        newdate = Caches[k].getElementsByTagName('groundspeak:date')[0].firstChild.data[0:10]
        lat1 = float(Caches[k].attributes['lat'].value)
        long1 = float(Caches[k].attributes['lon'].value)
        if newdate == currdate:
            currnbcaches += 1
            currdist += dist_vincenty([lat0,long0],[lat1,long1])
        else:
            if currnbcaches > MaxNbCaches:
                MaxNbCaches2 = MaxNbCaches
                MaxNbCaches = currnbcaches
                DateMaxNbCaches = currdate
            elif currnbcaches > MaxNbCaches2:
                MaxNbCaches2 = currnbcaches
            if currdist > MaxDist:
                MaxDist2 = MaxDist
                MaxDist = currdist
                DateMaxDist = currdate
            elif currdist > MaxDist2:
                MaxDist2 = currdist
            currdist = 0.0
            currnbcaches = 1
            currdate = newdate
        lat0 = lat1
        long0 = long1
    # we do it again for the last date
    if currnbcaches > MaxNbCaches:
        MaxNbCaches2 = MaxNbCaches
        MaxNbCaches = currnbcaches
        DateMaxNbCaches = currdate
    elif currnbcaches > MaxNbCaches2:
        MaxNbCaches2 = currnbcaches
    if currdist > MaxDist:
        MaxDist2 = MaxDist
        MaxDist = currdist
        DateMaxDist = currdate
    elif currdist > MaxDist2:
        MaxDist2 = currdist
    print("Distances in 1 day:",MaxDist, DateMaxDist, MaxDist2)
    print("Number of caches in 1 day:", MaxNbCaches, DateMaxNbCaches, MaxNbCaches2)


fichier = '4662145.gpx'

mygpx = minidom.parse(fichier)
Caches = mygpx.getElementsByTagName('wpt')

# remove logs other than "Found it" or "Attended"
removeotherlogs(Caches)

# adjust date for paris time zone
timezone(Caches)

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
statperday(Caches)
