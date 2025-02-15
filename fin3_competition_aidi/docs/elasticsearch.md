# Elasticsearch

>https://www.elastic.co/jp/elasticsearch

ベクトルデータベースおよび検索エンジンとして使用する．

今回は一時的な利用かつ大規模なデータ処理を必要としないため，プロジェクトディレクトリに閉じたローカルの環境で動作させる．  
そのため，後続の記載はローカルでの一時的な使用を想定した最低限の設定である．  
本格的に利用する場合は，Elastic Platform との連携等，高機能な環境を構築することが望ましい．

## 事前準備

 ### 1. 圧縮ファイルのダウンロードおよび任意ディレクトリでの展開
 ローカルにダウンロードした圧縮ファイルを展開することでプロジェクトディレクトリに閉じて使用することができる．  
以下から開発環境に合わせた圧縮ファイルをダウンロードする．
>https://www.elastic.co/jp/downloads/elasticsearch

解凍ファイルをプロジェクトディレクトリ内の任意のパス（ex. ./fin3_conpetition_aidi/data/）に格納する．

注意点として，MacOSの場合は単に解凍するだけでは使用できず，展開前に以下コマンドを実行する必要がある．  
(セキュリティ設定に変更を加えているので，コマンドの意味を調べてから実行すること)
```
xattr -d -r com.apple.quarantine <archive-or-directory>
```
理由については以下を参照：
>https://www.elastic.co/guide/en/elasticsearch/reference/current/targz.html#install-macos

### 2. 設定ファイル（ `elasticsearch.yml` ）の編集

elasticsearch ディレクトリ内の以下configファイルを編集する．  
`<expanded-direcroty>/elasticsearch/config/elasticsearch.yml`  

なお，テンプレートを以下パスに用意してある．  
[/templates/elasticsearch/elasticsearch_template.yml](../../templates/elasticsearch/elasticsearch_template.yml)

#### 2.1. Elasticsearch に登録するデータのパス  
デフォルトでは以下に格納される  
```powershell
# Windows
C:\ProgramData\Elastic\Elasticsearch\data
```
```bash
# Linux/MacOS
/var/lib/elasticsearch/
```
上記を設定変更する場合は，`elasticsearch.yml`に次の設定を追記することで指定したディレクトリにデータの登録先を変更することができる．
```yaml
path.data: /path/to/data
```

#### 2.2. ログデータの保存先のパス
`elasticsearch.yml`に次の設定を追記することで指定したディレクトリにログを保存することができる．
```yaml
path.logs: /path/to/logs
```

#### 2.3. ネットワーク設定（ローカルアクセス用）
ローカルマシンからのみ接続を許可するため，`elasticsearch.yml`に次の設定を追記する．
```yaml
network.host: 127.0.0.1
http.port: 9200
```

#### 2.4. セキュリティ機能（認証・認可など）を無効化
ローカル開発のため，デフォルトで有効になっている以下セキュリティ機能を無効化する．
- ユーザー認証（Basic認証、APIキー認証など）
- ロールベースアクセス制御（RBAC）
- TLS/SSL 暗号化通信
- 監査ログの記録

`elasticsearch.yml`に次の設定を追記する．
```yaml
xpack.security.enabled: false
```

### 3. 起動
起動スクリプトの実行により Elasticsearch を起動する．
```powershell
# Windows
cd <expanded-direcroty>
.\bin\elasticsearch.bat
```
```bash
# Linux/MacOS
cd <expanded-direcroty>
./bin/elasticsearch
```
稼働確認のため接続する
```cmd
curl http://localhost:9200
```
JSONレスポンスが返ってくれば無事に起動できている．
```json
{
  "name": "your-PC-name",
  "cluster_name": "elasticsearch",
  "version": {
    "number": "8.x.x",
    ...
  }
}
```