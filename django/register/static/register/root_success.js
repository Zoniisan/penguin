$(function () {
    // ソケット作成
    const registrationSocket = new WebSocket(
        'ws://' +
        window.location.host +
        '/ws/register/registration/'
    );

    // 企画情報を入力したら、待機企画情報を更新する
    setTimeout(function () {
        registrationSocket.send(JSON.stringify({}));
    }, 300);
});
