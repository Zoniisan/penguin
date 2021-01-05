$(function () {
    // ソケット作成
    var ws_protocol = get_ws_protocol();
    const registrationSocket = new WebSocket(
        ws_protocol +
        window.location.host +
        '/ws/register/registration/'
    );

    // 読み込み時に情報を取得
    setTimeout(function () {
        registrationSocket.send(JSON.stringify({}));
    }, 300);

    registrationSocket.onmessage = function (e) {
        const data = JSON.parse(e.data);

        // 対応中企画
        document.querySelector('#windows').innerHTML = '';
        for (let obj of data['windows']) {
            if (obj['call_id'] == '---') {
                document.querySelector('#windows').innerHTML += $.format(
                    '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>---</td></tr>',
                    obj['name'], obj['staff'], obj['call_id'], obj['kind'], obj['str'], obj['temp_leader'], obj['id']
                )
            } else {
                document.querySelector('#windows').innerHTML += $.format(
                    '<tr><td class="table-success">%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td><a class="btn btn-primary" href="/register/staff/admin/detail/%s">詳細</a></td></tr>',
                    obj['name'], obj['staff'], obj['call_id'], obj['kind'], obj['str'], obj['temp_leader'], obj['register_id']
                )
            }
        }

        // 待機状態企画
        document.querySelector('#waiting').innerHTML = '';
        for (let obj of data['waiting']) {
            document.querySelector('#waiting').innerHTML += $.format(
                '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td><a class="btn btn-primary" href="/register/staff/admin/detail/%s">詳細</a></td></tr>',
                obj['call_id'], obj['kind'], obj['str'], obj['temp_leader'], obj['id']
            )
        }

        // 保留状態企画
        document.querySelector('#pending').innerHTML = '';
        for (let obj of data['pending']) {
            document.querySelector('#pending').innerHTML += $.format(
                '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td><a class="btn btn-primary" href="/register/staff/admin/detail/%s">詳細</a></td></tr>',
                obj['call_id'], obj['kind'], obj['str'], obj['temp_leader'], obj['id']
            )
        }
    }
});
