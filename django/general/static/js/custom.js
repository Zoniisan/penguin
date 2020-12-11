$(function () {
        $('tr[data-href]', 'table.table-clickable').on('click', function () {
                location.href = $(this).data('href');
            }

        );
    }

);

$(".table-check tbody tr").click(function (e) {
    //ignore when click on the checkbox
    if ($(e.target).is(':checkbox')) return;

    var $cb = $(this).find(':checkbox');
    $cb.prop('checked', !$cb.is(':checked'));
});
