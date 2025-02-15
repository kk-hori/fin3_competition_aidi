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

### 検索対象ドキュメントデータの取得
PDFファイルを取得する．保護がかかっている場合は解除しておく．

## 提出ファイル作成までのスクリプト実行手順

### 1. PDFのテキスト化
PDFファイルをインプットとして，`make_results_aidi_from_pdf.py` を実行する．  

### 2. チャンク分割
1.で取得できるMarkdownファイルをインプットとして `make_files_chunked_from_md.py` を実行する．

### 3. チャンクの埋め込みベクトル化
2.で取得できるJSONファイルをインプットとして `make_json_embeddings_from_json.py` を実行する．

### 4. ベクトルデータベース作成
3.で取得したJSONデータをインプットとして `elasticsearch_store_data.py` を実行する．  
一度上記のスクリプトを実行すると，Elasticsearchに特定のインデックスで登録される．  
登録したデータを削除する場合は `elasticsearch_delete_data.py` を実行する．

### 5. 補足データ作成
1.で取得できるMarkdownファイルをインプットとして `make_json_company_from_md.py`　を実行する．

### 6. 提出用データの作成
`make_csv_submission.py` を実行する．

## ディレクトリ構成
```
.
├── README.md
├── .env（ユーザ自身で作成）
├── requirements.txt
├── config.json : プログラム全体の設定ファイル
├── fin3_competition_aidi : メインディレクトリ
│   ├── data : データ格納ディレクトリ
│   ├── docs : ドキュメント格納ディレクトリ
│   ├── input : スクリプト実行時のインプットファイル格納ディレクトリ
│   ├── output : スクリプト実行時のアウトプットファイル出力先ディレクトリ
│   ├── notebook : notebook形式(.ipynb)格納ディレクトリ
│   └── src : スクリプト(.py)格納ディレクトリ
├── templates : テンプレートファイル格納ディレクトリ
└── tests : (未使用)
```
