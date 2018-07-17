from __future__ import absolute_import
from celery import shared_task, task
import pymssql
from cloud.CVApi import *
from cloud.models import *
from django.db import connection
from xml.dom.minidom import parse, parseString
from . import remote
from .models import *
import datetime


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


def handle_func(jobid, steprunid):
    if not is_connection_usable():
        connection.close()
    try:
        conn = pymssql.connect(host='cv-server\COMMVAULT', user='sa_cloud', password='1qaz@WSX', database='CommServ')
        cur = conn.cursor()
    except:
        print("链接失败!")
    else:
        try:
            cur.execute(
                """SELECT *  FROM [commserv].[dbo].[RunningBackups] where jobid={0}""".format(jobid))
            backup_task_list = cur.fetchall()

            cur.execute(
                """SELECT *  FROM [commserv].[dbo].[RunningRestores] where jobid={0}""".format(jobid))
            restore_task_list = cur.fetchall()
        except:
            print("任务不存在!")  # 1.修改当前步骤状态为DONE
            steprun = StepRun.objects.filter(id=steprunid)
            steprun = steprun[0]
            steprun.state = "DONE"
        else:
            # 查询备份/恢复是否报错，将报错信息写入当前Step的operator字段中，并结束当前任务
            if backup_task_list:
                for backup_job in backup_task_list:
                    print("备份进度：", backup_job[42])
                    if backup_job[42] == 100:
                        steprun = StepRun.objects.filter(id=steprunid)
                        steprun = steprun[0]
                        if backup_job["DelayReason"]:
                            steprun.operator = backup_job["DelayReason"]
                            steprun.save()
                            cur.close()
                            conn.close()
                            exit(1)
                        else:
                            steprun.state = "DONE"
                            steprun.save()
                            cur.close()
                            conn.close()
                    else:
                        cur.close()
                        conn.close()
                        time.sleep(30)
                        handle_func(jobid, steprunid)
            elif restore_task_list:
                for restore_job in restore_task_list:
                    print("恢复进度：", restore_job[35])
                    if restore_job[35] == 100:
                        steprun = StepRun.objects.filter(id=steprunid)
                        steprun = steprun[0]
                        if restore_job["DelayReason"]:
                            steprun.operator = restore_job["DelayReason"]
                            steprun.save()
                            cur.close()
                            conn.close()
                            exit(1)
                        else:
                            steprun.state = "DONE"
                            steprun.save()
                            cur.close()
                            conn.close()
                    else:
                        cur.close()
                        conn.close()
                        time.sleep(30)
                        handle_func(jobid, steprunid)
            else:
                print("当前没有在执行的任务!")


@task
def handle_job(jobid, steprunid):
    """
    根据jobid查询任务状态，每半分钟查询一次，如果完成就在steprun中写入DONE
    """
    handle_func(jobid, steprunid)


@task
def exec_script(steprunid,username,fullname):
    """
    执行当前步骤在指定系统下的所有脚本
    """
    end_step_tag = True
    steprun = StepRun.objects.filter(id=steprunid)
    steprun = steprun[0]
    scriptruns = steprun.scriptrun_set.exclude(state="9").exclude(state="DONE").exclude(result=0)  # 查询失败或者未执行的脚本
    for script in scriptruns:
        cmd = r"{0}".format(script.script.scriptpath + script.script.filename)
        ip = script.script.ip
        username = script.script.username
        password = script.script.password
        script_type = script.script.type
        system_tag = ""
        if script_type == "SSH":
            system_tag = "Linux"
        if script_type == "BAT":
            system_tag = "Windows"
        rm_obj = remote.ServerByPara(cmd, ip, username, password, system_tag)  # 服务器系统从视图中传入
        result = rm_obj.run()
        script.result = result["exec_tag"]
        # 处理脚本执行失败问题
        if result == 1:
            print("当前脚本执行失败,结束任务!")  # 2.写入错误信息至operator
            script.operator = result['data']
            script.save()
            end_step_tag = False
            steprun.state = "EDIT"
            steprun.save()
            break
        script.state = "DONE"
        script.save()
    if end_step_tag:
        steprun.state = "DONE"
        steprun.save()

        task = steprun.processtask_set.filter(state="0")
        if len(task) > 0:
            task[0].endtime = datetime.datetime.now()
            task[0].state = "1"
            task[0].operator = username
            task[0].save()

            nextstep = steprun.step.next.exclude(state="9")
            if len(nextstep) > 0:
                nextsteprun = nextstep[0].steprun_set.exclude(state="9").filter(processrun=steprun.processrun)
                if len(nextsteprun) > 0:
                    mysteprun = nextsteprun[0]
                    myprocesstask = ProcessTask()
                    myprocesstask.processrun = steprun.processrun
                    myprocesstask.steprun = mysteprun
                    myprocesstask.starttime = datetime.datetime.now()
                    myprocesstask.senduser = username
                    myprocesstask.receiveuser = username
                    myprocesstask.type = "RUN"
                    myprocesstask.state = "0"
                    myprocesstask.content = steprun.processrun.DataSet.clientName + "的" + steprun.processrun.process.name + "流程进行到“" + nextstep[
                                                0].name + "”，请" + fullname + "处理。"
                    myprocesstask.save()
