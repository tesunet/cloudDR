var FormWizard = function () {


    return {
        //main function to initiate the module
        init: function () {
            if (!jQuery().bootstrapWizard) {
                return;
            }

            var form = $('#submit_form');



            var handleTitle = function(tab, navigation, index) {
                var total = navigation.find('li').length;
                var current = index + 1;
                // set done steps
                jQuery('li', $('#form_wizard_1')).removeClass("done");
                var li_list = navigation.find('li');
                for (var i = 0; i < index; i++) {
                    jQuery(li_list[i]).addClass("done");
                }

                if (current == 1) {
                    $('#form_wizard_1').find('.button-previous').hide();
                } else {
                    $('#form_wizard_1').find('.button-previous').show();
                }

                if (current >= total) {
                    $('#form_wizard_1').find('.button-next').hide();
                    $('#form_wizard_1').find('.button-submit').show();
                } else {
                    $('#form_wizard_1').find('.button-next').show();
                    $('#form_wizard_1').find('.button-submit').hide();
                }
                App.scrollTo($('.page-title'));
            }

            var next1 = function() {
                var myrestoreTime = ""
                if($("input[name='optionsRadios']:checked").val()=="2" && $('#datetimepicker').val()!="")
                    myrestoreTime = $('#datetimepicker').val()
                $.ajax({
                type: "POST",
                dataType: 'json',
                url: "../../filecrossnext/",
                data:
                    {
                        restoreTime:myrestoreTime,
                        steprunid:$('#steprunid').val(),
                        stepindex:"1"
                    },
                success: function (data) {
                    if (data["res"] == "执行成功。") {
                        $('#steprunid').val(data["data"]);
                        $('#steprunid2').val(data["data"]);
                        $('#divtable').hide();
                        $('#radio1').prop("disabled", "disabled");
                        $('#radio2').prop("disabled", "disabled");
                        $('#datetimepicker').prop("readonly", "readonly");

                        $('#instancename').removeProp("readonly");
                         $('#currentvm').removeProp("readonly");
                         $('#description').removeProp("readonly");
                         $("#bt_select").show();
                         $("#templatediv").addClass("input-group")
                         $("#clone").show();
                         $("#refresh").show();
                         $("#bt_ip").show();
                         $("#bt_hostname").show();
                         $("#bt_installcv").show();
                         $("#bt_registercv").show();
                         $("#bt_adddisk").show();
                         $("#bt_shutdown").show();
                         $("#bt_reboot").show();
                         $("#bt_startup").show();


                        return true
                    }
                    else
                        alert(data["res"]);
                        return false
                },
                error: function (e) {
                    alert("执行失败，请于管理员联系。");
                    return false
                }
            });
            }
            var next2 = function() {
                $.ajax({
                type: "POST",
                dataType: 'json',
                url: "../../filecrossnext/",
                data:
                    {
                        steprunid:$('#steprunid').val(),
                        stepindex:"2"
                    },
                success: function (data) {
                    if (data["res"] == "执行成功。") {
                        $('#steprunid').val(data["data"]);
                        $('#steprunid3').val(data["data"]);
                        $('#instancename').prop("readonly", "readonly");
                         $('#currentvm').prop("readonly", "readonly");
                         $('#description').prop("readonly", "readonly");
                         $("#bt_select").hide();
                         $("#templatediv").removeClass("input-group")
                         $("#clone").hide();
                         $("#refresh").hide();
                         $("#bt_ip").hide();
                         $("#bt_hostname").hide();
                         $("#bt_installcv").hide();
                         $("#bt_registercv").hide();
                         $("#bt_adddisk").hide();
                         $("#bt_shutdown").hide();
                         $("#bt_reboot").hide();
                         $("#bt_startup").hide();

                        return true
                    }
                    else
                        alert(data["res"]);
                        return false
                },
                error: function (e) {
                    alert("执行失败，请于管理员联系。");
                    return false
                }
            });
            }

            var previous2 = function() {
                $.ajax({
                type: "POST",
                dataType: 'json',
                url: "../../filecrossprevious/",
                data:
                    {
                        steprunid:$('#steprunid').val(),
                    },
                success: function (data) {
                    if (data["res"] == "执行成功。") {
                        $('#steprunid').val(data["data"]);
                        $('#divtable').show();
                        $('#radio1').removeProp("disabled");
                        $('#radio2').removeProp("disabled");
                        $('#datetimepicker').removeProp("readonly");

                        return true
                    }
                    else
                        alert(data["res"]);
                        return false
                },
                error: function (e) {
                    alert("执行失败，请于管理员联系。");
                    return false
                }
            });
            }

           var previous3 = function() {
                $.ajax({
                type: "POST",
                dataType: 'json',
                url: "../../filecrossprevious/",
                data:
                    {
                        steprunid:$('#steprunid').val(),
                    },
                success: function (data) {
                    if (data["res"] == "执行成功。") {
                        $('#steprunid').val(data["data"]);

                        $('#instancename').removeProp("readonly");
                         $('#currentvm').removeProp("readonly");
                         $('#description').removeProp("readonly");
                         $("#bt_select").show();
                         $("#templatediv").addClass("input-group")
                         $("#clone").show();
                         $("#refresh").show();
                         $("#bt_ip").show();
                         $("#bt_hostname").show();
                         $("#bt_installcv").show();
                         $("#bt_registercv").show();
                         $("#bt_adddisk").show();
                         $("#bt_shutdown").show();
                         $("#bt_reboot").show();
                         $("#bt_startup").show();


                        return true
                    }
                    else
                        alert(data["res"]);
                        return false
                },
                error: function (e) {
                    alert("执行失败，请于管理员联系。");
                    return false
                }
            });
            }

            // default form wizard
            $('#form_wizard_1').bootstrapWizard({
                'nextSelector': '.button-next',
                'previousSelector': '.button-previous',
                onTabClick: function (tab, navigation, index, clickedIndex) {

                    if ($('#steprunid').val()!= $('#steprunid'+ (clickedIndex+1).toString()).val()){
                        $('#form_wizard_1').find('.button-previous').hide();
                        $('#form_wizard_1').find('.button-submit').hide();
                        $('#form_wizard_1').find('.button-next').hide();
                    }else{
                        var total = navigation.find('li').length;
                        var current = clickedIndex + 1;
                        if (current == 1) {
                            $('#form_wizard_1').find('.button-previous').hide();
                        } else {
                            $('#form_wizard_1').find('.button-previous').show();
                        }

                        if (current >= total) {
                            $('#form_wizard_1').find('.button-next').hide();
                            $('#form_wizard_1').find('.button-submit').show();
                        } else {
                            $('#form_wizard_1').find('.button-next').show();
                            $('#form_wizard_1').find('.button-submit').hide();
                        }
                        App.scrollTo($('.page-title'));
                    }

                },
                onNext: function (tab, navigation, index) {
                    if(index==1){
                        next1()
                    }
                    if(index==2){
                        next2()
                    }


                    if (form.valid() == false) {
                        return false;
                    }

                    handleTitle(tab, navigation, index);
                },
                onPrevious: function (tab, navigation, index) {
                    if(index==0){
                        previous2()
                    }
                    if(index==1){
                        previous3()
                    }
                    handleTitle(tab, navigation, index);
                },
                onTabShow: function (tab, navigation, index) {
                    var total = navigation.find('li').length;
                    var current = index + 1;
                    var $percent = (current / total) * 100;
                    $('#form_wizard_1').find('.progress-bar').css({
                        width: $percent + '%'
                    });
                }
            });
            if ($('#steprunid').val()== $('#steprunid1').val()) {
                $('#form_wizard_1').find('.button-previous').hide();
            }
            $('#form_wizard_1 .button-submit').click(function () {
                alert('Finished! Hope you like it :)');
            }).hide();

        }

    };

}();

