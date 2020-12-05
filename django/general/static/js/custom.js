$(function () {
        $('tr[data-href]', 'table.table-clickable').on('click', function () {
                location.href = $(this).data('href');
            }

        );
    }

);
