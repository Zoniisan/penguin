// 窓口の情報を取得
var windowData = JSON.parse(document.getElementById('window-data').textContent);

// ソケット作成
const registrationSocket = new WebSocket(
    'ws://' +
    window.location.host +
    '/ws/register/registration/'
);

// 窓口が対応する企画種別について、待機・保留の企画一覧をリクエスト
setTimeout(function () {
    registrationSocket.send(JSON.stringify({
        'window_id': windowData['window_id']
    }))
}, 300);

registrationSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);

    // 待機
    document.querySelector('#waiting').innerHTML = '';
    for (let obj of data["waiting"]) {
        document.querySelector('#waiting').innerHTML += $.format(
            '<tr><td class="h1">%s</td><td>%s<br>%s<br>%s</td><td><a href="/register/staff/window/%s/%s" class="btn btn-primary">呼出</a></td></tr>',
            obj["call_id"], obj["kind"], obj["str"], obj["temp_leader"], windowData["window_id"], obj[
                "id"],
        );
    }

    // 保留
    document.querySelector('#pending').innerHTML = '';
    for (let obj of data["pending"]) {
        document.querySelector('#pending').innerHTML += $.format(
            '<tr><td class="h1">%s</td><td>%s<br>%s<br>%s</td><td><a href="/register/staff/window/%s/%s" class="btn btn-primary">呼出</a></td></tr>',
            obj["call_id"], obj["kind"], obj["str"], obj["temp_leader"], windowData["window_id"], obj[
                "id"],
        );
    }
};
