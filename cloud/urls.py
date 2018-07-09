from django.contrib import admin
from django.conf.urls import patterns

from django.conf import settings

urlpatterns = patterns('cloud.views',
                       (r'^$', 'index'),
                       (r'^index/$', 'index'),
                       (r'^get_dashboard_amchart_1/$', 'get_dashboard_amchart_1'),
                       (r'^get_dashboard_amchart_2/$', 'get_dashboard_amchart_2'),
                       (r'^get_dashboard_amchart_3/$', 'get_dashboard_amchart_3'),
                       (r'^get_dashboard_amchart_4/$', 'get_dashboard_amchart_4'),
                        (r'^not_display_jobs/$', 'not_display_jobs'),
                       (r'^downloadlist/$', 'downloadlist'),
                       (r'^download/$', 'download'),
                       (r'^login/$', 'login'),
                       (r'^userlogin/$', 'userlogin'),
                       (r'^registUser/$', 'registUser'),
                       (r'^forgetPassword/$', 'forgetPassword'),
                       (
                           r'^resetpassword/([0-9a-zA-Z]{8}-[0-9a-zA-Z]{4}-[0-9a-zA-Z]{4}-[0-9a-zA-Z]{4}-[0-9a-zA-Z]{12})/$',
                           'resetpassword'),
                       (r'^reset/$', 'reset'),
                       (r'^activate/$', 'activate'),
                       (r'^useractivate/$', 'useractivate'),
                       (r'^password/$', 'password'),
                       (r'^userpassword/$', 'userpassword'),
                       (r'^useredit/$', 'useredit'),
                       (r'^usersave/$', 'usersave'),
                       (r'^childuser/$', 'childuser'),
                       (r'^childuserdata/$', 'childuserdata'),
                       (r'^childusersave/$', 'childusersave'),
                       (r'^childuserdel/$', 'childuserdel'),
                       (r'^getallclients/$', 'getallclients'),

                       (r'^script/$', 'script'),
                       (r'^scriptdata/$', 'scriptdata'),
                       (r'^scriptdel/$', 'scriptdel'),
                       (r'^scriptsave/$', 'scriptsave'),
                       (r'^scriptexport/$', 'scriptexport'),
                       (r'^processscriptsave/$', 'processscriptsave'),
                       (r'^get_scripts/$', 'get_scripts'),
                       (r'^get_script_data/$', 'get_script_data'),
                        (r'^remove_script/$', 'remove_script'),

                       (r'^group/$', 'group'),
                       (r'^groupsave/$', 'groupsave'),
                       (r'^groupdel/$', 'groupdel'),
                       (r'^getusers/$', 'getusers'),
                       (r'^getselectedusers/$', 'getselectedusers'),
                       (r'^groupsaveuser/$', 'groupsaveuser'),

                       (r'^resourcepool/$', 'resourcepool'),
                       (r'^resourcepooldata/$', 'resourcepooldata'),
                       (r'^resourcepoolsave/$', 'resourcepoolsave'),
                       (r'^resourcepooldel/$', 'resourcepooldel'),
                       (r'^getvendorlist/$', 'getvendorlist'),
                       (r'^computerresource/$', 'computerresource'),
                       (r'^computerresourcedata/$', 'computerresourcedata'),
                       (r'^computerresourcepooldata/$', 'computerresourcepooldata'),
                       (r'^computerresourcesave/$', 'computerresourcesave'),
                       (r'^computerresourcedel/$', 'computerresourcedel'),
                       (r'^computerresourcepooldatafordrill/$', 'computerresourcepooldatafordrill'),
                       (r'^computerresourcedatafordrill/$', 'computerresourcedatafordrill'),

                       (r'^vmresource/$', 'vmresource'),
                       (r'^vmresourcedata/$', 'vmresourcedata'),
                       (r'^vmresourcepooldata/$', 'vmresourcepooldata'),
                       (r'^vmresourcesave/$', 'vmresourcesave'),
                       (r'^vmresourcedel/$', 'vmresourcedel'),
                       (r'^vmresourcedestroy/$', 'vmresourcedestroy'),
                       (r'^vmresourcepooldatafordrill/$', 'vmresourcepooldatafordrill'),
                       (r'^vmresourcedatafordrill/$', 'vmresourcedatafordrill'),

                       (r'^getvmresourcelist/$', 'getvmresourcelist'),
                       (r'^vmlistmanage/', 'vmlistmanage'),
                       (r'^vmlistmanagedata/$', 'vmlistmanagedata'),
                       (r'^getvmtemplate/', 'getvmtemplate'),

                       (r'^backupresource/$', 'backupresource'),
                       (r'^backupresourcedata/$', 'backupresourcedata'),
                       (r'^backupresourcepooldata/$', 'backupresourcepooldata'),
                       (r'^backupresourcesave/$', 'backupresourcesave'),
                       (r'^backupresourcedel/$', 'backupresourcedel'),
                       (r'^getbackupcert/$', 'getbackupcert'),

                       (r'^schduleresource/$', 'schduleresource'),
                       (r'^schduleresourcedata/$', 'schduleresourcedata'),
                       (r'^schduleresourcepooldata/$', 'schduleresourcepooldata'),
                       (r'^schduleresourcesave/$', 'schduleresourcesave'),
                       (r'^schduleresourcedel/$', 'schduleresourcedel'),
                       (r'^getschdulecert/$', 'getschdulecert'),

                       (r'^serverconfig/$', 'serverconfig'),
                       (r'^serverconfigsave/$', 'serverconfigsave'),
                       (r'^match/$', 'match'),
                       (r'^matchdata/$', 'matchdata'),
                       (r'^matching/$', 'matching'),
                       (r'^matchsave/$', 'matchsave'),

                       (r'^phyproconfig/$', 'phyproconfig'),
                       (r'^phyproconfigdata/$', 'phyproconfigdata'),
                       (r'^getphydataget/$', 'getphydataget'),
                       (r'^phyproconfigsaveapp/$', 'phyproconfigsaveapp'),
                       (r'^phyproconfigsavefile/$', 'phyproconfigsavefile'),
                       (r'^phyproconfigsaveoracle/$', 'phyproconfigsaveoracle'),
                       (r'^phyproconfigsavemssql/$', 'phyproconfigsavemssql'),

                       (r'^vmproconfig/$', 'vmproconfig'),
                       (r'^vmproconfigdata/$', 'vmproconfigdata'),
                       (r'^vmproconfigsave/$', 'vmproconfigsave'),
                       (r'^getvmlist/$', 'getvmlist'),
                       (r'^get_dc/$', 'get_dc'),
                       (r'^get_cluster/$', 'get_cluster'),
                       (r'^clonevm/$', 'clonevm'),
                       (r'^get_progress/$', 'get_progress'),
                       (r'^vm_ipsave/$', 'vm_ipsave'),
                       (r'^vm_hostsave/$', 'vm_hostsave'),
                       (r'^vm_disksave/$', 'vm_disksave'),
                       (r'^vm_installcvsave/$', 'vm_installcvsave'),
                       (r'^registercvsave/$', 'registercvsave'),
                       (r'^vmlistmanagesave/$', 'vmlistmanagesave'),
                       (r'^vmappsave/$', 'vmappsave'),
                       (r'^vmproconfigdel/$', 'vmproconfigdel'),
                       (r'^vmappdel/$', 'vmappdel'),
                       (r'^rebootvm/$', 'rebootvm'),
                       (r'^shutdownvm/$', 'shutdownvm'),
                       (r'^poweronvm/$', 'poweronvm'),
                       (r'^get_vm_state/$', 'get_vm_state'),
                       (r'^get_dc_clt_from_pool/$', 'get_dc_clt_from_pool'),

                       (r'^racproconfig/$', 'racproconfig'),
                       (r'^racproconfigdata/$', 'racproconfigdata'),
                       (r'^racproconfigsave/$', 'racproconfigsave'),
                       (r'^racproconfigdel/$', 'racproconfigdel'),

                       (r'^workflowset/$', 'workflowset'),
                       (r'^getsetps/$', 'getsetps'),
                       (r'^setpsave/$', 'setpsave'),
                       (r'^disasterdrill/$', 'disasterdrill'),
                       (r'^disasterdrilldata/$', 'disasterdrilldata'),
                       (r'^manualrecovery/$', 'manualrecovery'),
                       (r'^manualrecoverydata/$', 'manualrecoverydata'),
                       (r'^oraclerecovery/(\d+)/$', 'oraclerecovery'),
                       (r'^dooraclerecovery/$', 'dooraclerecovery'),
                       (r'^oraclerecoverydata/$', 'oraclerecoverydata'),

                       (r'^mssqlrecovery/(\d+)/$', 'mssqlrecovery'),
                       (r'^domssqlrecovery/$', 'domssqlrecovery'),
                       (r'^mssqlrecoverydata/$', 'mssqlrecoverydata'),

                       (r'^filerecovery/(\d+)/$', 'filerecovery'),
                       (r'^dofilerecovery/$', 'dofilerecovery'),
                       (r'^filerecoverydata/$', 'filerecoverydata'),
                       (r'^getfiletree/$', 'getfiletree'),

                       (r'^vmrecovery/(\d+)/$', 'vmrecovery'),
                       (r'^getproxylist/$', 'getproxylist'),
                       (r'^dovmrecovery/$', 'dovmrecovery'),
                       (r'^vmrecoverydata/$', 'vmrecoverydata'),

                       (r'^addPhyClient/$', 'addPhyClient'),
                       (r'^checkPhyClient/$', 'checkPhyClient'),

                       (r'^report/$', 'report'),
                       (r'^reportdata/$', 'reportdata'),
                        (r'^creatprocessrun/$', 'creatprocessrun'),
                       (r'^filecross/(\d+)/$', 'filecross'),

                        (r'^filecrossprevious/$', 'filecrossprevious'),
                       (r'^filecrossnext/$', 'filecrossnext'),
                        (r'^getsinglevm/$', 'getsinglevm'),
                        (r'^filecrossfinish/$', 'filecrossfinish'),
                       )
