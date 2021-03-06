$(function () {
    // 音声 ON ボタンを設置
    unmute_button();
    // 企画登録 QR コード部の処理
    token_socket();
    // 対応中の整理番号部の処理
    registration_socket();

    // 音声 ON ボタンを設置
    function unmute_button() {
        $("#btn-unmute").on("click", function () {
            document.querySelector("#popi").play();
            $(this).remove()
        });
    }

    // 企画登録 QR コード部の処理
    function token_socket() {
        // ソケットを作成
        var ws_protocol = get_ws_protocol();
        const tokenSocket = new WebSocket(
            ws_protocol +
            window.location.host +
            '/ws/register/token/'
        );

        // 読み込み時、企画登録 QR コードを更新
        setTimeout(function () {
            tokenSocket.send(JSON.stringify({}));
        }, 300);

        // 企画登録 QR コードが更新されたら、その内容を表示
        tokenSocket.onmessage = function (e) {
            const data = JSON.parse(e.data);
            document.querySelector('#token-qrcode').src = data.qrcode;
            document.querySelector('#token-url').innerHTML = data.url;
            document.querySelector('#token-create-datetime').innerHTML = data.create_datetime;
            // QR コードハイライト
            $("#qr-header").effect("highlight");
            // QR コード更新音声
            document.querySelector("#popi").play();
        };
    }

    function registration_socket() {
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

            // （あれば）直前に呼出操作を行った企画
            var callWindowId = data['call_window_id']

            // 対応中企画
            document.querySelector('#window-name').innerHTML = '';
            document.querySelector('#waiting-call-id').innerHTML = '';
            for (let obj of data['windows']) {
                document.querySelector('#window-name').innerHTML += $.format(
                    '<th>%s</th>', obj['name']
                )
                if (obj['id'] == callWindowId) {
                    document.querySelector('#waiting-call-id').innerHTML += $.format(
                        '<td id="call-window-highlight"><span>%s</td>', obj['call_id']
                    )
                } else {
                    document.querySelector('#waiting-call-id').innerHTML += $.format(
                        '<td>%s</td>', obj['call_id']
                    )
                }
            }
            if (callWindowId) {
                $("#call-window-highlight").effect("highlight", 5000).dequeue().effect("pulsate", 2000);
                document.querySelector("#chime").play();
            }

            // 保留企画
            document.querySelector('#pending-call-id').innerHTML = '';
            for (let obj of data["pending"]) {
                document.querySelector('#pending-call-id').innerHTML += $.format(
                    '%s ', obj['call_id']
                )
            }
        };
    }
});
