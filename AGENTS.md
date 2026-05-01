# AGENTS.md

コーディング AI がこのリポジトリで効率的に作業するための参照ドキュメントです。

---

## プロジェクト概要

認証機能（サインアップ・サインイン・サインアウト・セッション確認）を備えた Web アプリケーションのベース実装。今後ここに機能を追加していく前提で構成されている。

---

## リポジトリ構成

```
/workspace/
├── backend/          # Python FastAPI バックエンド
│   ├── app.py        # FastAPI アプリケーション本体
│   ├── models.py     # 共通 Pydantic モデル（HTTPExceptionBody 等）
│   ├── settings.py   # 環境変数設定（Pydantic BaseSettings）
│   ├── lib/          # ビジネスロジック層
│   └── views/        # HTTPルートハンドラ層
├── database/         # バックエンドと共有する DB 層（PYTHONPATH に含まれる）
│   ├── database.py   # SQLAlchemy エンジン・セッション
│   ├── tables.py     # SQLModel テーブル定義
│   ├── utils.py      # Fields ヘルパークラス
│   └── migrations/   # Alembic マイグレーション
├── frontend/         # React TypeScript フロントエンド
│   └── src/
│       ├── App.tsx         # ルーティング定義
│       ├── atoms.ts        # Jotai グローバル状態
│       ├── api-spec.d.ts   # 自動生成 OpenAPI 型定義（編集不要）
│       ├── lib/            # 共通ロジック
│       ├── components/     # 共通コンポーネント
│       └── pages/          # ページコンポーネント
├── .devcontainer/    # 開発コンテナ設定（Docker + Nginx）
├── .vscode/tasks.json
└── generate-api-spec.sh
```

---

## 技術スタック

| 領域 | 技術 | バージョン |
|------|------|-----------|
| バックエンド | FastAPI | 0.135+ |
| ORM | SQLModel + SQLAlchemy | 0.0.38 / 2.0 |
| DB | PostgreSQL | 18 |
| マイグレーション | Alembic | latest |
| 認証 | PyJWT (HS256, HttpOnly Cookie) | 2.12 |
| パスワード | PBKDF2-SHA256 | 標準ライブラリ |
| フロントエンド | React + TypeScript | 19 / 6.0 |
| ルーティング | React Router | 7 |
| 状態管理 | Jotai | 2.19 |
| UI コンポーネント | Ant Design | 6 |
| API クライアント | openapi-fetch | 0.17 |
| ビルドツール | Vite | 8 |
| Python ランタイム | Python | 3.14 |
| JS ランタイム | Bun | 1 |
| Linter (Python) | Ruff | — |
| Linter (JS/TS) | OXC | 1.62 |

---

## 開発環境

Dev Container（Docker Compose）で動作する。ポート 8080 に Nginx が立ち、`/api/*` をバックエンド（8000）に、`/` をフロントエンド（5173）にリバースプロキシする。

---

## よく使うコマンド

```bash
# 開発サーバー起動
fastapi dev backend/app.py          # バックエンド（port 8000）
bun run --cwd frontend dev --host   # フロントエンド（port 5173）

# テスト
pytest backend/tests/

# API 型定義の再生成（FastAPI の OpenAPI スキーマ → TypeScript）
bash generate-api-spec.sh
```

---

## バックエンド設計パターン

### 新しいエンドポイントグループを追加する

1. `backend/views/<name>.py` にルーターを作成
2. `backend/app.py` で `app.include_router(...)` に追加（プレフィックスは `/api/<name>`）

```python
# backend/views/articles.py の例
from fastapi import APIRouter
router = APIRouter()

@router.get("/")
async def list_articles(): ...
```

```python
# backend/app.py に追加
import views.articles as views_articles
app.include_router(views_articles.router, prefix="/api/articles")
```

### DB セッションの使い方

```python
from database import get_database_session

async with get_database_session() as db:
    result = await db.exec(select(UserTable).where(...))
    user = result.first()
```

### エラーレスポンス

カスタムエラー型は `backend/models.py` の `HTTPExceptionBody[T]` を使う。エンドポイントの `responses=` に型を宣言することで OpenAPI に反映される（→ フロントエンドの型推論に効く）。

```python
@router.post("/", responses={400: {"model": HTTPExceptionBody[MyErrorType]}})
async def create_something(...):
    raise HTTPException(status_code=400, detail="MY_ERROR_TYPE")
```

### 認証が必要なエンドポイント

```python
from lib.session import AuthSession, get_session
from fastapi import Depends

@router.get("/me")
async def get_me(session: AuthSession = Depends(get_session)) -> AuthSession:
    return session  # session.id, session.name, session.email が利用可能
```

---

## データベース設計パターン

### テーブル定義（`database/tables.py`）

