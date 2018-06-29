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
                url: "../../filecrossnext1/",
                data:
                    {
                        restoreTime:myrestoreTime,
                        setprunid:$('#steprunid').val(),
                    },
                success: function (data) {
                    if (data["res"] == "执行成功。") {
                        $('#steprunid').val(data["data"]);
                        $('#steprunid2').val(data["data"]);
                        $('#divtable').hide();
                        $('#radio1').prop("disabled", "disabled");
                        $('#radio2').prop("disabled", "disabled");
                        $('#datetimepicker').prop("readonly", "readonly");

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


                    if (form.valid() == false) {
                        return false;
                    }

                    handleTitle(tab, navigation, index);
                },
                onPrevious: function (tab, navigation, index) {

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

jQuery(document).ready(function() {

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

    if($('#steprunstate1').val()=="DONE"){
         $('#li1').addClass("done");
         $('#divtable').hide();
        $('#radio1').prop("disabled", "disabled");
        $('#radio2').prop("disabled", "disabled");
        $('#datetimepicker').prop("readonly", "readonly");

    }
    if($('#steprunstate2').val()=="EDIT"){
         $('#li2').addClass("active");
         $('#tab2').addClass("active");

    }
    $('#datetimepicker').datetimepicker({
        format:'yyyy-mm-dd hh:ii:ss',
        });

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