var setting = {
    async: {
        enable: true,
        url:'../../getfiletree/',
        autoParam:["id"],
        otherParam:{"clientName":$('#sourceClient').val()},
        dataFilter: filter
    },
    check: {
        enable: true,
        chkStyle: "checkbox",               //多选
        chkboxType: { "Y": "s", "N": "ps" }  //不级联父节点选择
    },
    view:{
        showLine:false
    },

};
function filter(treeId, parentNode, childNodes) {
    if (!childNodes) return null;
    for (var i=0, l=childNodes.length; i<l; i++) {
        childNodes[i].name = childNodes[i].name.replace(/\.n/g, '.');
    }
    return childNodes;
}

jQuery(document).ready(function() {

    //第一步，选择恢复时间点
    $('#sample_1').dataTable( {
        "bAutoWidth": true,
        "bSort": false,
        "bProcessing": true,
        "ajax": "../../filerecoverydata?clientName=" + $('#sourceClient').val(),
        "columns": [
            { "data": "jobId" },
            { "data": "jobType" },
            { "data": "Level" },
            { "data": "StartTime" },
            { "data": "LastTime" },
            { "data": null },
        ],

        "columnDefs": [{
                "targets": -1,
                "data": null,
                "defaultContent": "<button  id='select' title='选择'  class='btn btn-xs btn-primary' type='button'><i class='fa fa-check'></i></button>"
        } ],

        "oLanguage": {
        "sLengthMenu": "&nbsp;&nbsp;每页显示 _MENU_ 条记录",
        "sZeroRecords": "抱歉， 没有找到",
        "sInfo": "从 _START_ 到 _END_ /共 _TOTAL_ 条数据",
        "sInfoEmpty":'',
        "sInfoFiltered": "(从 _MAX_ 条数据中检索)",
        "sSearch": "搜索",
        "oPaginate": {
        "sFirst": "首页",
        "sPrevious": "前一页",
        "sNext": "后一页",
        "sLast": "尾页"
        },
        "sZeroRecords": "没有检索到数据",

        }
        } );
    $('#sample_1 tbody').on( 'click', 'button#select', function () {
        var table = $('#sample_1').DataTable();
        var data = table.row( $(this).parents('tr') ).data();
        $("#datetimepicker").val( data.LastTime);
        $("input[name='optionsRadios'][value='1']").prop("checked",false);
        $("input[name='optionsRadios'][value='2']").prop("checked",true);
    });

    if($('#datetimepicker').val()==""){
        $("input[name='optionsRadios'][value='1']").prop("checked",true);
        $("input[name='optionsRadios'][value='2']").prop("checked",false);
    }else{
         $("input[name='optionsRadios'][value='1']").prop("checked",false);
        $("input[name='optionsRadios'][value='2']").prop("checked",true);
    }
    if($('#steprunid').val()!=$('#steprunid1').val()){

         $('#divtable').hide();
        $('#radio1').prop("disabled", "disabled");
        $('#radio2').prop("disabled", "disabled");
        $('#datetimepicker').prop("readonly", "readonly");

    }else{
         $('#li1').addClass("active");
         $('#tab1').addClass("active");
    }
    if($('#steprunstate1').val()=="DONE"){
         $('#li1').addClass("done");
    }

    $('#datetimepicker').datetimepicker({
        format:'yyyy-mm-dd hh:ii:ss',
        });



    //第二步，创建恢复资源
    $('#sample_2').dataTable({
        "bAutoWidth": true,
        "bSort": false,
        "bProcessing": true,
        "ajax": "../../getvmtemplate/",
        "columns": [
            {"data": "id"},
            {"data": "template_name"},
            {"data": "name"},
            {"data": "description"},
            {"data": null}
        ],

        "columnDefs": [{
            "targets": -1,
            "data": null,
            "defaultContent": "<button  id='select' title='选择'  class='btn btn-xs btn-primary' type='button'><i class='fa fa-check'></i></button>"
        }],
        "oLanguage": {
            "sLengthMenu": "&nbsp;&nbsp;每页显示 _MENU_ 条记录",
            "sZeroRecords": "抱歉， 没有找到",
            "sInfo": "从 _START_ 到 _END_ /共 _TOTAL_ 条数据",
            "sInfoEmpty": '',
            "sInfoFiltered": "(从 _MAX_ 条数据中检索)",
            "sSearch": "搜索",
            "oPaginate": {
                "sFirst": "首页",
                "sPrevious": "前一页",
                "sNext": "后一页",
                "sLast": "尾页"
            },
            "sZeroRecords": "没有检索到数据",

        }
    });

    $('#sample_2 tbody').on('click', 'button#select', function () {
        var table = $('#sample_2').DataTable();
        var data = table.row($(this).parents('tr')).data();
        $("#datacenter").empty();
        $("#template_name").val(data.template_name);
        $("#cpu_").val(data.cpu);
        $("#memory_").val(data.memory);
        $("#disk_").val(data.disks);
        $("#name").val(data.name);
        $("#poolid").val(data.pool_id);
        $("#template_id").val(data.id);
        $("#system").val(data.system);
        $("#datacenter").val(data.datacenter);
        $("#cluster").val(data.cluster);
        $('#static1').modal('hide');
    });

    if($('#steprunid').val()!=$('#steprunid2').val()){
        $('#instancename').prop("readonly", "readonly");
         $('#currentvm').prop("readonly", "readonly");
         $('#description').prop("readonly", "readonly");
         $("#bt_select").hide();
         $("#templatediv").removeClass("input-group")
         $("#clone").hide();
         $("#refresh").hide();
         $("#bt_ip").hide();
         $("#bt_hostname").hide();
         $("#bt_installcv").hide();
         $("#bt_registercv").hide();
         $("#bt_adddisk").hide();
         $("#bt_shutdown").hide();
         $("#bt_reboot").hide();
         $("#bt_startup").hide();


    }else{
         $('#li2').addClass("active");
         $('#tab2').addClass("active");
    }
    if($('#steprunstate2').val()=="DONE"){
         $('#li2').addClass("done");
    }

    if ($("#id").val()==""){
        $("#clone_tag").val("0");
        $("#div1").show();
        $("#div2").hide();
        $("#div3").hide();
        $("#id").val("0")
    }
    else{
        $.ajax({
            type: "POST",
            url: "../../getsinglevm/",
            dataType: 'json',
            data: {id: $("#id").val()},
            success: function (data) {
                $("#bt_select").hide();
                $("#templatediv").removeClass("input-group")
                $('#instancename').prop("readonly", "readonly");
                 $('#currentvm').prop("readonly", "readonly");
                 $('#description').prop("readonly", "readonly");
                $("#onstate").hide();
                $("#offstate").hide();
                $("#template_name").val(data["template_template_name"]);
                $("#id").val(data["id"]);
                $("#poolid").val(data["pool_id"]);
                $("#template_id").val(data["template_id"]);
                $("#uuid").val(data["uuid"]);
                $("#cpu_").val(data["cpu"]);
                $("#memory_").val(data["memory"]);
                $("#disk_").val(data["disks"]);
                $("#name").val(data["template_name"]);
                $("#ip").val(data["ip"]);
                $("#hostname").val(data["hostname"]);
                $("#clone_tag").val(data["clone"]);
                $("#datacenter").val(data["datacenter"]);
                $("#cluster").val(data["cluster"]);
                $("#instancename").val(data["instance_name"]);
                $("#currentvm").val(data["name"]);
                var name = data["name"];
                var poolid= data["pool_id"]
                if (data.clone == "0") {
                    $("#div1").hide();
                    $("#div2").show();
                    $("#div3").hide();

                    $.ajax({
                        type: "POST",
                        url: "../../get_progress/",
                        dataType: 'json',
                        data: {poolid: data["pool_id"], name: data["template_name"], id: data["id"]},
                        success: function (data) {
                            if (data["state"] == "3") {
                                $("#uuid").val(data["uuid"]);
                                $("#div1").hide();
                                $("#div2").hide();
                                $("#div3").show();

                                $("#clone_tag").val("1");
                                $.ajax({
                                    type: "POST",
                                    url: "../../get_vm_state/",
                                    dataType: 'json',
                                    data: {poolid: poolid, name: name},
                                    success: function (data) {
                                        if (data['state'] == "poweredOn") {
                                            $("#onstate").show();
                                            $("#offstate").hide();
                                        } else if (data['state'] == "poweredOff") {
                                            $("#onstate").hide();
                                            $("#offstate").show();
                                        } else {
                                            $("#onstate").hide();
                                            $("#offstate").hide();
                                            alert('未定位到当前虚机');
                                        }
                                    }
                                });
                            } else {
                                $("#progress").attr("style", "width: " + data["progress"] + "%;");

                            }
                        },
                    })
                }
                else {
                    $("#div1").hide();
                    $("#div2").hide();
                    $("#div3").show();
                    $.ajax({
                        type: "POST",
                        url: "../../get_vm_state/",
                        dataType: 'json',
                        data: {poolid: poolid, name: name},
                        success: function (data) {
                            if (data['state'] == "poweredOn") {
                                $("#onstate").show();
                                $("#offstate").hide();
                            } else if (data['state'] == "poweredOff") {
                                $("#onstate").hide();
                                $("#offstate").show();
                            } else {
                                $("#onstate").hide();
                                $("#offstate").hide();
                                alert('未定位到当前虚机');
                            }
                        }
                    });
                }
            }
        });



    }


    $("#refresh").click(function () {
        $.ajax({
            type: "POST",
            url: "../../get_progress/",
            dataType: 'json',
            data: {poolid: $("#poolid").val(), name: $("#name").val(), id: $("#id").val()},
            success: function (data) {
                if (data["state"] == "3") {
                    $("#uuid").val(data["uuid"]);
                    $("#div1").hide()
                    $("#div2").hide()
                    $("#div3").show()
                    $("#clone_tag").val("1");
                } else {
                    $("#progress").attr("style", "width: " + data["progress"] + "%;");

                }
            },
        })
    });

    $("#ipsave").click(function () {
        var table = $('#sample_1').DataTable();

        $.ajax({
            type: "POST",
            url: "../../vm_ipsave/",
            dataType: 'json',
            data: {
                id: $("#id").val(),
                uuid: $("#uuid").val(),
                poolid: $("#poolid").val(),
                path: $("#ip_path").val(),
                ip: $("#ip_ip").val(),
                mask: $("#ip_mask").val(),
                gateway: $("#ip_gateway").val(),
                dns: $("#ip_dns").val(),
                user: $("#ip_user").val(),
                password: $("#ip_password").val()
            },
            success: function (data) {
                if (data["value"] == "1") {

                    $("#ip").val($("#ip_ip").val());
                    table.ajax.reload();
                    alert(data["text"]);
                } else {
                    alert(data["text"]);

                }
            },
        })
    });

    $("#hostsave").click(function () {
        var table = $('#sample_1').DataTable();
        $.ajax({
            type: "POST",
            url: "../../vm_hostsave/",
            dataType: 'json',
            data: {
                id: $("#id").val(),
                uuid: $("#uuid").val(),
                poolid: $("#poolid").val(),
                path: $("#host_path").val(),
                hostname: $("#host_name").val(),
                user: $("#host_user").val(),
                password: $("#host_password").val()
            },
            success: function (data) {
                if (data["value"] == "1") {

                    $("#hostname").val($("#host_name").val());
                    table.ajax.reload();
                    alert(data["text"]);
                } else {
                    alert(data["text"]);

                }
            },
        })
    });
    $("#disksave").click(function () {
        var table = $('#sample_1').DataTable();
        $.ajax({
            type: "POST",
            url: "../../vm_disksave/",
            dataType: 'json',
            data: {
                id: $("#id").val(),
                name: $("#currentvm").val(),
                uuid: $("#uuid").val(),
                poolid: $("#poolid").val(),
                disksize: $("#disksize").val(),
                disktype: $("#disktype").val(),
                selectdisk: $("#selectdisk").val(),
                path: $("#disk_path").val(),
                user: $("#disk_user").val(),
                password: $("#disk_password").val()
            },
            success: function (data) {
                if (data["value"] == "1") {

                    $("#disk_").val(data["size"]);
                    table.ajax.reload();
                    alert(data["text"]);
                } else {
                    alert(data["text"]);

                }
            },
        })
    });
    $("#installcvsave").click(function () {
        var table = $('#sample_1').DataTable();
        $.ajax({
            type: "POST",
            url: "../../vm_installcvsave/",
            dataType: 'json',
            data: {
                id: $("#id").val(),
                uuid: $("#uuid").val(),
                poolid: $("#poolid").val(),
                hostname: $("#hostname").val(),
                path: $("#installcv_path").val(),
                user: $("#installcv_user").val(),
                password: $("#installcv_password").val()
            },
            success: function (data) {
                if (data["value"] == "1") {
                    alert(data["text"]);
                } else {
                    alert(data["text"]);

                }
            },
        })
    });
    $("#bt_registercv").click(function () {
        var table = $('#sample_1').DataTable();
        $.ajax({
            type: "POST",
            url: "../../registercvsave/",
            dataType: 'json',
            data: {hostname: $("#hostname").val()},
            success: function (data) {
                if (data["value"] == "1") {
                    alert(data["text"]);
                } else {
                    alert(data["text"]);

                }
            },
        })
    });

    $("#clone").click(function () {
        if ($("#template_id").val()==""){
            alert("输入有误，请选择虚机模板。");
        }
        else {
            if ($("#instancename").val()=="") {
                alert("输入有误，请输入实例名称。");
            }
            else{
                if ($("#currentvm").val()=="") {
                    alert("输入有误，请输入新虚机名称。")
                }
                else {
                    $.ajax({
                        type: "POST",
                        dataType: 'json',
                        url: "../../clonevm/",
                        data: $('#submit_form').serialize(),
                        success: function (data) {
                            if (data["value"] == "1") {
                                $("#id").val(data["id"]);
                                $("#div1").hide();
                                $("#div2").show();
                                $("#div3").hide();
                            } else {
                                alert(data);

                            }
                        },
                        error: function (e) {
                            alert("克隆失败，请于客服联系。");
                        }
                    })
                }
            }
        }
    });

    $("#bt_shutdown").click(function () {
        $.ajax({
            type: "POST",
            url: "../../shutdownvm/",
            dataType: 'json',
            data: {
                currentvm: $("#currentvm").val(),
                poolid: $("#poolid").val(),
            },
            success: function (data) {
                alert(data['text']);
                $("#onstate").hide();
                $("#offstate").show();
            },
        });
    });

    $("#bt_reboot").click(function () {
        $.ajax({
            type: "POST",
            url: "../../rebootvm/",
            dataType: 'json',
            data: {
                uuid: $("#uuid").val(),
                hostname: $("#hostname").val(),
                poolid: $("#poolid").val(),
            },
            success: function (data) {
                alert(data['text']);
            },
        });
    });

    $("#bt_startup").click(function () {
        $.ajax({
            type: "POST",
            url: "../../poweronvm/",
            dataType: 'json',
            data: {
                currentvm: $("#currentvm").val(),
                poolid: $("#poolid").val(),
            },
            success: function (data) {
                alert(data['text']);
                $("#onstate").show();
                $("#offstate").hide();
            },
        });
    });

    //第三步，选择恢复资源
    if($('#steprunid').val()!=$('#steprunid3').val()){
        $('#destClient').prop("disabled", "disabled");


    }else{
         $('#li3').addClass("active");
         $('#tab3').addClass("active");
    }
    if($('#steprunstate3').val()=="DONE"){
         $('#li3').addClass("done");
    }

    $.fn.zTree.init($("#treeDemo"), setting);

    $('#selectpath').click(function(){
            $('#fs_se_1').empty();
            var treeObj = $.fn.zTree.getZTreeObj("treeDemo");
            var nodes = treeObj.getCheckedNodes(true);
            for (var k = 0, length = nodes.length; k < length; k++) {
                var halfCheck = nodes[k].getCheckStatus();
                if (!halfCheck.half){
                    $("#fs_se_1").append("<option value='\\" + nodes[k].id + "\\'>\\" + nodes[k].id + "\\</option>");
                }
            }
            if (nodes.length==0)
                $("#fs_se_1").append("<option value='\\'>\\</option>");
         })
    FormWizard.init();
    // $.ajax({
    //     type: "POST",
    //     dataType: 'json',
    //     url: "../filecrossin/",
    //     data:
    //         {
    //             id: $("#id").val(),
    //             name: $("#name").val(),
    //             remark: $("#remark").val(),
    //         },
    //     success: function (data) {
    //         var myres = data["res"];
    //         var mydata = data["data"];
    //         if (myres == "新增成功。") {
    //             $("#id").val(data["data"])
    //             $("#se_1").append("<option selected id='" + mydata + "' remark='" + $("#remark").val() + "'>" + $("#name").val() + "</option>");
    //             $("#title").text($("#name").val())
    //         }
    //         if (myres == "修改成功。") {
    //             $("#" + $("#id").val()).text($("#name").val())
    //             $("#" + $("#id").val()).attr('remark', $("#remark").val())
    //             $("#user").show()
    //
    //         }
    //         alert(myres);
    //     },
    //     error: function (e) {
    //         alert("页面出现错误，请于管理员联系。");
    //     }
    // });
});