#import requests
from xlrelease.HttpRequest import HttpRequest
#from requests.auth import HTTPBasicAuth
import json
import sets
import datetime
import time
import dateutil.parser
import dateutil.parser as dp
from java.time import LocalDate, ZoneId
import com.xebialabs.xlrelease.api.XLReleaseServiceHolder as XLReleaseServiceHolder
import com.xebialabs.xlrelease.api.v1.forms.ReleasesFilters as ReleasesFilters

import org.slf4j.LoggerFactory as LoggerFactory

logger = LoggerFactory.getLogger("David Tile")

import planner.planner
reload(planner.planner)
from planner.planner import Planner

the_planner = Planner(server)

HTTP_SUCCESS = sets.Set([200, 201, 202, 203, 204, 205, 206, 207, 208])
HTTP_ERROR = sets.Set([400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410,412, 413, 414, 415])

filterReleaseTags = list(releaseTags)
filterReleaseFolders = list(folderFilter)
filterStatuses = ["FAILED", "COMPLETED", "SKIPPED", "ABORTED"]

releaseApi = XLReleaseServiceHolder.getReleaseApi()

dict = []
httpRequest = HttpRequest(server)

def get_Releases():
    today = LocalDate.now()
    filterTime = 0
    currentTime = int(round(time.time()))
    if timePeriod == 'Last 6 months':
        fromDate = today.minusMonths(6)
        filterTime = currentTime - 15811200
    elif timePeriod == 'Last 3 months':
        fromDate = today.minusMonths(3)
        filterTime = currentTime - 7905600
    elif timePeriod == 'Last 30 days':
        fromDate = today.minusDays(30)
        filterTime = currentTime - 2592000
    elif timePeriod == 'Last year':
        filterTime = currentTime - 31536000
        fromDate = today.minusYears(1)
    # reqURL = '/api/v1/releases'
    # headers = { "Content-Type": "application/json", "Accept": "application/json" }
    # myResponse = httpRequest.get(reqURL, headers=headers)#requests.get(reqURL,headers=headers, auth=HTTPBasicAuth(username, password))
    # if(myResponse.getStatus() in HTTP_SUCCESS):
    #     release = json.loads(myResponse.getResponse())
    # logger.info(str(releaseTags))

    if filterReleaseTags != [] or filterReleaseFolders != []:
        releaseFilters = []
        releases = []
        releaseFilters = ReleasesFilters()
        for filterReleaseTag in filterReleaseTags:
            releaseFilters.tags = [filterReleaseTag]
            # releaseFilters.parentId = "Applications/Folderb2fa16fcc9ae41eb9b9187abe2dd5d65"
            # releaseFilters.parentId = "TEST"
        for filterReleaseFolder in filterReleaseFolders:
            releaseFilters.parentId = str(filterReleaseFolder)
            releases += releaseApi.searchReleases(releaseFilters)
        # releases = releaseApi.searchReleases(releaseFilters)
        # logger.info(str(releases))
        for x in releases:
            get_planned_dates(x.id)
    else:
        releases = releaseApi.getReleases()
        for x in releases:
                # yourdate = dateutil.parser.parse(x['scheduledStartDate'])
                # yourdate = yourdate.replace(tzinfo=None, microsecond=0)
                # filtDate = datetime.datetime.fromtimestamp(filterTime)
                # if filtDate < yourdate:
            logger.info(str(x))
            get_planned_dates(x.id)
    # else:
    #     print("Error code %s" % myResponse.getStatus())

def get_planned_dates(releaseId):
        # reqURL = '/api/extension/planner?releaseId=%s&configurationId=%s&password=%s' % (releaseId, server['id'], server['password'])
        # headers = { "Content-Type": "application/json", "Accept": "application/json" }
        # myResponse = httpRequest.get(reqURL,headers=headers)#, auth=HTTPBasicAuth(username, password))
        # if(myResponse.getStatus() in HTTP_SUCCESS):
        #     release = json.loads(myResponse.getResponse())
        #     print_dates(release['entity']['Release'])
        # else:
        #     print("Error code %s" % myResponse.getStatus() )
        release = the_planner.get_Releases2(releaseId)
        print_dates(release)

def print_dates(release):
    global dict
    temp = {}
    temp['release'] = {}
    temp['release']['name'] = release['title']
    if release['startDate'] != None:
        temp['release']['startDate'] = int(release['startDate'])
    else:
        temp['release']['startDate'] = int(release['scheduledStartDate'])
    if release['endDate'] != None:
        temp['release']['endDate'] = int(release['endDate'])
    else:
        temp['release']['endDate'] = int(release['dueDate'])
    temp['release']['phases'] = []
    phases = release['phases']
    startDate = None
    endDate = None
    for x in phases:
        if x['startDate'] == None:
            startDate = int(x['scheduledStartDate'])
        else:
            startDate = int(x['startDate'])
        if x['endDate'] == None:
            endDate = int(x['dueDate'])
        else:
            endDate =int(x['endDate'])
        tempPhase = {}
        tempPhase['name'] = x['title']
        tempPhase['startDate'] = startDate
        tempPhase['endDate'] = endDate
        temp['release']['phases'].append(tempPhase)

    dict.append(temp)

get_Releases()
data = json.dumps(dict)
