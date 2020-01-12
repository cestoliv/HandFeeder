from urllib.parse import urlparse
import string
from datetime import datetime
from dateutil import parser

def domainOfUrl(url):
    urlObj = urlparse(url)
    domain = urlObj.netloc

    if not domain :
        return 24
    else:
        return domain

def parseDate(dateString):
    return parser.parse(dateString)

def dateToString(date):
    # year_month_day_hour_minutes_secondes
    dateString = str(date.year) + "_" + \
    str(date.strftime("%m")) + "_" + \
    str(date.strftime("%d")) + "_" + \
    str(date.strftime("%H")) + "_" + \
    str(date.strftime("%M")) + "_" + \
    str(date.strftime("%S"))
    return dateString

def dateFromString(string):
    return datetime.strptime(string, '%Y_%m_%d_%H_%M_%S')

def numberToMonth(num):
    if num == 1:
        return "janvier"
    elif num == 2:
        return "février"
    elif num == 3:
        return "mars"
    elif num == 4:
        return "avril"
    elif num == 5:
        return "mai"
    elif num == 6:
        return "juin"
    elif num == 7:
        return "juillet"
    elif num == 8:
        return "août"
    elif num == 9:
        return "septembre"
    elif num == 10:
        return "octobre"
    elif num == 11:
        return "novembre"
    else:
        return "décembre"

def getExtension(path):
    return path.split(".")[-1]