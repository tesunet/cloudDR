import pymssql


class SQLServerFilter(object):
    """
    SQL Server数据查询
    """

    def __init__(self):
        self._conn = pymssql.connect(host='cv-server\COMMVAULT', user='sa_cloud', password='1qaz@WSX',
                                     database='CommServ')
        self._cur = self._conn.cursor()
        self.schedule_list = []
        self.client_list = []
        self.client_info_dict = {}
        self.client_match_dict = {}
        self.vm_ware_list = []
        self.job_list = []
        self.back_up_set_list = []

    def _get_client_match_dict(self, client_id=True):
        """
        客户端名称与id构成的键值对
        :param client_id:
        :return:
        """
        client_list_sql = """
        SELECT [ClientId],[Client]
        FROM [commserv].[dbo].[CommCellClientConfig] 
        WHERE [ClientStatus] = 'installed'
        """
        client_list = self.filter_all(client_list_sql)
        if client_id:
            for client in client_list:
                self.client_match_dict[client[0]] = client[1]
        else:
            for client in client_list:
                self.client_match_dict[client[1]] = client[0]
        return self.client_match_dict

    def filter_all(self, filter_sql):
        self._cur.execute(filter_sql)
        return self._cur.fetchall()

    def get_client_info(self, client):
        """
        客户端信息
        {"backupsetList":
            [{"subclientId": "70", "agentId": null, "agentType": "Windows File System", "clientId": "7", "clientName": "win-db-restor.hzx", "instanceName": "DefaultInstanceName", "backupsetName": "defaultBackupSet", "backupsetId": "33", "instanceId": "1"},
            {"subclientId": "73", "agentId": null, "agentType": "SQL Server", "clientId": "7", "clientName": "win-db-restor.hzx", "instanceName": "WIN-DB-RESTOR", "backupsetName": "defaultBackupSet", "backupsetId": "36", "instanceId": "27"}
            ],
        "clientId": "7",
        "agentList": [
            {"appId": "106", "clientName": "win-db-restor.hzx", "agentType": "Virtual Server"},
            {"appId": "81", "clientName": "win-db-restor.hzx", "agentType": "SQL Server"},
            {"appId": "22", "clientName": "win-db-restor.hzx", "agentType": "Oracle"},
            {"appId": "33", "clientName": "win-db-restor.hzx", "agentType": "File System"}],
        "clientName": "win-db-restor.hzx",
        "platform": {"hostName": "Win-DB-Restor", "ProcessorType": "WinX64", "platform": "Windows Server (R) 2008 Enterprise"}
        }
        :param client:
        :return:
        """
        try:
            client = int(client)
            client_info_list_sql = """
                SELECT config.[ClientId],config.[Client],config.[NetworkInterface],config.[OS [Version]]], config.[Hardware], os.[osName]
                FROM [commserv].[dbo].[CommCellClientConfig] AS config
                INNER JOIN [commserv].[dbo].[ClientOSNameView] AS os ON config.[ClientId]=os.[clientId]
                WHERE config.[ClientStatus]='installed' AND config.[ClientId]='{0}'
                """.format(client)
        except:
            client_info_list_sql = """
                SELECT config.[ClientId],config.[Client],config.[NetworkInterface],config.[OS [Version]]], config.[Hardware], os.[osName]
                FROM [commserv].[dbo].[CommCellClientConfig] AS config
                INNER JOIN [commserv].[dbo].[ClientOSNameView] AS os ON config.[ClientId]=os.[clientId]
                WHERE config.[ClientStatus]='installed' AND config.[Client]='{0}'
                """.format(client)

        client_info_list = self.filter_all(client_info_list_sql)[0]

        self.client_info_dict["clientName"] = client_info_list[1]
        self.client_info_dict["clientId"] = client
        self.client_info_dict["platform"] = {
            "hostName": client_info_list[2],
            "platform": client_info_list[3],
            "ProcessorType": client_info_list[4],
        }

        agent_info_list_sql = """
            SELECT DISTINCT ida.[AppTypeID],ida.[AppTypeName]
            FROM [commserv].[dbo].[CNIDAInfoView] AS ida 
            INNER JOIN [commserv].[dbo].[CNClientInfoView] AS client ON ida.[ClientID] = client.[ID]
            WHERE client.[OSName] = '{1}'
        """.format(client, client_info_list[5])
        agent_info_list = self.filter_all(agent_info_list_sql)
        agent_list = []
        for agent in agent_info_list:
            agent_list.append({
                "clientName": client_info_list[0],
                "appId": agent[0],
                "agentType": agent[1],
            })

        self.client_info_dict["agentList"] = agent_list

        # backupset_list = []
        # # backupsetid,instanceid
        #
        # sub_client_list_sql = """
        #     SELECT DISTINCT [appid] FROM [commserv].[dbo].[CommCellSubClientConfig]
        # """
        # sub_client_list = self.filter_all(sub_client_list_sql)
        # for sub_client_id in sub_client_list:
        #     back_up_set_list_sql = """
        #         SELECT DISTINCT sub.[appid],sub.[clientid],sub.[clientname],sub.[instance],sub.[backupset], ida.[AppTypeID], ida.[AppTypeName]
        #         FROM [commserv].[dbo].[CommCellSubClientConfig] as sub
        #         INNER JOIN [commserv].[dbo].[CNIDAInfoView] AS ida ON sub.[clientid] = ida.[ClientID]
        #         WHERE sub.[clientid] = '{0}'
        #     """.format(client)
        #     back_up_set_list = self.filter_all(back_up_set_list_sql)
        #     for back_up_set in back_up_set_list:
        #         #{"subclientId": "70", "agentId": null, "agentType": "Windows File System", "clientId": "7",
        #         # "clientName": "win-db-restor.hzx", "instanceName": "DefaultInstanceName",
        #         # "backupsetName": "defaultBackupSet", "backupsetId": "33", "instanceId": "1"},
        #         backupset_list.append({
        #             "subclientId": back_up_set[0],
        #             "agentId": back_up_set[5],
        #             "agentType": back_up_set[6],
        #             "clientId": back_up_set[1],
        #             "clientName": back_up_set[2],
        #             "instanceName": back_up_set[3],
        #             "backupsetName": back_up_set[4],
        #             "backupsetId": "",
        #             "instanceId": "",
        #         })
        #
        # self.client_info_dict["backupsetList"] = backupset_list

        return self.client_info_dict

    def get_sp_list(self):
        """
        [{"SPName": "Backup To Disk", "SPId": "28"},
         {"SPName": "SP-30DAYS2", "SPId": "27"},
         {"SPName": "SP-7DAY2", "SPId": "26"}]
        :return:
        """
        pass

    def get_schedule_list(self):
        """
        [{"SchduleId": "30", "SchduleName": "FILE"},
        {"SchduleId": "31", "SchduleName": "DB_BRONZE"},
        {"SchduleId": "32", "SchduleName": "DB_GOLDEN"},
        {"SchduleId": "33", "SchduleName": "DB_SLIVE"},
        {"SchduleId": "34", "SchduleName": "VM_BRONZE"}]
        "System Created " 除外
        :return:
        """
        schedule_list_sql = """
            SELECT [SchedulePolicyId],[SchedulePolicyName]
            FROM [commserv].[dbo].[CommCellBkSchedulePolicy]
            WHERE [SchedulePolicyName] NOT LIKE 'System Created%'
        """
        schedule_list = self.filter_all(schedule_list_sql)
        for schedule in schedule_list:
            self.schedule_list.append({
                "SchduleId": schedule[0],
                "SchduleName": schedule[1]
            })
        return self.schedule_list

    def get_client_list(self):
        """
        [{"clientName": "cv-server", "clientId": 2},
        {"clientName": "win-2qls3b7jx3v.hzx", "clientId": 3},
        {"clientName": "vctest.hzx", "clientId": 5},
        {"clientName": "win-db-restor.hzx", "clientId": 7},
        {"clientName": "linux1.hzx", "clientId": 11},
        {"clientName": "dbserver", "clientId": 12},
        {"clientName": "192.168.100.136", "clientId": 13},
        {"clientName": "t2.hzx", "clientId": 14},
        {"clientName": "disktest.hzx", "clientId": 22},
        {"clientName": "192.168.100.60", "clientId": 24}]
        :return:
        """
        client_list_sql = """
        SELECT [ClientId],[Client]
        FROM [commserv].[dbo].[CommCellClientConfig] 
        WHERE [ClientStatus] = 'installed'
        """
        client_list = self.filter_all(client_list_sql)
        for client in client_list:
            self.client_list.append({
                "clientName": client[0],
                "clientId": client[1],
            })
        return self.client_list

    def get_sub_client_info(self, sub_client_id):
        """
        子客户端信息
        :param sub_client_id:
        :return:
        """
        pass

    def get_vm_ware_vm_list(self, client):
        """
        {"VMName":, "VMGuID":}
        """
        try:
            client = int(client)
        except:
            client = self._get_client_match_dict(client_id=False)[client]

        vm_ware_list_sql = """
           SELECT [GUID],[name]
          FROM [commserv].[dbo].[APP_VM]
          WHERE [clientId] = '{0}'
          """.format(client)

        vm_ware_list = self.filter_all(vm_ware_list_sql)
        for vm_ware in vm_ware_list:
            self.vm_ware_list.append({
                "VMName": vm_ware[1],
                "VMGuID": vm_ware[0],
            })
        return self.vm_ware_list

    def get_back_up_set(self, client, agent_type=None, back_up_set=None):
        """
        {"data": {
            "clientId": "3",
            "agentId": null,
            "backupsetName": "default",
            "agentType": "Oracle Database",
            "backupsetId": "55",
            "subclientId": "118",
            "clientName": "win-2qls3b7jx3v.hzx",
            "instanceId": "35",
            "instanceName": "ORCL"
            }
        }
        :return:
        """
        # backupsetid,instanceid
        try:
            client = int(client)
        except:
            client = self._get_client_match_dict(client_id=False)[client]


        temp_list = []
        # sql过滤条件
        if client:
            client_condition = "sub.[clientid] = '{0}'".format(client)
            temp_list.append(client_condition)
        if agent_type:
            agent_type_condition = "ida.[AppTypeName]='{0}'".format(agent_type)
            temp_list.append(agent_type_condition)
        if back_up_set:
            back_up_set_condition = "sub.[backupset] = '{0}'".format(back_up_set)
            temp_list.append(back_up_set_condition)

        temp_string = ""
        for temp in temp_list:
            temp_string += "{0} AND ".format(temp)

        if temp_string:
            temp_string = temp_string[:-5]

        back_up_set_list_sql = """
            SELECT DISTINCT sub.[appid],sub.[clientid],sub.[clientname],sub.[instance],sub.[backupset], ida.[AppTypeID], ida.[AppTypeName]
            FROM [commserv].[dbo].[CommCellSubClientConfig] as sub
            INNER JOIN [commserv].[dbo].[CNIDAInfoView] AS ida ON sub.[clientid] = ida.[ClientID]
            WHERE {0};
        """.format(temp_string)

        print(back_up_set_list_sql)
        back_up_set_list = self.filter_all(back_up_set_list_sql)
        for back_up_set in back_up_set_list:
            # {"subclientId": "70", "agentId": null, "agentType": "Windows File System", "clientId": "7",
            # "clientName": "win-db-restor.hzx", "instanceName": "DefaultInstanceName",
            # "backupsetName": "defaultBackupSet", "backupsetId": "33", "instanceId": "1"},
            self.back_up_set_list.append({
                "subclientId": back_up_set[0],
                "agentId": back_up_set[5],
                "agentType": back_up_set[6],
                "clientId": back_up_set[1],
                "clientName": back_up_set[2],
                "instanceName": back_up_set[3],
                "backupsetName": back_up_set[4],
                "backupsetId": "",
                "instanceId": "",
            })
        return self.back_up_set_list

    def get_job_list(self, client, agent_type=None, back_up_set=None, set_type="backup"):
        """
        [
        {"jobId": "4434717",
        "Level": "FULL",
        "diskSize": "12686824213",       ?
        "client": null,
        "StartTime": "1531547827",
        "jobType": "Backup",            ?
        "agentType": "Virtual Server",
        "appSize": "21475050052",
        "LastTime": "1531550082",
        "backupSetName": "defaultBackupSet",
        "status": "Completed w/ one or more errors"},
        ...
        ]
        :return:
        """
        status_list = {"Running": "运行", "Waiting": "等待", "Pending": "阻塞", "Suspend": "终止", "commpleted": "完成",
                       "Failed": "失败", "Failed to Start": "启动失败", "Killed": "杀掉"}

        temp_list = []
        # sql过滤条件
        if client:
            client_condition = "[clientname] = '{0}'".format(client)
            temp_list.append(client_condition)
        if agent_type:
            # if agent_type == "Windows File System":
            #     agent_type = "File"
            agent_type_condition = "[idataagent] = '{0}'".format(agent_type)
            temp_list.append(agent_type_condition)
        if back_up_set:
            back_up_set_condition = "[backupset] = '{0}'".format(agent_type)
            temp_list.append(back_up_set_condition)

        temp_string = ""
        for temp in temp_list:
            temp_string += "{0} AND ".format(temp)

        if temp_string:
            temp_string = temp_string[:-5]

        # 查出来的数据有差异 <<<<<<<<<<<<<<<<<<<<<<<<<<<< ?
        # 过滤条件
        job_list_sql = """
            SELECT [jobid],[backuplevel],[clientname],[startdateunixsec],[idataagent],[numbytesuncomp],[enddateunixsec],[backupset],[jobstatus]
            FROM [commserv].[dbo].[CommcellBackupInfoStats]
            WHERE {0}
            ORDER BY [startdate] DESC;
        """.format(temp_string)

        print(job_list_sql)
        job_list = self.filter_all(job_list_sql)
        for job in job_list:
            self.job_list.append({
                "jobId": job[0],
                "Level": job[1],
                "diskSize": "12686824213",  # ???
                "client": job[2],
                "StartTime": job[3],
                "jobType": "Backup",  # ??? 备份/恢复
                "agentType": job[4],
                "appSize": job[5],
                "LastTime": job[6],
                "backupSetName": job[7],
                "status": status_list[job[8]] if job[8] in status_list.keys() else job[8],
            })
        return self.job_list

    def get_vm_ware_data_store_list(self, client):
        pass


