import myjdapi
import time
import requests
from bs4 import BeautifulSoup

def getMovies(html):
    movies = []
    for items in html.select('item'):
        name = items.select('title')[0].text
        link = items.find('link').next_sibling.replace("\n","")
        if "[ENGLISCH]" in name:
            #print(name)
            #print(link)
            hlink = '<a href="' + link + '">' + name.split(" ")[1] + '</a>'
            html_hlink = BeautifulSoup(hlink, 'html.parser')
            hlink = html_hlink.select('a')
            #print(str(hlink) + '\n')
            movies.append(hlink)

    return movies

def downloadLink(html, name):
    print("prepare for download\n Name: " + str(name))
    foundMovie = False
    for p in html.select('p'):

        for ps in p.select('strong'):
            if(name in ps.text):
                aa = p.select('a')
                print("Searching downloadlinks:\n")
                for a in aa:
                    ul = False
                    href = a.get('href')
                    linkar = href.split("/")
                    linkar_size = len(linkar)
                    if(linkar[linkar_size-1].split("_")[0] == "ul"):
                        print("Found uploaded.net link!")
                        download(name, str(href))
                        foundMovie = True
                        time.sleep(10)
                        ul = True
                if not ul:
                    for a in aa:
                        href = a.get('href')
                        print("Found something else than uploaded.net!")
                        download(name, str(href))
                        foundMovie = True
                        time.sleep(10)
                        break
    return foundMovie

def getURL():
    return "http://serienjunkies.org/xml/feeds/episoden.xml"

def getName():
    return "eserienjunkies"

def fetchSite(site):
    try:
        r = requests.get(str(site))
        t = r.text
        html = BeautifulSoup(t, 'html.parser')
        return html
    except:
        print('Could not fetch site')
        bot.sendMessage(address_pool[0], "Could not fetch site: " + str(site))
        return None

def download(name, url):
    jd=myjdapi.Myjdapi()
    jd.set_app_key("appkey")

    jd.connect("username@email.com","passphrase")

    jd.update_devices()

    devices = jd.list_devices()
    jd_id = jd.get_device(device_name="")
    linkgrabber = myjdapi.Linkgrabber(jd_id)

    downloadlink = url
    package = name
    linkgrabber.add_links(params=[{
        "autostart" : False,
        "links" : downloadlink,
        "packageName" : package,
        "extractPassword" : None,
        "priority" : "DEFAULT",
        "downloadPassword" : None,
        "destinationFolder" : None,
        "overwritePackagizerRules" : False
        }])
    print("added to jdownloader..\n")

    jd.disconnect()
