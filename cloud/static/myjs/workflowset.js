$(document).ready(function() {
    $("#stepdiv").empty();
    $.ajax({
        type: "POST",
        url: "../getsetps/",
        data:
            {
                process: $("#process").val()
            },
        dataType: "json",
        success: function (data) {
            var divtxt = ""
            for (var i = 0; i < data.length; i++) {
                var first=""
                var last=""
                if(i==0)
                    first="first"
                if(i==data.length-1)
                    last="last"
                divtxt += "<div onclick=\"myFunction(this)\" id='div_" +data[i]["id"] + "' class='col-md-2 mt-step-col "+ first + " " + last + "  active' data-toggle='modal'  data-target='#static'><div class='mt-step-number bg-white'>" + (i+1).toString() + "</div><div class='mt-step-title uppercase font-grey-cascade'><span id='name_" +data[i]["id"] + "'>" +data[i]["name"] + "</span><input hidden id='approval_" +data[i]["id"] + "' type='text' name='approval_" +data[i]["id"] + "' value='" + data[i]["approval"] +  "'><input hidden id='skip_" +data[i]["id"] + "' type='text' name='skip_" +data[i]["id"] + "' value='" + data[i]["skip"] +  "'><input hidden id='group_" +data[i]["id"] + "' type='text' name='group_" +data[i]["id"] + "' value='" + data[i]["group"] +  "'><input hidden id='time_" +data[i]["id"] + "' type='text' name='time_" +data[i]["id"] + "' value='" + data[i]["time"] +  "'></div><div class=\"mt-step-content font-grey-cascade\"><span id='curstring_" +data[i]["id"] + "'>" +data[i]["curstring"]  + "</div></div>"

            }
            $("#stepdiv").append(divtxt)
        },
        error : function(e){
                alert("流程读取失败，请于客服联系。");
            }
    });

    $("#process").change(function () {
        $("#stepdiv").empty();
        $.ajax({
            type: "POST",
            url: "../getsetps/",
            data:
                {
                    process: $("#process").val()
                },
            dataType: "json",
            success: function (data) {
                var divtxt = ""
                for (var i = 0; i < data.length; i++) {
                    var first=""
                    var last=""
                    if(i==0)
                        first="first"
                    if(i==data.length-1)
                        last="last"
                    divtxt += "<div onclick=\"myFunction(this)\" id='div_" +data[i]["id"] + "' class='col-md-2 mt-step-col "+ first + " " + last + "  active' data-toggle='modal'  data-target='#static'><div class='mt-step-number bg-white'>" + (i+1).toString() + "</div><div class='mt-step-title uppercase font-grey-cascade'><span id='name_" +data[i]["id"] + "'>" +data[i]["name"] + "</span><input hidden id='approval_" +data[i]["id"] + "' type='text' name='approval_" +data[i]["id"] + "' value='" + data[i]["approval"] +  "'><input hidden id='skip_" +data[i]["id"] + "' type='text' name='skip_" +data[i]["id"] + "' value='" + data[i]["skip"] +  "'><input hidden id='group_" +data[i]["id"] + "' type='text' name='group_" +data[i]["id"] + "' value='" + data[i]["group"] +  "'><input hidden id='time_" +data[i]["id"] + "' type='text' name='time_" +data[i]["id"] + "' value='" + data[i]["time"] +  "'></div><div class=\"mt-step-content font-grey-cascade\"><span id='curstring_" +data[i]["id"] + "'>" +data[i]["curstring"]  + "</div></div>"

                }
                $("#stepdiv").append(divtxt)
            },
                error : function(e){
                alert("流程读取失败，请于客服联系。");
            }
        });
    });
    $("#approval").change(function () {
        if($("#approval").val()!="1"){
            $("#group").prop("disabled", true)
             $("#group").val("")
        }
        else
            $("#group").removeProp("disabled");

    });
    $('#save').click(function(){
        $.ajax({
            type: "POST",
            url: "../setpsave/",
            data: {
                        id: $("#id").val(),
                        name:$("#name").val(),
                        time:$("#time").val(),
                        skip:$("#skip").val(),
                        approval:$("#approval").val(),
                        group:$("#group").val(),
                    },
            success:function(data){
                    alert(data);
                    $("#name_" + $("#id").val()).text($("#name").val());
                    $("#time_" + $("#id").val()).val($("#time").val());
                    $("#approval_" + $("#id").val()).val($("#approval").val());
                    $("#skip_" + $("#id").val()).val($("#skip").val());
                    $("#group_" + $("#id").val()).val($("#group").val());
                    var approvaltext =""
                    if($("#approval").val()=="1")
                        approvaltext="需审批"
                    var skiptext =""
                    if($("#skip").val()=="1")
                        skiptext="可跳过"
                    $("#curstring_" + $("#id").val()).text(approvaltext+skiptext);
                    $('#static').modal('hide');
            },
            error : function(e){
                alert("保存失败，请于客服联系。");
            }
        });
    })
} );

function myFunction(ob)
{
    var id=$(ob).attr("id");
    $("#id").val(id.replace("div_", ""));
    $("#name").val($("#"+id.replace("div", "name")).text());
    $("#time").val($("#"+id.replace("div", "time")).val());
    $("#skip").val($("#"+id.replace("div", "skip")).val());
    $("#approval").val($("#"+id.replace("div", "approval")).val());
    $("#group").val($("#"+id.replace("div", "group")).val());
    if($("#approval").val()!="1") {
        $("#group").val("")
        $("#group").prop("disabled", true)
    }
    else
        $("#group").removeProp("disabled");
}