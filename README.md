# PENGUIN
PErsonal New-generation Graphic User Interface for November festival

11 月祭に係る事務手続きを補助する Web アプリケーション

## Release
`master` ブランチに push すると下記サイトにリリースされます。

https://dev-penguin.zuya.tokyo/

* このサイトは PENGUIN を模した開発成果物です。
* 11 月祭に関する情報や、**個人情報は絶対に入力しない**でください。
* このサイトに入力された情報は誰でも閲覧できます。
* ログインする際は eptid を入力します。
    * 一般学生としてログイン: e001 - e103
    * スタッフとしてログイン: e201 - e232
    * システム管理者としてログイン: e000
    * 教職員としてログイン: e301
    * ただし、誰でもユーザー情報を更新・削除できるのでここに記載されている内容と現況が異なる場合があります。
* メール送信機能は無効にしています。また、slack は実在するあるワークスペースに送信されます。
    * このワークスペースに招待を希望する場合はお知らせください。


情報は下記 Wiki サイトに掲載します。

https://dev-wiki.zuya.tokyo/penguin/

## Development
開発する際は次の手順に従ってください。

### Prerequests
* [docker-compose](https://docs.docker.com/compose/install/)
* (Optional) [pipenv](https://pypi.org/project/pipenv/)
    * docker-compose を使わずに python 環境を手元に作りたい場合は必要です。

### Steps
1. `git clone https://github.com/Zoniisan/penguin`
1. `make`
    * 環境変数ファイル（git 管理外）が設定されます。
1. 環境設定ファイルを下記のとおり編集します。
    * `django/penguin/.env`
        * `SECRET_KEY` ... ランダムな 50 文字の文字列を設定してください。漏洩注意！
        * `DATABASE_URL` 内の `DB_PASS` ... ランダムな文字列を設定してください。漏洩注意！
        * `SLACK_***` ... slack 関連の設定については Wiki を参照してください。編集しない場合、slack の内容は標準出力に流れます。
    * `.env_postgres`
        * `DB_PASS` ... 上述の `DB_PASS` と同様の内容を記載してください。
1. (Optional) `make install`
    * python の開発向け仮想環境が作成されます（`pipenv install --dev` ）。
    * flake8 - vscode 連携を用いるときなど、手元に python の仮想環境を持ちたい人は使用してください。
1. (Optional) `make loaddata`
    * ユーザー情報などの初期データが投入されます。
    * 投入されるデータは Wiki を参照してください。
1. `make start`
    * 開発用サーバーが起動します。

### `manage.py`
`makemigrations` などのコマンドを利用する際は、下記コマンドを実行してください。
```
docker-compose -f docker-compose.dev.yml exec django python manage.py [COMMAND]
```
* 長すぎるので alias を作成することをおすすめします。

## Contribute
* まずはこのリポジトリを見つけてくれてありがとうございます。
* このリポジトリの owner は非エンジニアで知識や技術がほぼありません。
* そのため、PR を送信していただいたら多分何も言わずに accept します。
    * そのまま自動的に https://dev-penguin.zuya.tokyo に release されます。
* 「ここが酷い」とか「新しいこんな機能どうですか」とかあれば Issue を立てるなどしてください。
* 今の所 Issue / PR の作成、及びブランチ名に係るレギュレーションは定めません。

## Contact
Zuya

Twitter: [@Zoniichan](https://twitter.com/zoniichan)
