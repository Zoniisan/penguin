$(function () {
    // ソケット作成
    const registrationSocket = new WebSocket(
        'ws://' +
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
