# Copyright 2020 XEBIALABS
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
import org.slf4j.LoggerFactory as LoggerFactory

logger = LoggerFactory.getLogger("Planner")

MANUAL_TASK_DURATION = 60*60*1000
AUTOMATED_TASK_DURATION = 1*60*1000
FROM_END_TO_START = False
releaseStart = 0
lastPhaseStart = 0

class Planner(object):
    def __init__(self, server):
        self.username = server['username']
        self.password = server['password']
        self.base_url = server['url']

    def get_Releases2(self, releaseId):
        reqURL = "%s/releases/" % (self.base_url)
        reqURL = reqURL + releaseId
        headers = { "Content-Type": "application/json", "Accept": "application/json" }
        myResponse = requests.get(reqURL,headers=headers, auth=HTTPBasicAuth(self.username, self.password))
        if(myResponse.ok):
            release = json.loads(myResponse.content)
            newRelease = self.planner(release)
            return newRelease

        else:
            print("Error code %s" % myResponse.status_code )
            return 0


    def planner(self, release):
        release = self.getPhaseTime(release)
        release = self.convert_to_string(release)
        return release

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
            if x['dueDate'] == None and x['done'] == False and x['plannedDuration'] == None:
                if x['hasBeenStarted'] == True:
                    if (x['type'] == "xlrelease.CustomScriptTask" or x['type'] == "xlrelease.NotificationTask"):
                        x['plannedDuration'] = AUTOMATED_TASK_DURATION
                        currentTime = int(round(time.time()))
                        if x['plannedDuration'] + x['startDate'] < currentTime:
                            x['plannedDuration'] = currentTime - x['startDate']
                        # elif x['plannedDuration'] + x['startDate'] > currentTime:
                        #     x['plannedDuration'] = x['plannedDuration']
                        # else:
                        #     x['plannedDuration'] = x['plannedDuration'] + (currentTime-x['startDate'])
                    else:
                        x['plannedDuration'] = MANUAL_TASK_DURATION
                        currentTime = int(round(time.time()))
                        currentTime = currentTime*1000
                        if x['plannedDuration'] + x['startDate'] < currentTime:
                            x['plannedDuration'] = currentTime - x['startDate']
                        # elif x['plannedDuration'] + x['startDate'] > currentTime:
                        #     x['plannedDuration'] = x['plannedDuration']
                        # else:
                        #     x['plannedDuration'] = x['plannedDuration'] + (currentTime-x['startDate'])
                else:
                    if (x['type'] == "xlrelease.CustomScriptTask" or x['type'] == "xlrelease.NotificationTask"):
                        x['plannedDuration'] = AUTOMATED_TASK_DURATION
                    else:
                        x['plannedDuration'] = MANUAL_TASK_DURATION

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
                                    logger.error("No phase end date")
                            else:
                                phases[x]['dueDate'] = tasks[i]['dueDate']
                                phases[x]['tasks'] = tasks
# def print_dates(release):
#     #response.entity = {"status": "OK", "Release": release}
#

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
        if release['currentTask'] != None:
            if release['currentTask']['startDate'] != None:
                release['currentTask']['startDate'] = str(release['currentTask']['startDate'])
            if release['currentTask']['endDate'] != None:
                release['currentTask']['endDate'] = str(release['currentTask']['endDate'])
        if release['currentSimpleTasks'] != None:
            crc = release['currentSimpleTasks']
            for h in crc:
                if h['startDate'] != None:
                    h['startDate'] = str(h['startDate'])
                if h['endDate'] != None:
                    h['startDate'] = str(h['endDate'])
                if h['dueDate'] != None:
                    h['dueDate'] = str(h['dueDate'])
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
#
    def get_furthest_date(self, a, b):
        if a > b:
            return a
        else:
            return b
