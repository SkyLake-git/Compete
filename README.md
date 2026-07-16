# Compete

AtCoder 用のテストケースユーティリティー<br>

## Features

- テストケースを問題ページから取得
- 全てのテストケースを自動実行
  - 実行可能ファイル (.exe) が必要
- 全てのテストケースを自動実行し、全て AC だった場合提出

## How to use

1. 必要なライブラリをインストール: `pip install -r requirements.txt`
2. 実行 `python main.py <command>` または `python -m main <command>` ([コマンドについて](./README.md#commands))
3. これだけ

## Commands

### `credentials`
エイリアス: `cred`

サイト別に認証情報を手動で登録します<br>
(現在 AtCoder のみ対応)<br><br>
サイト別の認証情報の取得方法については [こちら](./README.md#how-to-get-credential-information)

### `preferences`
エイリアス: `pref`

設定を変更します<br>
設定キーの詳細については [こちら](./README.md#preferences-1)

### `start [problem_id]`

問題ページをスクレイピングし、テストケースを取得します<br>
`problem_id` は以下の形式で入力する必要があります: `CONTEST_X`<br>
AtCoder Beginner Contest 400 の A問題 の場合、 `abc400_a` と入力すればよいです

### `test`

実行可能ファイルに対して、全てのテストケースを実行します<br>
提出は行いません<br>

### `watch`

現在のコンテストにおけるあなたの提出を確認します<br>
定期的に更新されます

### `submit`

実行可能ファイルに対して、全てのテストケースを実行します<br>
全てのテストケースにおいて AC だった場合、自動で提出します<br>
提出に成功後、全ての提出の WJ が解消されるまで `watch` します<br>

> [!IMPORTANT]
> 自動提出は、進行中のコンテストのみ可能です。<br>
> その他のコンテストへの提出は Cloudflare Turnstile により不可能です。

> [!TIP]
> ソースコードファイルに以下のようにコメントを追加することで、提出するコードの範囲を指定することができます。
> ```text
> // compete BOF          (提出ソースコードの始まりを指定)
> write your code here
> // compete EOF          (提出ソースコードの終わりを指定)
> ```

コマンド実行時に必要なセットアップが出来ていない場合セットアップウィザードに移行します。

## How to get credential information

### AtCoder

(Google Chrome の場合)
1. AtCoder にログインしているブラウザーで AtCoder サイトを開く
2. 開発者ツールを開く
3. タブの `アプリケーション` を選択
4. 左リストの `ストレージ` から `Cookie` を選択
5. `https://atcoder.jp` を選択
6. 右リスト内の `REVEL_SESSION` を選択し、下に出てくる `Cookie Value` の内容が認証情報
7. 完了

## Preferences

| キー                        | 型         | デフォルト値 | 説明                                                        |
|---------------------------|-----------|--------|-----------------------------------------------------------|
| `executable_path`         | `string`  | `null` | 実行可能ファイルを指定する                                             |
| `source_path`             | `string`  | `null` | ソースコードファイルを指定する                                           |
| `language_id`             | `int`     | `null` | 提出する際の言語を指定する                                             |
| `request_dbg_remain_tail` | `boolean` | `true` | `true` の場合、通信の結果をコンソールに残します                               |


`executable_path`と　`source_path` を指定しない場合、このライブラリの親ディレクトリにある<br>
`CMakeLists.txt` を読み取り自動で指定します。<br><br>
`language_id` を指定しない場合、提出の際にエラーが発生します。<br>

### Language Ids
| Language ID | 説明          |
|-------------|-------------|
| `0`         | C++ (GCC)   |
| `1`         | C++ (Clang) |
