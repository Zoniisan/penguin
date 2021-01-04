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
        const tokenSocket = new WebSocket(
            'ws://' +
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

    // 対応中の整理番号部の処理
    function registration_socket() {
        // ソケット作成
        const registrationSocket = new WebSocket(
            'ws://' +
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
            document.querySelector('#window-name').innerHTML = '';
            document.querySelector('#waiting-call-id').innerHTML = '';
            for (let obj of data['windows']) {
                document.querySelector('#window-name').innerHTML += $.format(
                    '<th>%s</th>', obj['name']
                )
                document.querySelector('#waiting-call-id').innerHTML += $.format(
                    '<td>%s</td>', obj['call_id']
                )
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
