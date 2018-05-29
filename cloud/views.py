# coding:utf-8

from django.shortcuts import render
from django.contrib import auth
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404, HttpResponse, JsonResponse
from cloud.models import *
from django.http import StreamingHttpResponse
import time
import datetime
from django.db.models import Q
import sys
import os
from cloud.tasks import just_save
import json
import random
from django.core.mail import send_mail
from cloudDR import settings
import uuid
import xml.dom.minidom
from xml.dom.minidom import parse, parseString
from cloud.CVApi import *
from django.db.models import Count
from django.db.models import Sum
from django.db import connection
from cloud.vmApi import *



#why
info = {"webaddr": "cv-server", "port": "81", "username": "admin", "passwd": "Admin@2017", "token": "",
        "lastlogin": 0}

def index(request):
    if request.user.is_authenticated():
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
            global info
            info = {"webaddr": webaddr, "port": port, "username": username, "passwd": passwd, "token": "",
                    "lastlogin": 0}
        # cvToken = CV_RestApi_Token()
        # cvToken.login(info)
        # cvAPI = CV_API(cvToken)
        # clientInfo = cvAPI.getClientInfo(3)
        # backupInfo = cvAPI.getSubclientInfo("22")
        # print uuid.uuid1()
        # print clientInfo
        # print cvAPI.getClientList()

        return render(request, "index.html", {'username': request.user.userinfo.fullname, "homepage": True})
    else:
        return HttpResponseRedirect("/login")


def get_dashboard_amchart_1(request):
    if request.user.is_authenticated():
        result = []
        times1 = []
        times2 = []
        type = "1"
        try:
            type = request.GET.get('type', '')
        except:
            pass
        allhost = ClientHost.objects.exclude(status="9").filter(owernID=request.user.userinfo.userGUID)
        hostlist = []
        if (len(allhost) > 0):
            for host in allhost:
                hostlist.append(host.clientName)
        nowtime = datetime.datetime.now()
        dttime = datetime.datetime.strptime(((nowtime - datetime.timedelta(days=6)).strftime("%Y-%m-%d")), '%Y-%m-%d')
        select = {'day': connection.ops.date_trunc_sql('day', 'startdate')}
        if type == "2":
            dttime = datetime.datetime.strptime(
                ((nowtime - datetime.timedelta(days=28 + nowtime.weekday())).strftime("%Y-%m-%d")), '%Y-%m-%d')
        if type == "3":
            q, r = divmod(nowtime.month - 1 + 7, 12)
            dttime = datetime.datetime(nowtime.year - 1 + q, r + 1, 1)
        if type == "4":
            q, r = divmod(nowtime.month - 1 + 1, 12)
            dttime = datetime.datetime(nowtime.year - 1 + q, r + 1, 1)
        joblist = Joblist.objects.filter(startdate__gte=dttime, clientname__in=hostlist)
        joblist1 = joblist.extra(select=select).values("day").annotate(num_day=Count('id')).order_by("day")
        for job in joblist1:
            times = 0
            try:
                times = int(job["num_day"])
            except:
                pass
            datarow = {"date": job["day"].strftime("%y-%m-%d"), "times": times}
            if type == "3" or type == "4":
                datarow = {"date": job["day"].strftime("%y-%m-%d"), "times": times}
            times1.append(datarow)
        joblist2 = joblist.filter(jobstatus__in=["Failed", "Killed", "Failed to Start"]).extra(select=select).values(
            "day").annotate(num_day=Count('id'))
        for job in joblist2:
            times = 0
            try:
                times = int(job["num_day"])
            except:
                pass
            datarow = {"date": job["day"].strftime("%y-%m-%d"), "times": times}
            if type == "3" or type == "4":
                datarow = {"date": job["day"].strftime("%y-%m-%d"), "times": times}
            times2.append(datarow)
        if type == "1":
            for i in range((nowtime - dttime).days + 1):
                day = dttime + datetime.timedelta(days=i)
                count1 = 0
                count2 = 0
                for time1 in times1:
                    if time1["date"] == day.strftime("%y-%m-%d"):
                        count1 = time1["times"]
                        break
                for time2 in times2:
                    if time2["date"] == day.strftime("%y-%m-%d"):
                        count2 = time2["times"]
                        break
                result.append(
                    {"date": day.strftime("%m-%d"), "times1": count1, "times2": count2, "times3": count1 - count2})
        if type == "2":
            count1 = 0
            count2 = 0
            strdt = dttime.strftime("%m-%d")
            for i in range((nowtime - dttime).days + 1):
                day = dttime + datetime.timedelta(days=i)
                for time1 in times1:
                    if time1["date"] == day.strftime("%y-%m-%d"):
                        count1 += time1["times"]
                        break
                for time2 in times2:
                    if time2["date"] == day.strftime("%y-%m-%d"):
                        count2 += time2["times"]
                        break
                if day.weekday() == 6 or i == (nowtime - dttime).days:
                    strdt = strdt + "/" + day.strftime("%m-%d")
                    result.append(
                        {"date": strdt, "times1": count1, "times2": count2, "times3": count1 - count2})
                    count1 = 0
                    count2 = 0
                    strdt = (day + datetime.timedelta(days=1)).strftime("%m-%d")
        if type == "3" or type == "4":
            count1 = 0
            count2 = 0
            for i in range((nowtime - dttime).days + 1):
                day = dttime + datetime.timedelta(days=i)
                for time1 in times1:
                    if time1["date"] == day.strftime("%y-%m-%d"):
                        count1 += time1["times"]
                        break
                for time2 in times2:
                    if time2["date"] == day.strftime("%y-%m-%d"):
                        count2 += time2["times"]
                        break
                if (day + datetime.timedelta(days=1)).day == 1 or i == (nowtime - dttime).days:
                    result.append(
                        {"date": day.strftime("%y-%m"), "times1": count1, "times2": count2, "times3": count1 - count2})
                    count1 = 0
                    count2 = 0

        return HttpResponse(json.dumps(result))


def get_dashboard_amchart_2(request):
    if request.user.is_authenticated():
        result = []
        times1 = []
        times2 = []
        type = "1"
        try:
            type = request.GET.get('type', '')
        except:
            pass
        hostlist = []
        allhost = ClientHost.objects.exclude(status="9").filter(owernID=request.user.userinfo.userGUID)
        if (len(allhost) > 0):
            for host in allhost:
                hostlist.append(host.clientName)
        nowtime = datetime.datetime.now()
        dttime = datetime.datetime.strptime(((nowtime - datetime.timedelta(days=6)).strftime("%Y-%m-%d")), '%Y-%m-%d')
        select = {'day': connection.ops.date_trunc_sql('day', 'startdate')}
        if type == "2":
            dttime = datetime.datetime.strptime(
                ((nowtime - datetime.timedelta(days=28 + nowtime.weekday())).strftime("%Y-%m-%d")), '%Y-%m-%d')
        if type == "3":
            q, r = divmod(nowtime.month - 1 + 7, 12)
            dttime = datetime.datetime(nowtime.year - 1 + q, r + 1, 1)
        if type == "4":
            q, r = divmod(nowtime.month - 1 + 1, 12)
            dttime = datetime.datetime(nowtime.year - 1 + q, r + 1, 1)

        joblist = Joblist.objects.filter(startdate__gte=dttime, clientname__in=hostlist)
        joblist1 = joblist.values("clientname").annotate(num_clientname=Count('id'))
        for job in joblist1:
            times = 0
            try:
                times = int(job["num_clientname"])
            except:
                pass
            lastjob = Joblist.objects.filter(clientname=job["clientname"]).latest("startdate")
            times1.append({"clientname": job["clientname"], "times": times,
                           "lasttime": lastjob.startdate.strftime("%Y-%m-%d %X")})
        joblist2 = joblist.filter(jobstatus__in=["Failed", "Killed", "Failed to Start"]).values("clientname").annotate(
            num_clientname=Count('id'))
        for job in joblist2:
            times = 0
            try:
                times = int(job["num_clientname"])
            except:
                pass
            times2.append({"clientname": job["clientname"], "times": times})
        for time1 in times1:
            count1 = time1["times"]
            count2 = 0
            for time2 in times2:
                if time1["clientname"] == time2["clientname"]:
                    count2 = time2["times"]
                    break
            result.append(
                {"clientname": time1["clientname"], "times1": count1, "times2": count2, "times3": count1 - count2,
                 "lasttime": time1["lasttime"]})
        return HttpResponse(json.dumps(result))


def get_dashboard_amchart_3(request):
    if request.user.is_authenticated():
        result = []
        ll = []
        rl = []
        type = "1"
        try:
            type = request.GET.get('type', '')
        except:
            pass
        allhost = ClientHost.objects.exclude(status="9").filter(owernID=request.user.userinfo.userGUID)
        hostlist = []
        if (len(allhost) > 0):
            for host in allhost:
                hostlist.append(host.clientName)
        nowtime = datetime.datetime.now()

        if type == "1":
            dttime = datetime.datetime.strptime(((nowtime - datetime.timedelta(days=6)).strftime("%Y-%m-%d")),
                                                '%Y-%m-%d')
            for i in range(7):
                ll = 0
                day = dttime + datetime.timedelta(days=i)
                s = datetime.datetime(day.year, day.month, day.day)
                e = datetime.datetime(day.year, day.month, day.day) + datetime.timedelta(days=1)
                curjoblist = Joblist.objects.filter(startdate__range=(s, e), clientname__in=hostlist).extra(
                    select={'llsum': 'sum(numbytesuncomp)'}).values('llsum')
                if curjoblist[0]["llsum"] is not None:
                    ll = curjoblist[0]["llsum"]

                rlsum = 0
                for clientname in hostlist:
                    rlfulljoblist = Joblist.objects.filter(startdate__lte=e, backuplevel='Full',
                                                           clientname=clientname).order_by("-startdate")
                    rl = 0
                    if len(rlfulljoblist) > 0:
                        rl = rlfulljoblist[0].diskcapacity
                        s = rlfulljoblist[0].startdate
                    print(clientname,rl)
                    rlsum = rlsum + rl
                    rlincjoblist = Joblist.objects.filter(startdate__range=(s, e), backuplevel='Incremental',
                                                          clientname=clientname)
                    rlincjoblist = rlincjoblist.extra(select={'rlsum': 'sum(numbytesuncomp)'}).values('rlsum')

                    if rlincjoblist[0]["rlsum"] is not None:
                        rl = rlincjoblist[0]["rlsum"]
                        rlsum = rlsum + rl
                result.append(
                    {"date": day.strftime("%m-%d"), "ll": int(ll / 1024 / 1024), "rl": int(rlsum / 1024 / 1024)})
        if type == "2":
            dttime = datetime.datetime.strptime(
                ((nowtime - datetime.timedelta(days=28 + nowtime.weekday())).strftime("%Y-%m-%d")), '%Y-%m-%d')
            for i in range(5):
                ll = 0
                day = dttime + datetime.timedelta(days=i * 7)
                s = datetime.datetime(day.year, day.month, day.day)
                e = datetime.datetime(day.year, day.month, day.day) + datetime.timedelta(days=7)
                curjoblist = Joblist.objects.filter(startdate__range=(s, e), clientname__in=hostlist).extra(
                    select={'llsum': 'sum(numbytesuncomp)'}).values('llsum')
                if curjoblist[0]["llsum"] is not None:
                    ll = curjoblist[0]["llsum"]

                rlsum = 0

                result.append({"date": s.strftime("%m-%d") + "/" + e.strftime("%m-%d"), "ll": int(ll / 1024 / 1024),
                               "rl": int(rlsum / 1024 / 1024)})

        if type == "3":
            q, r = divmod(nowtime.month - 1 + 7, 12)
            dttime = datetime.datetime(nowtime.year - 1 + q, r + 1, 1)
            for i in range(6):
                ll = 0
                q, r = divmod(dttime.month - 1 + i, 12)
                day = datetime.datetime(dttime.year + q, r + 1, 1)
                s = datetime.datetime(day.year, day.month, day.day)
                q, r = divmod(s.month - 1 + 1, 12)
                e = datetime.datetime(s.year + q, r + 1, 1)
                curjoblist = Joblist.objects.filter(startdate__range=(s, e), clientname__in=hostlist).extra(
                    select={'llsum': 'sum(numbytesuncomp)'}).values('llsum')
                if curjoblist[0]["llsum"] is not None:
                    ll = curjoblist[0]["llsum"]

                rlsum = 0

                result.append(
                    {"date": s.strftime("%y-%m"), "ll": int(ll / 1024 / 1024), "rl": int(rlsum / 1024 / 1024)})
        if type == "4":
            q, r = divmod(nowtime.month - 1 + 1, 12)
            dttime = datetime.datetime(nowtime.year - 1 + q, r + 1, 1)
            for i in range(12):
                ll = 0
                q, r = divmod(dttime.month - 1 + i, 12)
                day = datetime.datetime(dttime.year + q, r + 1, 1)
                s = datetime.datetime(day.year, day.month, day.day)
                q, r = divmod(s.month - 1 + 1, 12)
                e = datetime.datetime(s.year + q, r + 1, 1)
                curjoblist = Joblist.objects.filter(startdate__range=(s, e), clientname__in=hostlist).extra(
                    select={'llsum': 'sum(numbytesuncomp)'}).values('llsum')
                if curjoblist[0]["llsum"] is not None:
                    ll = curjoblist[0]["llsum"]

                rlsum = 0

                result.append(
                    {"date": s.strftime("%y-%m"), "ll": int(ll / 1024 / 1024), "rl": int(rlsum / 1024 / 1024)})

        return HttpResponse(json.dumps(result))


def get_dashboard_amchart_4(request):
    if request.user.is_authenticated():
        type = "1"
        try:
            type = request.GET.get('type', '')
        except:
            pass
        hostlist = []
        allhost = ClientHost.objects.exclude(status="9").filter(owernID=request.user.userinfo.userGUID)
        if (len(allhost) > 0):
            for host in allhost:
                hostlist.append(host.clientName)
        result = []
        nowtime = datetime.datetime.now()
        dttime = datetime.datetime.strptime(((nowtime - datetime.timedelta(days=6)).strftime("%Y-%m-%d")), '%Y-%m-%d')
        select = {'day': connection.ops.date_trunc_sql('day', 'startdate')}
        if type == "2":
            dttime = datetime.datetime.strptime(
                ((nowtime - datetime.timedelta(days=28 + nowtime.weekday())).strftime("%Y-%m-%d")), '%Y-%m-%d')
        if type == "3":
            q, r = divmod(nowtime.month - 1 + 7, 12)
            dttime = datetime.datetime(nowtime.year - 1 + q, r + 1, 1)
        if type == "4":
            q, r = divmod(nowtime.month - 1 + 1, 12)
            dttime = datetime.datetime(nowtime.year - 1 + q, r + 1, 1)
        joblist = Joblist.objects.filter(startdate__gte=dttime, clientname__in=hostlist).values("jobstatus").annotate(
            num_jobstatus=Count('jobstatus')).values("jobstatus", "num_jobstatus")
        Completed = 0
        Failed = 0
        errors = 0
        for job in joblist:
            if str(job["jobstatus"]) == "Success":
                Completed += int(job["num_jobstatus"])
            else:
                if str(job["jobstatus"]) == "Failed":
                    Failed += int(job["num_jobstatus"])
                else:
                    if str(job["jobstatus"]) == "Killed":
                        Failed += int(job["num_jobstatus"])
                    else:
                        if str(job["jobstatus"]) == "Failed to Start":
                            Failed += int(job["num_jobstatus"])
                        else:
                            errors = job["num_jobstatus"]
        result.append({"country": "成功", "value": Completed})
        result.append({"country": "失败", "value": Failed})
        result.append({"country": "报警", "value": errors})

        return HttpResponse(json.dumps(result))


def downloadlist(request):
    if request.user.is_authenticated():
        return render(request, "downloadlist.html", {'username': request.user.userinfo.fullname, "downloadpage": True})
    else:
        return HttpResponseRedirect("/login")


def download(request):
    if request.user.is_authenticated():
        try:
            def file_iterator(file_name, chunk_size=512):
                with open(file_name, "rb") as f:
                    while True:
                        c = f.read(chunk_size)
                        if c:
                            yield c
                        else:
                            break

            #the_file_name = "/var/www/cloudDR/download/" + request.GET.get('filename', '').replace('^', ' ')
            the_file_name = "download/" + request.GET.get('filename', '').replace('^', ' ')
            response = StreamingHttpResponse(file_iterator(the_file_name))
            response['Content-Type'] = 'application/octet-stream; charset=unicode'
            response['Content-Disposition'] = 'attachment;filename="{0}"'.format(the_file_name)
            return response
        except:
            return HttpResponseRedirect("/downloadlist")
    else:
        return HttpResponseRedirect("/login")


def login(request):
    auth.logout(request)
    try:
        del request.session['ispuser']
        del request.session['isadmin']
    except KeyError:
        pass
    return render(request, 'login.html', context_instance=RequestContext(request))


def userlogin(request):
    if request.method == 'POST':
        result = ""
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_active:
            auth.login(request, user)
            myuserinfo = user.userinfo
            if myuserinfo.forgetpassword:
                myuserinfo.forgetpassword = ""
                myuserinfo.save()
            if request.user.is_authenticated():
                if myuserinfo.state == "0":
                    result = "success1"
                else:
                    result = "success"
                if (request.POST.get('remember', '') != '1'):
                    request.session.set_expiry(0)
                myuser = User.objects.get(username=username)
                usertype = myuser.userinfo.type
                if usertype == '1':
                    request.session['ispuser'] = True
                else:
                    request.session['ispuser'] = False
                request.session['isadmin'] = myuser.is_superuser
            else:
                result = "登录失败，请于客服联系。"
        else:
            result = "用户名或密码不正确。"

    return HttpResponse(result)


