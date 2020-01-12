import feedparser
import pickle
import os
import requests
import shutil
from bs4 import BeautifulSoup

import pprint

import urls
import tools

def updateLocalFile():
    urlsList = urls.getUrls()

    # read all url
    for curUrl in urlsList:
        print("Start fetching " + curUrl + "...")
        try:
            # get feed
            feed = feedparser.parse(curUrl)

            if "bozo_exception" in feed.keys():
                print("Error with", curUrl, ":", feed["bozo_exception"])
            else:
                # read all entries
                for entrie in feed['entries']:
                    print("       " + entrie["title"])
                    # get publication date
                    date = tools.parseDate(entrie["published"])
                    dateString = tools.dateToString(date)

                    # get publisher domain
                    domain = tools.domainOfUrl(curUrl)

                    # if not exists, create a directory for the feed
                    if not os.path.exists("../datas/fluxs/"):
                        os.mkdir("../datas/fluxs/")
                    if not os.path.exists("../datas/fluxs/" + domain):
                        os.mkdir("../datas/fluxs/" + domain)

                    if not os.path.isfile('../datas/fluxs/' + domain + "/" + dateString + ".pkl"):

                        # download enclosure
                        enclosure = ""
                        # check for enclosure in links
                        for i in range(len(entrie["links"])):
                            if entrie["links"][i]["rel"] == "enclosure":
                                # get file name
                                enclosure = dateString + "." + tools.getExtension(entrie["links"][i]["href"])
                                resp = requests.get(entrie["links"][i]["href"], stream=True)
                                local_file = open('../datas/fluxs/' + domain + "/" + enclosure, 'wb')
                                resp.raw.decode_content = True
                                shutil.copyfileobj(resp.raw, local_file)
                                del resp
                        # get enclosure in the summary
                        if enclosure=="":
                            print("              no enclosure in links")
                            try:
                                soup = BeautifulSoup(entrie['summary'])
                                image_url = soup.find('img')['src']
                                if image_url:
                                    # get file name
                                    enclosure = dateString + "." + tools.getExtension(image_url)
                                    resp = requests.get(image_url, stream=True)
                                    local_file = open('../datas/fluxs/' + domain + "/" + enclosure, 'wb')
                                    resp.raw.decode_content = True
                                    shutil.copyfileobj(resp.raw, local_file)
                                    del resp
                            except:
                                print("              no enclosure in summary")
                        # get enclosure in the content
                        if enclosure=="":
                            try:
                                soup = BeautifulSoup(entrie['content'][0]["value"])
                                image_url = soup.find('img')['src']
                                if image_url:
                                    # get file name
                                    enclosure = dateString + "." + tools.getExtension(image_url)
                                    resp = requests.get(image_url, stream=True)
                                    local_file = open('../datas/fluxs/' + domain + "/" + enclosure, 'wb')
                                    resp.raw.decode_content = True
                                    shutil.copyfileobj(resp.raw, local_file)
                                    del resp
                            except:
                                print("              no enclosure in content")
                                enclosure = ""

                        # save entrie in a pickle
                        with open('../datas/fluxs/' + domain + "/" + dateString + ".pkl", 'wb') as entrieFile:
                            pickler = pickle.Pickler(entrieFile)
                            pickler.dump({
                                "domain" : domain,
                                "title": entrie["title"],
                                "summary": entrie["summary"],
                                "link": entrie["link"],
                                "date": dateString,
                                "enclosure": enclosure
                            })

        except Exception as e:
            print("Error with", curUrl, ":", e)
    
    print("UPDATED !")

def getListOfEntries():
    if not os.path.exists("../datas/fluxs/"):
        os.mkdir("../datas/fluxs/")
    entries = []
    feedsFolders = os.listdir("../datas/fluxs")
    for folder in feedsFolders:
        files = os.listdir("../datas/fluxs/" + folder)
        for curFile in files:
            if tools.getExtension(curFile) == "pkl":
                try:
                    with open("../datas/fluxs/" + folder + "/" + curFile, 'rb') as fileObj:
                        depickler = pickle.Unpickler(fileObj)
                        entrie = depickler.load()
                        entries.append(entrie)
                except Exception as e:
                    print("Error when getting " + folder + "/" + curFile + " informations... " + e)

    sortedEntries = sorted(entries, key=lambda cols: cols["date"])

    return list(reversed(sortedEntries))