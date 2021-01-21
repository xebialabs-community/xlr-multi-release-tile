# Copyright 2021 XEBIALABS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import requests
from requests.auth import HTTPBasicAuth
import json
import time
import datetime
#import com.xebialabs.xlrelease.api.v1
#import com.xebialabs.xlrelease.domain
from java.time import LocalDate, ZoneId
# beter way to do this
import java.util.Date
import dateutil.parser
import org.slf4j.LoggerFactory as LoggerFactory
# import com.xebialabs.xlrelease.api.v1 as releaseApi
import com.xebialabs.xlrelease.api.XLReleaseServiceHolder as XLReleaseServiceHolder

logger = LoggerFactory.getLogger("Planner")
releaseApi = XLReleaseServiceHolder.getReleaseApi()
phaseApi = XLReleaseServiceHolder.getPhaseApi()
taskApi = XLReleaseServiceHolder.getTaskApi()

MANUAL_TASK_DURATION = 60*60*1000
AUTOMATED_TASK_DURATION = 1*60*1000

hardcodedVars = ["Release-Ready", "CodeFrozen-Flag", "PendSecurityScan", "Dependency-Flag", "NoOpenDefects-Flag", "BXImpact-Flag"]
class Planner(object):
    def __init__(self):
        return

    def build_object(self, releaseId, archived):
        newRelease = {}
        newRelease['release'] = {}
        if archived:
            release = releaseApi.getArchivedRelease(releaseId)
            logger.info("count")
            #getArchivedRelease
        else:
            release = releaseApi.getRelease(releaseId)
            logger.info("count")
        variableMap = []
        # variableSpot['name'] = {}
        for var in release.variables:
            if str(var.key) in hardcodedVars:
                variableSpot = {}
                variableSpot['name'] = str(var.key)
                variableSpot['value'] = str(var.value)
                variableMap.append(variableSpot)
        newRelease['variables'] = variableMap
        newRelease['owner'] = str(release.owner)
        newRelease['title'] = release.title
        newRelease['scheduledStartDate'] = release.scheduledStartDate
        newRelease['startDate'] = release.startDate
        newRelease['dueDate'] = release.dueDate
        newRelease['endDate'] = release.endDate
        newRelease['plannedDuration'] = release.plannedDuration
        newRelease['status'] = str(release.status)
        newRelease['phases'] = []
        phases = release.phases
        test = []
        # logger.info(str(phases))
        for x in phases:
            phase_list = {}
            phase_list['title'] = x.title
            phase_list['scheduledStartDate'] = x.scheduledStartDate
            phase_list['startDate'] = x.startDate
            phase_list['dueDate'] = x.dueDate
            phase_list['endDate'] = x.endDate
            phase_list['plannedDuration'] = x.plannedDuration
            if phase_list['plannedDuration'] != None:
                phase_list['plannedDuration'] = phase_list['plannedDuration']*1000
            phase_list['status'] = str(x.status)
            phase_list['tasks'] = []
            tasks = x.tasks
            for w in tasks:
                task_list = {}
                task_list = self.getTaskFromObject(task_list, w)
                phase_list['tasks'].append(task_list)
            newRelease['phases'].append(phase_list)
        del release
        newRelease = self.convertToEpoch(newRelease)
        newRelease = self.planner(newRelease)
        return newRelease

    def getTaskFromObject(self, task_list, w):
        task_list['title'] = w.title
        task_list['owner'] = w.owner
        task_list['scheduledStartDate'] = w.scheduledStartDate
        task_list['startDate'] = w.startDate
        task_list['dueDate'] = w.dueDate
        task_list['endDate'] = w.endDate
        task_list['plannedDuration'] = w.plannedDuration
        if task_list['plannedDuration'] != None:
            task_list['plannedDuration'] = task_list['plannedDuration']*1000
        task_list['automated'] = w.automated
        task_list['status'] = str(w.status)
        task_list['type'] = w.type
        if str(w.type) == "xlrelease.SequentialGroup":
            task_list['tasks'] = []
            for tasks in w.tasks:
                new_task_list = {}
                new_task_list = self.getTaskFromObject(new_task_list, tasks)
                task_list['tasks'].append(new_task_list)
        elif str(w.type) == "xlrelease.GateTask":
            # task_list['dependencies'] = json.loads(w.dependencies)
            # for a in task_list['dependencies']:
            #     logger.info(str(a.targetTitle))
            for a in w.dependencies:
                if str(a.targetTitle) == str(a.targetDisplayPath):
                    task_list['automated'] = True
                else:
                    task_list['automated'] = False
            #     task_list['targetTitle'] = str(a.targetTitle)
            #     task_list['targetDisplayPath'] = str(a.targetDisplayPath)
                # logger.info(str(a.targetTitle))
                # logger.info(str(a.targetDisplayPath))
        ###gate task stuff
        # if str(w.type) == "xlrelease.GateTask":
        #     logger.info(w.title)
        #     for a in w.dependencies:
        #         logger.info(str(a.targetTitle))
        #         logger.info(str(a.targetDisplayPath))
        return task_list


    def convertToEpoch(self, release):
        # if str(type(release['startDate'])) == "<type 'java.util.Date'>":
        if isinstance(release['startDate'], java.util.Date):
            release['startDate'] = release['startDate'].getTime()
        if isinstance(release['scheduledStartDate'], java.util.Date):
            release['scheduledStartDate'] = release['scheduledStartDate'].getTime()
        if isinstance(release['startDate'], java.util.Date):
            release['startDate'] = release['startDate'].getTime()
        if isinstance(release['endDate'], java.util.Date):
            release['endDate'] = release['endDate'].getTime()
        if isinstance(release['dueDate'], java.util.Date):
            release['dueDate'] = release['dueDate'].getTime()
        if isinstance(release['plannedDuration'], java.util.Date):
            release['plannedDuration'] = release['plannedDuration'].getTime()
        phases = release['phases']
        for x in phases:
            if isinstance(x['scheduledStartDate'], java.util.Date):
                x['scheduledStartDate'] = x['scheduledStartDate'].getTime()
            if isinstance(x['startDate'], java.util.Date):
                x['startDate'] = x['startDate'].getTime()
            if isinstance(x['endDate'], java.util.Date):
                x['endDate'] = x['endDate'].getTime()
            if isinstance(x['dueDate'], java.util.Date):
                x['dueDate'] = x['dueDate'].getTime()
            if isinstance(x['plannedDuration'], java.util.Date):
                x['plannedDuration'] = x['plannedDuration'].getTime()
            tasks = x['tasks']
            self.taskConvertToEpoch(tasks)
        return release
    def taskConvertToEpoch(self, tasks):
        for w in tasks:
            if isinstance(w['scheduledStartDate'], java.util.Date):
                w['scheduledStartDate'] = w['scheduledStartDate'].getTime()
            if isinstance(w['startDate'], java.util.Date):
                w['startDate'] = w['startDate'].getTime()
            if isinstance(w['endDate'], java.util.Date):
                w['endDate'] = w['endDate'].getTime()
            if isinstance(w['dueDate'], java.util.Date):
                w['dueDate'] = w['dueDate'].getTime()
            if isinstance(w['plannedDuration'], java.util.Date):
                w['plannedDuration'] = w['plannedDuration'].getTime()
            if str(w['type']) == "xlrelease.SequentialGroup":
                self.taskConvertToEpoch(w['tasks'])

    def get_Releases(self, releaseId):
        self.planner(release)


    def planner(self, release):
        release = self.getPhaseTime(release)
        release = self.convert_to_string(release)
        #response.entity = {"status": "OK", "Release": release}
        return release
        # self.print_dates(release)

    def getPhaseTime(self, release):
        phases = release['phases']
        if phases[0]['startDate'] == None:
            phases[0]['scheduledStartDate'] = release['scheduledStartDate']
        phases[0]['tasks'][0]['scheduledStartDate'] = release['scheduledStartDate']
        for x in phases:
            if x['endDate'] == None:
                tasks = x['tasks']
                self.set_task_duration(tasks)
                x['tasks'] = tasks
        self.set_dates(phases)
        release['phases'] = phases
        return release

    def set_task_duration(self, tasks):
        for x in tasks:
            if x['dueDate'] == None and x['endDate'] == None and x['plannedDuration'] == None:
                if x['status'] == "IN_PROGRESS" or x['status'] == "DONE" or x['status'] == "FAILED":
                    if str(x['type']) == "xlrelease.SequentialGroup":
                        self.set_task_duration(x['tasks'])
                        plannedDuration =0
                        for task in x['tasks']:
                            plannedDuration += task['plannedDuration']
                        x['plannedDuration'] = plannedDuration
                        currentTime = int(round(time.time()))
                        currentTime = currentTime*1000
                        if x['plannedDuration'] + x['startDate'] < currentTime:
                            x['plannedDuration'] = currentTime - x['startDate']
                    elif x['automated']:
                        if str(x['type']) == "xlrelease.GateTask":
                            x['plannedDuration'] = 0
                        else:
                            x['plannedDuration'] = AUTOMATED_TASK_DURATION
                        currentTime = int(round(time.time()))
                        currentTime = currentTime*1000
                        if x['plannedDuration'] + x['startDate'] < currentTime:
                            x['plannedDuration'] = currentTime - x['startDate']
                    else:
                        x['plannedDuration'] = MANUAL_TASK_DURATION
                        currentTime = int(round(time.time()))
                        currentTime = currentTime*1000
                        if x['plannedDuration'] + x['startDate'] < currentTime:
                            x['plannedDuration'] = currentTime - x['startDate']
                else:
                    if str(x['type']) == "xlrelease.SequentialGroup":
                        self.set_task_duration(x['tasks'])
                        plannedDuration =0
                        for task in x['tasks']:
                            if task['plannedDuration'] != None:
                                plannedDuration += task['plannedDuration']
                            else:
                                plannedDuration += 0
                        x['plannedDuration'] = plannedDuration
                        # logger.info(x['title'])
                        # logger.info(str(x['plannedDuration']))
                    elif x['automated']:#(x['type'] == "xlrelease.CustomScriptTask" or x['type'] == "xlrelease.NotificationTask"):
                        if str(x['type']) == "xlrelease.GateTask":
                            x['plannedDuration'] = 0
                        else:
                            x['plannedDuration'] = AUTOMATED_TASK_DURATION
                    else:
                        x['plannedDuration'] = MANUAL_TASK_DURATION
            ###may not need this
            elif(str(x['type']) == "xlrelease.SequentialGroup"):
                x['tasks'] = self.set_task_duration(x['tasks'])
            # logger.info(x['title'])
            # logger.info(str(x['plannedDuration']))

    def set_dates(self, phases):
        for x in range(len(phases)):
            tasks = phases[x]['tasks']
            if tasks[0]['scheduledStartDate'] == None and tasks[0]['startDate'] == None:
                tasks[0]['scheduledStartDate'] = phases[x-1]['dueDate']
            if phases[x]['endDate'] == None:
                for i in range(len(tasks)):
                    if tasks[i]['scheduledStartDate'] == None and tasks[i]['startDate'] == None:
                        tasks[i]['scheduledStartDate'] = tasks[i-1]['dueDate']
                    if tasks[i]['dueDate'] == None and tasks[i]['endDate'] == None:
                        if tasks[i]['startDate'] == None:
                            tasks[i]['dueDate'] = tasks[i]['scheduledStartDate'] + tasks[i]['plannedDuration']
                        else:
                            tasks[i]['dueDate'] = tasks[i]['startDate'] + tasks[i]['plannedDuration']
                        if i == (len(tasks)-1):
                            if phases[x]['scheduledStartDate'] == None and phases[x]['startDate'] == None:
                                phases[x]['scheduledStartDate'] = tasks[0]['scheduledStartDate']
                            temp = str(phases[x]['scheduledStartDate'])
                            if phases[x]['dueDate'] != None or phases[x]['plannedDuration'] != None:
                                if phases[x]['dueDate'] != None:
                                    phases[x]['dueDate'] = self.get_furthest_date(phases[x]['dueDate'], tasks[i]['dueDate'])
                                elif phases[x]['plannedDuration'] != None:
                                    if phases[x]['startDate'] == None:
                                        phases[x]['dueDate'] = phases[x]['scheduledStartDate'] + phases[x]['plannedDuration']
                                    else:
                                        phases[x]['dueDate'] = phases[x]['startDate'] + phases[x]['plannedDuration']
                                        phases[x]['dueDate'] = self.get_furthest_date(phases[x]['dueDate'], tasks[i]['dueDate'])
                                else:
                                    print "No phase end date"
                            else:
                                phases[x]['dueDate'] = tasks[i]['dueDate']
                                phases[x]['tasks'] = tasks
    def print_dates(self, release):
        logger.info(release['startDate'])
        logger.info("In print dates")
        return release
        #response.entity = {"status": "OK", "Release": release}

    def convert_to_string(self, release):
        if release['scheduledStartDate'] != None:
            release['scheduledStartDate'] = str(release['scheduledStartDate'])
        if release['startDate'] != None:
            release['startDate'] = str(release['startDate'])
        if release['endDate'] != None:
            release['endDate'] = str(release['endDate'])
        if release['dueDate'] != None:
            release['dueDate'] = str(release['dueDate'])
        if release['plannedDuration'] != None:
            release['plannedDuration'] = str(release['plannedDuration'])
        phases = release['phases']
        for x in phases:
            if x['scheduledStartDate'] != None:
                x['scheduledStartDate'] = str(x['scheduledStartDate'])
            if x['startDate'] != None:
                x['startDate'] = str(x['startDate'])
            if x['endDate'] != None:
                x['endDate'] = str(x['endDate'])
            if x['dueDate'] != None:
                x['dueDate'] = str(x['dueDate'])
            if x['plannedDuration'] != None:
                x['plannedDuration'] = str(x['plannedDuration'])
            tasks = x['tasks']
            for w in tasks:
                # for key in w:
                #     if key != None:
                #         w[key] = str(w[key])
                if w['scheduledStartDate'] != None:
                    w['scheduledStartDate'] = str(w['scheduledStartDate'])
                if w['startDate'] != None:
                    w['startDate'] = str(w['startDate'])
                if w['endDate'] != None:
                    w['endDate'] = str(w['endDate'])
                if w['dueDate'] != None:
                    w['dueDate'] = str(w['dueDate'])
                if w['plannedDuration'] != None:
                    w['plannedDuration'] = str(w['plannedDuration'])
        return release

    def get_furthest_date(self, a, b):
        if a > b:
            return a
        else:
            return b
