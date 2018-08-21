$(document).ready(function () {
    $('#sample_1').dataTable({
        "bAutoWidth": true,
        "bSort": false,
        "bProcessing": true,
        "ajax": "../falconstorsearchdata?runstate=" + $('#runstate').val() + "&startdate=" + $('#startdate').val() + "&enddate=" + $('#enddate').val() + "&processname=" + $('#processname').val()+ "&runperson=" + $('#runperson').val(),
        "columns": [
            {"data": "processrun_id"},
            {"data": "process_name"},
            {"data": "createuser"},
            {"data": "state"},
            {"data": "run_reason"},
            {"data": "starttime"},
            {"data": "endtime"},
            {"data": "process_id"},
            {"data": "process_url"},
            {"data": null},
        ],
        "columnDefs": [{
            "targets": 0,
            "render": function (data, type, full) {
                return "<td><a href='process_url'>data</a></td>".replace("data", data).replace("process_url", full.process_url + "/" + full.processrun_id)
            }
        }, {
            "visible": false,
            "targets": -2  // 倒数第一列
        }, {
            "visible": false,
            "targets": -3  // 倒数第一列
        }, {
            "targets": -1,  // 指定最后一列添加按钮；
            "data": null,
            "width": "60px",  // 指定列宽；
            "defaultContent": "<button title='报告'  id='report' class='btn btn-xs btn-primary' type='button'><i class='fa fa-arrow-down'></i>"
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
    $('#startdate').datetimepicker({
        autoclose: true,
        minView: "month",
        format: 'yyyy-mm-dd',
    });
    $('#enddate').datetimepicker({
        autoclose: true,
        minView: "month",
        format: 'yyyy-mm-dd',
    });
    $('#cx').click(function () {
        var table = $('#sample_1').DataTable();
        table.ajax.url("../falconstorsearchdata?runstate=" + $('#runstate').val() + "&startdate=" + $('#startdate').val() + "&enddate=" + $('#enddate').val() + "&processname=" + $('#processname').val()+ "&runperson=" + $('#runperson').val()).load();
    })

    // 生成报告
    $('#sample_1 tbody').on('click', 'button#report', function () {
        var table = $('#sample_1').DataTable();
        var data = table.row($(this).parents('tr')).data();
        $("#processid").val(data.process_id);
        $("#processrunid").val(data.processrun_id);
        $("#static01").modal({backdrop: "static"});

        // 写入当前时间
        var myDate = new Date();
        $("#run_time").val(myDate.toLocaleString());
    });

});