`BaseTable`（UUID PK）と `TimestampMixin`（created_at, updated_at）を継承する。

```python
class ArticleTable(TimestampMixin, BaseTable, table=True):
    __tablename__ = "article"

    author_id: uuid.UUID = Fields.foreign_key(column="user.id", index=True)
    title: str = Fields.text()
    body: str = Fields.text()
    published_at: datetime | None = Field(default=None, index=True)

    author: UserTable | None = Fields.relationship_has_one(back_populates="articles")
    comments: list["CommentTable"] = Fields.relationship_has_many(back_populates="article")
```

### Fields ヘルパー（`database/utils.py`）

| メソッド | 用途 |
|---------|------|
| `Fields.uuid(primary_key=True)` | UUID 型 PK |
| `Fields.text(unique=False, index=False)` | TEXT 型（VARCHAR ではなく TEXT を使う） |
| `Fields.jsonb()` | JSONB 型（default `{}`) |
| `Fields.foreign_key(column="table.id", index=True)` | 外部キー（UUID） |
| `Fields.relationship_has_one(back_populates=...)` | 1 対 1 リレーション |
| `Fields.relationship_has_many(back_populates=..., cascade_delete=True)` | 1 対 多リレーション（デフォルトでカスケード削除） |

### マイグレーション作成ルール

- `database/tables.py` を変更したら必ずマイグレーションを生成して適用する
- rev-id は `date -u +'%Y%m%d_%H%M%S'` 形式を使う（既存の命名規則に合わせる）

---

## フロントエンド設計パターン

### 新しいページを追加する

1. `frontend/src/pages/<Name>Page.tsx` を作成
2. `frontend/src/App.tsx` の `<Routes>` に `<Route>` を追加

### 認証済みセッションの取得

```typescript
// lib/auth.ts の useSession() を使う（未認証なら /signin にリダイレクト）
import { useSession } from "../lib/auth";

const IndexPage: FC = () => {
  const session = useSession();
  // session.name, session.email が利用可能
};
```

### API 呼び出し

```typescript
import { client } from "../lib/api";

// openapi-fetch による型安全な呼び出し
const { data, error } = await client.POST("/api/auth/signin", {
  body: { email, password },
});
```

### API 型定義の更新フロー

バックエンドの API を変更したら以下を実行する：

```bash
bash generate-api-spec.sh
```

これにより `frontend/src/api-spec.d.ts` が再生成される（このファイルは直接編集しない）。

### 状態管理（Jotai）

グローバル状態は `frontend/src/atoms.ts` に定義する。現在は `authSessionAtom`（起動時に `/api/auth/session` を fetch する非同期 atom）のみ。

---

## テスト

### 構成

- フレームワーク: pytest + anyio（非同期テスト）
- HTTP テスト: `httpx.AsyncClient` + ASGI transport（実際のアプリに対してリクエストを投げる）
- モック: `unittest.mock`

### 既存テストの場所

```
backend/tests/lib/test_user.py    # ユーザー登録・認証のユニットテスト
backend/tests/views/test_auth.py  # 認証エンドポイントの統合テスト
```

### テスト追加のパターン

```python
# views テストの例（test_auth.py を参考にする）
import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import patch, AsyncMock
from app import app

@pytest.mark.anyio
async def test_something():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/auth/signup", json={...})
    assert response.status_code == 200
```

---

## 重要ファイルの早引き

| ファイル | 内容 |
|---------|------|
| [backend/app.py](backend/app.py) | FastAPI インスタンス、ルーター登録 |
| [backend/settings.py](backend/settings.py) | 環境変数定義 |
| [backend/models.py](backend/models.py) | 共通レスポンス型（HTTPExceptionBody） |
| [backend/lib/session.py](backend/lib/session.py) | JWT セッション（get/set/clear） |
| [backend/lib/user.py](backend/lib/user.py) | ユーザー登録・認証ロジック |
| [backend/views/auth.py](backend/views/auth.py) | 認証エンドポイント（実装の参考） |
| [database/tables.py](database/tables.py) | テーブル定義（全テーブルここに追加） |
| [database/utils.py](database/utils.py) | Fields ヘルパー |
| [database/database.py](database/database.py) | get_database_session() |
| [frontend/src/App.tsx](frontend/src/App.tsx) | ルーティング |
| [frontend/src/atoms.ts](frontend/src/atoms.ts) | グローバル状態 |
| [frontend/src/lib/api.ts](frontend/src/lib/api.ts) | openapi-fetch クライアント |
| [frontend/src/lib/auth.ts](frontend/src/lib/auth.ts) | useSession(), signout() |
| [generate-api-spec.sh](generate-api-spec.sh) | OpenAPI → TypeScript 型生成 |
| [.vscode/tasks.json](.vscode/tasks.json) | VSCode タスク定義（コマンド参照） |
