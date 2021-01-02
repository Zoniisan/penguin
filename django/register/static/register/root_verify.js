$(function () {
    // ソケット作成
    const tokenSocket = new WebSocket(
        'ws://' +
        window.location.host +
        '/ws/register/token/'
    );

    // 企画登録 QR コードの更新をリクエスト
    setTimeout(function () {
        tokenSocket.send({})
    }, 300);

    // 企画登録ページにリダイレクト
    setTimeout(function () {
        location.href = "../create"
    }, 300);
});