if __name__ == "__main__":
    sql_server = SQLServerFilter()
    # list = sql_server.get_job_list("cv-server", "Windows File System")
    list = sql_server.get_back_up_set("cv-server", "Windows File System")

    print(list)
    print(len(list))
    # {'backupsetId': '3', 'agentType': 'Windows File System', 'instanceId': '1', 'subclientId': '2',
    #  'instanceName': 'DefaultInstanceName', 'backupsetName': 'defaultBackupSet', 'agentId': None, 'clientId': '2',
    #  'clientName': 'cv-server'}

    # [{'instanceId': '', 'clientId': 2, 'backupsetName': 'Indexing BackupSet', 'clientName': 'cv-server',
    #   'agentType': 'Windows File System', 'instanceName': '', 'subclientId': 3, 'backupsetId': '', 'agentId': 33},

    #  {'instanceId': '', 'clientId': 2, 'backupsetName': 'defaultBackupSet', 'clientName': 'cv-server',
    #   'agentType': 'Windows File System', 'instanceName': '', 'subclientId': 2, 'backupsetId': '', 'agentId': 33},

    #  {'instanceId': '', 'clientId': 2, 'backupsetName': 'DR-BackupSet', 'clientName': 'cv-server',
    #   'agentType': 'Windows File System', 'instanceName': '', 'subclientId': 1, 'backupsetId': '', 'agentId': 33},
    #  {'instanceId': '', 'clientId': 2, 'backupsetName': 'defaultBackupSet', 'clientName': 'cv-server',
    #   'agentType': 'Windows File System', 'instanceName': '', 'subclientId': 18, 'backupsetId': '', 'agentId': 33},
    #  {'instanceId': '', 'clientId': 2, 'backupsetName': 'defaultBackupSet', 'clientName': 'cv-server',
    #   'agentType': 'Windows File System', 'instanceName': '', 'subclientId': 63, 'backupsetId': '', 'agentId': 33}]
    # temp_list = []
    # for node in list:
    #     temp_list.append(node["jobId"])
    # print(sorted(temp_list))
    #
    # print(len(temp_list))
