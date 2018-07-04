from __future__ import absolute_import
from celery import shared_task, task
import pymssql
from cloud.CVApi import *
from cloud.models import *
from django.db import connection
from xml.dom.minidom import parse, parseString


def is_connection_usable():
    try:
        connection.connection.ping()
    except:
        return False
    else:
        return True


@shared_task
def just_save():
    if not is_connection_usable():
        connection.close()
    conn = pymssql.connect(host='cv-server\COMMVAULT', user='sa_cloud', password='1qaz@WSX', database='CommServ')
    cur = conn.cursor()
    cur.execute('select * from CommCellBackupInfo')
    joblist = cur.fetchall()
    cur.close()
    conn.close()

    info = {"webaddr": "cv-server", "port": "81", "username": "admin", "passwd": "Admin@2017", "token": "",
            "lastlogin": 0}
    cvvendor = Vendor.objects.filter(name='CommVault')
    if (len(cvvendor) > 0):
        doc = parseString(cvvendor[0].content)
        try:
            webaddr = (doc.getElementsByTagName("webaddr"))[0].childNodes[0].data
        except:
            pass
        try:
            port = (doc.getElementsByTagName("port"))[0].childNodes[0].data
        except:
            pass
        try:
            username = (doc.getElementsByTagName("username"))[0].childNodes[0].data
        except:
            pass
        try:
            passwd = (doc.getElementsByTagName("passwd"))[0].childNodes[0].data
        except:
            pass
        info = {"webaddr": webaddr, "port": port, "username": username, "passwd": passwd, "token": "",
                "lastlogin": 0}
    cvToken = CV_RestApi_Token()
    cvToken.login(info)
    RestApi = CV_RestApi(cvToken)
    for job in joblist:
        oldjob = Joblist.objects.filter(jobid=job[0])
        if len(oldjob) > 0:
            oldjob[0].isAged = job[26]
            oldjob[0].isAgedStr = job[27]
            oldjob[0].save()
        else:
            sizeOfMediaOnDisk = 0
            try:
                tree = RestApi.getCmd('Job/' + str(job[0]))
                jobdetail = tree.findall(".//jobs/jobSummary")
                if len(jobdetail) > 0:
                    sizeOfMediaOnDisk = jobdetail[0].attrib["sizeOfMediaOnDisk"]
            except:
                pass

            newjob = Joblist()
            newjob.jobid = job[0]
            newjob.appid = job[1]
            newjob.jobinitfrom = job[2]
            newjob.clientname = job[3]
            newjob.idataagent = job[4]
            newjob.instance = job[5]
            newjob.backupset = job[6]
            newjob.subclient = job[7]
            newjob.data_sp = job[8]
            newjob.backuplevelInt = job[9]
            newjob.backuplevel = job[10]
            newjob.incrlevel = job[11]
            newjob.jobstatusInt = job[12]
            newjob.jobstatus = job[13]
            newjob.jobfailedreason = job[14]
            newjob.transferTime = job[15]
            newjob.startdateunixsec = job[16]
            newjob.enddateunixsec = job[17]
            newjob.startdate = job[18]
            newjob.enddate = job[19]
            newjob.durationunixsec = job[20]
            newjob.duration = job[21]
            newjob.numstreams = job[22]
            newjob.numbytesuncomp = job[23]
            newjob.numbytescomp = job[24]
            newjob.numobjects = job[25]
            newjob.isAged = job[26]
            newjob.isAgedStr = job[27]
            newjob.xmlJobOptions = job[28]
            newjob.retentionDays = job[29]
            newjob.systemStateBackup = job[30]
            newjob.inPrimaryCopy = job[31]
            newjob.failedobjects = job[32]
            newjob.totalBackupSize = job[33]
            newjob.encrypted = job[34]
            newjob.diskcapacity = sizeOfMediaOnDisk
            newjob.result = ""
            newjob.save()
