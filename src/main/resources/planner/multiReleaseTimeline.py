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
# import com.xebialabs.xlrelease.api.v1.FolderApi as folderApi
# import com.xebialabs.xlrelease.api.v1.FolderApi as folderApi

import org.slf4j.LoggerFactory as LoggerFactory

logger = LoggerFactory.getLogger("David Tile")

import planner.planner
reload(planner.planner)
from planner.planner import Planner

the_planner = Planner()

HTTP_SUCCESS = sets.Set([200, 201, 202, 203, 204, 205, 206, 207, 208])
HTTP_ERROR = sets.Set([400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410,412, 413, 414, 415])

filterReleaseTags = list(releaseTags)
filterReleaseFolders = list(folderFilter)
filterStatuses = ["FAILED", "COMPLETED", "SKIPPED", "ABORTED"]
releaseApi = XLReleaseServiceHolder.getReleaseApi()
appServices = XLReleaseServiceHolder.getApiServices()
taskApi = XLReleaseServiceHolder.getTaskApi()
# logger.info(str(appServices))
svcs = XLReleaseServiceHolder.getApiServices()
for api in svcs:
    if api.serviceName() == 'folderApi':
        folder_api = api

dict = []
# httpRequest = HttpRequest(server)

def get_Releases():
    releases = []
    archivedReleases = []
    if filterReleaseTags != [] or filterReleaseFolders != []:
        inArchived = False
        releases = getFilteredReleases(inArchived)
        logger.info("Filtered Releases")
    else:
        logger.info("Regular Release")
        releaseFilters = ReleasesFilters()
        releaseFilters.withCompleted()
        releases = gatherReleases(releaseFilters)

    if archived:
        if filterReleaseTags != [] or filterReleaseFolders != []:
            inArchived = True
            archivedReleases = getFilteredReleases(inArchived)
        else:
            releaseFilters = ReleasesFilters()
            releaseFilters.setOnlyArchived(True)
            archivedReleases = gatherReleases(releaseFilters)
        # releases = list(releases) + list(archivedReleases)
    if releases != []:
        for x in releases:
            arch = False
            if titleFilter(x.id, x.title, arch):
                if(fromDateTime is None and toDateTime is None and endFromDateTime is None and endToDateTime is None):
                    get_planned_dates(x.id, arch)
                else:
                    if(dateFilter(x.startDate, x.dueDate)):
                        get_planned_dates(x.id, arch)
    ##archived portion
    if archivedReleases != []:
        for x in archivedReleases:
            arch = True
            if titleFilter(x.id, x.title, arch):
                if(fromDateTime is None and toDateTime is None and endFromDateTime is None and endToDateTime is None):
                    get_planned_dates(x.id, arch)
                else:
                    if(dateFilter(x.startDate, x.dueDate)):
                        get_planned_dates(x.id, arch)

def getFilteredReleases(inArchived):
    releaseFilters = []
    releases = []
    releaseFilters = ReleasesFilters()
    if inArchived:
        releaseFilters.setOnlyArchived(True)
    if filterReleaseTags != [] and filterReleaseFolders == []:
        for filterReleaseTag in filterReleaseTags:
            releaseFilters.tags = [filterReleaseTag]
            releases += gatherReleases(releaseFilters)
    elif filterReleaseFolders != [] and filterReleaseTags == []:
        for filterReleaseFolder in filterReleaseFolders:
            folderId = checkForFolder(filterReleaseFolder)
            releaseFilters.parentId = str(folderId)
            releases += gatherReleases(releaseFilters)
    else:
        for filterReleaseFolder in filterReleaseFolders:
            folderId = checkForFolder(filterReleaseFolder)
            for filterReleaseTag in filterReleaseTags:
                releaseFilters.tags = [filterReleaseTag]
                releaseFilters.parentId = str(folderId)
                releases += gatherReleases(releaseFilters)
    return releases

def titleFilter(releaseId, theReleaseTitle, arch):
    if releaseTitle and taskTitle:
        if checkForApplicationName(releaseTitle, theReleaseTitle) and checkForTaskTitle(releaseId, taskTitle, arch):
            return True
    elif releaseTitle:
        if checkForApplicationName(releaseTitle, theReleaseTitle):
            return True
    elif taskTitle:
        if checkForTaskTitle(releaseId, taskTitle, arch):
            return True
    else:
        return True
    return False
            # if(checkForTaskTitle(x.id, taskTitle)):
            #     logger.info("hi")
            # if checkForApplicationName(releaseTitle, x.title):

