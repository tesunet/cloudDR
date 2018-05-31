# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User


class Group(models.Model):
    name = models.CharField(u"组名", blank=True, null=True,max_length=50)
    remark = models.CharField(u"说明", blank=True, null=True, max_length=5000)
    state = models.CharField(u"状态", blank=True, null=True, max_length=20)
    sort = models.IntegerField(u"排序", blank=True, null=True)


class UserInfo(models.Model):
    group = models.ManyToManyField(Group)
    user = models.OneToOneField(User, blank=True, null=True, )
    userGUID = models.CharField("GUID", null=True, max_length=50)
    fullname = models.CharField("姓名", blank=True, max_length=50)
    phone = models.CharField("电话", blank=True, null=True, max_length=50)
    pnode = models.ForeignKey('self', blank=True, null=True, related_name='children', verbose_name='父节点')
    type = models.CharField("类型", blank=True, null=True, max_length=20)
    state = models.CharField("状态", blank=True, null=True, max_length=20)
    company = models.CharField("公司", blank=True, null=True, max_length=100)
    tell = models.CharField("电话", blank=True, null=True, max_length=50)
    forgetpassword = models.CharField("修改密码地址", blank=True, null=True, max_length=50)


class ResourcePool(models.Model):
    name = models.CharField("名称", blank=True, max_length=50)
    type = models.CharField("类型", blank=True, null=True, max_length=20)
    supplier = models.CharField("供应商", blank=True, null=True, max_length=50)
    certificate = models.CharField("证书", blank=True, null=True, max_length=5000)
    specifications = models.CharField("规格", blank=True, null=True, max_length=5000)
    description = models.CharField("描述", blank=True, null=True, max_length=50)
    level = models.CharField("级别", blank=True, null=True, max_length=10)
    state = models.CharField("状态", blank=True, null=True, max_length=20)
    creatdate = models.DateTimeField("创建时间", blank=True, null=True)
    updatedate = models.DateTimeField("修改时间", blank=True, null=True)


class ComputerResource(models.Model):
    name = models.CharField("名称", blank=True, max_length=50)
    pool = models.ForeignKey(ResourcePool, blank=True, null=True)
    certificate = models.CharField("证书", blank=True, null=True, max_length=5000)
    specifications = models.CharField("规格", blank=True, null=True, max_length=5000)
    cost = models.IntegerField("成本", blank=True, null=True)
    description = models.CharField("描述", blank=True, null=True, max_length=50)
    state = models.CharField("状态", blank=True, null=True, max_length=20)
    creatdate = models.DateTimeField("创建时间", blank=True, null=True)
    updatedate = models.DateTimeField("修改时间", blank=True, null=True)


class VmResource(models.Model):
    pool = models.ForeignKey(ResourcePool, blank=True, null=True)
    name = models.CharField("名称", blank=True, max_length=50)
    template_name = models.CharField("模板名称", blank=True, max_length=50)
    system = models.CharField("系统", blank=True, max_length=50)
    specifications = models.CharField("规格", blank=True, null=True, max_length=5000)
    description = models.CharField("描述", blank=True, null=True, max_length=50)
    state = models.CharField("状态", blank=True, null=True, max_length=20)
    vm_num = models.IntegerField("虚机数", blank=True, null=True)
    uuid = models.CharField("uuid", blank=True, null=True, max_length=256)
    vm_type = models.CharField("虚机类型", blank=True, null=True, max_length=50)
    template = models.ForeignKey("self", blank=True, null=True, verbose_name="模板")
    creatdate = models.DateTimeField("创建时间", blank=True, null=True)
    updatedate = models.DateTimeField("修改时间", blank=True, null=True)

    class Meta:
        verbose_name = "虚机资源"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class BackupResource(models.Model):
    name = models.CharField("名称", blank=True, max_length=50)
    pool = models.ForeignKey(ResourcePool, blank=True, null=True)
    certificate = models.CharField("证书", blank=True, null=True, max_length=5000)
    specifications = models.CharField("规格", blank=True, null=True, max_length=5000)
    cost = models.IntegerField("成本", blank=True, null=True)
    description = models.CharField("描述", blank=True, null=True, max_length=50)
    state = models.CharField("状态", blank=True, null=True, max_length=20)
    creatdate = models.DateTimeField("创建时间", blank=True, null=True)
    updatedate = models.DateTimeField("修改时间", blank=True, null=True)


class SchduleResource(models.Model):
    name = models.CharField("名称", blank=True, max_length=50)
    pool = models.ForeignKey(ResourcePool, blank=True, null=True)
    certificate = models.CharField("证书", blank=True, null=True, max_length=5000)
    specifications = models.CharField("规格", blank=True, null=True, max_length=5000)
    cost = models.IntegerField("成本", blank=True, null=True)
    description = models.CharField("描述", blank=True, null=True, max_length=50)
    state = models.CharField("状态", blank=True, null=True, max_length=20)
    creatdate = models.DateTimeField("创建时间", blank=True, null=True)
    updatedate = models.DateTimeField("修改时间", blank=True, null=True)


