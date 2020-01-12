urlsPath = "../datas/urls.txt"

import shutil
import tools

def getUrls():
    try:
        with open(urlsPath, "r") as urlsTxt:
            urls = urlsTxt.read().split("\n")
            if urls[0] == "":
                urls = []
            return urls
    except:
        return []

def addUrl(urlToAdd):
    codeError = tools.domainOfUrl(urlToAdd)
    if codeError == 24:
        # Wrong url format (http:// ...)
        return 24
    else:
        with open(urlsPath, "a") as urlsTxt:
            if (len(getUrls()) == 0) or (getUrls()[0] == ""):
                urlsTxt.write(urlToAdd)
            else:
                urlsTxt.write("\n" + urlToAdd)
            return 1

def removeUrl(urlToRemove):
    # Remove from urls
    urls = getUrls()
    newUrls = []
    for i in range(len(urls)):
        if urls[i] != urlToRemove:
            newUrls.append(urls[i])

    with open(urlsPath, "w") as urlsTxt:
        urlsTxt.write("\n".join(newUrls))
    # Remove cache files
    try:
        shutil.rmtree("../datas/fluxs/" + tools.domainOfUrl(urlToRemove))
    except:
        print(tools.domainOfUrl(urlToRemove) + " : cache empty")

def cleanFile():
    urls = getUrls()
    for url in urls:
        removeUrl(url)

def resetFile():
    cleanFile()
    addUrl('https://ploum.net/rss')
    addUrl('https://opensource.com/feed')
    addUrl("https://www.frandroid.com/feed")
    addUrl("https://www.androidpit.fr/feed/format/news.xml")