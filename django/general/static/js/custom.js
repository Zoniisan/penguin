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

// python における format のような関数
// 第 1 引数（str）における %s 部を、第 2 引数以降の変数で置換する
$.format = function (format) {
    var i = 0,
        j = 0,
        r = "",
        next = function (args) {
            j += 1;
            i += 1;
            return args[j] !== void 0 ? args[j] : "";
        };

    for (i = 0; i < format.length; i++) {
        if (format.charCodeAt(i) === 37) {
            switch (format.charCodeAt(i + 1)) {
                case 115:
                    r += next(arguments);
                    break;
                case 100:
                    r += Number(next(arguments));
                    break;
                default:
                    r += format[i];
                    break;
            }
        } else {
            r += format[i];
        }
    }
    return r;
};

// 選択した企画種別に応じて、飲食物提供の選択肢を動的に設定
function get_food_status() {
    // JSON データで飲食物提供に関する情報を取得
    var foodData = JSON.parse(document.getElementById('food-data').textContent);

    // 企画種別を変更するごとに発動
    $('#id_kind').on('change', function () {
        // 選択した 企画種別の ID
        var kind_id = $(this).val();
        // 企画種別に対応する飲食物提供情報を取得
        if (kind_id) {
            var food = foodData.find(element => element.kind_id == kind_id).food;
        }
        switch (food) {
            case 'true':
                // 飲食物提供必須
                $("#id_food").prop({
                    "checked": true,
                    "disabled": true
                });
                $("#alert-food").html('この企画種別は飲食物提供<strong>必須</strong>です！')
                break;
            case 'false':
                // 飲食物提供禁止
                $("#id_food").prop({
                    "checked": false,
                    "disabled": true
                });
                $("#alert-food").html('この企画種別は飲食物提供<strong>禁止</strong>です！')
                break;
            case 'select':
                // 飲食物提供選択可能
                $("#id_food").prop({
                    "checked": false,
                    "disabled": false
                });
                $("#alert-food").html('この企画種別は飲食物を提供するかどうかを選択できます。')
                break;
            default:
                // 企画種別未選択
                $("#id_food").prop({
                    "checked": false,
                    "disabled": true
                });
                $("#alert-food").html('企画種別を選択してください。')
        }
    }).change();
}