class ClientHost(models.Model):
    clientGUID = models.CharField("GUID", null=True, max_length=50)
    clientName = models.CharField("主机名称", max_length=200)
    owernID = models.CharField("用户GUID", blank=True, null=True, max_length=50)
    hostType = models.CharField("主机类型", blank=True, null=True, max_length=50)
    vendor = models.CharField("vendor", blank=True, null=True, max_length=1000)
    zone = models.CharField("zone", blank=True, null=True, max_length=1000)
    clientID = models.IntegerField("主机ID", blank=True, null=True)
    proxyClientID = models.CharField("代理主机列表", blank=True, null=True, max_length=5000)
    creditInfo = models.CharField("认证信息", blank=True, null=True, max_length=1000)
    agentTypeList = models.CharField("代理类型列表", blank=True, null=True, max_length=2000)
    status = models.CharField("状态", blank=True, null=True, max_length=20)
    platform = models.CharField("平台", blank=True, null=True, max_length=50)
    appGroup = models.CharField("应用组", blank=True, null=True, max_length=50)
    comment = models.CharField("描述", blank=True, null=True, max_length=1000)
    installTime = models.DateTimeField("安装时间", blank=True, null=True)
    activeTime = models.DateTimeField("激活时间", blank=True, null=True)
    firstProtectTime = models.DateTimeField("首次保护时间", blank=True, null=True)
    lastProtectTime = models.DateTimeField("最近保护时间", blank=True, null=True)


class DataSet(models.Model):
    dataSetGUID = models.CharField("GUID", null=True, max_length=50)
    clientGUID = models.CharField("主机GUID", null=True, max_length=50)
    clientName = models.CharField("主机名称", max_length=200)
    owernID = models.CharField("用户GUID", blank=True, null=True, max_length=50)
    vendor = models.CharField("vendor", blank=True, null=True, max_length=1000)
    zone = models.CharField("zone", blank=True, null=True, max_length=1000)
    clientID = models.IntegerField("主机ID", blank=True, null=True)
    instanceName = models.CharField("实例名称", blank=True, null=True, max_length=500)
    agentType = models.CharField("代理类型", blank=True, null=True, max_length=50)
    credit = models.CharField("认证信息", blank=True, null=True, max_length=1000)
    status = models.CharField("状态", blank=True, null=True, max_length=20)
    appGroup = models.CharField("应用组名称", blank=True, null=True, max_length=50)
    comment = models.CharField("描述", blank=True, null=True, max_length=1000)
    content = models.CharField("保护内容", blank=True, null=True, max_length=5000)
    installTime = models.DateTimeField("安装时间", blank=True, null=True)
    activeTime = models.DateTimeField("激活时间", blank=True, null=True)
    firstProtectTime = models.DateTimeField("首次保护时间", blank=True, null=True)
    lastProtectTime = models.DateTimeField("最近保护时间", blank=True, null=True)


class Vendor(models.Model):
    vendorGUID = models.CharField("GUID", null=True, max_length=50)
    name = models.CharField("名称", blank=True, null=True, max_length=50)
    type = models.CharField("类型", blank=True, null=True, max_length=50)
    content = models.CharField("内容", blank=True, null=True, max_length=5000)
    status = models.CharField("状态", blank=True, null=True, max_length=20)


class Joblist(models.Model):
    jobid = models.IntegerField("任务ID")
    appid = models.IntegerField(blank=True, null=True)
    jobinitfrom = models.CharField(blank=True, null=True, max_length=200)
    clientname = models.CharField(blank=True, null=True, max_length=200)
    idataagent = models.CharField(blank=True, null=True, max_length=200)
    instance = models.CharField(blank=True, null=True, max_length=200)
    backupset = models.CharField(blank=True, null=True, max_length=200)
    subclient = models.CharField(blank=True, null=True, max_length=200)
    data_sp = models.CharField(blank=True, null=True, max_length=50)
    backuplevelInt = models.IntegerField(blank=True, null=True)
    backuplevel = models.CharField(blank=True, null=True, max_length=200)
    incrlevel = models.IntegerField(blank=True, null=True)
    jobstatusInt = models.IntegerField(blank=True, null=True)
    jobstatus = models.CharField(blank=True, null=True, max_length=200)
    jobfailedreason = models.CharField(blank=True, null=True, max_length=5000)
    transferTime = models.IntegerField(blank=True, null=True)
    startdateunixsec = models.BigIntegerField(blank=True, null=True)
    enddateunixsec = models.BigIntegerField(blank=True, null=True)
    startdate = models.DateTimeField("开始时间", blank=True, null=True)
    enddate = models.DateTimeField("结束时间", blank=True, null=True)
    durationunixsec = models.IntegerField(blank=True, null=True)
    duration = models.CharField(blank=True, null=True, max_length=200)
    numstreams = models.IntegerField(blank=True, null=True)
    numbytesuncomp = models.BigIntegerField(blank=True, null=True)
    numbytescomp = models.BigIntegerField(blank=True, null=True)
    numobjects = models.BigIntegerField(blank=True, null=True)
    isAged = models.IntegerField(blank=True, null=True)
    isAgedStr = models.CharField(blank=True, null=True, max_length=20)
    xmlJobOptions = models.CharField(blank=True, null=True, max_length=5000)
    retentionDays = models.CharField(blank=True, null=True, max_length=200)
    systemStateBackup = models.IntegerField(blank=True, null=True)
    inPrimaryCopy = models.IntegerField(blank=True, null=True)
    failedobjects = models.IntegerField(blank=True, null=True)
    totalBackupSize = models.BigIntegerField(blank=True, null=True)
    encrypted = models.CharField(blank=True, null=True, max_length=200)
    diskcapacity = models.BigIntegerField(blank=True, null=True)
    result = models.CharField(blank=True, null=True, max_length=200)
