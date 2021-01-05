$(document).ready(function () {
    $.extend($.fn.dataTable.defaults, {
        language: {
            url: "http://cdn.datatables.net/plug-ins/9dcbecd42ad/i18n/Japanese.json"
        }
    });
    var table = $('#registration').DataTable({
        'serverSide': true,
        'ajax': '/api/registration/?format=datatables',
        'columns': [{
                'data': 'verbose_id'
            },
            {
                'data': 'kind',
                'name': 'kind.name'
            },
            {
                'data': 'group',
                'name': 'group, group_kana'
            },
            {
                'data': 'temp_leader',
                'name': 'temp_leader.last_name, temp_leader.first_name, temp_leader.last_name_kana, temp_leader.first_name_kana'
            },
            {
                'data': 'finish_datetime'
            },
        ],
        'createdRow': function (row, data, dataIndex) {
            // data-hrefにURLを追加してから、クリック時にそちらへ遷移させる
            var id = data.id
            var urlForm = `/register/staff/admin/detail/${id}`;
            $(row).attr('data-href', urlForm)
                // クリックしたら遷移
                .click(function (e) {
                    window.location = $(e.target).closest('tr').data('href');
                });
        },
    });
    $('.btn-kind').on('click', function () {
        table.columns().search('');
        var rel = $(this).attr('rel');
        $(".btn-kind").removeClass("btn-primary").addClass("btn-secondary");
        $(this).removeClass("btn-secondary").addClass("btn-primary");
        if (rel) {
            table.columns(1).search(rel).draw();
        } else {
            table.draw();
        }
    });
});