def gatherReleases(releaseFilters):
    newReleases =[]
    releases = []
    i = 0
    newReleases = releaseApi.searchReleases(releaseFilters, i, 100)
    # releases = newReleases
    while newReleases:
        releases = list(releases) + list(newReleases)
        newReleases = []
        i = i+1
        newReleases = releaseApi.searchReleases(releaseFilters, i, 100)
    return releases

def checkForApplicationName(applicationName, releaseTitle):
    if applicationName != None:
        if applicationName in releaseTitle:
            return True
        else:
            return False
    else:
        return True

def checkForFolder(folderName):
    folders = generateFolderList()
    for folder in folders:
        if folder.title == folderName:
            return folder.id

def generateFolderList():
    masterList = []
    folders = folder_api.listRoot()
    masterList.extend(folders)
    for folder in masterList:
        if folder_api.list(folder.id, 0, 50, 1, False) != []:
            subFolders = folder_api.list(folder.id, 0, 50, 1, False)
            masterList.extend(subFolders)
    return masterList

def getSubFolders(folderId):
    subFolders = []
    folders = folder_api.list(folderId, 0, 50, 1, False)
    while folders != []:
        for folder in folders:
            folders = getSubFolders(folder.id)
    return b
    # if a:
    #     folders.extend(a)

    # if folders != []:
    #     for folder in folders:
    #         folders += getSubFolders(folder.id)
    # return folders
def checkForTaskTitle(releaseId, taskTitle, arch):
    if(taskTitle != ""):
        if arch:
            release = releaseApi.getArchivedRelease(releaseId)
            b = release.getTasksByTitle("", taskTitle)
        else:
            b = taskApi.searchTasksByTitle(taskTitle, "",  releaseId)
        if b:
            return True
        else:
            return False

def dateFilter(releaseStartDate, releaseEndDate):
    if fromDateTime is not None:
        if not releaseStartDate.after(fromDateTime):
            return False
    if toDateTime is not None:
        if not releaseStartDate.before(toDateTime):
            return False
    if endFromDateTime is not None:
        if not releaseEndDate.after(endFromDateTime):
            logger.info(str(releaseEndDate))
            return False
    if endToDateTime is not None:
        if not releaseEndDate.before(endToDateTime):
            return False
    return True

def get_planned_dates(releaseId, arch):
        multiPlanner = Planner()
        release = multiPlanner.build_object(releaseId, arch)
        # release = the_planner.get_Releases2(releaseId)

        print_dates(release)

def print_dates(release):
    global dict
    temp = {}
    temp['release'] = {}
    temp['release']['name'] = release['title']
    temp['release']['status'] = release['status']
    temp['release']['owner'] = release['owner']

    if release['startDate'] != None:
        temp['release']['startDate'] = int(release['startDate'])
    else:
        temp['release']['startDate'] = int(release['scheduledStartDate'])
    if release['endDate'] != None:
        temp['release']['endDate'] = int(release['endDate'])
    else:
        temp['release']['endDate'] = int(release['dueDate'])
    temp['release']['phases'] = []
    temp['release']['task'] = {}
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
        tempPhase['status'] = str(x['status'])
        tempPhase['startDate'] = startDate
        tempPhase['endDate'] = endDate
        temp['release']['phases'].append(tempPhase)
        tasks = x['tasks']
        for w in tasks:
            if w['title'] == taskTitle:
                if w['startDate'] == None:
                    startDate = int(w['scheduledStartDate'])
                else:
                    startDate = int(w['startDate'])
                if w['endDate'] == None:
                    endDate = int(w['dueDate'])
                else:
                    endDate =int(w['endDate'])
                tempTask = {}
                tempTask['name'] = w['title']
                tempTask['startDate'] = startDate
                tempTask['endDate'] = endDate
                tempTask['owner'] = str(w['owner'])
                tempTask['status'] = str(w['status'])
                temp['release']['task'] = tempTask


    dict.append(temp)

get_Releases()
data = json.dumps(dict)
