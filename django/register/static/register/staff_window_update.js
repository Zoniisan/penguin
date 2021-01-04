$(function () {
    // 企画種別ごとの飲食物提供情報を取得
    get_food_status();
    // 企画対応の開始を通知
    registration_socket();

    function registration_socket() {
        // 窓口情報を取得
        var windowData = JSON.parse(document.getElementById("window-data").textContent);
        var windowId = windowData["id"];

        // ソケット作成
        const registrationSocket = new WebSocket(
            'ws://' +
            window.location.host +
            '/ws/register/registration/'
        );

        // 呼出操作を行った窓口の ID を渡す
        setTimeout(function () {
            registrationSocket.send(JSON.stringify({
                'call_window_id': windowId
            }))
        }, 300);
    }
});
