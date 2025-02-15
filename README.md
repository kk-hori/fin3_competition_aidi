# fin3_competition_aidi
第3回金融データ活用チャレンジの個人作業用リポジトリ
>https://signate.jp/competitions/1515

企業のESG（環境・社会・ガバナンス）レポートや統合報告書のドキュメント（PDF）の内容に関する RAG を構築する．

RAG構築に不可欠なデータ前処理およびデータ検索処理として，以下を採用した．
 - PDF前処理 : Azure AI Document intelligence（Microsoft Azure の Azure AI services の1サービス）
 - 検索処理 : Elasticsearch（OSSの分散検索および分析エンジン）

## 開発環境
使用する言語は `Python (version: 3.11.6)` である．  
プロジェクトルート直下の `requirements.txt` をもとに外部ライブラリをインストールする．

## コミットルール

### 外部ライブラリを新規にインストールしたとき
必ず `requirements.txt` を更新する．

### コミットテンプレートの使用
共通のテンプレートを使用しコミットメッセージを作成する．  
使用するテンプレートは以下パスに格納してある．  
[./templates/git/commit_template.txt](./templates/git/commit_template.txt)

本テンプレートを使用するように設定すること．  
例えば，ローカルリポジトリでのみ有効にする場合はプロジェクトルート直下で以下のコマンドを実行する：
```
git config --local commit ./template templates/git/commit_template.txt
```

## 事前準備
各スクリプト実行前に，以下を準備する．

### Azure AI Document intelligence　の実行環境構築と接続情報の取得
[Azure_AI_Document_intelligence.md](./fin3_competition_aidi/docs/Azure_AI_Document_intelligence.md) の前半を参照．

### Elasticsearch の実行環境構築
[Erasticsearch.md](./fin3_competition_aidi/docs/elasticsearch.md) の前半を参照．

### OpenAI or Azure OpenAI モデルの接続情報の取得
公式リファレンスを参照し，APIキーを取得する．

### .envファイルの作成
上記の各情報を設定した `.env` ファイルを作成し，プロジェクトルート直下に格納する．  
以下にテンプレートを用意してある．  
[./templates/dot_env_dotenv_temlate.txt](./templates/dot_env/dotenv_template.txt)

