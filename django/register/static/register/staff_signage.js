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
            tokenSocket.send({});
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
        const registrationSocket = new WebSocket(
            'ws://' +
            window.location.host +
            '/ws/register/registration/'
        );

        // 更新要求（300ms待機後）
        setTimeout(function () {
            registrationSocket.send(JSON.stringify({
                'update': true
            }))
        }, 300);

        registrationSocket.onmessage = function (e) {
            const data = JSON.parse(e.data);
            document.querySelector('#called-window-name').innerHTML = '';
            document.querySelector('#called-registration-call-id').innerHTML = '';
            document.querySelector('#pending').innerHTML = '';

            // 呼出中
            for (let obj of data["called"]) {
                document.querySelector('#called-window-name').innerHTML += '<th>' + obj["window-name"] + '</th>';
                document.querySelector('#called-registration-call-id').innerHTML += '<td id="window_' + obj["window_id"] + '">' + obj["registration-call-id"] + '</td>';
                if (data["call_window"] == obj["window_id"]) {
                    $('#window_' + obj["window_id"]).effect('pulsate', '', 1000);
                    $('#window_' + obj["window_id"]).addClass('table-warning');
                }
            }

            // 保留
            for (let obj of data["pending"]) {
                document.querySelector('#pending').innerHTML += '<th>' + obj["call_id"] + ' </th>';
            }
        };
    }
});
