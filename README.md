# fin3-competition-aidi
第3回金融データ活用チャレンジの個人作業用リポジトリ．
>https://signate.jp/competitions/1515

Azure AI Document Intelligence による RAG 構築を目指す．

## ディレクトリ構成
後日記載

## 開発環境
使用する言語は `Python (version: 3.11.6)` である．

### 仮想環境
仮想環境等は各自で構築すること．  
なお，仮想環境管理用のファイルは Git の管理対象外とするため，仮想環境管理ツール等は各自で判断すること．

### 外部ライブラリ
インストール対象の外部ライブラリは，プロジェクトルート直下の `requirements.txt` に記載してある．

## コミットルール

### ブランチ
後日記載

### `requirements.txt`
外部ライブラリをインストールした際は，プロジェクトルート直下の上記ファイルに反映すること．

### コミットテンプレートの使用
共通のテンプレートを使用しコミットメッセージを作成する．  
使用するテンプレートは以下パスに格納してある：
```
.templates/git/commit_template.txt
```
本テンプレートを使用するように設定すること．  
例えば，ローカルリポジトリでのみ有効にする場合はプロジェクトルート直下で以下のコマンドを実行する：
```
git config --local commit.template templates/git/commit_template.txt
```
