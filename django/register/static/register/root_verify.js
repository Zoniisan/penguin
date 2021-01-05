$(function () {
    // ソケット作成
    var ws_protocol = get_ws_protocol();
    const tokenSocket = new WebSocket(
        ws_protocol +
        window.location.host +
        '/ws/register/token/'
    );

    // 企画登録 QR コードの更新をリクエスト
    setTimeout(function () {
        tokenSocket.send(JSON.stringify({}))
    }, 300);

    // 企画登録ページにリダイレクト
    setTimeout(function () {
        location.href = "../create"
    }, 300);
});
