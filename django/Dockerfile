# 公式からpython3.8 on alpine linuxイメージをpull
FROM python:3.8-alpine

# 作業ディレクトリを設定
WORKDIR /usr/src/django

# 環境変数を設定
# Pythonがpyc filesとdiscへ書き込むことを防ぐ
ENV PYTHONDONTWRITEBYTECODE 1
# Pythonが標準入出力をバッファリングすることを防ぐ
ENV PYTHONUNBUFFERED 1

# psycopg2 / pip のインストール
RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add postgresql-dev tzdata \
    && pip install --upgrade pip \
    && pip install psycopg2 pipenv \
    && apk del build-deps

# ホストのpipfileをコンテナの作業ディレクトリにコピー
COPY Pipfile /usr/src/django/

# pipfileからパッケージをインストールしてDjango環境を構築
# 終了後は pipienv をアンインストール
RUN pipenv install --skip-lock --system \
    && pip uninstall -y pipenv virtualenv-clone virtualenv

# ホストのカレントディレクトリ（現在は django ディレクトリ）を作業ディレクトリにコピー
COPY . /usr/src/django/