def registUser(request):
    if request.method == 'POST':
        result = ""
        myusername = request.POST.get('username', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')

        alluser = User.objects.filter(username=myusername)
        if (len(alluser) > 0):
            result = u"用户名" + myusername + u'已存在。'
        else:
            alluser = User.objects.filter(email=email)
            if (len(alluser) > 0):
                result = u"邮箱" + email + u'已被注册。'
            else:
                newuser = User()
                newuser.username = myusername
                newuser.set_password("password")
                newuser.email = email
                newuser.save()
                # 用户扩展信息 profile
                profile = UserInfo()  # e*************************
                profile.user_id = newuser.id
                profile.userGUID = uuid.uuid1()
                profile.phone = phone
                profile.type = "1"
                profile.state = "0"
                profile.save()
                result = "success1"
                user = auth.authenticate(username=myusername, password="password")
                if user is not None and user.is_active:
                    auth.login(request, user)
                try:
                    subject = u'注册成功'
                    message = u'用户:' + myusername + u'您好。' \
                              + u"\n您在云灾备系统注册成功，初始密码为password，点击链接进入登录页面:" \
                              + u"http://127.0.0.1:8000/login/"
                    send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
                except:
                    pass
        return HttpResponse(result)


def forgetPassword(request):
    if request.method == 'POST':
        result = ""
        email = request.POST.get('email', '')
        alluser = User.objects.filter(email=email)
        if (len(alluser) <= 0):
            result = u"邮箱" + email + u'不存在。'
        else:
            myuserinfo = alluser[0].userinfo
            url = str(uuid.uuid1())
            subject = u'密码重置'
            message = u'用户:' + alluser[0].username + u'您好。' \
                      + u"\n您在云灾备系统申请了密码重置，点击链接进入密码重置页面:" \
                      + u"http://127.0.0.1:8000/resetpassword/" + url
            send_mail(subject, message, settings.EMAIL_HOST_USER, [alluser[0].email])
            myuserinfo.forgetpassword = url
            myuserinfo.save()
            result = "邮件发送成功，请注意查收。"
        return HttpResponse(result)


def resetpassword(request, offset):
    myuserinfo = UserInfo.objects.filter(forgetpassword=offset)
    if len(myuserinfo) > 0:
        myusername = myuserinfo[0].user.username
        return render(request, 'reset.html', {"myusername": myusername})
    else:
        return render(request, 'reset.html', {"error": True})


def reset(request):
    if request.method == 'POST':
        result = ""
        myusername = request.POST.get('username', '')
        password = request.POST.get('password', '')

        alluser = User.objects.filter(username=myusername)
        if (len(alluser) > 0):
            alluser[0].set_password(password)
            alluser[0].save()
            myuserinfo = alluser[0].userinfo
            myuserinfo.forgetpassword = ""
            myuserinfo.save()
            if myuserinfo.state == "0":
                result = "success1"
            else:
                result = "success"
            auth.logout(request)
            user = auth.authenticate(username=myusername, password=password)
            if user is not None and user.is_active:
                auth.login(request, user)
                usertype = myuserinfo.type
                if usertype == '1':
                    request.session['ispuser'] = True
                else:
                    request.session['ispuser'] = False
                request.session['isadmin'] = alluser[0].is_superuser
        else:
            result = "用户不存在。"
        return HttpResponse(result)


def activate(request):
    if request.user.is_authenticated():
        myuser = request.user
        myuserinfo = myuser.userinfo
        if myuserinfo.state == "0":
            company = myuserinfo.company
            fullname = myuserinfo.fullname
            tell = myuserinfo.tell
            if not myuserinfo.company:
                company = ""
            if not myuserinfo.fullname:
                fullname = ""
            if not myuserinfo.tell:
                tell = ""
            return render(request, 'activate.html',
                          {"myusername": myuser.username, "fullname": fullname, "company": company, "tell": tell})
        else:
            return render(request, 'activate.html', {"error": True})
    else:
        return HttpResponseRedirect("/login")


def useractivate(request):
    if request.method == 'POST':
        result = ""
        myusername = request.POST.get('username', '')
        company = request.POST.get('company', '')
        fullname = request.POST.get('fullname', '')
        tell = request.POST.get('tell', '')
        password = request.POST.get('password', '')

        alluser = User.objects.filter(username=myusername)
        if (len(alluser) > 0):
            alluser[0].set_password(password)
            alluser[0].save()

            myuserinfo = alluser[0].userinfo
            myuserinfo.fullname = fullname
            myuserinfo.company = company
            myuserinfo.tell = tell
            myuserinfo.state = "1"
            myuserinfo.save()
            user = auth.authenticate(username=myusername, password=password)
            if user is not None and user.is_active:
                auth.login(request, user)
                usertype = myuserinfo.type
                if usertype == '1':
                    request.session['ispuser'] = True
                else:
                    request.session['ispuser'] = False
                request.session['isadmin'] = alluser[0].is_superuser
            result = "success"
        else:
            result = "用户不存在。"
        return HttpResponse(result)


def password(request):
    if request.user.is_authenticated():
        return render(request, 'password.html', {"myusername": request.user.username})
    else:
        return HttpResponseRedirect("/login")


def userpassword(request):
    if request.method == 'POST':
        result = ""
        username = request.POST.get('username', '')
        oldpassword = request.POST.get('oldpassword', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=oldpassword)
        if user is not None and user.is_active:
            alluser = User.objects.filter(username=username)
            if (len(alluser) > 0):
                alluser[0].set_password(password)
                alluser[0].save()
                myuserinfo = alluser[0].userinfo
                myuserinfo.forgetpassword = ""
                myuserinfo.save()
                result = "success"
                auth.logout(request)
                user = auth.authenticate(username=username, password=password)
                if user is not None and user.is_active:
                    auth.login(request, user)
                    usertype = myuserinfo.type
                    if usertype == '1':
                        request.session['ispuser'] = True
                    else:
                        request.session['ispuser'] = False
                    request.session['isadmin'] = alluser[0].is_superuser
            else:
                result = "用户异常，修改密码失败。"
        else:
            result = "旧密码输入错误，请重新输入。"

    return HttpResponse(result)


def useredit(request):
    if request.user.is_authenticated():
        myuser = request.user
        myuserinfo = myuser.userinfo
        email = myuser.email
        phone = myuserinfo.phone
        company = myuserinfo.company
        fullname = myuserinfo.fullname
        tell = myuserinfo.tell
        if not myuserinfo.company:
            company = ""
        if not myuserinfo.fullname:
            fullname = ""
        if not myuserinfo.tell:
            tell = ""
        return render(request, 'useredit.html',
                      {'username': request.user.userinfo.fullname, "edituserpage": True, "myusername": myuser.username,
                       "email": email, "phone": phone, "fullname": fullname, "company": company, "tell": tell})
    else:
        return HttpResponseRedirect("/login")


def usersave(request):
    if request.method == 'POST':
        result = ""
        myusername = request.POST.get('username', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        company = request.POST.get('company', '')
        fullname = request.POST.get('fullname', '')
        tell = request.POST.get('tell', '')

        alluser = User.objects.filter(username=myusername)
        if (len(alluser) > 0):
            alluser[0].email = email
            alluser[0].save()
            myuserinfo = alluser[0].userinfo
            myuserinfo.phone = phone
            myuserinfo.fullname = fullname
            myuserinfo.company = company
            myuserinfo.tell = tell
            myuserinfo.save()
            result = "保存成功。"
        else:
            result = "用户异常。"
        return HttpResponse(result)


def childuser(request):
    if request.user.is_authenticated() and request.session['ispuser']:
        return render(request, 'childuser.html', {'username': request.user.userinfo.fullname, "childuserpage": True})
    else:
        return HttpResponseRedirect("/login")


def childuserdata(request):
    if request.user.is_authenticated() and request.session['ispuser']:
        result = []
        myuser = request.user
        myuserinfo = myuser.userinfo
        alluserinfo = UserInfo.objects.filter(pnode=myuserinfo)
        if (len(alluserinfo) > 0):
            for userinfo in alluserinfo:
                user = userinfo.user
                if user.is_active == 1:
                    id = user.id
                    username = user.username
                    email = user.email
                    phone = userinfo.phone
                    company = userinfo.company
                    fullname = userinfo.fullname
                    tell = userinfo.tell
                    state = "未激活"
                    if userinfo.state == "1":
                        state = "已激活"
                    result.append({"id": id, "username": username, "email": email, "phone": phone, "company": company,
                                   "fullname": fullname, "tell": tell, "state": state})
        return HttpResponse(json.dumps({"data": result}))


def childusersave(request):
    if request.user.is_authenticated() and request.session['ispuser']:
        if request.method == 'POST':
            result = ""
            id = request.POST.get('id', '')
            myusername = request.POST.get('username', '')
            email = request.POST.get('email', '')
            phone = request.POST.get('phone', '')
            company = request.POST.get('company', '')
            fullname = request.POST.get('fullname', '')
            tell = request.POST.get('tell', '')
            try:
                id = int(id)
            except:
                raise Http404()
            if id == 0:
                alluser = User.objects.filter(username=myusername)
                if (len(alluser) > 0):
                    result = u"用户名" + myusername + u'已存在。'
                else:
                    alluser = User.objects.filter(email=email)
                    if (len(alluser) > 0):
                        result = u"邮箱" + email + u'已被注册。'
                    else:
                        newuser = User()
                        newuser.username = myusername
                        newuser.set_password("password")
                        newuser.email = email
                        newuser.save()
                        # 用户扩展信息 profile
                        profile = UserInfo()  # e*************************
                        profile.user_id = newuser.id
                        profile.userGUID = uuid.uuid1()
                        profile.pnode = request.user.userinfo
                        profile.phone = phone
                        profile.fullname = fullname
                        profile.company = company
                        profile.tell = tell
                        profile.type = "2"
                        profile.state = "0"
                        profile.save()
                        result = "保存成功。"
                        try:
                            subject = u'注册成功'
                            message = u'用户:' + myusername + u'您好。' \
                                      + "用户" + request.user.userinfo.fullname + u"\n已为您在云灾备系统成功分配账号，初始密码为password，点击链接进入登录页面:" \
                                      + u"http://127.0.0.1:8000/login/"
                            send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
                        except:
                            pass
            else:
                alluser = User.objects.filter(username=myusername)
                if (len(alluser) > 0):
                    alluser[0].email = email
                    alluser[0].save()
                    myuserinfo = alluser[0].userinfo
                    myuserinfo.phone = phone
                    myuserinfo.fullname = fullname
                    myuserinfo.company = company
                    myuserinfo.tell = tell
                    myuserinfo.save()
                    result = "保存成功。"
                else:
                    result = "用户异常。"
            return HttpResponse(result)


def childuserdel(request):
    if request.user.is_authenticated() and request.session['ispuser']:
        if 'id' in request.POST:
            id = request.POST.get('id', '')
            try:
                id = int(id)
            except:
                raise Http404()
            myuser = User.objects.get(id=id)
            myuser.is_active = 0
            myuser.save()
            return HttpResponse(1)
        else:
            return HttpResponse(0)


def resourcepool(request):
    if request.user.is_authenticated() and request.session['isadmin']:
        return render(request, 'resourcepool.html',
                      {'username': request.user.userinfo.fullname, "resourcepoolpage": True})
    else:
        return HttpResponseRedirect("/login")


def resourcepooldata(request):
    if request.user.is_authenticated() and request.session['isadmin']:
        result = []
        allresourcepool = ResourcePool.objects.exclude(state="9")
        if (len(allresourcepool) > 0):
            for resourcepool in allresourcepool:
                id = resourcepool.id
                name = resourcepool.name
                type = resourcepool.type
                supplier = resourcepool.supplier
                certificate = resourcepool.certificate
                description = resourcepool.description
                doc = parseString(certificate)

                ip = ""
                username = ""
                password = ""
                for node in doc.getElementsByTagName("CERT_LIST"):
                    for hostnode in node.getElementsByTagName("CERT"):
                        ip = hostnode.getAttribute("ip")
                        username = hostnode.getAttribute("username")
                        password = hostnode.getAttribute("password")
                        if type == '虚机资源':
                            datacenter = hostnode.getAttribute("datacenter")
                            cluster = hostnode.getAttribute("cluster")
                if type == '虚机资源':
                    result.append(
                        {"id": id, "name": name, "type": type, "supplier": supplier, "description": description,
                         "ip": ip, "username": username, "password": password, "cluster": cluster,
                         "datacenter": datacenter})
                else:
                    result.append(
                        {"id": id, "name": name, "type": type, "supplier": supplier, "description": description,
                         "ip": ip, "username": username, "password": password})
        return HttpResponse(json.dumps({"data": result}))


def getvendorlist(request):
    if request.user.is_authenticated() and request.session['isadmin']:
        if request.method == 'POST':
            result = []
            type = request.POST.get('type', '')
            vendorlist = Vendor.objects.exclude(status="9").filter(type=type)
            for vendor in vendorlist:
                result.append({"vendorGUID": vendor.vendorGUID, "name": vendor.name})

            return HttpResponse(json.dumps(result))


def resourcepoolsave(request):
    if request.user.is_authenticated() and request.session['ispuser']:
        if request.method == 'POST':
            result = ""
            id = request.POST.get('id', '')
            name = request.POST.get('name', '')
            type = request.POST.get('type', '')
            description = request.POST.get('description', '')
            supplier = request.POST.get('supplier', '')
            ip = request.POST.get('ip', '')
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')

            # 获取datacenter cluster
            datacenter = request.POST.get('datacenter', '')
            cluster = request.POST.get('cluster', '')

            try:
                id = int(id)
            except:
                raise Http404()
            if id == 0:  #
                allpool = ResourcePool.objects.filter(name=name)
                if (len(allpool) > 0):
                    result = u"资源池名称" + name + u'已存在。'
                else:
                    newpool = ResourcePool()
                    newpool.name = name
                    newpool.type = type
                    newpool.description = description
                    newpool.supplier = supplier

                    impl = xml.dom.minidom.getDOMImplementation()
                    dom = impl.createDocument(None, 'CERT_LIST', None)
                    root = dom.documentElement
                    nameE = dom.createElement('CERT')

                    nameE.setAttribute("ip", ip)  # 增加属性
                    nameE.setAttribute("username", username)  # 增加属性
                    nameE.setAttribute("password", password)  # 增加属性

                    if type == '虚机资源':
                        newpool.datacenter = datacenter
                        newpool.cluster = cluster
                        nameE.setAttribute("datacenter", datacenter)
                        nameE.setAttribute("cluster", cluster)

                    root.appendChild(nameE)
                    newpool.certificate = dom.toxml()

                    newpool.creatdate = datetime.datetime.now()
                    newpool.updatedate = datetime.datetime.now()
                    newpool.state = "0"
                    newpool.save()
                    result = "保存成功。"
            else:
                allpool = ResourcePool.objects.filter(id=id)
                if (len(allpool) > 0):
                    allpool1 = ResourcePool.objects.filter(name=name).exclude(id=id)
                    if (len(allpool1) > 0):
                        result = u"资源池名称" + name + u'已存在。'
                    else:
                        newpool = allpool[0]
                        newpool.name = name
                        newpool.type = type
                        newpool.description = description
                        newpool.supplier = supplier
                        impl = xml.dom.minidom.getDOMImplementation()
                        dom = impl.createDocument(None, 'CERT_LIST', None)
                        root = dom.documentElement
                        nameE = dom.createElement('CERT')
                        nameE.setAttribute("ip", ip)  # 增加属性
                        nameE.setAttribute("username", username)  # 增加属性
                        nameE.setAttribute("password", password)  # 增加属性
                        if type == '虚机资源':
                            newpool.datacenter = datacenter
                            newpool.cluster = cluster
                            nameE.setAttribute("datacenter", datacenter)
                            nameE.setAttribute("cluster", cluster)

                        root.appendChild(nameE)
                        newpool.certificate = dom.toxml()
                        newpool.updatedate = datetime.datetime.now()
                        newpool.save()
                        result = "保存成功。"
                else:
                    result = "数据异常。"
            return HttpResponse(result)


def resourcepooldel(request):
    if request.user.is_authenticated() and request.session['isadmin']:
        if 'id' in request.POST:
            id = request.POST.get('id', '')
            try:
                id = int(id)
            except:
                raise Http404()
            mypoll = ResourcePool.objects.get(id=id)
            mypoll.name = mypoll.name + u"(已删除)"
            mypoll.state = "9"
            mypoll.save()
            return HttpResponse(1)
        else:
            return HttpResponse(0)


def computerresource(request):
    if request.user.is_authenticated() and request.session['isadmin']:
        return render(request, 'computerresource.html',
                      {'username': request.user.userinfo.fullname, "computerresourcepage": True})
    else:
        return HttpResponseRedirect("/login")


def computerresourcedata(request):
    if request.user.is_authenticated() and request.session['isadmin']:
        result = []
        allresource = ComputerResource.objects.exclude(state="9")
        if (len(allresource) > 0):
            for resource in allresource:
                id = resource.id
                name = resource.name
                poolid = resource.pool.id
                poolname = resource.pool.name
                certificate = resource.certificate
                specifications = resource.specifications
                description = resource.description
                state = "空闲"
                if resource.state == "1":
                    state = "已使用"
                doc = parseString(certificate)
                ip = ""
                username = ""
                password = ""
                for node in doc.getElementsByTagName("CERT_LIST"):
                    for hostnode in node.getElementsByTagName("CERT"):
                        ip = hostnode.getAttribute("ip")
                        username = hostnode.getAttribute("username")
                        password = hostnode.getAttribute("password")

                doc2 = parseString(specifications)
                disks = []
                for node in doc2.getElementsByTagName("SPEC_LIST"):
                    cpu = node.getAttribute("cpu")
                    memory = node.getAttribute("memory")
                    for hostnode in node.getElementsByTagName("DISK"):
                        disk_size = hostnode.getAttribute("size")
                        disk_name = hostnode.getAttribute("name")
                        disk_type = hostnode.getAttribute("type")
                        disks.append({"size": disk_size, "name": disk_name, "type": disk_type})
                result.append(
                    {"id": id, "name": name, "poolid": poolid, "poolname": poolname, "description": description,
                     "state": state, "ip": ip, "username": username, "password": password, "cpu": cpu, "memory": memory,
                     "disks": disks})
        return HttpResponse(json.dumps({"data": result}))


def computerresourcepooldata(request):
    if request.user.is_authenticated() and request.session['isadmin']:
        result = []
        allresourcepool = ResourcePool.objects.exclude(state="9").filter(type="主机资源")
        if (len(allresourcepool) > 0):
            for resourcepool in allresourcepool:
                id = resourcepool.id
                name = resourcepool.name
                type = resourcepool.type
                supplier = resourcepool.supplier
                certificate = resourcepool.certificate
                description = resourcepool.description
                doc = parseString(certificate)
                ip = ""
                username = ""
                password = ""
                for node in doc.getElementsByTagName("CERT_LIST"):
                    for hostnode in node.getElementsByTagName("CERT"):
                        ip = hostnode.getAttribute("ip")
                        username = hostnode.getAttribute("username")
                        password = hostnode.getAttribute("password")
                result.append({"id": id, "name": name, "type": type, "supplier": supplier, "description": description,
                               "ip": ip, "username": username, "password": password})
        return HttpResponse(json.dumps({"data": result}))


def computerresourcepooldatafordrill(request):
    if request.user.is_authenticated() and request.session['isadmin']:
        result = []
        allresourcepool = ResourcePool.objects.exclude(state="9").filter(type="主机资源")
        if (len(allresourcepool) > 0):
            for i in range(0, len(allresourcepool)):
                myresource = []
                id = allresourcepool[i].id
                name = allresourcepool[i].name
                if i == 0:
                    allresource = ComputerResource.objects.exclude(state="9").filter(pool_id=id)
                    if (len(allresource) > 0):
                        for resource in allresource:
                            resourceid = resource.id
                            resourcename = resource.name
                            myresource.append({"id": resourceid, "name": resourcename})

                result.append({"id": id, "name": name, "myresource": myresource})
        return HttpResponse(json.dumps({"data": result}))


def computerresourcedatafordrill(request):
    if request.user.is_authenticated():
        result = []
        id = request.POST.get('id', '')
        allresource = ComputerResource.objects.exclude(state="9").filter(pool_id=id)
        if (len(allresource) > 0):
            for resource in allresource:
                resourceid = resource.id
                resourcename = resource.name
                result.append({"id": resourceid, "name": resourcename})
        return HttpResponse(json.dumps({"data": result}))


def computerresourcesave(request):
    if request.user.is_authenticated() and request.session['ispuser']:
        if request.method == 'POST':
            result = ""
            id = request.POST.get('id', '')
            name = request.POST.get('name', '')
            poolid = request.POST.get('poolid', '')
            description = request.POST.get('description', '')

            ip = request.POST.get('ip', '')
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')

            cpu = request.POST.get('cpu', '')
            memory = request.POST.get('memory', '')

            disk1_size = request.POST.get('disk1_size', '')
            disk2_size = request.POST.get('disk2_size', '')
            disk3_size = request.POST.get('disk3_size', '')
            disk4_size = request.POST.get('disk4_size', '')
            disk5_size = request.POST.get('disk5_size', '')
            disk6_size = request.POST.get('disk6_size', '')

            disk1_name = request.POST.get('disk1_name', '')
            disk2_name = request.POST.get('disk2_name', '')
            disk3_name = request.POST.get('disk3_name', '')
            disk4_name = request.POST.get('disk4_name', '')
            disk5_name = request.POST.get('disk5_name', '')
            disk6_name = request.POST.get('disk6_name', '')

            disk1_type = request.POST.get('disk1_type', '')
            disk2_type = request.POST.get('disk2_type', '')
            disk3_type = request.POST.get('disk3_type', '')
            disk4_type = request.POST.get('disk4_type', '')
            disk5_type = request.POST.get('disk5_type', '')
            disk6_type = request.POST.get('disk6_type', '')

            try:
                id = int(id)
            except:
                raise Http404()
            try:
                poolid = int(poolid)
            except:
                raise Http404()
            if id == 0:
                allresource = ComputerResource.objects.filter(name=name)
                if (len(allresource) > 0):
                    result = u"主机资源名称" + name + u'已存在。'
                else:
                    resource = ComputerResource()
                    resource.name = name
                    mypoll = ResourcePool.objects.get(id=poolid)
                    resource.pool = mypoll
                    resource.description = description

                    impl = xml.dom.minidom.getDOMImplementation()
                    dom = impl.createDocument(None, 'CERT_LIST', None)
                    root = dom.documentElement
                    nameE = dom.createElement('CERT')
                    nameE.setAttribute("ip", ip)  # 增加属性
                    nameE.setAttribute("username", username)  # 增加属性
                    nameE.setAttribute("password", password)  # 增加属性
                    root.appendChild(nameE)
                    resource.certificate = dom.toxml()

                    dom1 = impl.createDocument(None, 'SPEC_LIST', None)
                    root = dom1.documentElement
                    root.setAttribute("cpu", cpu)
                    root.setAttribute("memory", memory)
                    if not disk1_size == '':
                        nameE = dom.createElement('DISK')
                        nameE.setAttribute("size", disk1_size)  # 增加属性
                        nameE.setAttribute("name", disk1_name)  # 增加属性
                        nameE.setAttribute("type", disk1_type)  # 增加属性
                        root.appendChild(nameE)
                    if not disk2_size == '':
                        nameE = dom.createElement('DISK')
                        nameE.setAttribute("size", disk2_size)  # 增加属性
                        nameE.setAttribute("name", disk2_name)  # 增加属性
                        nameE.setAttribute("type", disk2_type)  # 增加属性
                        root.appendChild(nameE)
                    if not disk3_size == '':
                        nameE = dom.createElement('DISK')
                        nameE.setAttribute("size", disk3_size)  # 增加属性
                        nameE.setAttribute("name", disk3_name)  # 增加属性
                        nameE.setAttribute("type", disk3_type)  # 增加属性
                        root.appendChild(nameE)
                    if not disk4_size == '':
                        nameE = dom.createElement('DISK')
                        nameE.setAttribute("size", disk4_size)  # 增加属性
                        nameE.setAttribute("name", disk4_name)  # 增加属性
                        nameE.setAttribute("type", disk4_type)  # 增加属性
                        root.appendChild(nameE)
                    if not disk5_size == '':
                        nameE = dom.createElement('DISK')
                        nameE.setAttribute("size", disk5_size)  # 增加属性
                        nameE.setAttribute("name", disk5_name)  # 增加属性
                        nameE.setAttribute("type", disk5_type)  # 增加属性
                        root.appendChild(nameE)
                    if not disk6_size == '':
                        nameE = dom.createElement('DISK')
                        nameE.setAttribute("size", disk6_size)  # 增加属性
                        nameE.setAttribute("name", disk6_name)  # 增加属性
                        nameE.setAttribute("type", disk6_type)  # 增加属性
                        root.appendChild(nameE)
                    resource.specifications = dom1.toxml()

                    resource.state = "0"
                    resource.creatdate = datetime.datetime.now()
                    resource.updatedate = datetime.datetime.now()
                    resource.save()
                    result = "保存成功。"
            else:
                allresource = ComputerResource.objects.filter(id=id)
                if (len(allresource) > 0):
                    allresource1 = ComputerResource.objects.filter(name=name).exclude(id=id)
                    if (len(allresource1) > 0):
                        result = u"主机资源名称" + name + u'已存在。'
                    else:
                        resource = allresource[0]
                        resource.name = name
                        mypoll = ResourcePool.objects.get(id=poolid)
                        resource.pool = mypoll
                        resource.description = description

                        impl = xml.dom.minidom.getDOMImplementation()
                        dom = impl.createDocument(None, 'CERT_LIST', None)
                        root = dom.documentElement
                        nameE = dom.createElement('CERT')
                        nameE.setAttribute("ip", ip)  # 增加属性
                        nameE.setAttribute("username", username)  # 增加属性
                        nameE.setAttribute("password", password)  # 增加属性
                        root.appendChild(nameE)
                        resource.certificate = dom.toxml()

                        dom1 = impl.createDocument(None, 'SPEC_LIST', None)
                        root = dom1.documentElement
                        root.setAttribute("cpu", cpu)
                        root.setAttribute("memory", memory)

                        if not disk1_size == '':
                            nameE = dom.createElement('DISK')
                            nameE.setAttribute("size", disk1_size)  # 增加属性
                            nameE.setAttribute("name", disk1_name)  # 增加属性
                            nameE.setAttribute("type", disk1_type)  # 增加属性
                            root.appendChild(nameE)
                        if not disk2_size == '':
                            nameE = dom.createElement('DISK')
                            nameE.setAttribute("size", disk2_size)  # 增加属性
                            nameE.setAttribute("name", disk2_name)  # 增加属性
                            nameE.setAttribute("type", disk2_type)  # 增加属性
                            root.appendChild(nameE)
                        if not disk3_size == '':
                            nameE = dom.createElement('DISK')
                            nameE.setAttribute("size", disk3_size)  # 增加属性
                            nameE.setAttribute("name", disk3_name)  # 增加属性
                            nameE.setAttribute("type", disk3_type)  # 增加属性
                            root.appendChild(nameE)
                        if not disk4_size == '':
                            nameE = dom.createElement('DISK')
                            nameE.setAttribute("size", disk4_size)  # 增加属性
                            nameE.setAttribute("name", disk4_name)  # 增加属性
                            nameE.setAttribute("type", disk4_type)  # 增加属性
                            root.appendChild(nameE)
                        if not disk5_size == '':
                            nameE = dom.createElement('DISK')
                            nameE.setAttribute("size", disk5_size)  # 增加属性
                            nameE.setAttribute("name", disk5_name)  # 增加属性
                            nameE.setAttribute("type", disk5_type)  # 增加属性
                            root.appendChild(nameE)
                        if not disk6_size == '':
                            nameE = dom.createElement('DISK')
                            nameE.setAttribute("size", disk6_size)  # 增加属性
                            nameE.setAttribute("name", disk6_name)  # 增加属性
                            nameE.setAttribute("type", disk6_type)  # 增加属性
                            root.appendChild(nameE)
                        resource.specifications = dom1.toxml()

                        resource.updatedate = datetime.datetime.now()
                        resource.save()
                        result = "保存成功。"
                else:
                    result = "数据异常。"
            return HttpResponse(result)


def computerresourcedel(request):
    if request.user.is_authenticated() and request.session['isadmin']:
        if 'id' in request.POST:
            id = request.POST.get('id', '')
            try:
                id = int(id)
            except:
                raise Http404()
            myresource = ComputerResource.objects.get(id=id)
            myresource.name = myresource.name + u"(已删除)"
            myresource.state = "9"
            myresource.save()
            return HttpResponse(1)
        else:
            return HttpResponse(0)


def vmresource(request):
    if request.user.is_authenticated() and request.session['isadmin']:
        return render(request, 'vmresource.html', {'username': request.user.userinfo.fullname, "vmresourcepage": True})
    else:
        return HttpResponseRedirect("/login")


def getvmresourcelist(request):
    if request.user.is_authenticated() and request.session['isadmin']:
        allresource = VmResource.objects.exclude(state="9")
        result = []
        pool_id = request.POST.get("pool_id", '')
        resourcepool = ResourcePool.objects.filter(id=pool_id)[0]
        certificate = resourcepool.certificate
        # 从资源池中获取certificate,并获取ip,user,password
        doc = parseString(certificate)
        ip = ""
        username = ""
        password = ""
        for node in doc.getElementsByTagName("CERT_LIST"):
            for hostnode in node.getElementsByTagName("CERT"):
                ip = hostnode.getAttribute("ip")
                username = hostnode.getAttribute("username")
                password = hostnode.getAttribute("password")
                datacenter = hostnode.getAttribute("datacenter")
                cluster = hostnode.getAttribute("cluster")

        vm_api = VM_API(ip, username, password)
        vmlist = vm_api.getvmlist(datacenter, cluster)

        for num, vm in enumerate(vmlist):
            vm_info_dict = {
                "id": num,
                "vm_name": vm['vmname'],
                "cpu": vm['cpu'],
                "memory": vm['memory'],
                "disk": vm['capacity'],
                "uuid": vm['uuid'],
            }

            result.append(vm_info_dict)
        return HttpResponse(json.dumps({"data": result}))


def vmresourcedata(request):
    if request.user.is_authenticated() and request.session['isadmin']:
        result = []
        allresource = VmResource.objects.exclude(state="9").filter(vm_type='模板虚机')
        if (len(allresource) > 0):
            for resource in allresource:
                id = resource.id
                name = resource.name
                pool_id = resource.pool_id
                specifications = resource.specifications
                description = resource.description
                template_name = resource.template_name  # ...对应的name
                system = resource.system
                uuid = resource.uuid

                vmlist = VmResource.objects.exclude(state="9").exclude(vm_type='模板虚机').filter(template_id=id)
                vm_num = len(vmlist)

                resourcepool = ResourcePool.objects.filter(id=pool_id)[0]
                certificate = resourcepool.certificate
                pool_name = resourcepool.name
                # 从资源池中获取certificate,并获取ip,user,password

                doc = parseString(certificate)
                ip = ""
                username = ""
                password = ""
                cert_name = ""
                for node in doc.getElementsByTagName("CERT_LIST"):
                    for hostnode in node.getElementsByTagName("CERT"):
                        ip = hostnode.getAttribute("ip")
                        username = hostnode.getAttribute("username")
                        password = hostnode.getAttribute("password")
                        datacenter = hostnode.getAttribute("datacenter")
                        cluster = hostnode.getAttribute("cluster")

                vm_api = VM_API(ip, username, password)
                vmlist = vm_api.getvmlist(datacenter, cluster, None, name)
                state_tag = """<i class="fa fa-stop fa-2x" style="color:#ff0000;font-size:25px" title="已停止"></i>"""
                for num, vm in enumerate(vmlist):
                    if vm['vmname'] == name:
                        state = vm["state"]
                        if state == "poweredOn":
                            state_tag = """<i class="fa fa-play fa-2" style="color:#00CC00;font-size:25px" title="运行中"></i>"""
                        else:
                            state_tag = """<i class="fa fa-stop fa-2" style="color:#ff0000;font-size:25px" title="已停止"></i>"""

                doc2 = parseString(specifications)
                for node in doc2.getElementsByTagName("SPEC_LIST"):
                    cpu = node.getAttribute("cpu")
                    memory = node.getAttribute("memory")
                    disk = node.getAttribute("disk")

                result.append(
                    {"id": id, "name": name, "description": description,
                     "cpu": cpu, "memory": memory,
                     "disks": disk, "template_name": template_name, "vm_num": vm_num, "state_tag": state_tag,
                     "system": system, "pool_id": pool_id, "pool_name": pool_name, "uuid": uuid})
        return HttpResponse(json.dumps({"data": result}))


def vmresourcepooldata(request):
    if request.user.is_authenticated() and request.session['isadmin']:
        result = []
        allresourcepool = ResourcePool.objects.filter(type="虚机资源").exclude(state=9)
        if (len(allresourcepool) > 0):
            for resourcepool in allresourcepool:
                id = resourcepool.id
                name = resourcepool.name
                type = resourcepool.type
                supplier = resourcepool.supplier
                certificate = resourcepool.certificate
                description = resourcepool.description
                doc = parseString(certificate)
                ip = ""
                username = ""
                password = ""
                for node in doc.getElementsByTagName("CERT_LIST"):
                    for hostnode in node.getElementsByTagName("CERT"):
                        ip = hostnode.getAttribute("ip")
                        username = hostnode.getAttribute("username")
                        password = hostnode.getAttribute("password")
                result.append({"id": id, "name": name, "type": type, "supplier": supplier, "description": description,
                               "ip": ip, "username": username, "password": password})

        return HttpResponse(json.dumps({"data": result}))


def vmresourcepooldatafordrill(request):
    if request.user.is_authenticated() and request.session['isadmin']:
        result = []
        allresourcepool = ResourcePool.objects.exclude(state="9").filter(type="虚机资源")
        if (len(allresourcepool) > 0):
            for i in range(0, len(allresourcepool)):
                myresource = []
                id = allresourcepool[i].id
                name = allresourcepool[i].name
                if i == 0:
                    allresource = VmResource.objects.exclude(state="9").filter(pool_id=id)
                    if (len(allresource) > 0):
                        for resource in allresource:
                            resourceid = resource.id
                            resourcename = resource.name
                            myresource.append({"id": resourceid, "name": resourcename})

                result.append({"id": id, "name": name, "myresource": myresource})
        return HttpResponse(json.dumps({"data": result}))


def vmresourcedatafordrill(request):
    if request.user.is_authenticated():
        result = []
        # id = request.POST.get('id', '')
        allresource = VmResource.objects.exclude(state="9")
        if (len(allresource) > 0):
            for resource in allresource:
                resourceid = resource.id
                resourcename = resource.name
                result.append({"id": resourceid, "name": resourcename})
        return HttpResponse(json.dumps({"data": result}))


def vmresourcesave(request):
    if request.user.is_authenticated() and request.session['ispuser']:
        if request.method == 'POST':
            result = ""
            # clone param
            datacenter = request.POST.get('datacenter', '')
            cluster = request.POST.get('cluster', '')
            instancename = request.POST.get('instancename', '')
            currentvm = request.POST.get('currentvm', '')
            clone_tag = request.POST.get('clone_tag', '')
            template_id = request.POST.get('template_id', '')

            id = request.POST.get('id', '')
            if clone_tag:
                vm_name = request.POST.get('currentvm', '')
            else:
                vm_name = request.POST.get('name', '')
            pool_id = request.POST.get('poolid', '')

            cpu = request.POST.get('cpu', '')
            memory = request.POST.get('memory', '')
            disk = request.POST.get('disk', '')

            template = request.POST.get('template', '')
            description = request.POST.get('description', '')
            system = request.POST.get('system')

            uuid = request.POST.get('uuid')

            try:
                id = int(id)
            except:
                raise Http404()

            if id == 0:
                allresource = VmResource.objects.filter(name=vm_name)
                if (len(allresource) > 0):
                    result = u"虚机资源名称" + vm_name + u'已存在。'
                else:
                    resource = VmResource()
                    resource.description = description

                    resource.pool_id = pool_id

                    if clone_tag:
                        resource.template_name = instancename
                        resource.vm_type = "克隆虚机"
                        resource.name = currentvm
                        resource.template_id = template_id
                    else:
                        resource.template_name = template
                        resource.vm_type = "模板虚机"
                        resource.name = vm_name
                    resource.system = system
                    resource.uuid = uuid

                    impl = xml.dom.minidom.getDOMImplementation()
                    dom1 = impl.createDocument(None, 'SPEC_LIST', None)
                    root = dom1.documentElement
                    root.setAttribute("cpu", cpu)
                    root.setAttribute("memory", memory)
                    root.setAttribute("disk", disk)
                    root.setAttribute("datacenter", datacenter)
                    root.setAttribute("cluster", cluster)

                    resource.specifications = dom1.toxml()

                    resource.state = "0"
                    resource.creatdate = datetime.datetime.now()
                    resource.updatedate = datetime.datetime.now()

                    resource.save()
                    result = "保存成功。"

            else:
                allresource = VmResource.objects.filter(id=id)
                if (len(allresource) > 0):
                    allresource1 = VmResource.objects.filter(name=vm_name).exclude(id=id)
                    if (len(allresource1) > 0):
                        result = u"虚机资源名称" + vm_name + u'已存在。'
                    else:
                        resource = allresource[0]
                        resource.name = vm_name
                        resource.template_name = template
                        resource.system = system
                        resource.uuid = uuid
                        resource.pool_id = pool_id
                        resource.description = description

                        impl = xml.dom.minidom.getDOMImplementation()
                        dom1 = impl.createDocument(None, 'SPEC_LIST', None)
                        root = dom1.documentElement
                        root.setAttribute("cpu", cpu)
                        root.setAttribute("memory", memory)
                        root.setAttribute("disk", disk)

                        resource.specifications = dom1.toxml()

                        resource.updatedate = datetime.datetime.now()
                        resource.save()
                        result = "保存成功。"
                else:
                    result = "数据异常。"
            return HttpResponse(result)


def vmresourcedel(request):
    if request.user.is_authenticated() and request.session['isadmin']:
        if 'id' in request.POST:
            id = request.POST.get('id', '')
            try:
                id = int(id)
            except:
                raise Http404()
            myresource = VmResource.objects.get(id=id)
            myresource.name = myresource.name + u"(已删除)"
            myresource.state = "9"
            myresource.save()
            return HttpResponse(1)
        else:
            return HttpResponse(0)


def vmlistmanage(request):
    if request.user.is_authenticated() and request.session['ispuser']:
        return render(request, 'vmlistmanage.html',
                      {'username': request.user.userinfo.fullname, "vmlistmanagepage": True})


def vmlistmanagedata(request):
    if request.user.is_authenticated() and request.session['isadmin']:
        result = []
        allresource = VmResource.objects.exclude(state="9").exclude(vm_type='模板虚机')
        if (len(allresource) > 0):
            for resource in allresource:
                id = resource.id
                name = resource.name
                pool_id = resource.pool_id
                specifications = resource.specifications
                description = resource.description
                instance_name = resource.template_name  # ...对应的name
                system = resource.system
                template_id = resource.template_id
                template_name = resource.template.name
                template_template_name = resource.template.template_name
                template_uuid = resource.template.uuid
                uuid = resource.uuid

                resourcepool = ResourcePool.objects.filter(id=pool_id)[0]
                certificate = resourcepool.certificate
                pool_name = resourcepool.name
                # 从资源池中获取certificate,并获取ip,user,password

                doc = parseString(certificate)
                ip = ""
                username = ""
                password = ""
                cert_name = ""
                for node in doc.getElementsByTagName("CERT_LIST"):
                    for hostnode in node.getElementsByTagName("CERT"):
                        ip = hostnode.getAttribute("ip")
                        username = hostnode.getAttribute("username")
                        password = hostnode.getAttribute("password")
                        datacenter = hostnode.getAttribute("datacenter")
                        cluster = hostnode.getAttribute("cluster")

                vm_api = VM_API(ip, username, password)
                vmlist = vm_api.getvmlist(datacenter, cluster, None, name)
                state_tag = """<i class="fa fa-stop fa-2x" style="color:#ff0000;font-size:25px" title="已停止"></i>"""
                for num, vm in enumerate(vmlist):
                    if vm['vmname'] == name:
                        state = vm["state"]
                        if state == "poweredOn":
                            state_tag = """<i class="fa fa-play fa-2" style="color:#00CC00;font-size:25px" title="运行中"></i>"""
                        else:
                            state_tag = """<i class="fa fa-stop fa-2x" style="color:#ff0000;font-size:25px" title="已停止"></i>"""

                doc2 = parseString(specifications)
                for node in doc2.getElementsByTagName("SPEC_LIST"):
                    cpu = node.getAttribute("cpu")
                    memory = node.getAttribute("memory")
                    disk = node.getAttribute("disk")
                    vmip = node.getAttribute("vmip")
                    hostname = node.getAttribute("hostname")
                    clone = node.getAttribute("clone")

                result.append(
                    {"id": id, "name": name, "description": description,
                     "cpu": cpu, "memory": memory, "datacenter": datacenter, "cluster": cluster, "ip": vmip,
                     "hostname": hostname,
                     "disks": disk, "instance_name": instance_name, "template_id": template_id, "clone": clone,
                     "template_name": template_name, "template_template_name": template_template_name,
                     "template_uuid": template_uuid, "state_tag": state_tag, "system": system, "pool_id": pool_id,
                     "pool_name": pool_name, "uuid": uuid})
        return HttpResponse(json.dumps({"data": result}))


def getvmtemplate(request):
    if request.user.is_authenticated() and request.session['isadmin']:
        id = request.POST.get('id', '')
        if id != "0":
            result = []
            allresource = VmResource.objects.exclude(state="9").filter(vm_type='模板虚机')
            if (len(allresource) > 0):
                for resource in allresource:
                    id = resource.id
                    name = resource.name
                    pool_id = resource.pool_id
                    specifications = resource.specifications
                    description = resource.description
                    template_name = resource.template_name  # ...对应的name
                    system = resource.system
                    uuid = resource.uuid

                    resourcepool = ResourcePool.objects.filter(id=pool_id)[0]
                    certificate = resourcepool.certificate
                    pool_name = resourcepool.name

                    doc1 = parseString(certificate)
                    for node in doc1.getElementsByTagName("CERT_LIST"):
                        for hostnode in node.getElementsByTagName("CERT"):
                            datacenter = hostnode.getAttribute("datacenter")
                            cluster = hostnode.getAttribute("cluster")

                    doc2 = parseString(specifications)
                    for node in doc2.getElementsByTagName("SPEC_LIST"):
                        cpu = node.getAttribute("cpu")
                        memory = node.getAttribute("memory")
                        disk = node.getAttribute("disk")

                    result.append(
                        {"id": id, "name": name, "description": description,
                         "cpu": cpu, "memory": memory, "system": system,
                         "disks": disk, "template_name": template_name, "system": system, "pool_id": pool_id,
                         "pool_name": pool_name, "uuid": uuid, "datacenter": datacenter, "cluster": cluster})
        else:
            result = []
            template_name = request.POST.get("template_name", "")
            resource = VmResource.objects.exclude(state="9").filter(vm_type='模板虚机').filter(template_name=template_name)[
                0]
            id = resource.id
            name = resource.name
            specifications = resource.specifications
            description = resource.description
            template_name = resource.template_name  # ...对应的name
            system = resource.system
            uuid = resource.uuid
            pool_id = resource.pool_id
            resourcepool = ResourcePool.objects.filter(id=pool_id)[0]
            certificate = resourcepool.certificate

            doc1 = parseString(certificate)
            for node in doc1.getElementsByTagName("CERT_LIST"):
                for hostnode in node.getElementsByTagName("CERT"):
                    datacenter = hostnode.getAttribute("datacenter")
                    cluster = hostnode.getAttribute("cluster")

            doc2 = parseString(specifications)
            for node in doc2.getElementsByTagName("SPEC_LIST"):
                cpu = node.getAttribute("cpu")
                memory = node.getAttribute("memory")
                disk = node.getAttribute("disk")

            result.append({"id": id, "name": name, "description": description,
                           "cpu": cpu, "memory": memory,
                           "disks": disk, "template_name": template_name, "system": system,
                           "uuid": uuid, "pool_id": pool_id, "datacenter": datacenter, "cluster": cluster})
        return HttpResponse(json.dumps({"data": result}))


def get_dc(request):
    if request.user.is_authenticated() and request.session['isadmin']:
        pool_id = request.POST.get("poolid", "")
        clusterlist = []
        if pool_id:
            resourcepool = ResourcePool.objects.filter(id=pool_id)[0]
            certificate = resourcepool.certificate
            doc = parseString(certificate)
            ip = ""
            username = ""
            password = ""
            for node in doc.getElementsByTagName("CERT_LIST"):
                for hostnode in node.getElementsByTagName("CERT"):
                    ip = hostnode.getAttribute("ip")
                    username = hostnode.getAttribute("username")
                    password = hostnode.getAttribute("password")
            vm_api = VM_API(ip, username, password)
            clusterlist = vm_api.getdatacenterlist()
        return JsonResponse({"data": clusterlist})


def get_cluster(request):
    if request.user.is_authenticated() and request.session['isadmin']:
        clusterlist = []
        pool_id = request.POST.get("poolid", "")
        datacenter = request.POST.get("datacenter", "")
        if pool_id:
            resourcepool = ResourcePool.objects.filter(id=pool_id)[0]
            certificate = resourcepool.certificate
            doc = parseString(certificate)
            ip = ""
            username = ""
            password = ""
            for node in doc.getElementsByTagName("CERT_LIST"):
                for hostnode in node.getElementsByTagName("CERT"):
                    ip = hostnode.getAttribute("ip")
                    username = hostnode.getAttribute("username")
                    password = hostnode.getAttribute("password")
            vm_api = VM_API(ip, username, password)
            clusterlist = vm_api.getclusterlist(datacenter)
        return JsonResponse({"data": clusterlist})


def clonevm(request):
    if request.user.is_authenticated() and request.session['ispuser']:
        if request.method == 'POST':
            result = {}
            # clone param
            datacenter = request.POST.get('datacenter', '')
            cluster = request.POST.get('cluster', '')
            instancename = request.POST.get('instancename', '')
            currentvm = request.POST.get('currentvm', '')
            template_id = request.POST.get('template_id', '')

            id = request.POST.get('id', '')
            vm_name = request.POST.get('currentvm', '')
            name = request.POST.get('name', '')
            pool_id = request.POST.get('poolid', '')

            cpu = request.POST.get('cpu', '')
            memory = request.POST.get('memory', '')
            disk = request.POST.get('disk', '')
            description = request.POST.get('description', '')
            system = request.POST.get('system')

            try:
                id = int(id)
            except:
                raise Http404()

            resourcepool = ResourcePool.objects.filter(id=pool_id)[0]
            certificate = resourcepool.certificate
            doc = parseString(certificate)
            ip = ""
            username = ""
            password = ""
            for node in doc.getElementsByTagName("CERT_LIST"):
                for hostnode in node.getElementsByTagName("CERT"):
                    ip = hostnode.getAttribute("ip")
                    username = hostnode.getAttribute("username")
                    password = hostnode.getAttribute("password")
            vm_api = VM_API(ip, username, password)
            task = vm_api.clone_vm(name, vm_name, datacenter, cluster)
            if task:

                if id == 0:
                    allresource = VmResource.objects.filter(name=vm_name)
                    if (len(allresource) > 0):
                        result = u"新虚机名称" + vm_name + u'已存在。'
                    else:
                        resource = VmResource()
                        resource.description = description

                        resource.pool_id = pool_id
                        resource.template_name = instancename
                        resource.vm_type = "实例虚机"
                        resource.name = currentvm
                        resource.template_id = template_id
                        resource.system = system

                        impl = xml.dom.minidom.getDOMImplementation()
                        dom1 = impl.createDocument(None, 'SPEC_LIST', None)
                        root = dom1.documentElement
                        root.setAttribute("cpu", cpu)
                        root.setAttribute("memory", memory)
                        root.setAttribute("disk", disk)
                        root.setAttribute("datacenter", datacenter)
                        root.setAttribute("cluster", cluster)
                        root.setAttribute("clone", "0")
                        root.setAttribute("clonetaskid", task.info.key)

                        resource.specifications = dom1.toxml()

                        resource.state = "0"
                        resource.creatdate = datetime.datetime.now()
                        resource.updatedate = datetime.datetime.now()

                        resource.save()
                        result = {"value": "1", "id": resource.id, "text": u"克隆启动成功。"}
                else:
                    result = {"value": "0", "text": u"克隆失败。"}
            else:
                result = {"value": "0", "text": u"克隆失败。"}
            return HttpResponse(json.dumps(result))


def get_progress(request):
    if request.user.is_authenticated() and request.session['isadmin']:
        pool_id = request.POST.get("poolid", "")
        template_name = request.POST.get("name", "")
        id = request.POST.get("id", "")
        name = request.POST.get('currentvm', '')
        try:
            id = int(id)
        except:
            raise Http404()
        if pool_id:
            resourcepool = ResourcePool.objects.filter(id=pool_id)[0]
            certificate = resourcepool.certificate
            doc = parseString(certificate)
            ip = ""
            username = ""
            password = ""
            for node in doc.getElementsByTagName("CERT_LIST"):
                for hostnode in node.getElementsByTagName("CERT"):
                    ip = hostnode.getAttribute("ip")
                    username = hostnode.getAttribute("username")
                    password = hostnode.getAttribute("password")
                    datacenter = hostnode.getAttribute("datacenter")
                    cluster = hostnode.getAttribute("cluster")
            vm_api = VM_API(ip, username, password)
            vmlist = vm_api.getvmlist(datacenter, cluster, None, template_name)
            progress = "0"
            state = "2"
            uuid = ""
            finished = True
            if len(vmlist) > 0:
                vm = vmlist[0]
                for task in vm["task"]:
                    if task["descriptionId"] == "VirtualMachine.clone":
                        resource = VmResource.objects.filter(id=id)
                        if (len(resource) > 0):

                            specifications = resource[0].specifications

                            doc2 = parseString(specifications)
                            for node in doc2.getElementsByTagName("SPEC_LIST"):
                                clonetaskid = node.getAttribute("clonetaskid")

                                if clonetaskid == task["key"] and task["state"] != "success":
                                    progress = task["progress"]
                                    finished = False
            if finished:
                state = "3"
                resource = VmResource.objects.filter(id=id)
                if (len(resource) > 0):
                    specifications = resource[0].specifications
                    name = resource[0].name
                    doc2 = parseString(specifications)
                    for node in doc2.getElementsByTagName("SPEC_LIST"):
                        node.setAttribute("clone", "1")
                        specifications = doc2.toxml()
                    newvmlsit = vm_api.getvmlist(datacenter, cluster, None, name)
                    if len(newvmlsit) > 0:
                        resource[0].uuid = newvmlsit[0]["uuid"]
                        resource[0].specifications = specifications
                        resource[0].save()

                        uuid = newvmlsit[0]["uuid"]
                        state = "3"
        result = {"progress": progress, "state": state, "uuid": uuid}
        return HttpResponse(json.dumps(result))


def vm_ipsave(request):
    if request.user.is_authenticated() and request.session['isadmin']:
        result = {}
        pool_id = request.POST.get("poolid", "")
        uuid = request.POST.get("uuid", "")
        path = request.POST.get("path", "")
        vmip = request.POST.get("ip", "")
        mask = request.POST.get("mask", "")
        gateway = request.POST.get("gateway", "")
        dns = request.POST.get("dns", "")
        vmuser = request.POST.get("user", "")
        vmpassword = request.POST.get("password", "")
        id = request.POST.get("id", "")
        try:
            id = int(id)
        except:
            raise Http404()

        if pool_id:
            resourcepool = ResourcePool.objects.filter(id=pool_id)[0]
            certificate = resourcepool.certificate
            doc = parseString(certificate)
            ip = ""
            username = ""
            password = ""
            for node in doc.getElementsByTagName("CERT_LIST"):
                for hostnode in node.getElementsByTagName("CERT"):
                    ip = hostnode.getAttribute("ip")
                    username = hostnode.getAttribute("username")
                    password = hostnode.getAttribute("password")
                    datacenter = hostnode.getAttribute("datacenter")
                    cluster = hostnode.getAttribute("cluster")
            vm_api = VM_API(ip, username, password)
            if vm_api.execute_program(uuid, vmuser, vmpassword, path, vmip + " " + mask + " " + gateway + " " + dns):
                resource = VmResource.objects.filter(id=id)
                if (len(resource) > 0):
                    specifications = resource[0].specifications
                    doc2 = parseString(specifications)
                    for node in doc2.getElementsByTagName("SPEC_LIST"):
                        node.setAttribute("vmip", vmip)
                        specifications = doc2.toxml()
                        resource[0].specifications = specifications
                        resource[0].save()
                result = {"value": "1", "text": "执行成功"}
            else:
                result = {"value": "0", "text": vm_api.msg}

        return HttpResponse(json.dumps(result))


def vm_hostsave(request):
    if request.user.is_authenticated() and request.session['isadmin']:
        result = {}
        pool_id = request.POST.get("poolid", "")
        uuid = request.POST.get("uuid", "")
        path = request.POST.get("path", "")
        hostname = request.POST.get("hostname", "")
        vmuser = request.POST.get("user", "")
        vmpassword = request.POST.get("password", "")
        id = request.POST.get("id", "")
        try:
            id = int(id)
        except:
            raise Http404()

        if pool_id:
            resourcepool = ResourcePool.objects.filter(id=pool_id)[0]
            certificate = resourcepool.certificate
            doc = parseString(certificate)
            ip = ""
            username = ""
            password = ""
            for node in doc.getElementsByTagName("CERT_LIST"):
                for hostnode in node.getElementsByTagName("CERT"):
                    ip = hostnode.getAttribute("ip")
                    username = hostnode.getAttribute("username")
                    password = hostnode.getAttribute("password")
                    datacenter = hostnode.getAttribute("datacenter")
                    cluster = hostnode.getAttribute("cluster")
            vm_api = VM_API(ip, username, password)
            if vm_api.execute_program(uuid, vmuser, vmpassword, path, hostname):
                resource = VmResource.objects.filter(id=id)
                if (len(resource) > 0):
                    specifications = resource[0].specifications
                    doc2 = parseString(specifications)
                    for node in doc2.getElementsByTagName("SPEC_LIST"):
                        node.setAttribute("hostname", hostname)
                        specifications = doc2.toxml()
                        resource[0].specifications = specifications
                        resource[0].save()
                result = {"value": "1", "text": "执行成功"}
            else:
                result = {"value": "0", "text": vm_api.msg}
        return HttpResponse(json.dumps(result))


def vm_disksave(request):
    if request.user.is_authenticated() and request.session['isadmin']:
        result = {}
        pool_id = request.POST.get("poolid", "")
        uuid = request.POST.get("uuid", "")
        disksize = request.POST.get("disksize", "")
        disktype = request.POST.get("disktype", "")
        selectdisk = request.POST.get("selectdisk", "")
        path = request.POST.get("path", "")
        vmuser = request.POST.get("user", "")
        vmpassword = request.POST.get("password", "")
        name = request.POST.get("name", "")
        id = request.POST.get("id", "")
        try:
            id = int(id)
        except:
            raise Http404()
        if pool_id:
            resourcepool = ResourcePool.objects.filter(id=pool_id)[0]
            certificate = resourcepool.certificate
            doc = parseString(certificate)
            ip = ""
            username = ""
            password = ""
            size = ""
            for node in doc.getElementsByTagName("CERT_LIST"):
                for hostnode in node.getElementsByTagName("CERT"):
                    ip = hostnode.getAttribute("ip")
                    username = hostnode.getAttribute("username")
                    password = hostnode.getAttribute("password")
            vm_api = VM_API(ip, username, password)

            try:
                disknum = vm_api.add_disk(name, disktype, disksize, uuid)  # disknum
                if disknum==-9:
                    result = {"value": "0", "text": "超时！！！", "size": size}
                else:
                    # initialize disk
                    if vm_api.execute_program(uuid, vmuser, vmpassword, path, str(disknum)+" "+selectdisk):
                        resource = VmResource.objects.filter(id=id)
                        if (len(resource) > 0):
                            specifications = resource[0].specifications
                            doc2 = parseString(specifications)
                            for node in doc2.getElementsByTagName("SPEC_LIST"):
                                oldsize = 0
                                newsize = 0
                                try:
                                    oldsize = int(node.getAttribute("disk"))
                                except:
                                    pass
                                try:
                                    newsize = int(disksize)
                                except:
                                    pass
                                size = str(oldsize + newsize)

                                node.setAttribute("disk", size)
                                specifications = doc2.toxml()
                                resource[0].specifications = specifications
                                resource[0].save()
                        result = {"value": "1", "text": "执行成功", "size": size}
                    else:
                        result = {"value": "0", "text": "执行失败", "size": size}
            except:
                result = {"value": "0", "text": vm_api.msg, "size": size}
        return HttpResponse(json.dumps(result))


def vm_installcvsave(request):
    if request.user.is_authenticated() and request.session['isadmin']:
        result = {}
        pool_id = request.POST.get("poolid", "")
        uuid = request.POST.get("uuid", "")
        path = request.POST.get("path", "")
        hostname = request.POST.get("hostname", "")
        vmuser = request.POST.get("user", "")
        vmpassword = request.POST.get("password", "")

        allhost = ClientHost.objects.exclude(status="9").filter(owernID=request.user.userinfo.userGUID).filter(
            clientName=hostname+"."+request.user.username)
        if (len(allhost) > 0):
            result = {"value": "0", "text": u"主机名" + hostname+"."+request.user.usernamee + u'已注册,请勿重复安装。'}

        else:
            cvToken = CV_RestApi_Token()
            cvToken.login(info)
            cvAPI = CV_API(cvToken)
            clientInfo = cvAPI.getClientInfo(hostname+"."+request.user.username)
            if clientInfo:
                result = {"value": "0", "text": u"主机" + hostname+"."+request.user.username + u'已安装客户端,请勿重复安装。'}
            else:
                if pool_id:
                    resourcepool = ResourcePool.objects.filter(id=pool_id)[0]
                    certificate = resourcepool.certificate
                    doc = parseString(certificate)
                    ip = ""
                    username = ""
                    password = ""
                    for node in doc.getElementsByTagName("CERT_LIST"):
                        for hostnode in node.getElementsByTagName("CERT"):
                            ip = hostnode.getAttribute("ip")
                            username = hostnode.getAttribute("username")
                            password = hostnode.getAttribute("password")
                            datacenter = hostnode.getAttribute("datacenter")
                            cluster = hostnode.getAttribute("cluster")
                    vm_api = VM_API(ip, username, password)
                    if vm_api.execute_program(uuid, vmuser, vmpassword, path, request.user.username):
                        result = {"value": "1", "text": "执行成功"}
                    else:
                        result = {"value": "0", "text": vm_api.msg}

        return HttpResponse(json.dumps(result))


def registercvsave(request):
    if request.user.is_authenticated() and request.session['isadmin']:
        result = {}
        hostname = request.POST.get("hostname", "")

        allhost = ClientHost.objects.exclude(status="9").filter(owernID=request.user.userinfo.userGUID).filter(
            clientName=hostname+"."+request.user.username)
        if (len(allhost) > 0):
            result = {"value": "0", "text": u"主机名" + hostname + u'已注册,请勿重复注册。'}

        else:
            cvToken = CV_RestApi_Token()
            cvToken.login(info)
            cvAPI = CV_API(cvToken)
            clientInfo = cvAPI.getClientInfo(hostname+"."+request.user.username)
            if not clientInfo:
                result = {"value": "0", "text": u"主机" + hostname + u'未安装客户端,请先安装commvalut客户端。'}
            else:
                agentTypeList = "<agentTypeList>"
                for node in clientInfo["agentList"]:
                    if node["agentType"] == "File System":
                        agentTypeList += "<agentType>FILESYSTEM</agentType>"
                    else:
                        if node["agentType"] == "Oracle":
                            agentTypeList += "<agentType>ORACLE</agentType>"
                        else:
                            if node["agentType"] == "SQL Server":
                                agentTypeList += "<agentType>MSSQL</agentType>"
                            else:
                                agentTypeList += "<agentType>" + node["agentType"] + "</agentType>"
                agentTypeList += "</agentTypeList>"
                clientID = clientInfo["clientId"]

                try:
                    clientID = int(clientID)
                except:
                    clientID = 0
                platform = clientInfo["platform"]["platform"]

                result = {}
                user = request.user
                if user is not None and user.is_active:
                    try:
                        clienthost = ClientHost()
                        clienthost.clientGUID = uuid.uuid1()
                        clienthost.clientName = hostname
                        clienthost.owernID = user.userinfo.userGUID
                        clienthost.hostType = "physical box"
                        clienthost.clientID = clientID
                        clienthost.agentTypeList = agentTypeList
                        clienthost.status = "0"
                        clienthost.platform = platform
                        clienthost.appGroup = "缺省"
                        clienthost.installTime = datetime.datetime.now()
                        clienthost.save()
                        result = {"value": "1", "text": u"注册成功。"}
                    except:
                        result = {"value": "0", "text": u"注册失败。"}

        return HttpResponse(json.dumps(result))


def rebootvm(request):
    if request.user.is_authenticated() and request.session['isadmin']:
        pool_id = request.POST.get("poolid", '')
        uuid = request.POST.get("uuid", '')
        hostname = request.POST.get("hostname", '')
        resourcepool = ResourcePool.objects.filter(id=int(pool_id))[0]
        certificate = resourcepool.certificate

        doc = parseString(certificate)
        ip = ""
        username = ""
        password = ""
        for node in doc.getElementsByTagName("CERT_LIST"):
            for hostnode in node.getElementsByTagName("CERT"):
                ip = hostnode.getAttribute("ip")
                username = hostnode.getAttribute("username")
                password = hostnode.getAttribute("password")
        vm_api = VM_API(ip, username, password)
        try:
            vmname, powerState = vm_api.reboot_vm(uuid, hostname, None)
            result = {"text": "重启成功"}
        except:
            result = {"text": "启动失败"}
        return JsonResponse(result)


def poweronvm(request):
    if request.user.is_authenticated() and request.session['isadmin']:
        result = {}
        pool_id = request.POST.get("poolid", "")
        name = request.POST.get("currentvm", "")

        if pool_id:
            resourcepool = ResourcePool.objects.filter(id=pool_id)[0]
            certificate = resourcepool.certificate
            doc = parseString(certificate)
            ip = ""
            username = ""
            password = ""
            for node in doc.getElementsByTagName("CERT_LIST"):
                for hostnode in node.getElementsByTagName("CERT"):
                    ip = hostnode.getAttribute("ip")
                    username = hostnode.getAttribute("username")
                    password = hostnode.getAttribute("password")

            vm_api = VM_API(ip, username, password)
            try:
                vm_api.power_on_vm(name)
            except:
                result = {"text": "开机失败"}
            result = {"text": "开机成功"}
        return JsonResponse(result)


def shutdownvm(request):
    if request.user.is_authenticated() and request.session['isadmin']:
        result = {}
        pool_id = request.POST.get("poolid", "")
        name = request.POST.get("currentvm", "")

        if pool_id:
            resourcepool = ResourcePool.objects.filter(id=pool_id)[0]
            certificate = resourcepool.certificate
            doc = parseString(certificate)
            ip = ""
            username = ""
            password = ""
            for node in doc.getElementsByTagName("CERT_LIST"):
                for hostnode in node.getElementsByTagName("CERT"):
                    ip = hostnode.getAttribute("ip")
                    username = hostnode.getAttribute("username")
                    password = hostnode.getAttribute("password")

            vm_api = VM_API(ip, username, password)
            try:
                vm_api.power_off_vm(name)
            except:
                result = {"text": "关机失败"}
            result = {"text": "关机成功"}
        return JsonResponse(result)


def get_vm_state(request):
    if request.user.is_authenticated() and request.session['isadmin']:
        pool_id = request.POST.get('poolid', '')
        name = request.POST.get('name', '')
        resourcepool = ResourcePool.objects.filter(id=pool_id)[0]
        certificate = resourcepool.certificate

        doc = parseString(certificate)
        ip = ""
        username = ""
        password = ""
        for node in doc.getElementsByTagName("CERT_LIST"):
            for hostnode in node.getElementsByTagName("CERT"):
                ip = hostnode.getAttribute("ip")
                username = hostnode.getAttribute("username")
                password = hostnode.getAttribute("password")
                datacenter = hostnode.getAttribute("datacenter")
                cluster = hostnode.getAttribute("cluster")
        vm_api = VM_API(ip, username, password)
        vmlist = vm_api.getvmlist(datacenter, cluster, None, name)
        state = ''
        for vm in vmlist:
            state = vm['state']
        result = {
            "state": state,
        }
        return JsonResponse(result)


def get_dc_clt_from_pool(request):
    if request.user.is_authenticated() and request.session['ispuser']:
        pool_id = request.POST.get("poolid", "")
        resourcepool = ResourcePool.objects.filter(id=pool_id)[0]
        certificate = resourcepool.certificate
        doc = parseString(certificate)
        datacenter = ""
        cluster = ""
        for node in doc.getElementsByTagName("CERT_LIST"):
            for hostnode in node.getElementsByTagName("CERT"):
                datacenter = hostnode.getAttribute("datacenter")
                cluster = hostnode.getAttribute("cluster")
        result = {
            "datacenter": datacenter,
            "cluster": cluster,
        }
        return JsonResponse(result)


def backupresource(request):
    if request.user.is_authenticated() and request.session['isadmin']:
        return render(request, 'backupresource.html',
                      {'username': request.user.userinfo.fullname, "backupresourcepage": True})
    else:
        return HttpResponseRedirect("/login")


def backupresourcedata(request):
    if request.user.is_authenticated() and request.session['isadmin']:
        result = []
        allresource = BackupResource.objects.exclude(state="9")
        if (len(allresource) > 0):
            for resource in allresource:
                id = resource.id
                name = resource.name
                poolid = resource.pool.id
                poolname = resource.pool.name
                certificate = resource.certificate
                specifications = resource.specifications
                description = resource.description
                state = "空闲"
                if resource.state == "1":
                    state = "已使用"
                doc = parseString(certificate)
                cert_name = ""
                for node in doc.getElementsByTagName("CERT_LIST"):
                    for hostnode in node.getElementsByTagName("CERT"):
                        cert_name = hostnode.getAttribute("name")
                print(specifications)
                doc2 = parseString(specifications)
                spec_type = ""
                spec_time = ""
                spec_size = ""
                spec_perform = ""

                for node in doc2.getElementsByTagName("SPEC_LIST"):
                    spec_type = node.getAttribute("type")
                    spec_time = node.getAttribute("time")
                    spec_size = node.getAttribute("size")
                    spec_perform = node.getAttribute("perform")
                result.append(
                    {"id": id, "name": name, "poolid": poolid, "poolname": poolname, "description": description,
                     "state": state, "cert_name": cert_name, "spec_type": spec_type, "spec_time": spec_time,
                     "spec_size": spec_size, "spec_perform": spec_perform})
        return HttpResponse(json.dumps({"data": result}))


def backupresourcepooldata(request):
    if request.user.is_authenticated() and request.session['isadmin']:
        result = []
        allresourcepool = ResourcePool.objects.exclude(state="9").filter(type="备份资源")
        if (len(allresourcepool) > 0):
            for resourcepool in allresourcepool:
                id = resourcepool.id
                name = resourcepool.name
                type = resourcepool.type
                supplier = resourcepool.supplier
                certificate = resourcepool.certificate
                description = resourcepool.description
                doc = parseString(certificate)
                ip = ""
                username = ""
                password = ""
                for node in doc.getElementsByTagName("CERT_LIST"):
                    for hostnode in node.getElementsByTagName("CERT"):
                        ip = hostnode.getAttribute("ip")
                        username = hostnode.getAttribute("username")
                        password = hostnode.getAttribute("password")
                result.append({"id": id, "name": name, "type": type, "supplier": supplier, "description": description,
                               "ip": ip, "username": username, "password": password})
        return HttpResponse(json.dumps({"data": result}))


def getbackupcert(request):
    if request.user.is_authenticated() and request.session['isadmin']:
        if request.method == 'POST':
            result = []
            if 'id' in request.POST:
                poolid = request.POST.get('poolid', '')
                try:
                    poolid = int(poolid)
                except:
                    raise Http404()

            cvToken = CV_RestApi_Token()
            cvToken.login(info)
            cvAPI = CV_API(cvToken)
            for node in cvAPI.getSPList():
                result.append({"id": node["SPName"], "name": node["SPName"]})

            return HttpResponse(json.dumps(result))


def backupresourcesave(request):
    if request.user.is_authenticated() and request.session['ispuser']:
        if request.method == 'POST':
            result = ""
            id = request.POST.get('id', '')
            name = request.POST.get('name', '')
            poolid = request.POST.get('poolid', '')
            description = request.POST.get('description', '')

            spec_type = request.POST.get('spec_type', '')
            spec_time = request.POST.get('spec_time', '')
            spec_size = request.POST.get('spec_size', '')
            spec_perform = request.POST.get('spec_perform', '')

            cert_name = request.POST.get('cert_name', '')

            try:
                id = int(id)
            except:
                raise Http404()
            try:
                poolid = int(poolid)
            except:
                raise Http404()
            if id == 0:
                allresource = BackupResource.objects.filter(name=name)
                if (len(allresource) > 0):
                    result = u"备份资源名称" + name + u'已存在。'
                else:
                    resource = BackupResource()
                    resource.name = name
                    mypoll = ResourcePool.objects.get(id=poolid)
                    resource.pool = mypoll  # ?????
                    resource.description = description

                    impl = xml.dom.minidom.getDOMImplementation()
                    dom = impl.createDocument(None, 'CERT_LIST', None)
                    root = dom.documentElement
                    nameE = dom.createElement('CERT')
                    nameE.setAttribute("name", cert_name)  # 增加属性
                    root.appendChild(nameE)
                    resource.certificate = dom.toxml()

                    dom1 = impl.createDocument(None, 'SPEC_LIST', None)
                    root = dom1.documentElement
                    root.setAttribute("type", spec_type)
                    root.setAttribute("time", spec_time)
                    root.setAttribute("size", spec_size)
                    root.setAttribute("perform", spec_perform)
                    resource.specifications = dom1.toxml()

                    resource.state = "0"
                    resource.creatdate = datetime.datetime.now()
                    resource.updatedate = datetime.datetime.now()
                    resource.save()
                    result = "保存成功。"
            else:
                allresource = BackupResource.objects.filter(id=id)
                if (len(allresource) > 0):
                    allresource1 = BackupResource.objects.filter(name=name).exclude(id=id)
                    if (len(allresource1) > 0):
                        result = u"备份资源名称" + name + u'已存在。'
                    else:
                        resource = allresource[0]
                        resource.name = name
                        mypoll = ResourcePool.objects.get(id=poolid)
                        resource.pool = mypoll
                        resource.description = description

                        impl = xml.dom.minidom.getDOMImplementation()
                        dom = impl.createDocument(None, 'CERT_LIST', None)
                        root = dom.documentElement
                        nameE = dom.createElement('CERT')
                        nameE.setAttribute("name", cert_name)  # 增加属性
                        root.appendChild(nameE)
                        resource.certificate = dom.toxml()

                        dom1 = impl.createDocument(None, 'SPEC_LIST', None)
                        root = dom1.documentElement
                        root.setAttribute("type", spec_type)
                        root.setAttribute("time", spec_time)
                        root.setAttribute("size", spec_size)
                        root.setAttribute("perform", spec_perform)
                        resource.specifications = dom1.toxml()

                        resource.updatedate = datetime.datetime.now()
                        resource.save()
                        result = "保存成功。"
                else:
                    result = "数据异常。"
            return HttpResponse(result)


def backupresourcedel(request):
    if request.user.is_authenticated() and request.session['isadmin']:
        if 'id' in request.POST:
            id = request.POST.get('id', '')
            try:
                id = int(id)
            except:
                raise Http404()
            myresource = BackupResource.objects.get(id=id)
            myresource.name = myresource.name + u"(已删除)"
            myresource.state = "9"
            myresource.save()
            return HttpResponse(1)
        else:
            return HttpResponse(0)


def schduleresource(request):
    if request.user.is_authenticated() and request.session['isadmin']:
        return render(request, 'schduleresource.html',
                      {'username': request.user.userinfo.fullname, "schduleresourcepage": True})
    else:
        return HttpResponseRedirect("/login")


def schduleresourcedata(request):
    if request.user.is_authenticated() and request.session['isadmin']:
        result = []
        allresource = SchduleResource.objects.exclude(state="9")
        if (len(allresource) > 0):
            for resource in allresource:
                id = resource.id
                name = resource.name
                poolid = resource.pool.id
                poolname = resource.pool.name
                certificate = resource.certificate
                specifications = resource.specifications
                description = resource.description
                state = "空闲"
                if resource.state == "1":
                    state = "已使用"
                doc = parseString(certificate)
                cert_name = ""
                for node in doc.getElementsByTagName("CERT_LIST"):
                    for hostnode in node.getElementsByTagName("CERT"):
                        cert_name = hostnode.getAttribute("name")

                doc2 = parseString(specifications)
                spec_type = ""
                spec_rpo = ""

                for node in doc2.getElementsByTagName("SPEC_LIST"):
                    spec_type = node.getAttribute("type")
                    spec_rpo = node.getAttribute("rpo")
                result.append(
                    {"id": id, "name": name, "poolid": poolid, "poolname": poolname, "description": description,
                     "state": state, "spec_type": spec_type, "spec_rpo": spec_rpo, "cert_name": cert_name})
        return HttpResponse(json.dumps({"data": result}))


def schduleresourcepooldata(request):
    if request.user.is_authenticated() and request.session['isadmin']:
        result = []
        allresourcepool = ResourcePool.objects.exclude(state="9").filter(type="计划资源")
        if (len(allresourcepool) > 0):
            for resourcepool in allresourcepool:
                id = resourcepool.id
                name = resourcepool.name
                type = resourcepool.type
                supplier = resourcepool.supplier
                certificate = resourcepool.certificate
                description = resourcepool.description
                doc = parseString(certificate)
                ip = ""
                username = ""
                password = ""
                for node in doc.getElementsByTagName("CERT_LIST"):
                    for hostnode in node.getElementsByTagName("CERT"):
                        ip = hostnode.getAttribute("ip")
                        username = hostnode.getAttribute("username")
                        password = hostnode.getAttribute("password")
                result.append({"id": id, "name": name, "type": type, "supplier": supplier, "description": description,
                               "ip": ip, "username": username, "password": password})
        return HttpResponse(json.dumps({"data": result}))


def getschdulecert(request):
    if request.user.is_authenticated() and request.session['isadmin']:
        if request.method == 'POST':

            result = []
            if 'id' in request.POST:
                poolid = request.POST.get('poolid', '')
                try:
                    poolid = int(poolid)
                except:
                    raise Http404()
            cvToken = CV_RestApi_Token()
            cvToken.login(info)
            cvAPI = CV_API(cvToken)
            for node in cvAPI.getSchduleList():
                result.append({"id": node["SchduleName"], "name": node["SchduleName"]})
            return HttpResponse(json.dumps(result))


def schduleresourcesave(request):
    if request.user.is_authenticated() and request.session['ispuser']:
        if request.method == 'POST':
            result = ""
            id = request.POST.get('id', '')
            name = request.POST.get('name', '')
            poolid = request.POST.get('poolid', '')
            description = request.POST.get('description', '')

            spec_type = request.POST.get('spec_type', '')
            spec_rpo = request.POST.get('spec_rpo', '')

            cert_name = request.POST.get('cert_name', '')

            try:
                id = int(id)
            except:
                raise Http404()
            try:
                poolid = int(poolid)
            except:
                raise Http404()
            if id == 0:
                allresource = SchduleResource.objects.filter(name=name)
                if (len(allresource) > 0):
                    result = u"计划资源名称" + name + u'已存在。'
                else:
                    resource = SchduleResource()
                    resource.name = name
                    mypoll = ResourcePool.objects.get(id=poolid)
                    resource.pool = mypoll
                    resource.description = description

                    impl = xml.dom.minidom.getDOMImplementation()
                    dom = impl.createDocument(None, 'CERT_LIST', None)
                    root = dom.documentElement
                    nameE = dom.createElement('CERT')
                    nameE.setAttribute("name", cert_name)  # 增加属性
                    root.appendChild(nameE)
                    resource.certificate = dom.toxml()

                    dom1 = impl.createDocument(None, 'SPEC_LIST', None)
                    root = dom1.documentElement
                    root.setAttribute("type", spec_type)
                    root.setAttribute("rpo", spec_rpo)
                    resource.specifications = dom1.toxml()

                    resource.state = "0"
                    resource.creatdate = datetime.datetime.now()
                    resource.updatedate = datetime.datetime.now()
                    resource.save()
                    result = "保存成功。"
            else:
                allresource = SchduleResource.objects.filter(id=id)
                if (len(allresource) > 0):
                    allresource1 = SchduleResource.objects.filter(name=name).exclude(id=id)
                    if (len(allresource1) > 0):
                        result = u"计划资源名称" + name + u'已存在。'
                    else:
                        resource = allresource[0]
                        resource.name = name
                        mypoll = ResourcePool.objects.get(id=poolid)
                        resource.pool = mypoll
                        resource.description = description

                        impl = xml.dom.minidom.getDOMImplementation()
                        dom = impl.createDocument(None, 'CERT_LIST', None)
                        root = dom.documentElement
                        nameE = dom.createElement('CERT')
                        nameE.setAttribute("name", cert_name)  # 增加属性
                        root.appendChild(nameE)
                        resource.certificate = dom.toxml()

                        dom1 = impl.createDocument(None, 'SPEC_LIST', None)
                        root = dom1.documentElement
                        root.setAttribute("type", spec_type)
                        root.setAttribute("rpo", spec_rpo)
                        resource.specifications = dom1.toxml()

                        resource.updatedate = datetime.datetime.now()
                        resource.save()
                        result = "保存成功。"
                else:
                    result = "数据异常。"
            return HttpResponse(result)


def schduleresourcedel(request):
    if request.user.is_authenticated() and request.session['isadmin']:
        if 'id' in request.POST:
            id = request.POST.get('id', '')
            try:
                id = int(id)
            except:
                raise Http404()
            myresource = SchduleResource.objects.get(id=id)
            myresource.name = myresource.name + u"(已删除)"
            myresource.state = "9"
            myresource.save()
            return HttpResponse(1)
        else:
            return HttpResponse(0)


from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def addPhyClient(request):
    username = request.GET.get('username', '').replace('^', ' ')
    password = request.GET.get('password', '').replace('^', ' ')
    clientName = request.GET.get('clientName', '').replace('^', ' ')
    vendor = request.GET.get('vendor', '').replace('^', ' ')
    zone = request.GET.get('zone', '').replace('^', ' ')

    client = clientName + u'.' + username
    cvToken = CV_RestApi_Token()
    cvToken.login(info)
    cvAPI = CV_API(cvToken)
    clientInfo = cvAPI.getClientInfo(client)
    agentTypeList = "<agentTypeList>"
    for node in clientInfo["agentList"]:
        if node["agentType"] == "File System":
            agentTypeList += "<agentType>FILESYSTEM</agentType>"
        else:
            if node["agentType"] == "Oracle":
                agentTypeList += "<agentType>ORACLE</agentType>"
            else:
                if node["agentType"] == "SQL Server":
                    agentTypeList += "<agentType>MSSQL</agentType>"
                else:
                    agentTypeList += "<agentType>" + node["agentType"] + "</agentType>"
    agentTypeList += "</agentTypeList>"
    clientID = clientInfo["clientId"]

    try:
        clientID = int(clientID)
    except:
        clientID = 0
    platform = clientInfo["platform"]

    result = {}
    user = auth.authenticate(username=username, password=password)
    if user is not None and user.is_active:
        allhost = ClientHost.objects.filter(clientName=clientName + "." + user.username)
        result = {"value": "-9", "text": u"新增失败。"}
        if (len(allhost) > 0):
            result = {"value": "-2", "text": u"主机名称" + clientName + u'已存在。'}
        else:
            try:
                clienthost = ClientHost()
                clienthost.clientGUID = uuid.uuid1()
                clienthost.clientName = clientName + "." + user.username
                clienthost.owernID = user.userinfo.userGUID
                clienthost.hostType = "physical box"
                clienthost.vendor = vendor
                clienthost.zone = zone
                clienthost.clientID = clientID
                clienthost.agentTypeList = agentTypeList
                clienthost.status = "0"
                clienthost.platform = platform
                clienthost.appGroup = "缺省"
                clienthost.installTime = datetime.datetime.now()
                clienthost.save()
                result = {"value": "1", "text": u"新增成功。"}
            except:
                result = {"value": "-9", "text": u"新增失败。"}
    else:
        result = {"value": "-1", "text": u"用户名密码错误。"}
    return HttpResponse(json.dumps(result))


@csrf_exempt
def checkPhyClient(request):
    username = request.GET.get('username', '').replace('^', ' ')
    password = request.GET.get('password', '').replace('^', ' ')
    clientName = request.GET.get('clientName', '').replace('^', ' ')

    result = {}
    user = auth.authenticate(username=username, password=password)
    if user is not None and user.is_active:
        allhost = ClientHost.objects.filter(clientName=clientName + "." + user.username)
        result = {"value": "-9", "text": u"新增失败。"}
        if (len(allhost) > 0):
            result = {"value": "-2", "text": u"主机名称" + clientName + u'已存在。'}
        else:
            cvToken = CV_RestApi_Token()
            cvToken.login(info)
            cvAPI = CV_API(cvToken)
            clientList = cvAPI.getClientList()
            for node in clientList:
                if node["clientName"] == clientName + u'.' + username:
                    result = {"value": "-3", "text": clientName + u"已安装，但需重新注册。"}
                    return HttpResponse(json.dumps(result))
            result = {"value": "1", "text": u"允许安装。", "clientName": "test1", "hostName": "test1"}
    else:
        result = {"value": "-1", "text": u"用户名密码错误。"}
    return HttpResponse(json.dumps(result))


def serverconfig(request):
    if request.user.is_authenticated() and request.session['isadmin']:
        cvvendor = Vendor.objects.filter(name='CommVault')
        id = 0
        webaddr = ""
        port = ""
        usernm = ""
        passwd = ""
        if (len(cvvendor) > 0):
            id = cvvendor[0].id
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
                usernm = (doc.getElementsByTagName("username"))[0].childNodes[0].data
            except:
                pass
            try:
                passwd = (doc.getElementsByTagName("passwd"))[0].childNodes[0].data
            except:
                pass
        return render(request, 'serverconfig.html',
                      {'username': request.user.userinfo.fullname, "serverconfigpage": True, "id": id,
                       "webaddr": webaddr, "port": port, "usernm": usernm, "passwd": passwd})
    else:
        return HttpResponseRedirect("/login")


def serverconfigsave(request):
    if request.method == 'POST':
        result = ""
        id = request.POST.get('id', '')
        webaddr = request.POST.get('webaddr', '')
        port = request.POST.get('port', '')
        usernm = request.POST.get('usernm', '')
        passwd = request.POST.get('passwd', '')
        cvvendor = Vendor.objects.filter(name='CommVault')
        if (len(cvvendor) > 0):
            cvvendor[
                0].content = "<?xml version=\"1.0\" ?><vendor><webaddr>" + webaddr + "</webaddr><port>" + port + "</port><username>" + usernm + "</username><passwd>" + passwd + "</passwd></vendor>"
            cvvendor[0].save()
            result = "保存成功。"
        else:
            cvvendor = Vendor()
            cvvendor.content = "<?xml version=\"1.0\" ?><vendor><webaddr>" + webaddr + "</webaddr><port>" + port + "</port><username>" + usernm + "</username><passwd>" + passwd + "</passwd></vendor>"
            cvvendor.name = "CommVault"
            cvvendor.save()
            result = "保存成功。"
        return HttpResponse(result)


def match(request):
    if request.user.is_authenticated() and request.session['isadmin']:
        cvvendor = Vendor.objects.filter(name='CommVault')
        id = 0
        webaddr = ""
        port = ""
        usernm = ""
        passwd = ""
        if (len(cvvendor) > 0):
            id = cvvendor[0].id
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
                usernm = (doc.getElementsByTagName("username"))[0].childNodes[0].data
            except:
                pass
            try:
                passwd = (doc.getElementsByTagName("passwd"))[0].childNodes[0].data
            except:
                pass
        return render(request, 'match.html',
                      {'username': request.user.userinfo.fullname, "matchpage": True, "id": id, "webaddr": webaddr,
                       "port": port, "usernm": usernm, "passwd": passwd})
    else:
        return HttpResponseRedirect("/login")


def matchdata(request):
    if request.user.is_authenticated() and request.session['isadmin']:
        result = []
        allhost = ClientHost.objects.exclude(status="9").filter(owernID=request.user.userinfo.userGUID)
        if (len(allhost) > 0):
            for host in allhost:
                clientName = host.clientName
                clientNames = clientName.split('.')
                clientName = clientNames[0]
                platform = host.platform
                agentTypeList = host.agentTypeList
                if host.hostType == "VMWARE":
                    agentTypeList = "<agentTypeList><agentType>Virtual Server</agentType></agentTypeList>"
                installTime = host.installTime.strftime('%Y-%m-%d')
                doc = parseString(agentTypeList)
                agentType = []
                for node in doc.getElementsByTagName("agentTypeList"):
                    for agenttypenode in node.getElementsByTagName("agentType"):
                        agentType.append(agenttypenode.childNodes[0].data)
                result.append({"clientName": clientName, "platform": platform,
                               "agentType": ','.join(agentType), "installTime": installTime})
        return HttpResponse(json.dumps({"data": result}))


def matching(request):
    if request.user.is_authenticated() and request.session['isadmin']:
        if request.method == 'POST':
            result = {}
            cvToken = CV_RestApi_Token()
            cvToken.login(info)
            cvAPI = CV_API(cvToken)
            returnclientList = []
            clientList = cvAPI.getClientList()
            for client in clientList:
                allhost = ClientHost.objects.filter(clientID=client["clientId"]).exclude(status="9").filter(
                    owernID=request.user.userinfo.userGUID)
                if (len(allhost) > 0):
                    client["selected"] = True
                else:
                    client["selected"] = False
                returnclientList.append(client)
            result = {"value": "1", "list": returnclientList}

            return HttpResponse(json.dumps(result))


def matchsave(request):
    if request.user.is_authenticated() and request.session['isadmin']:
        if request.method == 'POST':
            result = ""

            password = request.POST.get('password', '')
            clientlist = request.POST.get('clientlist', '')
            myclientlist = clientlist.split("*!-!*")
            myclientlist.remove("")

            oldhost = ClientHost.objects.exclude(status="9").filter(
                owernID=request.user.userinfo.userGUID)
            for client in oldhost:
                if str(client.clientID) not in clientlist:
                    client.status = "9"
                    # client.save()
            for listid in myclientlist:
                cvToken = CV_RestApi_Token()
                cvToken.login(info)
                cvAPI = CV_API(cvToken)

                clientInfo = cvAPI.getClientInfo(int(listid))
                newhost = ClientHost.objects.exclude(status="9").filter(
                    owernID=request.user.userinfo.userGUID).filter(clientID=int(listid)).exclude(status="9")
                clientName = clientInfo["clientName"]
                hostType = ""
                proxyClient = ""
                creditInfo = ""
                agentTypeList = ""
                platform = clientInfo["platform"]["platform"]
                if "WINDOWS" in (clientInfo["platform"]["platform"]).upper() or "LINUX" in (
                        clientInfo["platform"]["platform"]).upper():
                    hostType = "physical box"
                    agentTypeList = "<agentTypeList>"
                    for node in clientInfo["agentList"]:
                        if node["agentType"] == "File System":
                            agentTypeList += "<agentType>FILESYSTEM</agentType>"
                        else:
                            if node["agentType"] == "Oracle":
                                agentTypeList += "<agentType>ORACLE</agentType>"
                            else:
                                if node["agentType"] == "SQL Server":
                                    agentTypeList += "<agentType>MSSQL</agentType>"
                                else:
                                    agentTypeList += "<agentType>" + node["agentType"] + "</agentType>"
                    agentTypeList += "</agentTypeList>"
                if (clientInfo["platform"]["platform"]).upper() == "ANY":
                    hostType = "VMWARE"
                    creditInfo = "<?xml version=\"1.0\" ?><creditInfo><HOST>" + clientInfo["instance"][
                        "HOST"] + "</HOST><USER>" + clientInfo["instance"]["USER"] + "</USER></creditInfo>"
                    proxyClient = "<?xml version=\"1.0\" ?><PROXYLIST>"
                    for node in clientInfo["instance"]["PROXYLIST"]:
                        proxyhost = ClientHost.objects.exclude(status="9").filter(
                            owernID=request.user.userinfo.userGUID).filter(clientID=int(node["clientId"])).exclude(
                            status="9")
                        if len(proxyhost) > 0:
                            proxyClient += "<PROXY>" + proxyhost[0].clientGUID + "</PROXY>"
                        else:
                            clienthost = ClientHost()
                            clienthost.clientGUID = uuid.uuid1()
                            clienthost.clientName = node["clientName"]
                            clienthost.owernID = request.user.userinfo.userGUID
                            clienthost.hostType = "physical box"
                            clienthost.clientID = int(node["clientId"])
                            clienthost.status = "0"
                            clienthost.appGroup = "缺省"
                            clienthost.installTime = datetime.datetime.now()
                            clienthost.save()
                            proxyClient += "<PROXY>" + clienthost.clientGUID + "</PROXY>"
                    proxyClient += "</PROXYLIST>>"
                if len(newhost) > 0:
                    newhost[0].clientName = clientName
                    newhost[0].hostType = hostType
                    newhost[0].proxyClientID = proxyClient
                    newhost[0].creditInfo = creditInfo
                    newhost[0].agentTypeList = agentTypeList
                    newhost[0].platform = platform
                    # newhost[0].save()
                else:
                    newhost = ClientHost()
                    newhost.clientGUID = uuid.uuid1()
                    newhost.owernID = request.user.userinfo.userGUID
                    newhost.clientName = clientName
                    newhost.clientID = int(listid)
                    newhost.hostType = hostType
                    newhost.proxyClientID = proxyClient
                    newhost.creditInfo = creditInfo
                    newhost.agentTypeList = agentTypeList
                    newhost.platform = platform
                    newhost.status = "0"
                    newhost.appGroup = "缺省"
                    newhost.installTime = datetime.datetime.now()
                    # newhost.save()
                for backupset in clientInfo["backupsetList"]:
                    backupInfo = cvAPI.getSubclientInfo(backupset["subclientId"])
                    try:
                        a = 1
                    except:
                        pass

            return HttpResponse(result)


def phyproconfig(request):
    if request.user.is_authenticated():
        backupresource = BackupResource.objects.exclude(state="9")
        fileschduleresource = SchduleResource.objects.exclude(state="9").filter(specifications__contains='type="文件"')
        dbschduleresource = SchduleResource.objects.exclude(state="9").filter(specifications__contains='type="数据库"')
        backups = []
        for backup in backupresource:
            backups.append({"id": backup.id, "name": backup.name + "(" + backup.description + ")"})
        fileschdules = []
        for fileschdule in fileschduleresource:
            fileschdules.append({"id": fileschdule.id, "name": fileschdule.name + "(" + fileschdule.description + ")"})
        dbschdules = []
        for dbschdule in dbschduleresource:
            dbschdules.append({"id": dbschdule.id, "name": dbschdule.name + "(" + dbschdule.description + ")"})
        return render(request, 'phyproconfig.html',
                      {'username': request.user.userinfo.fullname, "backupresource": backups,
                       "fileschduleresource": fileschdules, "dbschduleresource": dbschdules, "phyproconfigpage": True})
    else:
        return HttpResponseRedirect("/login")


def phyproconfigdata(request):
    if request.user.is_authenticated():
        result = []
        allhost = ClientHost.objects.exclude(status="9").filter(hostType="physical box").filter(
            owernID=request.user.userinfo.userGUID)
        if (len(allhost) > 0):
            for host in allhost:
                id = host.id
                clientName = host.clientName
                clientNames = clientName.split('.')
                clientName = clientNames[0]
                clientGUID = host.clientGUID
                platform = host.platform
                agentTypeList = host.agentTypeList
                appGroup = host.appGroup
                status = "否"
                if host.status == "1":
                    status = "是"
                doc = parseString(agentTypeList)
                agentType = []
                for node in doc.getElementsByTagName("agentTypeList"):
                    for agenttypenode in node.getElementsByTagName("agentType"):
                        agentType.append(agenttypenode.childNodes[0].data)
                result.append({"id": id, "clientName": clientName, "clientGUID": clientGUID, "platform": platform,
                               "appGroup": appGroup,
                               "status": status, "agentType": agentType})
        return HttpResponse(json.dumps({"data": result}))


def getphydataget(request):
    if request.user.is_authenticated():
        if request.method == 'POST':
            result = {}
            clientGUID = request.POST.get('clientGUID', '')
            fs = request.POST.get('fs', '')
            oracle = request.POST.get('oracle', '')
            mssql = request.POST.get('mssql', '')

            if fs == "1":
                alldataset = DataSet.objects.filter(clientGUID=clientGUID, agentType='FILESYSTEM').exclude(status="9")
                if (len(alldataset) > 0):
                    id = alldataset[0].id
                    dataSetGUID = alldataset[0].dataSetGUID
                    content = alldataset[0].content
                    backupContent = ""
                    isBackupOS = ""
                    schdule = ""
                    storage = ""
                    path = []
                    try:
                        doc = parseString(content)
                        try:
                            isBackupOS = (doc.getElementsByTagName("isBackupOS"))[0].childNodes[0].data
                        except:
                            pass
                        try:
                            schdule = (doc.getElementsByTagName("schdule"))[0].childNodes[0].data
                        except:
                            pass
                        try:
                            storage = (doc.getElementsByTagName("storage"))[0].childNodes[0].data
                        except:
                            pass
                        try:
                            backupContent = (doc.getElementsByTagName("backupContent"))[0]
                            for mypath in backupContent.childNodes:
                                try:
                                    path.append(mypath.childNodes[0].data)
                                except:
                                    pass
                        except:
                            pass
                    except:
                        pass
                    result["fs"] = {"id": id, "dataSetGUID": dataSetGUID, "path": path, "isBackupOS": isBackupOS,
                                    "schdule": schdule, "storage": storage}
            if oracle == "1":
                alldataset = DataSet.objects.filter(clientGUID=clientGUID, agentType='ORACLE').exclude(status="9")
                if (len(alldataset) > 0):
                    id = alldataset[0].id
                    dataSetGUID = alldataset[0].dataSetGUID
                    content = alldataset[0].content
                    name = alldataset[0].instanceName
                    dbschdule = ""
                    logschdule = ""
                    dbstorage = ""
                    logstorage = ""
                    username = ""
                    oraclehome = ""
                    conn1 = ""
                    conn2 = ""
                    conn3 = ""
                    try:
                        doc = parseString(content)
                        try:
                            dbschdule = (doc.getElementsByTagName("dbschdule"))[0].childNodes[0].data
                        except:
                            pass
                        try:
                            logschdule = (doc.getElementsByTagName("logschdule"))[0].childNodes[0].data
                        except:
                            pass
                        try:
                            dbstorage = (doc.getElementsByTagName("dbstorage"))[0].childNodes[0].data
                        except:
                            pass
                        try:
                            logstorage = (doc.getElementsByTagName("logstorage"))[0].childNodes[0].data
                        except:
                            pass
                        try:
                            backupContentnode = (doc.getElementsByTagName("backupContent"))[0]

                            username = (backupContentnode.getElementsByTagName("username"))[0].childNodes[0].data
                            oraclehome = (backupContentnode.getElementsByTagName("oraclehome"))[0].childNodes[0].data
                            conn1 = (backupContentnode.getElementsByTagName("conn1"))[0].childNodes[0].data
                            conn2 = (backupContentnode.getElementsByTagName("conn2"))[0].childNodes[0].data
                            conn3 = (backupContentnode.getElementsByTagName("conn3"))[0].childNodes[0].data
                        except:
                            pass
                    except:
                        pass
                    result["oracle"] = {"id": id, "dataSetGUID": dataSetGUID, "dbschdule": dbschdule,
                                        "logschdule": logschdule,
                                        "dbstorage": dbstorage, "logstorage": logstorage, "username": username,
                                        "oraclehome": oraclehome, "conn1": conn1, "conn2": conn2, "conn3": conn3,
                                        "name": name}
            if mssql == "1":
                alldataset = DataSet.objects.filter(clientGUID=clientGUID, agentType='MSSQL').exclude(status="9")
                if (len(alldataset) > 0):
                    id = alldataset[0].id
                    dataSetGUID = alldataset[0].dataSetGUID
                    content = alldataset[0].content
                    name = alldataset[0].instanceName
                    dbschdule = ""
                    logschdule = ""
                    dbstorage = ""
                    logstorage = ""
                    username = ""
                    isvvs = ""
                    iscover = ""
                    try:
                        doc = parseString(content)
                        try:
                            dbschdule = (doc.getElementsByTagName("dbschdule"))[0].childNodes[0].data
                        except:
                            pass
                        try:
                            logschdule = (doc.getElementsByTagName("logschdule"))[0].childNodes[0].data
                        except:
                            pass
                        try:
                            dbstorage = (doc.getElementsByTagName("dbstorage"))[0].childNodes[0].data
                        except:
                            pass
                        try:
                            logstorage = (doc.getElementsByTagName("logstorage"))[0].childNodes[0].data
                        except:
                            pass
                        try:
                            backupContentnode = (doc.getElementsByTagName("backupContent"))[0]
                            username = (backupContentnode.getElementsByTagName("username"))[0].childNodes[0].data
                            isvvs = (backupContentnode.getElementsByTagName("isvvs"))[0].childNodes[0].data
                            iscover = (backupContentnode.getElementsByTagName("iscover"))[0].childNodes[0].data
                        except:
                            pass
                    except:
                        pass
                    result["mssql"] = {"id": id, "dataSetGUID": dataSetGUID, "dbschdule": dbschdule,
                                       "logschdule": logschdule,
                                       "dbstorage": dbstorage, "logstorage": logstorage, "username": username,
                                       "isvvs": isvvs, "iscover": iscover, "name": name}
            return HttpResponse(json.dumps(result))


def phyproconfigsaveapp(request):
    if request.user.is_authenticated():
        if request.method == 'POST':
            result = {}
            result["text"] = u"保存成功。"
            clientGUID = request.POST.get('clientGUID', '')
            appGroup = request.POST.get('appGroup', '')

            myclient = ClientHost.objects.get(clientGUID=clientGUID)
            if appGroup == "":
                appGroup = "缺省"
            myclient.appGroup = appGroup
            myclient.save()

            return HttpResponse(json.dumps(result))


def phyproconfigsavefile(request):
    if request.user.is_authenticated():
        if request.method == 'POST':
            result = {}
            result["text"] = u"保存成功。"
            password = request.POST.get('password', '')
            fs = request.POST.get('fs', '')
            clientGUID = request.POST.get('clientGUID', '')
            appGroup = request.POST.get('appGroup', '')
            fs_dataSetGUID = request.POST.get('fs_dataSetGUID', '')
            fs_schdule = request.POST.get('fs_schdule', '')
            fs_storage = request.POST.get('fs_storage', '')
            fs_isBackupOS = request.POST.get('fs_isBackupOS', '')
            fs_backupContent = request.POST.get('fs_backupContent')
            fs_backupContent = fs_backupContent.split("*!-!*")
            fs_isupdate = request.POST.get('fs_isupdate', '')
            user = auth.authenticate(username=request.user.username, password=password)
            if user is not None and user.is_active:
                myclient = ClientHost.objects.get(clientGUID=clientGUID)
                if appGroup == "":
                    appGroup = "缺省"
                myclient.appGroup = appGroup
                myclient.save()

                if (fs == "1"):

                    databaseschdule = ""
                    databasestorage = ""
                    alldataset = DataSet.objects.filter(clientGUID=clientGUID, agentType='FILESYSTEM').exclude(
                        status="9")
                    if (len(alldataset) > 0):
                        try:
                            databasecontent = alldataset[0].content
                            doc = parseString(databasecontent)
                            try:
                                databaseschdule = (doc.getElementsByTagName("schdule"))[0].childNodes[0].data
                            except:
                                pass
                            try:
                                databasestorage = (doc.getElementsByTagName("storage"))[0].childNodes[0].data
                            except:
                                pass
                        except:
                            pass

                    impl = xml.dom.minidom.getDOMImplementation()
                    dom = impl.createDocument(None, 'content', None)
                    root = dom.documentElement
                    backupcontentnode = dom.createElement('backupContent')
                    for path in fs_backupContent:
                        if path != "":
                            pathNode = dom.createElement('path')
                            pathTextNode = dom.createTextNode(path)
                            pathNode.appendChild(pathTextNode)
                            backupcontentnode.appendChild(pathNode)
                        else:
                            fs_backupContent.remove(path)

                    if len(fs_backupContent) == 0:
                        pathNode = dom.createElement('path')
                        pathTextNode = dom.createTextNode("\\")
                        pathNode.appendChild(pathTextNode)
                        backupcontentnode.appendChild(pathNode)
                    root.appendChild(backupcontentnode)
                    schduleNode = dom.createElement('schdule')
                    schduleTextNode = dom.createTextNode(fs_schdule)
                    schduleNode.appendChild(schduleTextNode)
                    root.appendChild(schduleNode)
                    storageNode = dom.createElement('storage')
                    storageTextNode = dom.createTextNode(fs_storage)
                    storageNode.appendChild(storageTextNode)
                    root.appendChild(storageNode)
                    isBackupOSNode = dom.createElement('isBackupOS')
                    isBackupOSTextNode = dom.createTextNode(fs_isBackupOS)
                    isBackupOSNode.appendChild(isBackupOSTextNode)
                    root.appendChild(isBackupOSNode)
                    content = dom.toxml()

                    storagename = None
                    schdulename = None
                    if databasestorage != fs_storage or fs_isupdate == 'TRUE':
                        try:
                            storage = BackupResource.objects.get(id=fs_storage)
                            doc = parseString(storage.certificate)
                            for node in doc.getElementsByTagName("CERT_LIST"):
                                for hostnode in node.getElementsByTagName("CERT"):
                                    storagename = hostnode.getAttribute("name")
                        except:
                            pass
                    if databaseschdule != fs_schdule or fs_isupdate == 'TRUE':
                        try:
                            schdule = SchduleResource.objects.get(id=fs_schdule)
                            doc = parseString(schdule.certificate)
                            for node in doc.getElementsByTagName("CERT_LIST"):
                                for hostnode in node.getElementsByTagName("CERT"):
                                    schdulename = hostnode.getAttribute("name")
                        except:
                            pass

                    paths = fs_backupContent
                    isBackupOS = False
                    if fs_isBackupOS == "TRUE":
                        isBackupOS = True
                    fsBackupContent = {"SPName": storagename, "Schdule": schdulename, "Paths": paths,
                                       "OS": isBackupOS}

                    if fs_dataSetGUID == "0":
                        fs_dataset = DataSet()
                        fs_dataset.dataSetGUID = uuid.uuid1()
                        fs_dataset.clientGUID = myclient.clientGUID
                        fs_dataset.clientName = myclient.clientName
                        fs_dataset.owernID = myclient.owernID
                        fs_dataset.vendor = myclient.vendor
                        fs_dataset.zone = myclient.zone
                        fs_dataset.clientID = myclient.clientID
                        fs_dataset.agentType = "FILESYSTEM"
                        fs_dataset.statu = "0"
                        fs_dataset.content = content
                        fs_dataset.installTime = datetime.datetime.now()
                        fs_dataset.save()
                        result["fs_GUID"] = str(fs_dataset.dataSetGUID)
                    else:
                        fs_dataset = DataSet.objects.get(dataSetGUID=fs_dataSetGUID)
                        fs_dataset.content = content
                        fs_dataset.save()
                        result["fs_GUID"] = str(fs_dataset.dataSetGUID)
                    cvToken = CV_RestApi_Token()
                    cvToken.login(info)
                    cvAPI = CV_API(cvToken)
                    if cvAPI.setFSBackupset(int(myclient.clientID), None, fsBackupContent):
                        pass
                    else:

                        result["text"] += u"应用环境信息异常：服务器端保存失败。" + cvAPI.msg


            else:
                result["text"] = u"密码错误。"

            return HttpResponse(json.dumps(result))


def phyproconfigsaveoracle(request):
    if request.user.is_authenticated():
        if request.method == 'POST':
            result = {}
            result["text"] = u"保存成功。"
            password = request.POST.get('password', '')
            oracle = request.POST.get('oracle', '')
            clientGUID = request.POST.get('clientGUID', '')
            appGroup = request.POST.get('appGroup', '')

            oracle_dataSetGUID = request.POST.get('oracle_dataSetGUID', '')
            oracle_dbschdule = request.POST.get('oracle_dbschdule', '')
            oracle_logschdule = request.POST.get('oracle_logschdule', '')
            oracle_dbstorage = request.POST.get('oracle_dbstorage', '')
            oracle_logstorage = request.POST.get('oracle_logstorage', '')
            oracle_username = request.POST.get('oracle_username', '')
            oracle_name = request.POST.get('oracle_name', '')
            oracle_mypassword = request.POST.get('oracle_mypassword', '')
            oracle_oraclehome = request.POST.get('oracle_oraclehome', '')
            oracle_conn1 = request.POST.get('oracle_conn1', '')
            oracle_conn2 = request.POST.get('oracle_conn2', '')
            oracle_conn3 = request.POST.get('oracle_conn3', '')
            oracle_isupdate = request.POST.get('oracle_isupdate', '')

            user = auth.authenticate(username=request.user.username, password=password)
            if user is not None and user.is_active:
                myclient = ClientHost.objects.get(clientGUID=clientGUID)
                if appGroup == "":
                    appGroup = "缺省"
                myclient.appGroup = appGroup
                myclient.save()

                if (oracle == "1"):
                    databaseschdule = ""
                    databasestorage = ""
                    databaseinstanceName = ""
                    databaseoraclehome = ""
                    databaseusername = ""
                    alldataset = DataSet.objects.filter(clientGUID=clientGUID, agentType='ORACLE').exclude(status="9")
                    if (len(alldataset) > 0):
                        databaseinstanceName = alldataset[0].instanceName
                        databasecontent = alldataset[0].content
                        try:
                            doc = parseString(databasecontent)
                            try:
                                databaseschdule = (doc.getElementsByTagName("dbschdule"))[0].childNodes[0].data
                            except:
                                pass
                            try:
                                databasestorage = (doc.getElementsByTagName("dbstorage"))[0].childNodes[0].data
                            except:
                                pass
                            try:
                                backupContentnode = (doc.getElementsByTagName("backupContent"))[0]

                                databaseusername = (backupContentnode.getElementsByTagName("username"))[0].childNodes[
                                    0].data
                                databaseoraclehome = \
                                    (backupContentnode.getElementsByTagName("oraclehome"))[0].childNodes[0].data
                            except:
                                pass
                        except:
                            pass

                    impl = xml.dom.minidom.getDOMImplementation()
                    dom = impl.createDocument(None, 'content', None)
                    root = dom.documentElement
                    backupNode = dom.createElement('backupContent')
                    usernameNode = dom.createElement('username')
                    usernameTextNode = dom.createTextNode(oracle_username)
                    usernameNode.appendChild(usernameTextNode)
                    backupNode.appendChild(usernameNode)
                    oraclehomeNode = dom.createElement('oraclehome')
                    oraclehomeTextNode = dom.createTextNode(oracle_oraclehome)
                    oraclehomeNode.appendChild(oraclehomeTextNode)
                    backupNode.appendChild(oraclehomeNode)
                    conn1Node = dom.createElement('conn1')
                    conn1TextNode = dom.createTextNode(oracle_conn1)
                    conn1Node.appendChild(conn1TextNode)
                    backupNode.appendChild(conn1Node)
                    conn2Node = dom.createElement('conn2')
                    conn2TextNode = dom.createTextNode(oracle_conn2)
                    conn2Node.appendChild(conn2TextNode)
                    backupNode.appendChild(conn2Node)
                    conn3Node = dom.createElement('conn3')
                    conn3TextNode = dom.createTextNode(oracle_conn3)
                    conn3Node.appendChild(conn3TextNode)
                    backupNode.appendChild(conn3Node)
                    root.appendChild(backupNode)

                    schduleNode = dom.createElement('schdule')
                    dbschduleNode = dom.createElement('dbschdule')
                    dbschduleTextNode = dom.createTextNode(oracle_dbschdule)
                    dbschduleNode.appendChild(dbschduleTextNode)
                    schduleNode.appendChild(dbschduleNode)
                    logschduleNode = dom.createElement('logschdule')
                    logschduleTextNode = dom.createTextNode(oracle_logschdule)
                    logschduleNode.appendChild(logschduleTextNode)
                    schduleNode.appendChild(logschduleNode)
                    root.appendChild(schduleNode)
                    storageNode = dom.createElement('storage')
                    dbstorageNode = dom.createElement('dbstorage')
                    dbstorageTextNode = dom.createTextNode(oracle_dbstorage)
                    dbstorageNode.appendChild(dbstorageTextNode)
                    storageNode.appendChild(dbstorageNode)
                    logstorageNode = dom.createElement('logstorage')
                    logstorageTextNode = dom.createTextNode(oracle_logstorage)
                    logstorageNode.appendChild(logstorageTextNode)
                    storageNode.appendChild(logstorageNode)
                    root.appendChild(storageNode)
                    content = dom.toxml()

                    clientName = myclient.clientName
                    clientNames = clientName.split('.')
                    clientName = clientNames[0]
                    storagename = None
                    schdulename = None
                    if databasestorage != oracle_dbstorage or oracle_isupdate == 'TRUE':
                        try:
                            storage = BackupResource.objects.get(id=oracle_dbstorage)
                            doc = parseString(storage.certificate)
                            for node in doc.getElementsByTagName("CERT_LIST"):
                                for hostnode in node.getElementsByTagName("CERT"):
                                    storagename = hostnode.getAttribute("name")
                        except:
                            pass
                    if databaseschdule != oracle_dbschdule or oracle_isupdate == 'TRUE':
                        try:
                            schdule = SchduleResource.objects.get(id=oracle_dbschdule)
                            doc = parseString(schdule.certificate)
                            for node in doc.getElementsByTagName("CERT_LIST"):
                                for hostnode in node.getElementsByTagName("CERT"):
                                    schdulename = hostnode.getAttribute("name")
                        except:
                            pass
                    oraCreditInfo = None
                    if databaseinstanceName != oracle_name or databasestorage != oracle_dbstorage or databaseoraclehome != oracle_oraclehome or databaseusername != oracle_username or oracle_isupdate == 'TRUE':
                        oraCreditInfo = {"instanceName": oracle_name,
                                         "userName": oracle_username, "passwd": oracle_mypassword, "OCS": "/",
                                         "SPName": storagename,
                                         "ORACLE-HOME": oracle_oraclehome,
                                         "Server": clientName}
                    oraBackupContent = {"SPName": storagename, "Schdule": schdulename}

                    if oracle_dataSetGUID == "0":
                        oracle_dataset = DataSet()
                        oracle_dataset.dataSetGUID = uuid.uuid1()
                        oracle_dataset.clientGUID = myclient.clientGUID
                        oracle_dataset.clientName = myclient.clientName
                        oracle_dataset.owernID = myclient.owernID
                        oracle_dataset.vendor = myclient.vendor
                        oracle_dataset.zone = myclient.zone
                        oracle_dataset.clientID = myclient.clientID
                        oracle_dataset.agentType = "ORACLE"
                        oracle_dataset.statu = "0"
                        oracle_dataset.instanceName = oracle_name
                        oracle_dataset.content = content
                        oracle_dataset.installTime = datetime.datetime.now()
                        oracle_dataset.save()
                        result["oracle_GUID"] = str(oracle_dataset.dataSetGUID)
                    else:
                        oracle_dataset = DataSet.objects.get(dataSetGUID=oracle_dataSetGUID)
                        oracle_dataset.content = content
                        oracle_dataset.instanceName = oracle_name
                        oracle_dataset.save()
                        result["oracle_GUID"] = str(oracle_dataset.dataSetGUID)
                    cvToken = CV_RestApi_Token()
                    cvToken.login(info)
                    cvAPI = CV_API(cvToken)
                    if cvAPI.setOracleBackupset(int(myclient.clientID), oracle_name, oraCreditInfo, oraBackupContent):
                        pass
                    else:
                        # b = cvClient.receiveText
                        # b=b.decode('gbk')
                        result["text"] += u"ORACLE信息异常：服务器端保存失败。" + cvAPI.msg

            else:
                result["text"] = u"密码错误。"

            return HttpResponse(json.dumps(result))


def phyproconfigsavemssql(request):
    if request.user.is_authenticated():
        if request.method == 'POST':
            result = {}
            result["text"] = u"保存成功。"
            password = request.POST.get('password', '')

            mssql = request.POST.get('mssql', '')
            clientGUID = request.POST.get('clientGUID', '')
            appGroup = request.POST.get('appGroup', '')

            mssql_dataSetGUID = request.POST.get('mssql_dataSetGUID', '')
            mssql_dbschdule = request.POST.get('mssql_dbschdule', '')
            mssql_logschdule = request.POST.get('mssql_logschdule', '')
            mssql_dbstorage = request.POST.get('mssql_dbstorage', '')
            mssql_logstorage = request.POST.get('mssql_logstorage', '')
            mssql_name = request.POST.get('mssql_name', '')
            mssql_username = request.POST.get('mssql_username', '')
            mssql_mypassword = request.POST.get('mssql_mypassword', '')
            mssql_isvvs = request.POST.get('mssql_isvvs', '')
            mssql_iscover = request.POST.get('mssql_iscover', '')
            mssql_isupdate = request.POST.get('mssql_isupdate', '')
            user = auth.authenticate(username=request.user.username, password=password)
            if user is not None and user.is_active:
                myclient = ClientHost.objects.get(clientGUID=clientGUID)
                if appGroup == "":
                    appGroup = "缺省"
                myclient.appGroup = appGroup
                myclient.save()
                if (mssql == "1"):
                    databaseschdule = ""
                    databasestorage = ""
                    databaseinstanceName = ""
                    alldataset = DataSet.objects.filter(clientGUID=clientGUID, agentType='MSSQL').exclude(status="9")
                    if (len(alldataset) > 0):
                        databaseinstanceName = alldataset[0].instanceName
                        databasecontent = alldataset[0].content
                        try:
                            doc = parseString(databasecontent)
                            try:
                                databaseschdule = (doc.getElementsByTagName("dbschdule"))[0].childNodes[0].data
                            except:
                                pass
                            try:
                                databasestorage = (doc.getElementsByTagName("dbstorage"))[0].childNodes[0].data
                            except:
                                pass
                        except:
                            pass

                    impl = xml.dom.minidom.getDOMImplementation()
                    dom = impl.createDocument(None, 'content', None)
                    root = dom.documentElement
                    backupNode = dom.createElement('backupContent')
                    usernameNode = dom.createElement('username')
                    usernameTextNode = dom.createTextNode(mssql_username)
                    usernameNode.appendChild(usernameTextNode)
                    backupNode.appendChild(usernameNode)

                    isvvsNode = dom.createElement('isvvs')
                    isvvsTextNode = dom.createTextNode(mssql_isvvs)
                    isvvsNode.appendChild(isvvsTextNode)
                    backupNode.appendChild(isvvsNode)
                    iscoverNode = dom.createElement('iscover')
                    iscoverTextNode = dom.createTextNode(mssql_iscover)
                    iscoverNode.appendChild(iscoverTextNode)
                    backupNode.appendChild(iscoverNode)
                    root.appendChild(backupNode)

                    schduleNode = dom.createElement('schdule')
                    dbschduleNode = dom.createElement('dbschdule')
                    dbschduleTextNode = dom.createTextNode(mssql_dbschdule)
                    dbschduleNode.appendChild(dbschduleTextNode)
                    schduleNode.appendChild(dbschduleNode)
                    logschduleNode = dom.createElement('logschdule')
                    logschduleTextNode = dom.createTextNode(mssql_logschdule)
                    logschduleNode.appendChild(logschduleTextNode)
                    schduleNode.appendChild(logschduleNode)
                    root.appendChild(schduleNode)
                    storageNode = dom.createElement('storage')
                    dbstorageNode = dom.createElement('dbstorage')
                    dbstorageTextNode = dom.createTextNode(mssql_dbstorage)
                    dbstorageNode.appendChild(dbstorageTextNode)
                    storageNode.appendChild(dbstorageNode)
                    logstorageNode = dom.createElement('logstorage')
                    logstorageTextNode = dom.createTextNode(mssql_logstorage)
                    logstorageNode.appendChild(logstorageTextNode)
                    storageNode.appendChild(logstorageNode)
                    root.appendChild(storageNode)
                    content = dom.toxml()

                    clientName = myclient.clientName
                    clientNames = clientName.split('.')
                    clientName = clientNames[0]
                    storagename = None
                    schdulename = None
                    if databasestorage != mssql_dbstorage or mssql_isupdate == 'TRUE':
                        try:
                            storage = BackupResource.objects.get(id=mssql_dbstorage)
                            doc = parseString(storage.certificate)
                            for node in doc.getElementsByTagName("CERT_LIST"):
                                for hostnode in node.getElementsByTagName("CERT"):
                                    storagename = hostnode.getAttribute("name")
                        except:
                            pass
                    if databaseschdule != mssql_dbschdule or mssql_isupdate == 'TRUE':
                        try:
                            schdule = SchduleResource.objects.get(id=mssql_dbschdule)
                            doc = parseString(schdule.certificate)
                            for node in doc.getElementsByTagName("CERT_LIST"):
                                for hostnode in node.getElementsByTagName("CERT"):
                                    schdulename = hostnode.getAttribute("name")
                        except:
                            pass
                    mssqlCreditInfo = None
                    if databaseinstanceName != mssql_name or databasestorage != mssql_dbstorage or mssql_isupdate == 'TRUE':
                        mssqlCreditInfo = {"instanceName": mssql_name, "SPName": storagename,
                                           "userName": mssql_username, "passwd": mssql_mypassword,
                                           "useVss": "True", "Server": clientName}
                    mssqlBackupContent = {"SPName": storagename, "Schdule": schdulename}

                    if mssql_dataSetGUID == "0":
                        mssql_dataset = DataSet()
                        mssql_dataset.dataSetGUID = uuid.uuid1()
                        mssql_dataset.clientGUID = myclient.clientGUID
                        mssql_dataset.clientName = myclient.clientName
                        mssql_dataset.owernID = myclient.owernID
                        mssql_dataset.vendor = myclient.vendor
                        mssql_dataset.zone = myclient.zone
                        mssql_dataset.clientID = myclient.clientID
                        mssql_dataset.agentType = "MSSQL"
                        mssql_dataset.instanceName = mssql_name
                        mssql_dataset.statu = "0"
                        mssql_dataset.content = content
                        mssql_dataset.installTime = datetime.datetime.now()
                        mssql_dataset.save()
                        result["mssql_GUID"] = str(mssql_dataset.dataSetGUID)
                    else:
                        mssql_dataset = DataSet.objects.get(dataSetGUID=mssql_dataSetGUID)
                        mssql_dataset.content = content
                        mssql_dataset.instanceName = mssql_name
                        mssql_dataset.save()
                        result["mssql_GUID"] = str(mssql_dataset.dataSetGUID)
                    cvToken = CV_RestApi_Token()
                    cvToken.login(info)
                    cvAPI = CV_API(cvToken)
                    if cvAPI.setMssqlBackupset(int(myclient.clientID), mssql_name, mssqlCreditInfo, mssqlBackupContent):
                        pass
                    else:
                        # b = cvClient.receiveText
                        # b=b.decode('gbk')
                        result["text"] += u"MSSQL信息异常：服务器端保存失败。" + cvAPI.msg

            else:
                result["text"] = u"密码错误。"

            return HttpResponse(json.dumps(result))


def vmproconfig(request):
    if request.user.is_authenticated():
        backupresource = BackupResource.objects.exclude(state="9")
        schduleresource = SchduleResource.objects.exclude(state="9").filter(specifications__contains='type="虚机"')
        backups = []
        for backup in backupresource:
            backups.append({"id": backup.id, "name": backup.name + "(" + backup.description + ")"})
        schdules = []
        for schdule in schduleresource:
            schdules.append({"id": schdule.id, "name": schdule.name + "(" + schdule.description + ")"})

        allhost = ClientHost.objects.exclude(status="9").filter(hostType="physical box").filter(
            owernID=request.user.userinfo.userGUID)
        pyhhost = []
        if (len(allhost) > 0):
            for host in allhost:
                agentTypeList = host.agentTypeList
                doc = parseString(agentTypeList)
                for node in doc.getElementsByTagName("agentTypeList"):
                    for agenttypenode in node.getElementsByTagName("agentType"):
                        if agenttypenode.childNodes[0].data == "Virtual Server":
                            clientName = host.clientName
                            clientNames = clientName.split('.')
                            clientName = clientNames[0]
                            pyhhost.append({"GUID": host.clientGUID, "NAME": clientName})
                            break
        return render(request, 'vmproconfig.html',
                      {'username': request.user.userinfo.fullname, "backupresource": backups,
                       "schduleresource": schdules, "pyhhost": pyhhost, "vmproconfigpage": True})
    else:
        return HttpResponseRedirect("/login")


def vmproconfigdata(request):
    if request.user.is_authenticated():
        result = []
        allhost = ClientHost.objects.exclude(status="9").filter(hostType="VMWARE").filter(
            owernID=request.user.userinfo.userGUID)
        if (len(allhost) > 0):
            for host in allhost:
                clientName = host.clientName
                clientNames = clientName.split('.')
                clientName = clientNames[0]
                clientGUID = host.clientGUID
                proxyClientID = host.proxyClientID
                creditInfo = host.creditInfo
                platform = host.platform
                status = "否"
                if host.status == "1":
                    status = "是"
                proxylist = []

                hostname = ""
                username = ""
                password = ""
                if creditInfo != "" and creditInfo != None:
                    doc = parseString(creditInfo)
                    for node in doc.getElementsByTagName("creditInfo"):
                        for hostnode in node.getElementsByTagName("HOST"):
                            hostname = hostnode.childNodes[0].data
                        for usernode in node.getElementsByTagName("USER"):
                            username = usernode.childNodes[0].data
                        for passwordnode in node.getElementsByTagName("PASSWD"):
                            password = passwordnode.childNodes[0].data
                if proxyClientID != "" and proxyClientID != None:
                    doc = parseString(proxyClientID)
                    for node in doc.getElementsByTagName("PROXYLIST"):
                        for proxylistnode in node.getElementsByTagName("PROXY"):
                            try:
                                proxy = ClientHost.objects.get(clientGUID=proxylistnode.childNodes[0].data)
                                proxylist.append({"clientGUID": proxy.clientGUID, "clientName": proxy.clientName, })
                            except:
                                pass

                alldataset = DataSet.objects.filter(clientGUID=clientGUID).exclude(status="9")
                if len(alldataset) > 0:
                    for dataset in alldataset:
                        appGroup = dataset.appGroup
                        dataSetGUID = dataset.dataSetGUID
                        content = dataset.content
                        schdule = ""
                        storage = ""
                        backupContentlist = []
                        if content != "" and content != None:
                            doc = parseString(content)
                            try:
                                schdule = (doc.getElementsByTagName("schdule"))[0].childNodes[0].data
                            except:
                                pass
                            try:
                                storage = (doc.getElementsByTagName("storage"))[0].childNodes[0].data
                            except:
                                pass
                            try:
                                for node in doc.getElementsByTagName("backupContent"):
                                    a = len(node.getElementsByTagName("VM"))
                                    for vmlistnode in node.getElementsByTagName("VM"):
                                        try:
                                            backupContentlist.append(vmlistnode.childNodes[0].data)

                                        except:
                                            pass
                            except:
                                pass

                        result.append(
                            {"clientName": clientName, "clientGUID": clientGUID, "platform": platform,
                             "proxylist": proxylist, "hostname": hostname, "username": username, "password": password,
                             "appGroup": appGroup,
                             "status": status, "dataSetGUID": dataSetGUID, "schdule": schdule, "storage": storage,
                             "backupContent": backupContentlist})
                else:
                    result.append(
                        {"clientName": clientName, "clientGUID": clientGUID, "platform": platform,
                         "proxylist": proxylist, "hostname": hostname, "username": username, "password": password,
                         "appGroup": "",
                         "status": status, "dataSetGUID": "", "schdule": "", "storage": "", "backupContent": []})
        return HttpResponse(json.dumps({"data": result}))


def getvmlist(request):
    if request.user.is_authenticated() and request.session['isadmin']:
        result = []
        if request.method == 'POST':
            result = []
            clientGUID = request.POST.get('clientGUID', '')
            allhost = ClientHost.objects.exclude(status="9").filter(hostType="VMWARE").filter(
                clientGUID=clientGUID)
            if (len(allhost) > 0):
                cvToken = CV_RestApi_Token()
                cvToken.login(info)
                cvAPI = CV_API(cvToken)
                vmlist = cvAPI.getVMWareVMList(allhost[0].clientName)
                for node in vmlist:
                    result.append({"vmid": node["VMName"], "vmname": node["VMName"]})


        return HttpResponse(json.dumps(result))


def vmproconfigsave(request):
    if request.user.is_authenticated():
        if request.method == 'POST':
            result = ""

            password = request.POST.get('password', '')
            clientGUID = request.POST.get('clientGUID', '')
            clientName = request.POST.get('clientName', '')
            hostname = request.POST.get('hostname', '')
            username = request.POST.get('username', '')
            mypassword = request.POST.get('mypassword', '')
            pyhhostlist = request.POST.get('pyhhostlist', '')
            pyhhostlist = pyhhostlist.split("*!-!*")

            user = auth.authenticate(username=request.user.username, password=password)
            if user is not None and user.is_active:
                creditInfo = ""
                proxyClientID = ""

                impl = xml.dom.minidom.getDOMImplementation()
                dom = impl.createDocument(None, 'creditInfo', None)
                root = dom.documentElement
                hostnamenode = dom.createElement('HOST')
                hostnameTextNode = dom.createTextNode(hostname)
                hostnamenode.appendChild(hostnameTextNode)
                root.appendChild(hostnamenode)
                usernamenode = dom.createElement('USER')
                usernameTextNode = dom.createTextNode(username)
                usernamenode.appendChild(usernameTextNode)
                root.appendChild(usernamenode)
                # passwordnode = dom.createElement('PASSWD')
                # passwordTextNode = dom.createTextNode(mypassword)
                # passwordnode.appendChild(passwordTextNode)
                # root.appendChild(passwordnode)
                creditInfo = dom.toxml()

                root = dom.documentElement
                dom = impl.createDocument(None, 'PROXYLIST', None)
                root = dom.documentElement
                for pyhhost in pyhhostlist:
                    if pyhhost != "":
                        proxyNode = dom.createElement('PROXY')
                        proxyTextNode = dom.createTextNode(pyhhost)
                        proxyNode.appendChild(proxyTextNode)
                        root.appendChild(proxyNode)
                proxyClientID = dom.toxml()

                if clientGUID == "0":
                    vsProxy = []
                    for pyhhost in pyhhostlist:
                        if pyhhost != "":
                            try:
                                pyclient = ClientHost.objects.get(clientGUID=pyhhost)
                                vsProxy.append(pyclient.clientName)
                            except:
                                pass
                    if len(vsProxy) == 0:
                        vsProxy = [""]
                    vsaClientInfo = {"vCenterHost": hostname, "proxyList": vsProxy, "userName": username,
                                     "passwd": mypassword}

                    cvToken = CV_RestApi_Token()
                    cvToken.login(info)
                    cvAPI = CV_API(cvToken)
                    rc = cvAPI.setVMWareClient(clientName + "." + request.user.username, vsaClientInfo)
                    if rc:
                        clientID = 0
                        try:
                            clentinfo = cvAPI.getClientInfo(clientName + "." + request.user.username)
                            clientID = clentinfo["clientId"]
                        except:
                            pass
                        client = ClientHost()
                        client.clientGUID = uuid.uuid1()
                        client.clientName = clientName + "." + request.user.username
                        client.owernID = request.user.userinfo.userGUID
                        client.clientID = clientID
                        client.hostType = "VMWARE"
                        client.proxyClientID = proxyClientID
                        client.creditInfo = creditInfo
                        client.status = "0"
                        client.platform = "VMWARE"
                        client.installTime = datetime.datetime.now()
                        client.save()
                        result = u"保存成功。"
                    else:
                        # b = cvClient.receiveText
                        # b=b.decode('gbk')
                        result = u"服务器端异常:" + cvAPI.msg + u",新增失败。"
                else:
                    client = ClientHost.objects.get(clientGUID=clientGUID)
                    client.creditInfo = creditInfo
                    client.proxyClientID = proxyClientID
                    client.clientName = clientName + "." + request.user.username
                    client.save()
                    result = u"保存成功。"

            else:
                result = u"密码错误。"

            return HttpResponse(result)


def vmappsave(request):
    if request.user.is_authenticated():
        if request.method == 'POST':
            result = ""

            password = request.POST.get('password', '')
            dataSetGUID = request.POST.get('dataSetGUID', '')
            appGroup = request.POST.get('appGroup', '')
            backupContent = request.POST.get('backupContent', '')
            schdule = request.POST.get('schdule', '')
            storage = request.POST.get('storage', '')
            myclientGUID = request.POST.get('myclientGUID', '')
            backupContentlist = backupContent.split("*!-!*")
            backupContentlist.remove("")

            user = auth.authenticate(username=request.user.username, password=password)
            if user is not None and user.is_active:
                content = ""
                impl = xml.dom.minidom.getDOMImplementation()
                dom = impl.createDocument(None, 'content', None)
                root = dom.documentElement
                backupcontentnode = dom.createElement('backupContent')
                for backupContent in backupContentlist:
                    if backupContent != "":
                        vmNode = dom.createElement('VM')
                        vmTextNode = dom.createTextNode(backupContent)
                        vmNode.appendChild(vmTextNode)
                        backupcontentnode.appendChild(vmNode)
                root.appendChild(backupcontentnode)
                schduleNode = dom.createElement('schdule')
                schduleTextNode = dom.createTextNode(schdule)
                schduleNode.appendChild(schduleTextNode)
                root.appendChild(schduleNode)
                storageNode = dom.createElement('storage')
                storageTextNode = dom.createTextNode(storage)
                storageNode.appendChild(storageTextNode)
                root.appendChild(storageNode)
                content = dom.toxml()
                myclient = ClientHost.objects.get(clientGUID=myclientGUID)

                databaseschdule = ""
                databasestorage = ""
                alldataset = DataSet.objects.filter(dataSetGUID=dataSetGUID)
                if (len(alldataset) > 0):
                    databasecontent = alldataset[0].content
                    doc = parseString(databasecontent)
                    try:
                        databaseschdule = (doc.getElementsByTagName("dbschdule"))[0].childNodes[0].data
                    except:
                        pass
                    try:
                        databasestorage = (doc.getElementsByTagName("dbstorage"))[0].childNodes[0].data
                    except:
                        pass
                storagename = None
                schdulename = None
                if databasestorage != storage:
                    try:
                        storage = BackupResource.objects.get(id=storage)
                        doc = parseString(storage.certificate)
                        for node in doc.getElementsByTagName("CERT_LIST"):
                            for hostnode in node.getElementsByTagName("CERT"):
                                storagename = hostnode.getAttribute("name")
                    except:
                        pass
                if databaseschdule != schdule:
                    try:
                        schdule = SchduleResource.objects.get(id=schdule)
                        doc = parseString(schdule.certificate)
                        for node in doc.getElementsByTagName("CERT_LIST"):
                            for hostnode in node.getElementsByTagName("CERT"):
                                schdulename = hostnode.getAttribute("name")
                    except:
                        pass

                if dataSetGUID == "0":
                    dataset = DataSet()
                    dataset.dataSetGUID = uuid.uuid1()
                    dataset.clientGUID = myclient.clientGUID
                    dataset.clientName = myclient.clientName
                    dataset.owernID = myclient.owernID
                    dataset.vendor = myclient.vendor
                    dataset.zone = myclient.zone
                    dataset.clientID = myclient.clientID
                    dataset.agentType = "Virtual Server"
                    dataset.statu = "0"
                    dataset.content = content
                    dataset.installTime = datetime.datetime.now()
                    dataset.appGroup = appGroup
                    dataset.save()
                    result = "保存成功。"
                else:
                    dataset = DataSet.objects.get(dataSetGUID=dataSetGUID)
                    dataset.content = content
                    dataset.appGroup = appGroup
                    dataset.save()
                    result = "保存成功。"

                proxylist = []
                if myclient.proxyClientID != "" and myclient.proxyClientID != None:
                    doc = parseString(myclient.proxyClientID)
                    for node in doc.getElementsByTagName("PROXYLIST"):
                        for proxylistnode in node.getElementsByTagName("PROXY"):
                            try:
                                proxy = ClientHost.objects.get(clientGUID=proxylistnode.childNodes[0].data)
                                listclientName = proxy.clientName
                                proxylist.append(listclientName)
                            except:
                                pass

                vsaBackupsetInfo = {"proxyList": proxylist, "vmList": backupContentlist, "SPName": storagename,
                                    "Schdule": schdulename}
                cvToken = CV_RestApi_Token()
                cvToken.login(info)
                cvAPI = CV_API(cvToken)
                if cvAPI.setVMWareBackupset(myclient.clientName, appGroup, vsaBackupsetInfo):
                    pass
                else:
                    result += u"虚机信息异常：服务器端保存失败。" + cvAPI.msg

            else:
                result = u"密码错误。"

            return HttpResponse(result)


def vmproconfigdel(request):
    if request.user.is_authenticated():
        if request.method == 'POST':
            clientGUID = request.POST.get('clientGUID', '')
            client = ClientHost.objects.get(clientGUID=clientGUID)
            info = {"webaddr": "test1", "port": "81", "username": "cvadmin", "passwd": "1qaz@WSX", "token": "",
                    "lastlogin": 0}
            cvToken = CV_RestApi_Token()
            cvToken.login(info)
            cvClient = CV_Client(cvToken, None)
            rs = cvClient.delVSAClient(client.clientName)
            if rs:
                client.status = "9"
                client.save()
                return HttpResponse("删除成功。")
            else:
                return HttpResponse(u"服务器端异常:" + cvClient.msg + u"，删除失败。")
        else:
            return HttpResponse("删除失败。")


def vmappdel(request):
    if request.user.is_authenticated():
        if request.method == 'POST':
            dataSetGUID = request.POST.get('dataSetGUID', '')
            dataset = DataSet.objects.get(dataSetGUID=dataSetGUID)
            dataset.status = "9"
            dataset.save()
            return HttpResponse("删除成功。")
        else:
            return HttpResponse("删除失败。")


def racproconfig(request):
    if request.user.is_authenticated():
        backupresource = BackupResource.objects.exclude(state="9")
        schduleresource = SchduleResource.objects.exclude(state="9").filter(specifications__contains='type="数据库"')
        backups = []
        for backup in backupresource:
            backups.append({"id": backup.id, "name": backup.name + "(" + backup.description + ")"})
        schdules = []
        for schdule in schduleresource:
            schdules.append({"id": schdule.id, "name": schdule.name + "(" + schdule.description + ")"})

        allhost = ClientHost.objects.exclude(status="9").filter(hostType="physical box").filter(
            owernID=request.user.userinfo.userGUID)
        pyhhost = []
        if (len(allhost) > 0):
            for host in allhost:
                agentTypeList = host.agentTypeList
                doc = parseString(agentTypeList)
                for node in doc.getElementsByTagName("agentTypeList"):
                    for agenttypenode in node.getElementsByTagName("agentType"):
                        if agenttypenode.childNodes[0].data == "ORACLE":
                            clientName = host.clientName
                            clientNames = clientName.split('.')
                            clientName = clientNames[0]
                            pyhhost.append({"GUID": host.clientGUID, "NAME": clientName})
                            break
        return render(request, 'racproconfig.html',
                      {'username': request.user.userinfo.fullname, "backupresource": backups,
                       "schduleresource": schdules, "pyhhost": pyhhost, "racproconfigpage": True})
    else:
        return HttpResponseRedirect("/login")


def racproconfigdata(request):
    if request.user.is_authenticated():
        result = []
        allhost = ClientHost.objects.exclude(status="9").filter(hostType="RAC").filter(
            owernID=request.user.userinfo.userGUID)
        if (len(allhost) > 0):
            for host in allhost:
                clientName = host.clientName
                clientNames = clientName.split('.')
                clientName = clientNames[0]
                clientGUID = host.clientGUID
                platform = host.platform
                proxyClientID = host.proxyClientID
                status = "否"
                if host.status == "1":
                    status = "是"
                proxylist = []
                if proxyClientID != "" and proxyClientID != None:
                    doc = parseString(proxyClientID)
                    for node in doc.getElementsByTagName("PROXYLIST"):
                        for proxylistnode in node.getElementsByTagName("PROXY"):
                            try:
                                proxy = ClientHost.objects.get(clientGUID=proxylistnode.childNodes[0].data)
                                listclientName = proxy.clientName
                                listclientName = listclientName.split('.')
                                listclientName = listclientName[0]
                                proxylist.append({"clientGUID": proxy.clientGUID, "clientName": listclientName})
                            except:
                                pass
                oracle_dbschdule = ""
                oracle_logschdule = ""
                oracle_dbstorage = ""
                oracle_logstorage = ""
                raclist = []
                databaseName = ""
                dataSetGUID = ""

                dataset = DataSet.objects.exclude(status="9").filter(clientGUID=clientGUID)
                if (len(dataset) > 0):
                    dataSetGUID = dataset[0].dataSetGUID
                    databaseName = dataset[0].instanceName
                    content = dataset[0].content
                    doc = parseString(content)
                    try:
                        oracle_dbschdule = (doc.getElementsByTagName("dbschdule"))[0].childNodes[0].data
                    except:
                        pass
                    try:
                        oracle_logschdule = (doc.getElementsByTagName("logschdule"))[0].childNodes[0].data
                    except:
                        pass
                    try:
                        oracle_dbstorage = (doc.getElementsByTagName("dbstorage"))[0].childNodes[0].data
                    except:
                        pass
                    try:
                        oracle_logstorage = (doc.getElementsByTagName("logstorage"))[0].childNodes[0].data
                    except:
                        pass
                    try:
                        backupContentnode = (doc.getElementsByTagName("backupContent"))[0]
                        for raclistnode in backupContentnode.getElementsByTagName("rac"):
                            rac_name = ""
                            rac_username = ""
                            rac_oraclehome = ""
                            rac_conn1 = ""
                            rac_conn2 = ""
                            rac_conn3 = ""
                            pyhGUID = ""
                            pyhclientName = ""
                            try:
                                pyhGUID = (raclistnode.getElementsByTagName("pyhGUID"))[0].childNodes[0].data
                                pyhclient = ClientHost.objects.exclude(status="9").filter(clientGUID=pyhGUID)
                                if len(pyhclient) > 0:
                                    pyhclientName = pyhclient[0].clientName
                                    pyhclientName = pyhclientName.split('.')
                                    pyhclientName = pyhclientName[0]
                            except:
                                pass

                            try:
                                rac_name = (raclistnode.getElementsByTagName("name"))[0].childNodes[0].data
                            except:
                                pass
                            try:
                                rac_username = (raclistnode.getElementsByTagName("username"))[0].childNodes[0].data
                            except:
                                pass
                            try:
                                rac_oraclehome = (raclistnode.getElementsByTagName("oraclehome"))[0].childNodes[0].data
                            except:
                                pass
                            try:
                                rac_conn1 = (raclistnode.getElementsByTagName("conn1"))[0].childNodes[0].data
                            except:
                                pass
                            try:
                                rac_conn2 = (raclistnode.getElementsByTagName("conn2"))[0].childNodes[0].data
                            except:
                                pass
                            try:
                                rac_conn3 = (raclistnode.getElementsByTagName("conn3"))[0].childNodes[0].data
                            except:
                                pass
                            raclist.append({"pyhGUID": pyhGUID, "pyhclientName": pyhclientName, "name": rac_name,
                                            "username": rac_username, "oraclehome": rac_oraclehome,
                                            "conn1": rac_conn1, "conn2": rac_conn2, "conn3": rac_conn3})
                    except:
                        pass

                result.append({"clientName": clientName, "clientGUID": clientGUID, "platform": platform,
                               "dataSetGUID": dataSetGUID, "proxylist": proxylist,
                               "status": status, "databaseName": databaseName, "oracle_dbschdule": oracle_dbschdule,
                               "oracle_logschdule": oracle_logschdule
                                  , "oracle_dbstorage": oracle_dbstorage, "oracle_logstorage": oracle_logstorage,
                               "raclist": raclist})
        return HttpResponse(json.dumps({"data": result}))


def racproconfigsave(request):
    if request.user.is_authenticated():
        if request.method == 'POST':
            result = u"保存成功。"
            password = request.POST.get('password', '')
            clientGUID = request.POST.get('clientGUID', '')
            clientName = request.POST.get('clientName', '')
            databaseName = request.POST.get('databaseName', '')
            dataSetGUID = request.POST.get('dataSetGUID', '')
            pyhhostlist = request.POST.get('pyhhostlist', '')
            pyhhostlist = pyhhostlist.split("*!-!*")
            oracle_dbschdule = request.POST.get('oracle_dbschdule', '')
            oracle_logschdule = request.POST.get('oracle_logschdule', '')
            oracle_dbstorage = request.POST.get('oracle_dbstorage', '')
            oracle_logstorage = request.POST.get('oracle_logstorage', '')

            oracle_name_1 = request.POST.get('oracle_name_1', '')
            oracle_username_1 = request.POST.get('oracle_username_1', '')
            oracle_mypassword_1 = request.POST.get('oracle_mypassword_1', '')
            oracle_oraclehome_1 = request.POST.get('oracle_oraclehome_1', '')
            oracle_conn1_1 = request.POST.get('oracle_conn1_1', '')
            oracle_conn2_1 = request.POST.get('oracle_conn2_1', '')
            oracle_conn3_1 = request.POST.get('oracle_conn3_1', '')
            oracle_pyhGUID_1 = request.POST.get('oracle_pyhGUID_1', '')

            oracle_name_2 = request.POST.get('oracle_name_2', '')
            oracle_username_2 = request.POST.get('oracle_username_2', '')
            oracle_mypassword_2 = request.POST.get('oracle_mypassword_2', '')
            oracle_oraclehome_2 = request.POST.get('oracle_oraclehome_2', '')
            oracle_conn1_2 = request.POST.get('oracle_conn1_2', '')
            oracle_conn2_2 = request.POST.get('oracle_conn2_2', '')
            oracle_conn3_2 = request.POST.get('oracle_conn3_2', '')
            oracle_pyhGUID_2 = request.POST.get('oracle_pyhGUID_2', '')

            oracle_name_3 = request.POST.get('oracle_name_3', '')
            oracle_username_3 = request.POST.get('oracle_username_3', '')
            oracle_mypassword_3 = request.POST.get('oracle_mypassword_3', '')
            oracle_oraclehome_3 = request.POST.get('oracle_oraclehome_3', '')
            oracle_conn1_3 = request.POST.get('oracle_conn1_3', '')
            oracle_conn2_3 = request.POST.get('oracle_conn2_3', '')
            oracle_conn3_3 = request.POST.get('oracle_conn3_3', '')
            oracle_pyhGUID_3 = request.POST.get('oracle_pyhGUID_3', '')

            oracle_name_4 = request.POST.get('oracle_name_4', '')
            oracle_username_4 = request.POST.get('oracle_username_4', '')
            oracle_mypassword_4 = request.POST.get('oracle_mypassword_4', '')
            oracle_oraclehome_4 = request.POST.get('oracle_oraclehome_4', '')
            oracle_conn1_4 = request.POST.get('oracle_conn1_4', '')
            oracle_conn2_4 = request.POST.get('oracle_conn2_4', '')
            oracle_conn3_4 = request.POST.get('oracle_conn3_4', '')
            oracle_pyhGUID_4 = request.POST.get('oracle_pyhGUID_4', '')

            oracle_name_5 = request.POST.get('oracle_name_5', '')
            oracle_username_5 = request.POST.get('oracle_username_5', '')
            oracle_mypassword_5 = request.POST.get('oracle_mypassword_5', '')
            oracle_oraclehome_5 = request.POST.get('oracle_oraclehome_5', '')
            oracle_conn1_5 = request.POST.get('oracle_conn1_5', '')
            oracle_conn2_5 = request.POST.get('oracle_conn2_5', '')
            oracle_conn3_5 = request.POST.get('oracle_conn3_5', '')
            oracle_pyhGUID_5 = request.POST.get('oracle_pyhGUID_5', '')

            user = auth.authenticate(username=request.user.username, password=password)
            if user is not None and user.is_active:
                proxyClientID = ""
                impl = xml.dom.minidom.getDOMImplementation()
                dom = impl.createDocument(None, 'PROXYLIST', None)
                root = dom.documentElement
                for pyhhost in pyhhostlist:
                    if pyhhost != "":
                        proxyNode = dom.createElement('PROXY')
                        proxyTextNode = dom.createTextNode(pyhhost)
                        proxyNode.appendChild(proxyTextNode)
                        root.appendChild(proxyNode)
                proxyClientID = dom.toxml()

                content = ""
                impl = xml.dom.minidom.getDOMImplementation()
                dom = impl.createDocument(None, 'content', None)
                root = dom.documentElement
                dbschduleNode = dom.createElement('dbschdule')
                dbschduleTextNode = dom.createTextNode(oracle_dbschdule)
                dbschduleNode.appendChild(dbschduleTextNode)
                root.appendChild(dbschduleNode)
                logschduleNode = dom.createElement('logschdule')
                logschduleTextNode = dom.createTextNode(oracle_logschdule)
                logschduleNode.appendChild(logschduleTextNode)
                root.appendChild(logschduleNode)
                dbstorageNode = dom.createElement('dbstorage')
                dbstorageTextNode = dom.createTextNode(oracle_dbstorage)
                dbstorageNode.appendChild(dbstorageTextNode)
                root.appendChild(dbstorageNode)
                logstorageNode = dom.createElement('logstorage')
                logstorageTextNode = dom.createTextNode(oracle_logstorage)
                logstorageNode.appendChild(logstorageTextNode)
                root.appendChild(logstorageNode)
                backupNode = dom.createElement('backupContent')
                if (oracle_pyhGUID_1 != "0"):
                    racNode = dom.createElement('rac')

                    pyhNode = dom.createElement('pyhGUID')
                    pyhTextNode = dom.createTextNode(oracle_pyhGUID_1)

                    pyhNode.appendChild(pyhTextNode)
                    racNode.appendChild(pyhNode)

                    nameNode = dom.createElement('name')
                    nameTextNode = dom.createTextNode(oracle_name_1)
                    nameNode.appendChild(nameTextNode)
                    racNode.appendChild(nameNode)

                    usernameNode = dom.createElement('username')
                    usernameTextNode = dom.createTextNode(oracle_username_1)
                    usernameNode.appendChild(usernameTextNode)
                    racNode.appendChild(usernameNode)

                    oraclehomeNode = dom.createElement('oraclehome')
                    oraclehomeTextNode = dom.createTextNode(oracle_oraclehome_1)
                    oraclehomeNode.appendChild(oraclehomeTextNode)
                    racNode.appendChild(oraclehomeNode)
                    conn1Node = dom.createElement('conn1')
                    conn1TextNode = dom.createTextNode(oracle_conn1_1)
                    conn1Node.appendChild(conn1TextNode)
                    racNode.appendChild(conn1Node)
                    conn2Node = dom.createElement('conn2')
                    conn2TextNode = dom.createTextNode(oracle_conn2_1)
                    conn2Node.appendChild(conn2TextNode)
                    racNode.appendChild(conn2Node)
                    conn3Node = dom.createElement('conn3')
                    conn3TextNode = dom.createTextNode(oracle_conn3_1)
                    conn3Node.appendChild(conn3TextNode)
                    racNode.appendChild(conn3Node)
                    backupNode.appendChild(racNode)
                if (oracle_pyhGUID_2 != "0"):
                    racNode = dom.createElement('rac')
                    pyhNode = dom.createElement('pyhGUID')
                    pyhTextNode = dom.createTextNode(oracle_pyhGUID_2)
                    pyhNode.appendChild(pyhTextNode)
                    racNode.appendChild(pyhNode)
                    nameNode = dom.createElement('name')
                    nameTextNode = dom.createTextNode(oracle_name_2)
                    nameNode.appendChild(nameTextNode)
                    racNode.appendChild(nameNode)

                    usernameNode = dom.createElement('username')
                    usernameTextNode = dom.createTextNode(oracle_username_2)
                    usernameNode.appendChild(usernameTextNode)
                    racNode.appendChild(usernameNode)

                    oraclehomeNode = dom.createElement('oraclehome')
                    oraclehomeTextNode = dom.createTextNode(oracle_oraclehome_2)
                    oraclehomeNode.appendChild(oraclehomeTextNode)
                    racNode.appendChild(oraclehomeNode)
                    conn1Node = dom.createElement('conn1')
                    conn1TextNode = dom.createTextNode(oracle_conn1_2)
                    conn1Node.appendChild(conn1TextNode)
                    racNode.appendChild(conn1Node)
                    conn2Node = dom.createElement('conn2')
                    conn2TextNode = dom.createTextNode(oracle_conn2_2)
                    conn2Node.appendChild(conn2TextNode)
                    racNode.appendChild(conn2Node)
                    conn3Node = dom.createElement('conn3')
                    conn3TextNode = dom.createTextNode(oracle_conn3_2)
                    conn3Node.appendChild(conn3TextNode)
                    racNode.appendChild(conn3Node)
                    backupNode.appendChild(racNode)
                if (oracle_pyhGUID_3 != "0"):
                    racNode = dom.createElement('rac')
                    pyhNode = dom.createElement('pyhGUID')
                    pyhTextNode = dom.createTextNode(oracle_pyhGUID_3)
                    pyhNode.appendChild(pyhTextNode)
                    racNode.appendChild(pyhNode)
                    nameNode = dom.createElement('name')
                    nameTextNode = dom.createTextNode(oracle_name_3)
                    nameNode.appendChild(nameTextNode)
                    racNode.appendChild(nameNode)

                    usernameNode = dom.createElement('username')
                    usernameTextNode = dom.createTextNode(oracle_username_3)
                    usernameNode.appendChild(usernameTextNode)
                    racNode.appendChild(usernameNode)

                    oraclehomeNode = dom.createElement('oraclehome')
                    oraclehomeTextNode = dom.createTextNode(oracle_oraclehome_3)
                    oraclehomeNode.appendChild(oraclehomeTextNode)
                    racNode.appendChild(oraclehomeNode)
                    conn1Node = dom.createElement('conn1')
                    conn1TextNode = dom.createTextNode(oracle_conn1_3)
                    conn1Node.appendChild(conn1TextNode)
                    racNode.appendChild(conn1Node)
                    conn2Node = dom.createElement('conn2')
                    conn2TextNode = dom.createTextNode(oracle_conn2_3)
                    conn2Node.appendChild(conn2TextNode)
                    racNode.appendChild(conn2Node)
                    conn3Node = dom.createElement('conn3')
                    conn3TextNode = dom.createTextNode(oracle_conn3_3)
                    conn3Node.appendChild(conn3TextNode)
                    racNode.appendChild(conn3Node)
                    backupNode.appendChild(racNode)
                if (oracle_pyhGUID_4 != "0"):
                    racNode = dom.createElement('rac')
                    pyhNode = dom.createElement('pyhGUID')
                    pyhTextNode = dom.createTextNode(oracle_pyhGUID_4)
                    pyhNode.appendChild(pyhTextNode)
                    racNode.appendChild(pyhNode)
                    nameNode = dom.createElement('name')
                    nameTextNode = dom.createTextNode(oracle_name_4)
                    nameNode.appendChild(nameTextNode)
                    racNode.appendChild(nameNode)

                    usernameNode = dom.createElement('username')
                    usernameTextNode = dom.createTextNode(oracle_username_4)
                    usernameNode.appendChild(usernameTextNode)
                    racNode.appendChild(usernameNode)

                    oraclehomeNode = dom.createElement('oraclehome')
                    oraclehomeTextNode = dom.createTextNode(oracle_oraclehome_4)
                    oraclehomeNode.appendChild(oraclehomeTextNode)
                    racNode.appendChild(oraclehomeNode)
                    conn1Node = dom.createElement('conn1')
                    conn1TextNode = dom.createTextNode(oracle_conn1_4)
                    conn1Node.appendChild(conn1TextNode)
                    racNode.appendChild(conn1Node)
                    conn2Node = dom.createElement('conn2')
                    conn2TextNode = dom.createTextNode(oracle_conn2_4)
                    conn2Node.appendChild(conn2TextNode)
                    racNode.appendChild(conn2Node)
                    conn3Node = dom.createElement('conn3')
                    conn3TextNode = dom.createTextNode(oracle_conn3_4)
                    conn3Node.appendChild(conn3TextNode)
                    racNode.appendChild(conn3Node)
                    backupNode.appendChild(racNode)
                if (oracle_pyhGUID_5 != "0"):
                    racNode = dom.createElement('rac')
                    pyhNode = dom.createElement('pyhGUID')
                    pyhTextNode = dom.createTextNode(oracle_pyhGUID_5)
                    pyhNode.appendChild(pyhTextNode)
                    racNode.appendChild(pyhNode)
                    nameNode = dom.createElement('name')
                    nameTextNode = dom.createTextNode(oracle_name_5)
                    nameNode.appendChild(nameTextNode)
                    racNode.appendChild(nameNode)

                    usernameNode = dom.createElement('username')
                    usernameTextNode = dom.createTextNode(oracle_username_5)
                    usernameNode.appendChild(usernameTextNode)
                    racNode.appendChild(usernameNode)

                    oraclehomeNode = dom.createElement('oraclehome')
                    oraclehomeTextNode = dom.createTextNode(oracle_oraclehome_5)
                    oraclehomeNode.appendChild(oraclehomeTextNode)
                    racNode.appendChild(oraclehomeNode)
                    conn1Node = dom.createElement('conn1')
                    conn1TextNode = dom.createTextNode(oracle_conn1_5)
                    conn1Node.appendChild(conn1TextNode)
                    racNode.appendChild(conn1Node)
                    conn2Node = dom.createElement('conn2')
                    conn2TextNode = dom.createTextNode(oracle_conn2_5)
                    conn2Node.appendChild(conn2TextNode)
                    racNode.appendChild(conn2Node)
                    conn3Node = dom.createElement('conn3')
                    conn3TextNode = dom.createTextNode(oracle_conn3_5)
                    conn3Node.appendChild(conn3TextNode)
                    racNode.appendChild(conn3Node)
                    backupNode.appendChild(racNode)
                root.appendChild(backupNode)
                content = dom.toxml()

                if clientGUID == "0":
                    client = ClientHost()
                    client.clientGUID = uuid.uuid1()
                    client.clientName = clientName + "." + request.user.username
                    client.owernID = request.user.userinfo.userGUID
                    client.hostType = "RAC"
                    client.proxyClientID = proxyClientID
                    client.status = "0"
                    client.platform = "RAC"
                    client.installTime = datetime.datetime.now()
                    client.save()

                    dataset = DataSet()
                    dataset.dataSetGUID = uuid.uuid1()
                    dataset.clientGUID = client.clientGUID
                    dataset.clientName = client.clientName
                    dataset.owernID = client.owernID
                    dataset.vendor = client.vendor
                    dataset.zone = client.zone
                    dataset.clientID = client.clientID
                    dataset.agentType = "RAC"
                    dataset.statu = "0"
                    dataset.instanceName = databaseName
                    dataset.content = content
                    dataset.installTime = datetime.datetime.now()
                    dataset.save()
                else:
                    client = ClientHost.objects.get(clientGUID=clientGUID)
                    client.proxyClientID = proxyClientID
                    client.clientName = clientName + "." + request.user.username
                    client.save()

                    dataset = DataSet.objects.get(dataSetGUID=dataSetGUID)
                    dataset.content = content
                    dataset.instanceName = databaseName
                    dataset.save()
            else:
                result = u"密码错误。"

            return HttpResponse(result)


def racproconfigdel(request):
    if request.user.is_authenticated():
        if request.method == 'POST':
            clientGUID = request.POST.get('clientGUID', '')
            dataSetGUID = request.POST.get('dataSetGUID', '')
            client = ClientHost.objects.get(clientGUID=clientGUID)
            client.status = "9"
            client.save()

            dataset = DataSet.objects.get(dataSetGUID=dataSetGUID)
            dataset.status = "9"
            dataset.save()
            return HttpResponse("删除成功。")
        else:
            return HttpResponse("删除失败。")


def disasterdrill(request):
    if request.user.is_authenticated():
        return render(request, 'disasterdrill.html',
                      {'username': request.user.userinfo.fullname, "disasterdrillpage": True})
    else:
        return HttpResponseRedirect("/login")


def disasterdrilldata(request):
    if request.user.is_authenticated():
        result = []
        allhost = ClientHost.objects.exclude(status="9").filter(owernID=request.user.userinfo.userGUID)
        if (len(allhost) > 0):
            for host in allhost:
                clientName = host.clientName
                clientNames = clientName.split('.')
                clientName = clientNames[0]
                clientGUID = host.clientGUID
                platform = host.platform
                appGroup = host.appGroup

                if host.hostType == "VMWARE":
                    alldataset = DataSet.objects.filter(clientGUID=clientGUID).exclude(status="9")
                    if len(alldataset) > 0:
                        for dataset in alldataset:
                            appGroup = dataset.appGroup
                            dataSetGUID = dataset.dataSetGUID
                            content = dataset.content
                            backupContentlist = []
                            if content != "" and content != None:
                                doc = parseString(content)
                                try:
                                    for node in doc.getElementsByTagName("backupContent"):
                                        a = len(node.getElementsByTagName("VM"))
                                        for vmlistnode in node.getElementsByTagName("VM"):
                                            try:
                                                backupContentlist.append(vmlistnode.childNodes[0].data)

                                            except:
                                                pass
                                except:
                                    pass
                            result.append(
                                {"clientName": clientName, "clientGUID": clientGUID, "type": host.hostType,
                                 "appGroup": appGroup, "dataSetGUID": dataSetGUID, "state": "正在运行",
                                 "backupContent": backupContentlist})
                else:
                    result.append(
                        {"clientName": clientName, "clientGUID": clientGUID, "platform": platform,
                         "type": host.hostType,
                         "appGroup": appGroup, "dataSetGUID": "", "state": "正在运行"})
        return HttpResponse(json.dumps({"data": result}))


def manualrecovery(request):
    if request.user.is_authenticated():
        return render(request, 'manualrecovery.html',
                      {'username': request.user.userinfo.fullname, "manualrecoverypage": True})
    else:
        return HttpResponseRedirect("/login")


def manualrecoverydata(request):
    if request.user.is_authenticated():
        result = []
        allhost = ClientHost.objects.exclude(status="9").filter(owernID=request.user.userinfo.userGUID)
        if (len(allhost) > 0):
            for host in allhost:
                clientName = host.clientName
                clientNames = clientName.split('.')
                clientName = clientNames[0]
                clientGUID = host.clientGUID
                clientID = host.id
                platform = host.platform
                status = "否"
                if host.status == "1":
                    status = "是"
                agentTypeList = host.agentTypeList
                agentType = []
                try:
                    doc = parseString(agentTypeList)
                    for node in doc.getElementsByTagName("agentTypeList"):
                        for agenttypenode in node.getElementsByTagName("agentType"):
                            agentType.append(agenttypenode.childNodes[0].data)
                except:
                    pass

                if host.hostType == "VMWARE":
                    alldataset = DataSet.objects.filter(clientGUID=clientGUID).exclude(status="9")
                    if len(alldataset) > 0:
                        for dataset in alldataset:
                            appGroup = dataset.appGroup
                            dataSetID = dataset.id
                            content = dataset.content
                            backupContentlist = []
                            if content != "" and content != None:
                                doc = parseString(content)
                                try:
                                    for node in doc.getElementsByTagName("backupContent"):
                                        a = len(node.getElementsByTagName("VM"))
                                        for vmlistnode in node.getElementsByTagName("VM"):
                                            try:
                                                backupContentlist.append(vmlistnode.childNodes[0].data)

                                            except:
                                                pass
                                except:
                                    pass
                            result.append(
                                {"clientName": appGroup, "id": dataSetID, "type": host.hostType, "platform": platform,
                                 "state": status, "backupContent": backupContentlist})
                else:
                    result.append(
                        {"clientName": clientName, "id": clientID, "platform": platform, "type": host.hostType,
                         "state": status, "agentType": agentType})
        return HttpResponse(json.dumps({"data": result}))


def oraclerecovery(request, offset):
    if request.user.is_authenticated():
        id = 0
        try:
            id = int(offset)
        except:
            raise Http404()
        myhost = ClientHost.objects.filter(id=id)
        if len(myhost) > 0:
            if myhost[0].owernID == request.user.userinfo.userGUID:
                alldataset = DataSet.objects.filter(clientGUID=myhost[0].clientGUID, agentType='ORACLE').exclude(
                    status="9")
                if len(alldataset) > 0:
                    allhost = ClientHost.objects.exclude(status="9").filter(hostType="physical box",
                                                                            owernID=request.user.userinfo.userGUID).filter(
                        agentTypeList__contains="<agentType>ORACLE</agentType>")
                    destClient = []
                    for host in allhost:
                        destClient.append(host.clientName)
                    return render(request, 'oraclerecovery.html', {'username': request.user.userinfo.fullname,
                                                                   "instanceName": alldataset[0].instanceName,
                                                                   "clientName": myhost[0].clientName,
                                                                   "destClient": destClient,
                                                                   "manualrecoverypage": True})
    else:
        return HttpResponseRedirect("/index")


def dooraclerecovery(request):
    if request.user.is_authenticated():
        if request.method == 'POST':
            sourceClient = request.POST.get('sourceClient', '')
            destClient = request.POST.get('destClient', '')
            restoreTime = request.POST.get('restoreTime', '')
            instanceName = request.POST.get('instanceName', '')

            oraRestoreOperator = {"restoreTime": restoreTime, "restorePath": None}

            cvToken = CV_RestApi_Token()
            cvToken.login(info)
            cvAPI = CV_API(cvToken)
            if cvAPI.restoreOracleBackupset(sourceClient, destClient, instanceName, oraRestoreOperator):
                return HttpResponse("恢复任务已经启动。" + cvAPI.msg)
            else:
                return HttpResponse(u"恢复任务启动失败。" + cvAPI.msg)
        else:
            return HttpResponse("恢复任务启动失败。")


def oraclerecoverydata(request):
    if request.user.is_authenticated():
        result = []
        cvToken = CV_RestApi_Token()
        cvToken.login(info)
        cvAPI = CV_API(cvToken)
        clientName = request.GET.get('clientName', '')
        cvBackup = cvAPI.getBackupset(clientName, "Oracle Database")

        result = cvAPI.getJobList(cvBackup["clientId"], agentType=None, backupset=cvBackup["backupsetName"],
                                  type="backup")
        for node in result:
            try:
                x = time.localtime(float(node["LastTime"]))
                node["LastTime"] = time.strftime('%Y-%m-%d %H:%M:%S', x)
            except:
                pass
            try:

                x = time.localtime(float(node["StartTime"]))
                node["StartTime"] = time.strftime('%Y-%m-%d %H:%M:%S', x)
            except:
                pass
        return HttpResponse(json.dumps({"data": result}))


def mssqlrecovery(request, offset):
    if request.user.is_authenticated():
        id = 0
        try:
            id = int(offset)
        except:
            raise Http404()
        myhost = ClientHost.objects.filter(id=id)
        if len(myhost) > 0:
            if myhost[0].owernID == request.user.userinfo.userGUID:
                alldataset = DataSet.objects.filter(clientGUID=myhost[0].clientGUID, agentType='MSSQL').exclude(
                    status="9")
                if len(alldataset) > 0:
                    allhost = ClientHost.objects.exclude(status="9").filter(hostType="physical box",
                                                                            owernID=request.user.userinfo.userGUID).filter(
                        agentTypeList__contains="<agentType>MSSQL</agentType>")
                    destClient = []
                    for host in allhost:
                        destClient.append(host.clientName)
                    return render(request, 'mssqlrecovery.html', {'username': request.user.userinfo.fullname,
                                                                  "instanceName": alldataset[0].instanceName,
                                                                  "clientName": myhost[0].clientName,
                                                                  "destClient": destClient, "manualrecoverypage": True})
    else:
        return HttpResponseRedirect("/index")


def domssqlrecovery(request):
    if request.user.is_authenticated():
        if request.method == 'POST':
            sourceClient = request.POST.get('sourceClient', '')
            destClient = request.POST.get('destClient', '')
            restoreTime = request.POST.get('restoreTime', '')
            instanceName = request.POST.get('instanceName', '')
            iscover = request.POST.get('iscover', '')
            overWrite = False
            if iscover == "TRUE":
                overWrite = True

            mssqlRestoreOperator = {"restoreTime": restoreTime, "overWrite": overWrite}
            cvToken = CV_RestApi_Token()
            cvToken.login(info)
            cvAPI = CV_API(cvToken)
            if cvAPI.restoreMssqlBackupset(sourceClient, destClient, instanceName, mssqlRestoreOperator):
                return HttpResponse("恢复任务已经启动。" + cvAPI.msg)
            else:
                return HttpResponse(u"恢复任务启动失败。" + cvAPI.msg)
            return HttpResponse("开发中...")
        else:
            return HttpResponse("恢复任务启动失败。")


def mssqlrecoverydata(request):
    if request.user.is_authenticated():
        result = []
        cvToken = CV_RestApi_Token()
        cvToken.login(info)
        cvAPI = CV_API(cvToken)
        clientName = request.GET.get('clientName', '')
        cvBackup = cvAPI.getBackupset(clientName, "SQL Server")

        result = cvAPI.getJobList(cvBackup["clientId"], agentType=None, backupset=cvBackup["backupsetName"],
                                  type="backup")
        for node in result:
            try:
                x = time.localtime(float(node["LastTime"]))
                node["LastTime"] = time.strftime('%Y-%m-%d %H:%M:%S', x)
            except:
                pass
            try:

                x = time.localtime(float(node["StartTime"]))
                node["StartTime"] = time.strftime('%Y-%m-%d %H:%M:%S', x)
            except:
                pass
        return HttpResponse(json.dumps({"data": result}))


def filerecovery(request, offset):
    if request.user.is_authenticated():
        id = 0
        try:
            id = int(offset)
        except:
            raise Http404()
        myhost = ClientHost.objects.filter(id=id)
        if len(myhost) > 0:
            if myhost[0].owernID == request.user.userinfo.userGUID:
                alldataset = DataSet.objects.filter(clientGUID=myhost[0].clientGUID, agentType='FILESYSTEM').exclude(
                    status="9")
                if len(alldataset) > 0:
                    allhost = ClientHost.objects.exclude(status="9").filter(hostType="physical box",
                                                                            owernID=request.user.userinfo.userGUID).filter(
                        agentTypeList__contains="<agentType>FILESYSTEM</agentType>")
                    destClient = []
                    for host in allhost:
                        destClient.append(host.clientName)
                    return render(request, 'filerecovery.html', {'username': request.user.userinfo.fullname,
                                                                 "instanceName": alldataset[0].instanceName,
                                                                 "clientName": myhost[0].clientName,
                                                                 "destClient": destClient, "manualrecoverypage": True})
    else:
        return HttpResponseRedirect("/index")


def dofilerecovery(request):
    if request.user.is_authenticated():

        if request.method == 'POST':
            sourceClient = request.POST.get('sourceClient', '')
            destClient = request.POST.get('destClient', '')
            restoreTime = request.POST.get('restoreTime', '')
            instanceName = request.POST.get('instanceName', '')
            iscover = request.POST.get('iscover', '')
            mypath = request.POST.get('mypath', '')
            selectedfile = request.POST.get('selectedfile')
            sourceItemlist = selectedfile.split("*!-!*")
            client = ClientHost.objects.filter(clientName=sourceClient)
            if len(client) > 0:
                if 'LINUX' in client[0].platform.upper():
                    for i in range(len(sourceItemlist)):
                        if sourceItemlist[i] == '\\':
                            sourceItemlist[i] = '/'
                        else:
                            sourceItemlist[i] = sourceItemlist[i][1:-1]
            inPlace = True
            if mypath != "same":
                inPlace = False
            else:
                mypath = ""
            overWrite = False
            if iscover == "TRUE":
                overWrite = True

            for sourceItem in sourceItemlist:
                if sourceItem == "":
                    sourceItemlist.remove(sourceItem)

            fileRestoreOperator = {"restoreTime": restoreTime, "overWrite": overWrite, "inPlace": inPlace,
                                   "destPath": mypath, "sourcePaths": sourceItemlist, "OS Restore": False}

            cvToken = CV_RestApi_Token()
            cvToken.login(info)
            cvAPI = CV_API(cvToken)
            if cvAPI.restoreFSBackupset(sourceClient, destClient, "defaultBackupSet", fileRestoreOperator):
                return HttpResponse("恢复任务已经启动。" + cvAPI.msg)
            else:
                return HttpResponse(u"恢复任务启动失败。" + cvAPI.msg)

            return HttpResponse("开发中...")
        else:
            return HttpResponse("恢复任务启动失败。")


def filerecoverydata(request):
    if request.user.is_authenticated():
        result = []
        cvToken = CV_RestApi_Token()
        cvToken.login(info)
        cvAPI = CV_API(cvToken)
        clientName = request.GET.get('clientName', '')
        cvBackup = cvAPI.getBackupset(clientName, "File System")

        result = cvAPI.getJobList(cvBackup["clientId"], agentType=None, backupset=cvBackup["backupsetName"],
                                  type="backup")
        for node in result:
            try:
                x = time.localtime(float(node["LastTime"]))
                node["LastTime"] = time.strftime('%Y-%m-%d %H:%M:%S', x)
            except:
                pass
            try:

                x = time.localtime(float(node["StartTime"]))
                node["StartTime"] = time.strftime('%Y-%m-%d %H:%M:%S', x)
            except:
                pass
        return HttpResponse(json.dumps({"data": result}))


def getfiletree(request):
    id = request.POST.get('id', '')
    clientName = request.POST.get('clientName', '')
    allhost = ClientHost.objects.exclude(status="9").filter(clientName=clientName)
    treedata = []
    if len(allhost) > 0:
        clientID = int(allhost[0].clientID)
        cvToken = CV_RestApi_Token()
        cvToken.login(info)
        cvAPI = CV_API(cvToken)
        list = cvAPI.browse(clientID, "File System", None, id, False)
        for node in list:
            root = {}
            root["id"] = node["path"]
            root["pId"] = id
            root["name"] = node["path"]
            if node["DorF"] == "D":
                root["isParent"] = True
            else:
                root["isParent"] = False
            treedata.append(root)
        treedata = json.dumps(treedata)

    return HttpResponse(treedata)


def vmrecovery(request, offset):
    if request.user.is_authenticated():
        id = 0
        try:
            id = int(offset)
        except:
            raise Http404()
        mydataset = DataSet.objects.filter(id=id)
        if len(mydataset) > 0:
            if mydataset[0].owernID == request.user.userinfo.userGUID:
                allhost = ClientHost.objects.exclude(status="9").filter(hostType="VMWARE",
                                                                        owernID=request.user.userinfo.userGUID)
                # allhost = ClientHost.objects.exclude(status="9").filter(hostType="VMWARE").exclude(clientGUID=mydataset[0].clientGUID)
                destClient = []
                vmlist = []
                dslist = []
                esxlist = []
                for host in allhost:
                    destClient.append(host.clientName)

                clientID = int(mydataset[0].clientID)
                cvToken = CV_RestApi_Token()
                cvToken.login(info)
                cvAPI = CV_API(cvToken)
                list = cvAPI.browse(clientID, "Virtual Server", mydataset[0].appGroup, None, False)

                for node in list:
                    vmlist.append({"name": node["displayName"], "id": node["name"]})

                VMWareDataStoreList = cvAPI.getVMWareDataStoreList(clientID)
                for VMWareDataStore in VMWareDataStoreList:
                    if {"text": VMWareDataStore["esxhost"], "value": VMWareDataStore["esxstrGUID"]} not in esxlist:
                        esxlist.append({"text": VMWareDataStore["esxhost"], "value": VMWareDataStore["esxstrGUID"]})
                    dslist.append({"text": VMWareDataStore["dataStoreName"],
                                   "value": VMWareDataStore["esxstrGUID"] + VMWareDataStore["dataStoreName"]})

                return render(request, 'vmrecovery.html',
                              {'username': request.user.userinfo.fullname, "appName": mydataset[0].appGroup,
                               "clientName": mydataset[0].clientName, "vmlist": vmlist, "esxlist": esxlist,
                               "dslist": dslist, "destClient": destClient, "manualrecoverypage": True})
            else:
                return HttpResponseRedirect("/manualrecovery")
        else:
            return HttpResponseRedirect("/manualrecovery")
    else:
        return HttpResponseRedirect("/index")


def getproxylist(request):
    if request.user.is_authenticated() and request.session['isadmin']:
        if request.method == 'POST':
            result = []
            clientName = request.POST.get('clientName', '')
            allhost = ClientHost.objects.exclude(status="9").filter(hostType="VMWARE").filter(
                clientName=clientName)
            if (len(allhost) > 0):
                proxyClientID = allhost[0].proxyClientID
                if proxyClientID != "" and proxyClientID != None:
                    doc = parseString(proxyClientID)
                    for node in doc.getElementsByTagName("PROXYLIST"):
                        for proxylistnode in node.getElementsByTagName("PROXY"):
                            try:
                                proxy = ClientHost.objects.get(clientGUID=proxylistnode.childNodes[0].data)
                                result.append(proxy.clientName)
                            except:
                                pass
            return HttpResponse(json.dumps(result))


def dovmrecovery(request):
    if request.user.is_authenticated():
        if request.method == 'POST':
            appName = request.POST.get('appName', '')
            sourceClient = request.POST.get('sourceClient', '')
            sourceVMName = request.POST.get('sourceVMName', '')
            sourceVMGUID = request.POST.get('sourceVMGUID', '')
            newname = request.POST.get('newname', '')
            destClient = request.POST.get('destClient', '')
            proxyClient = request.POST.get('proxyClient', '')
            esxhost = request.POST.get('esxlist', '')
            dataStoreName = request.POST.get('dslist', '')
            disk = request.POST.get('disk', '')
            power = request.POST.get('power', '')
            iscover = request.POST.get('iscover', '')
            restoreTime = request.POST.get('restoreTime', '')
            mypower = False
            myiscover = False
            if power == "TRUE":
                mypower = True
            if iscover == "TRUE":
                myiscover = True
            hostname = ""
            username = ""

            allhost = ClientHost.objects.exclude(status="9").filter(hostType="VMWARE").filter(
                clientName=sourceClient)
            if len(allhost) > 0:
                creditInfo = allhost[0].creditInfo
                if creditInfo != "" and creditInfo != None:
                    doc = parseString(creditInfo)
                    for node in doc.getElementsByTagName("creditInfo"):
                        for hostnode in node.getElementsByTagName("HOST"):
                            hostname = hostnode.childNodes[0].data
                        for usernode in node.getElementsByTagName("USER"):
                            username = usernode.childNodes[0].data
                    vsaBrowseProxy = ""
                    proxyClientID = allhost[0].proxyClientID
                    if proxyClientID != "" and proxyClientID != None:
                        doc = parseString(proxyClientID)
                        for node in doc.getElementsByTagName("PROXYLIST"):
                            for proxylistnode in node.getElementsByTagName("PROXY"):
                                try:
                                    proxy = ClientHost.objects.get(clientGUID=proxylistnode.childNodes[0].data)
                                    vsaBrowseProxy = proxy.clientName
                                    break
                                except:
                                    pass

                    vmRestoreOperator = {"vsaClientName": sourceClient, "vmGUID": sourceVMGUID, "vmName": sourceVMName,
                                         "vsaBrowseProxy": vsaBrowseProxy,
                                         "vsaRestoreProxy": proxyClient, "vCenterHost": hostname,
                                         "vcenterUser": username, "DCName": esxhost, "esxHost": esxhost,
                                         "datastore": dataStoreName,
                                         "newVMName": newname, "diskOption": disk, "Power": mypower,
                                         "overWrite": myiscover, "restoreTime": restoreTime}
                    cvToken = CV_RestApi_Token()
                    cvToken.login(info)
                    cvAPI = CV_API(cvToken)
                    if cvAPI.restoreVMWareBackupset(sourceClient, destClient, appName, vmRestoreOperator):
                        return HttpResponse("恢复任务已经启动。" + cvAPI.msg)
                    else:
                        return HttpResponse(u"恢复任务启动失败。" + cvAPI.msg)

                return HttpResponse("虚拟中心主机信息配置错误。")
            else:
                return HttpResponse("客户端不存在。")
        else:
            return HttpResponse("恢复任务启动失败。")


def vmrecoverydata(request):
    if request.user.is_authenticated():
        result = []
        cvToken = CV_RestApi_Token()
        cvToken.login(info)
        cvAPI = CV_API(cvToken)
        clientName = request.GET.get('clientName', '')
        cvBackup = cvAPI.getBackupset(clientName, "Virtual")

        result = cvAPI.getJobList(cvBackup["clientId"], agentType=None, backupset=cvBackup["backupsetName"],
                                  type="backup")
        for node in result:
            try:
                x = time.localtime(float(node["LastTime"]))
                node["LastTime"] = time.strftime('%Y-%m-%d %H:%M:%S', x)
            except:
                pass
            try:

                x = time.localtime(float(node["StartTime"]))
                node["StartTime"] = time.strftime('%Y-%m-%d %H:%M:%S', x)
            except:
                pass
        return HttpResponse(json.dumps({"data": result}))


def report(request):
    if request.user.is_authenticated():
        nowtime = datetime.datetime.now()
        endtime = nowtime.strftime("%Y-%m-%d")
        starttime = (nowtime - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        allhost = ClientHost.objects.exclude(status="9").filter(owernID=request.user.userinfo.userGUID)
        client = []
        for host in allhost:
            client.append(host.clientName)

        return render(request, "report.html",
                      {'username': request.user.userinfo.fullname, "starttime": starttime, "endtime": endtime,
                       "client": client, "reportpage": True})
    else:
        return HttpResponseRedirect("/login")


def reportdata(request):
    if request.user.is_authenticated():
        result = []
        client = request.GET.get('client', '')
        type = request.GET.get('type', '')
        startdate = request.GET.get('startdate', '')
        enddate = request.GET.get('enddate', '')

        joblist = Joblist.objects.all().order_by("-startdate")
        if client != "":
            joblist = joblist.filter(clientname=client)
        if type != "":
            joblist = joblist.filter(idataagent=type)
        if startdate != "":
            date_time = datetime.datetime.strptime(startdate, '%Y-%m-%d')
            joblist = joblist.filter(startdate__gte=date_time)
        if enddate != "":
            date_time = datetime.datetime.strptime(enddate, '%Y-%m-%d') + datetime.timedelta(
                days=1) - datetime.timedelta(seconds=1)
            joblist = joblist.filter(startdate__lte=date_time)

        for job in joblist:
            result.append({"jobid": job.jobid, "clientname": job.clientname, "idataagent": job.idataagent,
                           "backuplevel": job.backuplevel, "backupset": job.backupset,
                           "startdate": job.startdate.strftime('%Y-%m-%d %H:%M:%S'),
                           "enddate": job.enddate.strftime('%Y-%m-%d %H:%M:%S'), "jobstatus": job.jobstatus,
                           "numbytesuncomp": str(job.numbytesuncomp / 1024 / 1024),
                           "diskcapacity": str(job.diskcapacity / 1024 / 1024)})
        return HttpResponse(json.dumps({"data": result}))
