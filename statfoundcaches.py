from xml.dom import minidom

def sortcaches(Caches):
    """ sort caches by found date and id if same found date"""

    Caches.sort(key = lambda x: x.getElementsByTagName('groundspeak:date')[0].firstChild.data)
    



fichier = '4662145.gpx'

mygpx = minidom.parse(fichier)
Caches = mygpx.getElementsByTagName('wpt')

NbCaches = Caches.length
print("Number of found caches: ",NbCaches)

# sort in the order they are found
sortcaches(Caches)
