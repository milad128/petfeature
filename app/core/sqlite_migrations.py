"""Lightweight SQLite schema patches for local development."""

import json

from sqlalchemy import inspect, text
from sqlalchemy.engine import Connection


def migrate_books_schema(connection: Connection) -> None:
    if connection.dialect.name != "sqlite":
        return

    existing = {column["name"] for column in inspect(connection).get_columns("books")}
    additions = {
        "buy_link_title": "VARCHAR(300)",
        "buy_link_url": "VARCHAR(1000)",
        "download_file": "VARCHAR(1000)",
    }
    for column_name, column_type in additions.items():
        if column_name not in existing:
            connection.execute(text(f"ALTER TABLE books ADD COLUMN {column_name} {column_type}"))

    if "buy_links" in existing:
        connection.execute(text("ALTER TABLE books DROP COLUMN buy_links"))

    if "show_in_library" not in existing:
        connection.execute(
            text("ALTER TABLE books ADD COLUMN show_in_library BOOLEAN NOT NULL DEFAULT 1")
        )

    media_link_columns = {
        column["name"] for column in inspect(connection).get_columns("book_media_links")
    }
    if "title" not in media_link_columns:
        connection.execute(text("ALTER TABLE book_media_links ADD COLUMN title VARCHAR(300)"))

    if "labels" in existing:
        migrate_labels_to_categories(connection)
        connection.execute(text("ALTER TABLE books DROP COLUMN labels"))


def migrate_labels_to_categories(connection: Connection) -> None:
    rows = connection.execute(text("SELECT id, labels FROM books")).fetchall()
    name_to_id: dict[str, int] = {
        row[0]: row[1]
        for row in connection.execute(text("SELECT name, id FROM categories")).fetchall()
    }
    for book_id, raw_labels in rows:
        try:
            labels = json.loads(raw_labels) if raw_labels else []
        except (TypeError, ValueError):
            continue
        for label in labels:
            label = str(label).strip()
            if not label:
                continue
            category_id = name_to_id.get(label)
            if category_id is None:
                result = connection.execute(
                    text("INSERT INTO categories (name) VALUES (:name)"), {"name": label}
                )
                category_id = result.lastrowid
                name_to_id[label] = category_id
            connection.execute(
                text(
                    "INSERT OR IGNORE INTO book_categories (book_id, category_id) "
                    "VALUES (:book_id, :category_id)"
                ),
                {"book_id": book_id, "category_id": category_id},
            )


# Backwards-compatible alias used during earlier rollout.
ensure_book_link_columns = migrate_books_schema
