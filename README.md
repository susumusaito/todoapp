# ToDo App

FastAPI + HTMX + Tailwind/DaisyUI + SQLite で構築したToDoアプリケーション。
Gemini APIによるAIコーチ機能付き。

## セットアップ

```bash
# 仮想環境の作成・有効化
python -m venv .venv
source .venv/bin/activate

# 依存パッケージのインストール
pip install -r requirements.txt

# 環境変数の設定
cp .env.example .env
# .env を編集して GEMINI_API_KEY を設定
```

## 起動方法

```bash
uvicorn app.main:app --reload
```

ブラウザで http://localhost:8000 にアクセス。

## 環境変数

| 変数名 | 説明 | デフォルト |
|--------|------|-----------|
| `GEMINI_API_KEY` | Google Gemini API キー | (必須) |
| `GEMINI_MODEL` | 使用するGeminiモデル | `gemini-2.0-flash` |

## 画面構成

- **ダッシュボード** (`/`): タスク一覧・作成フォーム・統計・AIコーチを1画面に表示
- タスクの追加・編集・削除はHTMXによるページ遷移なしの部分更新

## エンドポイント一覧

| メソッド | パス | 説明 |
|---------|------|------|
| GET | `/` | ダッシュボード表示 |
| POST | `/todos` | タスク作成 |
| PUT | `/todos/{id}` | タスク更新 |
| DELETE | `/todos/{id}` | タスク削除 |
| POST | `/ai-coach/generate` | AIコーチアドバイス生成 |

## 技術スタック

- **バックエンド**: FastAPI + SQLModel (SQLite)
- **フロントエンド**: Tailwind CSS + DaisyUI + HTMX (すべてCDN、Node不要)
- **AI**: Google Gemini API
- **テンプレート**: Jinja2
