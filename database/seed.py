import asyncio
from datetime import datetime, timezone

from lib.user import hash_password
from tables import ArticleTable, UserTable

from database import get_database_session

dt_now = datetime.now(timezone.utc)

user_alice = UserTable(
    email="alice@example.com",
    name="Alice",
    password_hash=hash_password("password"),
)
user_bob = UserTable(
    email="bob@example.com",
    name="Bob",
    password_hash=hash_password("password"),
)
user_charlie = UserTable(
    email="charlie@example.com",
    name="Charlie",
    password_hash=hash_password("password"),
)

seed_users: list[UserTable] = [user_alice, user_bob, user_charlie]

seed_articles: list[ArticleTable] = [
    ArticleTable(
        author_id=user_alice.id,
        title="はじめてのブログ",
        body="こんにちは！ Alice です。\n初めての投稿です。",
        published_at=dt_now,
    ),
    ArticleTable(
        author_id=user_bob.id,
        title="今日の出来事",
        body="こんにちは！ Bob です。\n今日あったことを書きます。",
        published_at=dt_now,
    ),
    ArticleTable(
        author_id=user_charlie.id,
        title="おすすめの本",
        body="こんにちは！ Charlie です。\n最近読んだ本を紹介します。",
        published_at=dt_now,
    ),
]


async def main():
    async with get_database_session() as db:
        for user in seed_users:
            db.add(user)
        for article in seed_articles:
            db.add(article)
        await db.commit()


if __name__ == "__main__":
    asyncio.run(main())
    print("ok")
