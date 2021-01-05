$(function () {
    // ソケット作成
    var ws_protocol = get_ws_protocol();
    const registrationSocket = new WebSocket(
        ws_protocol +
        window.location.host +
        '/ws/register/registration/'
    );

    // 窓口を閉じたことを通知
    setTimeout(function () {
        registrationSocket.send(JSON.stringify({}))
    }, 300);

    // スタッフメニューページにリダイレクト
    setTimeout(function () {
        location.href = "../menu"
    }, 300);
});
