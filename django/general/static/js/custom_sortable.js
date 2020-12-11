var sortable_tbody = document.getElementById('sortable-tbody');
var sortable_form = document.getElementById('sortable-form');
var sortable = Sortable.create(sortable_tbody, {
    onSort: function(evt) {
        var items = sortable_tbody.querySelectorAll('tr');
        for (var i = 0; i < items.length; i++) {
            field_id = '#id_new_order_' + items[i].id
            sortable_form.querySelector(field_id).value = i;
        }
    },
    delay: 50,
});
