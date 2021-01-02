// ソケット作成
const registrationSocket = new WebSocket(
    'ws://' +
    window.location.host +
    '/ws/register/registration/'
);

// 窓口の情報を取得
var windowData = JSON.parse(document.getElementById('window-data').textContent);

// 対応中の企画情報を更新
setTimeout(function () {
    registrationSocket.send(JSON.stringify({
        'update': true,
        'call_window': windowData['window_id']
    }))
}, 300);

// 企画種別ごとの飲食物提供情報を取得
get_food_status();
