$(function () {
    // 企画種別ごとの飲食物提供情報を取得
    get_food_status();
    // 企画対応の開始を通知
    registration_socket();

    function registration_socket() {
        // ソケット作成
        const registrationSocket = new WebSocket(
            'ws://' +
            window.location.host +
            '/ws/register/registration/'
        );

        // 対応中の企画情報を更新
        setTimeout(function () {
            registrationSocket.send(JSON.stringify({}))
        }, 300);
    }
});
