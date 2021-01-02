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

// スタッフメニューページにリダイレクト
setTimeout(function () {
    location.href = "../menu"
}, 300);
