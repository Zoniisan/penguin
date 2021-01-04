$(function () {
    // 窓口情報を取得
    var windowData = JSON.parse(document.getElementById("window-data").textContent);
    var windowId = windowData["id"];
    var kindIdList = windowData["kind_id_list"];

    // ソケット作成
    const registrationSocket = new WebSocket(
        'ws://' +
        window.location.host +
        '/ws/register/registration/'
    );

    // 窓口が対応する企画種別について、待機・保留の企画一覧をリクエスト
    setTimeout(function () {
        registrationSocket.send(JSON.stringify({}))
    }, 300);

    registrationSocket.onmessage = function (e) {
        const data = JSON.parse(e.data);

        // 待機
        waiting_list = data["waiting"].filter(function(item, _){
            if (kindIdList.includes(item["kind_id"])) return true;
        })
        document.querySelector('#waiting').innerHTML = '';
        for (let obj of waiting_list) {
            document.querySelector('#waiting').innerHTML += $.format(
                '<tr><td class="h1">%s</td><td>%s<br>%s<br>%s</td><td><a href="/register/staff/window/%s/%s" class="btn btn-primary">呼出</a></td></tr>',
                obj["call_id"], obj["kind"], obj["str"], obj["temp_leader"], windowId, obj[
                    "id"],
            );
        }

        // 保留
        pending_list = data["pending"].filter(function(item, _){
            if (kindIdList.includes(item["kind_id"])) return true;
        })
        document.querySelector('#pending').innerHTML = '';
        for (let obj of pending_list) {
            document.querySelector('#pending').innerHTML += $.format(
                '<tr><td class="h1">%s</td><td>%s<br>%s<br>%s</td><td><a href="/register/staff/window/%s/%s" class="btn btn-primary">呼出</a></td></tr>',
                obj["call_id"], obj["kind"], obj["str"], obj["temp_leader"], windowId, obj[
                    "id"],
            );
        }
    };
});
