# X 自動投稿

## セットアップ

### 1. X Developer PortalでAPIキーを取得

https://developer.x.com/en/portal/dashboard

- App作成 → Keys and Tokens から以下4つを取得:
  - API Key
  - API Key Secret
  - Access Token
  - Access Token Secret

※ App permissions を **Read and Write** にすること

### 2. GitHubリポジトリにSecretsを登録

Settings → Secrets and variables → Actions で以下を追加:

| Secret名 | 値 |
|---|---|
| `X_API_KEY` | API Key |
| `X_API_SECRET` | API Key Secret |
| `X_ACCESS_TOKEN` | Access Token |
| `X_ACCESS_TOKEN_SECRET` | Access Token Secret |

### 3. 投稿テンプレを編集

`templates/posts.json` にネタを追加:

```json
[
  {"text": "投稿したい内容", "posted": false},
  {"text": "別の投稿 #hashtag", "posted": false}
]
```

## 使い方

### 自動投稿（毎日12:00 JST）
GitHub Actionsが自動で `posts.json` からランダムに1つ投稿。

### 手動投稿
GitHub Actions → X Auto Post → Run workflow
- テキスト欄に書けばその内容を投稿
- 空欄ならテンプレからランダム

### ローカルで実行
```bash
export X_API_KEY="..."
export X_API_SECRET="..."
export X_ACCESS_TOKEN="..."
export X_ACCESS_TOKEN_SECRET="..."

cd x-auto-post
pip install -r requirements.txt

# テンプレからランダム
python post.py

# 直接テキスト指定
python post.py --text "投稿したい内容"
```
